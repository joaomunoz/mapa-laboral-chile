"""
<src/Analisis/JOINS/CW_Demanda_Publica/crosswalk.py>
Actualizado 02-11-26 17:02

Estima las vacantes del sector público, para corregir que ENADEL solo vea empresas privadas.

Salidas: Salida/vacantes_publicas_carrera_region.csv y Salida/vacantes_publicas_validacion.csv

Método: V_pub = V_priv × (entradas públicas / entradas privadas), por nivel.
  - Entradas: panel de ENE (cada persona se repite cada 3 meses). Es quien hoy es asalariado y hace 3
    meses no trabajaba como asalariado público ni privado. Se excluyen los cambios entre público y
    privado porque un error de respuesta en la categoría parecería una entrada.
  - Se calibra en vez de usar las entradas como vacantes, porque 4 trimestres de entradas cuentan a la
    misma rotación muchas veces y dan cerca de 11 veces las vacantes privadas estimadas.
  - Supuesto clave: una entrada pública equivale a la misma proporción de vacantes que una privada.

Reparto: el sector público (Adm. pública, Enseñanza, Salud, otros) sale de las entradas. Las carreras
salen de quienes trabajan en el sector público en CASEN, con la distribución territorial de cada carrera
en la tabla de ocupados. La región sale de los asalariados públicos con título en ENE, según dónde trabajan.

Límite: incluye reemplazos de jubilados públicos, por lo que sumarla a las jubilaciones puede contar dos
veces. El Paso 5 trae la versión sin jubilaciones.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers"))
from comun.normalizador import REGIONES  # noqa: E402
from esquema import VACANTES_PUBLICAS_CARRERA_REGION, VALIDACION_PUBLICA  # noqa: E402
import obtener  # noqa: E402

log = logging.getLogger(__name__)
DIR_SALIDA = Path(__file__).parent / "Salida"
FACTOR_10_MESES, N_MINIMO, GL_MINIMO, REMUESTREOS = 3 / 10, 60, 9, 500
NIVELES = ("Tecnico", "Profesional")
ACTIVIDADES_PUBLICAS = {15: "O", 16: "P", 17: "Q"}


def grupo_actividad(serie: pd.Series) -> pd.Series:
    """Adm. pública, Enseñanza y Salud se separan; el resto del empleo público es muy pequeño."""
    return serie.map(ACTIVIDADES_PUBLICAS).fillna("otros")


def transiciones(e: pd.DataFrame) -> pd.DataFrame:
    """Asalariados con título hoy, con su estado 3 meses antes cuando la persona fue encuestada."""
    previo = e[["idrph", "periodo", "estado"]].assign(periodo=lambda d: d["periodo"] + 3).rename(columns={"estado": "estado_previo"})
    d = e[e["nivel_titulo"].notna() & e["estado"].isin(["publico", "privado"])].merge(previo, on=["idrph", "periodo"], how="left")
    t = d[d["estado_previo"].notna()].copy()
    t["entra"] = t["estado_previo"] == "otro"
    t["actividad_grupo"] = grupo_actividad(t["r_p_rev4cl_caenes"])
    return t


def entradas_anuales(t: pd.DataFrame, stock: pd.Series) -> pd.Series:
    """Tasa trimestral de entrada, medida en el panel, aplicada al stock actual y anualizada."""
    entra = t[t["entra"]].groupby(["estado", "nivel_titulo"])["fact_cal"].sum()
    return (entra / t.groupby(["estado", "nivel_titulo"])["fact_cal"].sum()).reindex(stock.index).fillna(0.0) * 4 * stock


def razon_publico_privado(t: pd.DataFrame, stock: pd.Series) -> pd.Series:
    an = entradas_anuales(t, stock)
    return pd.Series({n: an[("publico", n)] / an[("privado", n)] for n in NIVELES})


def margen(t: pd.DataFrame, stock: pd.Series) -> pd.DataFrame:
    """Percentiles 2,5 y 97,5 remuestreando conglomerados: la incertidumbre viene de pocas entradas."""
    rng = np.random.default_rng(2026)
    grupos = {u: g for u, g in t.groupby("conglomerado")}
    llaves = np.array(list(grupos))
    filas = []
    for _ in range(REMUESTREOS):
        x = pd.concat([grupos[u] for u in rng.choice(llaves, len(llaves))], ignore_index=True)
        filas.append(razon_publico_privado(x, stock))
    return pd.DataFrame(filas).quantile([0.025, 0.975])


def mezcla_actividad(t: pd.DataFrame) -> pd.DataFrame:
    x = t[(t["estado"] == "publico") & t["entra"]]
    m = x.groupby(["nivel_titulo", "actividad_grupo"])["fact_cal"].sum()
    return m.div(m.groupby(level="nivel_titulo").transform("sum")).rename("parte").reset_index()


def partes_regionales(e: pd.DataFrame) -> pd.DataFrame:
    """Reparto regional por nivel y actividad; una celda débil usa el total público de la región y nivel."""
    o = e[e["nivel_titulo"].notna() & (e["estado"] == "publico")].copy()
    # La vacante está donde se ubica el empleo; sin ese dato (0,07%), donde vive la persona.
    o["codigo_region"] = o["codigo_region_trabajo"].fillna(o["codigo_region"]).astype(int)
    o["actividad_grupo"] = grupo_actividad(o["r_p_rev4cl_caenes"])
    c = o.groupby(["codigo_region", "nivel_titulo", "actividad_grupo"], as_index=False).agg(
        w=("fact_cal", "sum"), n=("idrph", "nunique"), psu=("conglomerado", "nunique"), h=("estrato", "nunique"))
    c["fiable"] = (c["n"] >= N_MINIMO) & (c["psu"] - c["h"] >= GL_MINIMO)
    reg = o.groupby(["codigo_region", "nivel_titulo"])["fact_cal"].sum().rename("reg").reset_index()
    nac = o.groupby(["nivel_titulo", "actividad_grupo"])["fact_cal"].sum() / o.groupby("nivel_titulo")["fact_cal"].sum()
    filas = []
    for (nivel, actividad), parte in nac.items():
        x = reg[reg["nivel_titulo"] == nivel].merge(c[(c["nivel_titulo"] == nivel) & (c["actividad_grupo"] == actividad)][["codigo_region", "w", "fiable"]], on="codigo_region", how="left")
        x["fiable"] = x["fiable"].astype("boolean").fillna(False).astype(bool)
        x["base"] = np.where(x["fiable"], x["w"], x["reg"] * parte)
        x["parte_region"] = x["base"] / x["base"].sum()
        filas.append(x.assign(nivel_titulo=nivel, actividad_grupo=actividad)[["codigo_region", "nivel_titulo", "actividad_grupo", "parte_region"]])
    return pd.concat(filas, ignore_index=True)


def mezcla_carreras(casen: pd.DataFrame) -> pd.DataFrame:
    casen = casen.assign(actividad_grupo=grupo_actividad(casen["rama1"]))
    m = casen.groupby(["nivel_titulo", "actividad_grupo", "carrera_generica"])["expr"].sum().rename("masa").reset_index()
    m["parte_carrera"] = m["masa"] / m.groupby(["nivel_titulo", "actividad_grupo"])["masa"].transform("sum")
    return m


def repartir(total: pd.Series, actividades: pd.DataFrame, regiones: pd.DataFrame, carreras: pd.DataFrame, ocupados: pd.DataFrame) -> pd.DataFrame:
    o = ocupados.groupby(["codigo_region", "carrera_generica"], as_index=False)["ocupados_estimados"].sum()
    o["territorial"] = o["ocupados_estimados"] / o.groupby("carrera_generica")["ocupados_estimados"].transform("sum")
    filas = []
    x = regiones.merge(actividades, on=["nivel_titulo", "actividad_grupo"])
    x["monto"] = x["nivel_titulo"].map(total) * x["parte"] * x["parte_region"]
    for f in x.itertuples(index=False):
        c = carreras[(carreras["nivel_titulo"] == f.nivel_titulo) & (carreras["actividad_grupo"] == f.actividad_grupo)]
        if c.empty:
            continue
        ter = o[o["codigo_region"] == f.codigo_region].set_index("carrera_generica")["territorial"].reindex(c["carrera_generica"]).fillna(0.0).to_numpy()
        cuota = c["parte_carrera"].to_numpy() * ter
        cuota = cuota if cuota.sum() > 0 else c["parte_carrera"].to_numpy()
        filas.append(pd.DataFrame({"codigo_region": f.codigo_region, "nivel_titulo": f.nivel_titulo,
                                   "carrera_generica": c["carrera_generica"].to_numpy(), "vacantes_publicas": f.monto * cuota / cuota.sum()}))
    r = pd.concat(filas, ignore_index=True).groupby(["codigo_region", "nivel_titulo", "carrera_generica"], as_index=False)["vacantes_publicas"].sum()
    r["nombre_region"] = r["codigo_region"].map(REGIONES)
    return r[list(VACANTES_PUBLICAS_CARRERA_REGION)].astype(VACANTES_PUBLICAS_CARRERA_REGION)


def validar(r: pd.DataFrame, total: pd.Series, actividades: pd.DataFrame) -> None:
    controles = {
        "Reparto conserva el total": np.isclose(r["vacantes_publicas"].sum(), total.sum(), rtol=1e-6),
        "Clave única": not r.duplicated(["codigo_region", "carrera_generica"]).any(),
        "Regiones 1-16": r["codigo_region"].nunique() == 16,
        "Mezcla de actividad suma 1": np.isclose(actividades.groupby("nivel_titulo")["parte"].sum(), 1).all(),
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    if not all(controles.values()):
        raise ValueError("Validaciones fallidas en la demanda pública")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    e = obtener.cargar_ene()
    t = transiciones(e)
    stock = e[e["nivel_titulo"].notna() & e["estado"].isin(["publico", "privado"])].groupby(["estado", "nivel_titulo"])["fact_cal"].sum() * FACTOR_10_MESES
    razon = razon_publico_privado(t, stock)
    rango = margen(t, stock)
    privadas = obtener.cargar_vacantes_privadas()
    total = privadas.reindex(razon.index) * razon
    log.info("Razón público/privado: %s | vacantes públicas: %s", razon.round(3).to_dict(), total.round().to_dict())
    actividades = mezcla_actividad(t)
    r = repartir(total, actividades, partes_regionales(e), mezcla_carreras(obtener.cargar_casen_publico()), obtener.cargar_ocupados())
    validar(r, total, actividades)
    filas = []
    entradas = entradas_anuales(t, stock)
    for n in NIVELES:
        filas += [
            {"prueba": "razon_publico_privado", "grupo": n, "valor": razon[n], "descripcion": "Entradas públicas / privadas"},
            {"prueba": "razon_minima_95", "grupo": n, "valor": rango.loc[0.025, n], "descripcion": "Remuestreo de conglomerados"},
            {"prueba": "razon_maxima_95", "grupo": n, "valor": rango.loc[0.975, n], "descripcion": "Remuestreo de conglomerados"},
            {"prueba": "vacantes_publicas", "grupo": n, "valor": total[n], "descripcion": "Vacantes privadas × razón"},
            {"prueba": "entradas_panel_publico", "grupo": n, "valor": int(t[(t["estado"] == "publico") & (t["nivel_titulo"] == n)]["entra"].sum()), "descripcion": "Casos en la muestra"},
            {"prueba": "entradas_anuales_privadas", "grupo": n, "valor": entradas[("privado", n)], "descripcion": "Se calibran; no son vacantes"},
        ]
    for f in actividades.itertuples():
        filas.append({"prueba": f"parte_actividad_{f.actividad_grupo}", "grupo": f.nivel_titulo, "valor": 100 * f.parte, "descripcion": "% de entradas públicas"})
    v = pd.DataFrame(filas)[list(VALIDACION_PUBLICA)].astype(VALIDACION_PUBLICA)
    DIR_SALIDA.mkdir(exist_ok=True)
    rutas = [(DIR_SALIDA / "vacantes_publicas_carrera_region.csv", r), (DIR_SALIDA / "vacantes_publicas_validacion.csv", v)]
    for ruta, tabla in rutas:
        tabla.to_csv(ruta, sep=";", index=False, encoding="utf-8")
        log.info("CSV generado: %s (%d filas)", ruta.name, len(tabla))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    for ruta, _ in rutas:
        inspeccion_rigurosa(ruta)
