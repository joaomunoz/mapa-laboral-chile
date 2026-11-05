"""
<src/Analisis/JOINS/Carreras_Por_Actividad/crosswalk.py>

Vincula las carreras de MiFuturo con las actividades económicas donde trabajan sus titulados, a nivel nacional.

Salida: Salida/carreras_por_actividad.csv

Decisiones (aprobadas el 02-11-26):
  - Afinidad: al menos 10% de los ocupados de la carrera en la actividad, y al menos el doble de lo normal.
    Son criterios de trabajo, no un estándar externo.
  - Indicios: lo que cumple esos umbrales con poca muestra se conserva con otra etiqueta. Si se ocultara, el
    mapa daría a entender que Ingeniería Civil en Minas no se vincula a la minería.
  - Mínimo de 10 casos para mostrar un indicio: la mitad tenía 4 casos o menos, y uno se apoyaba en 1 solo
    caso. Bajo ese mínimo quedan como indicio_debil. Es un criterio de trabajo, no un estándar estadístico.

Ponderación: el dato de MiFuturo se publica por institución y se resume por carrera según los títulos de
2021-2023, las cohortes de la empleabilidad al primer año. Si una carrera no tiene títulos en esos años,
se usa el promedio simple: es preferible a dejarla sin dato, y se informa cuántas son.

Ingresos: cada año sale de cohortes distintas (año 1: 2021-2023; año 5: 2017-2019), así que no siguen a las
mismas personas. Por eso no deben presentarse como una evolución.

No trabajan: se mide de 22 a 54 años. Con todas las edades pesan los jubilados: Pedagogía Básica
pasa de 9,8% a 35,0%. Incluye desocupados e inactivos, y por eso no equivale a desempleo. No se desglosa porque la
parte con muestra suficiente baja de 63 carreras a cerca de la mitad.

Este vínculo es NACIONAL: no dice cuántos titulados de una carrera hay en una región.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from esquema import CARRERAS_POR_ACTIVIDAD
import obtener

log = logging.getLogger(__name__)

RUTA_SALIDA = Path(__file__).parent / "Salida" / "carreras_por_actividad.csv"
PCT_AFIN_MINIMO, INDICE_AFIN_MINIMO = 10.0, 2.0
CASOS_MINIMOS_INDICIO = 10
ANIOS_COHORTES = (2021, 2023)
ANIO_TITULADOS = 2025
CARRERAS_MIFUTURO = 190
MAX_INSTITUCIONES_ALERTA = 2
Z_95 = 1.96
EDAD_MINIMA, EDAD_MAXIMA = 22, 54
OCUPADO = 1
N_MINIMO, GL_MINIMO, CV_MAXIMO, CV_POCO_FIABLE = 60, 9, 30, 15
CARRERAS_CON_DATO_NO_TRABAJAN = 63
COLUMNAS_MIFUTURO = ["empleabilidad_1er_anio", "ingreso_medio_1er_anio", "ingreso_medio_5to_anio"]


def promedio(grupo: pd.DataFrame, columna: str) -> float:
    """Promedio ponderado por títulos; simple si los casos con dato no tienen títulos en esos años."""
    x = grupo.dropna(subset=[columna])
    if x.empty:
        return np.nan
    return float(np.average(x[columna], weights=x["peso"])) if x["peso"].sum() > 0 else float(x[columna].mean())


def resumir_carreras(mifuturo: pd.DataFrame, titulados: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Deja una fila por carrera con sus datos nacionales de MiFuturo y Titulados."""
    cohortes = titulados[titulados["anio"].between(*ANIOS_COHORTES)]
    pesos = (cohortes.groupby(["codigo_institucion", "carrera_generica"], as_index=False)["total_titulaciones"].sum()
             .rename(columns={"codigo_institucion": "id_institucion", "total_titulaciones": "peso"}))
    m = mifuturo.merge(pesos, on=["id_institucion", "carrera_generica"], how="left", validate="many_to_one").fillna({"peso": 0.0})
    r = pd.DataFrame([{"carrera_generica": carrera, **{c: promedio(g, c) for c in COLUMNAS_MIFUTURO}} for carrera, g in m.groupby("carrera_generica")])
    grupos = m.groupby("carrera_generica")["peso"]
    respaldo = pd.DataFrame({"n_instituciones": grupos.size(), "total": grupos.sum(), "mayor": grupos.max()})
    respaldo["pct_institucion_principal"] = 100 * respaldo["mayor"] / respaldo["total"].where(respaldo["total"] > 0)
    respaldo["alerta_pocas_instituciones"] = respaldo["n_instituciones"] <= MAX_INSTITUCIONES_ALERTA
    r = r.merge(respaldo[["n_instituciones", "pct_institucion_principal", "alerta_pocas_instituciones"]], on="carrera_generica", validate="one_to_one")
    sin_peso = int((respaldo["total"] == 0).sum())
    columnas_titulos = {"total_titulaciones": "titulados_2025", "titulaciones_hombres": "titulados_2025_hombres", "titulaciones_mujeres": "titulados_2025_mujeres"}
    ultimo = titulados[titulados["anio"] == ANIO_TITULADOS].groupby("carrera_generica")[list(columnas_titulos)].sum().rename(columns=columnas_titulos)
    r = r.merge(ultimo, on="carrera_generica", how="left").fillna({c: 0 for c in columnas_titulos.values()})
    return r, sin_peso


def medir_no_trabajan(casen: pd.DataFrame, diseno: pd.DataFrame) -> pd.DataFrame:
    """% de titulados de 22 a 54 años que no trabajan, por carrera, con su error por linealización de Taylor."""
    diseno = diseno.assign(h=diseno.groupby("varstrat")["varunit"].transform("size"))
    filas = []
    for carrera, x in casen[casen["edad"].between(EDAD_MINIMA, EDAD_MAXIMA)].groupby("carrera_generica"):
        no_trabaja = (x["activ"] != OCUPADO).astype(float)
        total = x["expr"].sum()
        p = (x["expr"] * no_trabaja).sum() / total
        y = x.assign(y=x["expr"] * (no_trabaja - p) / total).groupby(["varstrat", "varunit"], as_index=False)["y"].sum()
        g = diseno.merge(y, how="left", on=["varstrat", "varunit"]).fillna({"y": 0.0})
        # Un estrato con un solo conglomerado no permite estimar varianza: no aporta.
        g = g[g["h"] > 1]
        media = g.groupby("varstrat")["y"].transform("mean")
        ee = float((g["h"] / (g["h"] - 1) * (g["y"] - media) ** 2).sum() ** 0.5)
        cv = 100 * ee / p if p > 0 else np.inf
        gl = x["varunit"].nunique() - x["varstrat"].nunique()
        no_fiable = len(x) < N_MINIMO or gl < GL_MINIMO or cv > CV_MAXIMO
        filas.append({"carrera_generica": carrera, "pct_no_trabajan": 100 * p, "pct_no_trabajan_min": 100 * max(p - Z_95 * ee, 0),
                      "pct_no_trabajan_max": 100 * min(p + Z_95 * ee, 1), "titulados_no_trabajan": p * total,
                      "fiabilidad_no_trabajan": "no_fiable" if no_fiable else "poco_fiable" if cv > CV_POCO_FIABLE else "fiable"})
    return pd.DataFrame(filas)


def clasificar_afinidad(t: pd.DataFrame) -> pd.Series:
    cumple = (t["pct_en_carrera"] >= PCT_AFIN_MINIMO) & (t["indice_especializacion"] >= INDICE_AFIN_MINIMO)
    firme = cumple & (t["fiabilidad"] != "no_fiable")
    con_casos = cumple & (t["n_celda"] >= CASOS_MINIMOS_INDICIO)
    return pd.Series(np.select([firme, con_casos, cumple], ["afin", "indicio_sin_muestra", "indicio_debil"], "no_afin"), index=t.index)


def construir(perfil: pd.DataFrame, carreras: pd.DataFrame, no_trabajan: pd.DataFrame) -> pd.DataFrame:
    t = perfil.merge(carreras, on="carrera_generica", how="inner", validate="many_to_one").rename(columns={"area_cine_sies": "area_cine"})
    t = t.merge(no_trabajan, on="carrera_generica", how="left", validate="many_to_one").fillna({"fiabilidad_no_trabajan": "no_fiable"})
    t["afinidad"] = clasificar_afinidad(t)
    t["pct_en_carrera_min"] = (t["pct_en_carrera"] - Z_95 * t["error_estandar"]).clip(lower=0)
    t["pct_en_carrera_max"] = (t["pct_en_carrera"] + Z_95 * t["error_estandar"]).clip(upper=100)
    t = t.rename(columns={"ocupados_expandidos": "ocupados_titulados"})
    return (t[list(CARRERAS_POR_ACTIVIDAD)].astype(CARRERAS_POR_ACTIVIDAD)
            .sort_values(["actividad_caenes", "indice_especializacion"], ascending=[True, False]).reset_index(drop=True))


def validar(t: pd.DataFrame, carreras: pd.DataFrame, perfil: pd.DataFrame, sin_peso: int) -> None:
    """Detiene el proceso si la tabla pierde carreras o contradice su propio criterio."""
    faltan = sorted(set(carreras["carrera_generica"]) - set(t["carrera_generica"]))
    fuera = t[(t["afinidad"] != "no_afin") & ((t["pct_en_carrera"] < PCT_AFIN_MINIMO) | (t["indice_especializacion"] < INDICE_AFIN_MINIMO))]
    fila = lambda c: t[t["carrera_generica"] == c].iloc[0]
    controles = {
        "Clave única": not t.duplicated(["carrera_generica", "actividad_caenes"]).any(),
        "190 carreras resumidas y una sola ausente de P9": len(carreras) == CARRERAS_MIFUTURO and len(faltan) == 1,
        "Filas conservadas de P9": len(t) == perfil["carrera_generica"].isin(carreras["carrera_generica"]).sum(),
        "Empleabilidad completa y en rango 0-100": t["empleabilidad_1er_anio"].between(0, 100).all(),
        "El % queda dentro de su rango": ((t["pct_en_carrera_min"] <= t["pct_en_carrera"]) & (t["pct_en_carrera"] <= t["pct_en_carrera_max"])).all(),
        "Ing. en Minas: 4.327 titulados en Minería": t.loc[(t["carrera_generica"] == "INGENIERIA EN MINAS") & (t["actividad_ciiu"] == "B"), "ocupados_titulados"].eq(4327).all(),
        "56 carreras con alerta de pocas instituciones": int(carreras["alerta_pocas_instituciones"].sum()) == 56,
        "Psicología: 44 instituciones": fila("PSICOLOGIA")["n_instituciones"] == 44,
        "Psicología: 11,6% no trabaja (9.747 personas)": np.isclose(fila("PSICOLOGIA")["pct_no_trabajan"], 11.6, atol=0.05) and np.isclose(fila("PSICOLOGIA")["titulados_no_trabajan"], 9747, atol=1),
        "63 carreras con dato usable de no trabajan": (t.drop_duplicates("carrera_generica")["fiabilidad_no_trabajan"] != "no_fiable").sum() == CARRERAS_CON_DATO_NO_TRABAJAN,
        "Afines y fiabilidad coherentes": (t.loc[t["afinidad"] == "afin", "fiabilidad"] != "no_fiable").all() and t.loc[t["afinidad"].str.startswith("indicio"), "fiabilidad"].eq("no_fiable").all(),
        "Indicios mostrados con al menos 10 casos, y débiles con menos": (t.loc[t["afinidad"] == "indicio_sin_muestra", "n_celda"] >= CASOS_MINIMOS_INDICIO).all() and (t.loc[t["afinidad"] == "indicio_debil", "n_celda"] < CASOS_MINIMOS_INDICIO).all(),
        "Ningún vínculo bajo los umbrales": fuera.empty,
        "Psicología: 8.212 títulos y 59,35% de empleabilidad": fila("PSICOLOGIA")["titulados_2025"] == 8212 and np.isclose(fila("PSICOLOGIA")["empleabilidad_1er_anio"], 59.3518, atol=0.001),
        "Medicina: 2.560 títulos": fila("MEDICINA")["titulados_2025"] == 2560,
        "Títulos por sexo: hombres y mujeres no superan el total": (t["titulados_2025_hombres"] + t["titulados_2025_mujeres"] <= t["titulados_2025"]).all(),
        "Enfermería: 845 hombres y 4.123 mujeres": (fila("ENFERMERIA")["titulados_2025_hombres"], fila("ENFERMERIA")["titulados_2025_mujeres"]) == (845, 4123),
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    afin = t[t["afinidad"] == "afin"]
    log.info("  [i] Afinidad: %s", t["afinidad"].value_counts().to_dict())
    log.info("  [i] Carreras: %d en la tabla; %d con vínculo afín; ausente de P9: %s", t["carrera_generica"].nunique(), afin["carrera_generica"].nunique(), faltan)
    log.info("  [i] Carreras con promedio simple: %d; sin ingreso: %d", sin_peso, t.drop_duplicates("carrera_generica")["ingreso_medio_5to_anio"].isna().sum())
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    perfil = obtener.cargar_perfil()
    carreras, sin_peso = resumir_carreras(obtener.cargar_mifuturo(), obtener.cargar_titulados())
    tabla = construir(perfil, carreras, medir_no_trabajan(obtener.cargar_casen(), obtener.cargar_diseno()))
    validar(tabla, carreras, perfil, sin_peso)
    RUTA_SALIDA.parent.mkdir(exist_ok=True)
    tabla.to_csv(RUTA_SALIDA, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", RUTA_SALIDA.name, len(tabla))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(RUTA_SALIDA)
