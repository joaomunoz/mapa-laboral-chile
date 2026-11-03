"""
<src/Analisis/JOINS/CW_Competencia_Desocupados/crosswalk.py>
Actualizado 02-11-26 16:40

Paso 2 del índice: estima Desocupados por carrera y región, parte del denominador de la fórmula.

Entradas: ENE, SIES y P4 (ver obtener.py); CASEN y P5 solo para validar.
Salidas:  Salida/desocupados_carrera_region.csv
          Salida/desocupados_region_titulo.csv
          Salida/desocupados_validacion.csv

Método, aprobado por el usuario el 01-11-26:
  1. Población: desocupados ENE (cae_especifico 8-9) con título superior, de 22 a 54 años. Ese rango
     cubre el 99% del stock SIES, que solo tiene titulaciones desde 2007.
  2. Título: según cine11_1d y P4. Se usa cine11_1d porque registra lo COMPLETADO: quien no
     terminó un magíster sigue compitiendo con su título profesional.
  3. Nivel: 10 meses con factor 3/10, porque fact_cal representa a la población en 3 meses. Da el
     promedio de un trimestre con más casos, pero no calza con un boletín puntual.
  4. Fiabilidad (estrategia a): la celda región × título se usa si no es no_fiable; el resto del
     total regional se reparte con la mezcla nacional de títulos.
  5. Reparto (revisado 02-11-26): peso = (50% stock SIES de la región + 50% activos CASEN de la carrera
     con su presencia regional) × tasa de desempleo. Solo usa la tasa propia si difiere de la de su nivel
     en más de 2 errores estándar, con al menos 100 activos; las demás usan la del nivel.

Por qué ese reparto: repartir solo por stock supone igual desempleo y asignaba unos 3.000 desocupados
a Medicina, cuya tasa es 0,5%. Pero usar todas las tasas agrega más ruido del que corrige, porque cada
carrera tiene pocos desocupados en la muestra. Por eso solo se aplican las diferencias claras. La
mezcla con CASEN corrige que SIES parte en 2007. Validado prediciendo una mitad de la muestra con la
otra. No usa empleabilidad, que el índice ya multiplica. desocupados_solo_stock conserva lo anterior.

Postítulo y posgrado se reparten, pero entra_al_indice = False: el índice es de pregrado terminal.
Límites: el stock usa la región de la SEDE y los desocupados la de RESIDENCIA. La presencia regional de
cada carrera (mitad CASEN del reparto) viene de la tabla de ocupados, ubicada por región de trabajo.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers"))
from comun.normalizador import REGIONES  # noqa: E402
from esquema import (  # noqa: E402
    DESOCUPADOS_CARRERA_REGION,
    DESOCUPADOS_REGION_TITULO,
    TITULOS_PREGRADO,
    VALIDACION_DESOCUPADOS,
)
import obtener  # noqa: E402

log = logging.getLogger(__name__)

DIR_SALIDA = Path(__file__).parent / "Salida"
FACTOR_10_MESES = 3 / 10
EDAD_MIN, EDAD_MAX = 22, 54
N_MINIMO, GL_MINIMO, CV_FIABLE, CV_MAXIMO = 60, 9, 15.0, 30.0
MESES_JAS = ["2026-07", "2026-08", "2026-09"]
REMUESTREOS = 500
PESO_STOCK, Z_TASA, N_TASA, PARTICIONES, EFECTO_DISENO = 0.5, 2.0, 100, 30, 1.8


def titulo_de_fila(cine: pd.Series, nivel: pd.Series) -> pd.Series:
    """Título más alto completado, con la llave de P4 (cine 4 separa profesional de postítulo)."""
    t = cine.map({3: "Tecnico_Superior", 4: "Profesional", 5: "Magister", 6: "Doctorado"})
    return t.mask((cine == 4) & (nivel == 10), "Postitulo")


def poblacion(ene: pd.DataFrame) -> pd.DataFrame:
    """Desocupados con título, en el rango de edad compatible con el stock."""
    d = ene[ene["cae_especifico"].between(8, 9) & ene["cine11_1d"].ge(3)].copy()
    d["titulo_comun"] = titulo_de_fila(d["cine11_1d"], d["nivel"])
    total = d["fact_cal"].sum() * FACTOR_10_MESES
    d = d[d["edad"].between(EDAD_MIN, EDAD_MAX)]
    log.info("Desocupados con título: %.0f; de %d a %d años: %.0f (%.1f%%)", total, EDAD_MIN, EDAD_MAX,
             d["fact_cal"].sum() * FACTOR_10_MESES, 100 * d["fact_cal"].sum() * FACTOR_10_MESES / total)
    return d


def error_total(g: pd.DataFrame, psu: pd.Series) -> float:
    """
    Error estándar de un total por linealización, a nivel de conglomerado.

    Agrupar por conglomerado también absorbe que una persona se repita en varios meses. Los
    conglomerados sin casos cuentan en n_h porque el dominio se estima sobre todo el diseño.
    """
    z = g.groupby(["estrato", "conglomerado"], sort=False)["fact_cal"].sum() * FACTOR_10_MESES
    h = z.groupby(level="estrato", sort=False).agg(s="sum", s2=lambda v: (v**2).sum())
    n_h = psu.reindex(h.index).to_numpy(dtype=float)
    aporte = np.where(n_h > 1, n_h / np.maximum(n_h - 1, 1) * (h["s2"] - h["s"]**2 / n_h), 0.0)
    return float(np.sqrt(aporte.sum()))


def clasificar(n: int, gl: int, cv: float) -> str:
    if n < N_MINIMO or gl < GL_MINIMO or cv > CV_MAXIMO:
        return "no_fiable"
    return "poco_fiable" if cv > CV_FIABLE else "fiable"


def celdas(d: pd.DataFrame, ene: pd.DataFrame) -> pd.DataFrame:
    """Calcula cada celda región × título y aplica la estrategia (a) para la no fiable."""
    psu = ene[["estrato", "conglomerado"]].drop_duplicates().groupby("estrato").size()
    log.info("Diseño ENE: %d estratos, %d conglomerados, %d estratos con uno solo",
             len(psu), psu.sum(), int((psu == 1).sum()))
    filas = []
    for (region, titulo), g in d.groupby(["codigo_region", "titulo_comun"]):
        n = g["idrph"].nunique()
        gl = g["conglomerado"].nunique() - g["estrato"].nunique()
        total = g["fact_cal"].sum() * FACTOR_10_MESES
        se = error_total(g, psu)
        cv = 100 * se / total
        filas.append({"codigo_region": region, "titulo_comun": titulo, "n_personas": n, "gl": gl,
                      "desocupados_directo": total, "error_estandar": se, "cv_pct": cv,
                      "fiabilidad_celda": clasificar(n, gl, cv)})
    c = pd.DataFrame(filas)
    c["origen_celda"] = np.where(c["fiabilidad_celda"] == "no_fiable", "mezcla_nacional", "celda_propia")
    mezcla = c.groupby("titulo_comun")["desocupados_directo"].sum()
    c["desocupados_usados"] = c["desocupados_directo"]
    for region, g in c.groupby("codigo_region"):
        debiles = g[g["origen_celda"] == "mezcla_nacional"]
        if len(debiles):
            pesos = debiles["titulo_comun"].map(mezcla)
            c.loc[debiles.index, "desocupados_usados"] = debiles["desocupados_directo"].sum() * pesos / pesos.sum()
    c["nombre_region"] = c["codigo_region"].map(REGIONES)
    return c[list(DESOCUPADOS_REGION_TITULO)].astype(DESOCUPADOS_REGION_TITULO)


def tasas_usadas(razon: pd.DataFrame, casen: pd.DataFrame) -> pd.DataFrame:
    """Tasa por carrera: la propia solo si es claramente distinta de la de su nivel."""
    a = casen[casen["activ"].isin([1, 2])]
    nivel = a[a["activ"] == 2].groupby("nivel_titulo")["expr"].sum() / a.groupby("nivel_titulo")["expr"].sum() * 100
    r = razon[["carrera_generica", "nivel_titulo", "tasa_desempleo_pct", "error_estandar", "n_activos"]].copy()
    r["tasa_nivel"] = r["nivel_titulo"].map(nivel)
    # Sin desocupados el error sale 0: esa carrera no se considera distinta por sí sola.
    clara = (r["n_activos"] >= N_TASA) & (r["error_estandar"] > 0) & ((r["tasa_desempleo_pct"] - r["tasa_nivel"]).abs() > Z_TASA * r["error_estandar"])
    r["origen_tasa"] = np.where(clara, "propia", "nivel")
    r["tasa_desempleo_usada"] = np.where(clara, r["tasa_desempleo_pct"], r["tasa_nivel"])
    return r.set_index("carrera_generica"), nivel


def pesos_casen(casen: pd.DataFrame, ocupados: pd.DataFrame) -> pd.DataFrame:
    """Activos de la carrera en CASEN, llevados a cada región según su presencia territorial."""
    act = casen[casen["activ"].isin([1, 2])].groupby("carrera_generica")["expr"].sum().rename("activos")
    o = ocupados.groupby(["codigo_region", "carrera_generica"], as_index=False)["ocupados_estimados"].sum()
    o["territorial"] = o["ocupados_estimados"] / o.groupby("carrera_generica")["ocupados_estimados"].transform("sum")
    o = o.merge(act, left_on="carrera_generica", right_index=True)
    o["casen"] = o["activos"] * o["territorial"]
    return o[["codigo_region", "carrera_generica", "casen"]]


def repartir(c: pd.DataFrame, stock: pd.DataFrame, tasas: tuple[pd.DataFrame, pd.Series], casen_reg: pd.DataFrame) -> pd.DataFrame:
    """Reparte cada celda. Postítulo y posgrado siguen solo por stock: no tienen perfil en CASEN."""
    tabla_tasas, tasa_nivel = tasas
    nivel_de = {"Tecnico_Superior": "Tecnico", "Profesional": "Profesional"}
    nacional = stock.groupby(["titulo_comun", "carrera_generica"], as_index=False)["stock_sies"].sum()
    partes = []
    for fila in c.itertuples(index=False):
        s = stock[(stock["codigo_region"] == fila.codigo_region) & (stock["titulo_comun"] == fila.titulo_comun)]
        origen = "stock_region"
        base = s
        if s["stock_sies"].sum() == 0:
            base, origen = nacional[nacional["titulo_comun"] == fila.titulo_comun], "stock_nacional"
        x = base[["carrera_generica", "stock_sies"]].copy()
        x["share_stock"] = x["stock_sies"] / x["stock_sies"].sum()
        if fila.titulo_comun in TITULOS_PREGRADO:
            nivel = nivel_de[fila.titulo_comun]
            cas = casen_reg[casen_reg["codigo_region"] == fila.codigo_region].set_index("carrera_generica")["casen"].reindex(x["carrera_generica"]).fillna(0.0).to_numpy()
            mezcla = PESO_STOCK * x["share_stock"].to_numpy() + (1 - PESO_STOCK) * (cas / cas.sum() if cas.sum() > 0 else x["share_stock"].to_numpy())
            t = tabla_tasas.reindex(x["carrera_generica"])
            x["tasa_desempleo_usada"] = t["tasa_desempleo_usada"].fillna(tasa_nivel[nivel]).to_numpy()
            x["origen_tasa"] = t["origen_tasa"].fillna("nivel").to_numpy()
            cuota = mezcla * x["tasa_desempleo_usada"].to_numpy()
        else:
            x["tasa_desempleo_usada"], x["origen_tasa"] = np.nan, "sin_ajuste"
            cuota = x["share_stock"].to_numpy()
        x["share_usada"] = cuota / cuota.sum()
        x["desocupados_estimados"] = fila.desocupados_usados * x["share_usada"]
        x["desocupados_solo_stock"] = fila.desocupados_usados * x["share_stock"]
        if origen == "stock_nacional":
            x["stock_sies"] = 0
        partes.append(x.assign(codigo_region=fila.codigo_region, nombre_region=fila.nombre_region,
                               titulo_comun=fila.titulo_comun, origen_reparto=origen,
                               origen_celda=fila.origen_celda, fiabilidad_celda=fila.fiabilidad_celda))
    r = pd.concat(partes, ignore_index=True)
    r["entra_al_indice"] = r["titulo_comun"].isin(TITULOS_PREGRADO)
    return r[list(DESOCUPADOS_CARRERA_REGION)].astype(DESOCUPADOS_CARRERA_REGION)


def disimilitud(a: pd.Series, b: pd.Series) -> float:
    i = a.index.union(b.index)
    a, b = a.reindex(i, fill_value=0.0), b.reindex(i, fill_value=0.0)
    return float(50 * (a / a.sum() - b / b.sum()).abs().sum())


def validar_con_casen(r: pd.DataFrame, casen: pd.DataFrame) -> pd.DataFrame:
    """¿La mezcla de carreras repartida se parece a la que CASEN mide en sus desocupados?"""
    rng = np.random.default_rng(2026)
    filas = []
    for titulo in TITULOS_PREGRADO:
        c = casen[casen["titulo_comun"] == titulo]
        des = c[c["activ"] == 2]
        real = des.groupby("carrera_generica")["expr"].sum()
        pred = r[r["titulo_comun"] == titulo].groupby("carrera_generica")["desocupados_estimados"].sum()
        tasa = c.groupby("carrera_generica").apply(lambda g: pd.Series({
            "n": g["activ"].isin([1, 2]).sum(),
            "u": 100 * g.loc[g["activ"] == 2, "expr"].sum() / g.loc[g["activ"].isin([1, 2]), "expr"].sum(),
        }), include_groups=False)
        tasa = tasa[tasa["n"] >= 200]
        pesos, carrera = des["expr"].to_numpy(dtype=float), des["carrera_generica"].to_numpy()
        ruido = []
        for _ in range(REMUESTREOS):
            i = rng.integers(0, len(des), len(des))
            ruido.append(disimilitud(real, pd.Series(pesos[i]).groupby(carrera[i]).sum()))
        filas += [
            {"prueba": "casos_casen", "grupo": titulo, "valor": len(des), "descripcion": "Desocupados en la muestra CASEN"},
            {"prueba": "disimilitud_mezcla", "grupo": titulo, "valor": disimilitud(real, pred),
             "descripcion": "Puntos de 100 entre la mezcla repartida y la de CASEN"},
            {"prueba": "piso_de_ruido", "grupo": titulo, "valor": float(np.mean(ruido)),
             "descripcion": "Mínimo esperable por tamaño de muestra"},
            {"prueba": "desempleo_minimo_por_carrera", "grupo": titulo, "valor": tasa["u"].min(),
             "descripcion": f"En {len(tasa)} carreras con 200 o más activos"},
            {"prueba": "desempleo_maximo_por_carrera", "grupo": titulo, "valor": tasa["u"].max(),
             "descripcion": f"En {len(tasa)} carreras con 200 o más activos"},
        ]
        log.info("  %s, tasa por carrera: %s", titulo, tasa["u"].sort_values().round(1).to_dict())
    return pd.DataFrame(filas)[list(VALIDACION_DESOCUPADOS)].astype(VALIDACION_DESOCUPADOS)


def prueba_mitades(casen: pd.DataFrame, r: pd.DataFrame) -> pd.DataFrame:
    """Predice los desocupados de una mitad de la muestra usando la otra, sin tocar la mitad evaluada."""
    a = casen[casen["activ"].isin([1, 2])]
    stock = r[r["entra_al_indice"]].groupby(["titulo_comun", "carrera_generica"])["desocupados_solo_stock"].sum()
    rng = np.random.default_rng(2026)
    u = a["varunit"].unique()
    res = {(t, v): [] for t in TITULOS_PREGRADO for v in ("solo_stock", "revisado")}
    for _ in range(PARTICIONES):
        elegidos = set(rng.choice(u, len(u) // 2, replace=False))
        x, y = a[a["varunit"].isin(elegidos)], a[~a["varunit"].isin(elegidos)]
        for titulo, nivel in zip(TITULOS_PREGRADO, ("Tecnico", "Profesional")):
            s = stock[titulo]
            xn = x[x["nivel_titulo"] == nivel]
            un = xn.loc[xn["activ"] == 2, "expr"].sum() / xn["expr"].sum()
            g = xn.groupby("carrera_generica").apply(lambda v: pd.Series({"n": len(v), "act": v["expr"].sum(), "u": v.loc[v["activ"] == 2, "expr"].sum() / v["expr"].sum()}), include_groups=False).reindex(s.index)
            se = np.sqrt(EFECTO_DISENO * un * (1 - un) / g["n"].replace(0, np.nan))
            clara = (g["n"] >= N_TASA) & ((g["u"] - un).abs() > Z_TASA * se)
            tasa = g["u"].where(clara, un).fillna(un)
            act = g["act"].fillna(0.0)
            pred = (PESO_STOCK * s / s.sum() + (1 - PESO_STOCK) * act / act.sum()) * tasa
            real = y[(y["nivel_titulo"] == nivel) & (y["activ"] == 2)].groupby("carrera_generica")["expr"].sum()
            res[(titulo, "solo_stock")].append(disimilitud(real, s))
            res[(titulo, "revisado")].append(disimilitud(real, pred))
    return pd.DataFrame([{"prueba": f"mitades_{v}", "grupo": t, "valor": float(np.mean(x)), "descripcion": f"Disimilitud promedio en {PARTICIONES} particiones; menos es mejor"} for (t, v), x in res.items()])[list(VALIDACION_DESOCUPADOS)].astype(VALIDACION_DESOCUPADOS)


def validar(r: pd.DataFrame, c: pd.DataFrame, d: pd.DataFrame, ene: pd.DataFrame) -> None:
    """Detiene el proceso si el reparto pierde personas o rompe la escala."""
    jas = ene[ene["mes"].isin(MESES_JAS) & ene["cae_especifico"].between(8, 9)]["fact_cal"].sum()
    todos = ene[ene["cae_especifico"].between(8, 9)]["fact_cal"].sum() * FACTOR_10_MESES
    objetivo = d["fact_cal"].sum() * FACTOR_10_MESES
    por_region = c.groupby("codigo_region")[["desocupados_directo", "desocupados_usados"]].sum()
    por_celda = r.groupby(["codigo_region", "titulo_comun"])["desocupados_estimados"].sum().reset_index().merge(
        c, on=["codigo_region", "titulo_comun"])
    controles = {
        "Clave única": not r.duplicated(["codigo_region", "titulo_comun", "carrera_generica"]).any(),
        "Regiones 1-16": r["codigo_region"].nunique() == 16,
        "Estrategia (a) conserva cada total regional": np.isclose(por_region["desocupados_directo"], por_region["desocupados_usados"]).all(),
        "Reparto conserva cada celda": np.isclose(por_celda["desocupados_estimados"], por_celda["desocupados_usados"]).all(),
        "Reparto conserva el total": np.isclose(r["desocupados_estimados"].sum(), objetivo),
        "Reparto anterior conserva el total": np.isclose(r["desocupados_solo_stock"].sum(), objetivo),
        "Escala de 10 meses cercana al trimestre JAS (±15%)": abs(todos / jas - 1) <= 0.15,
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    log.info("  [i] Todos los desocupados: 10 meses × 3/10 = %.0f; JAS = %.0f", todos, jas)
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ene = obtener.cargar_ene()
    d = poblacion(ene)
    c = celdas(d, ene)
    casen = obtener.cargar_casen()
    r = repartir(c, obtener.cargar_stock(), tasas_usadas(obtener.cargar_razon(), casen), pesos_casen(casen, obtener.cargar_ocupados()))
    validar(r, c, d, ene)
    v = pd.concat([validar_con_casen(r, casen), prueba_mitades(casen, r)], ignore_index=True)
    DIR_SALIDA.mkdir(exist_ok=True)
    rutas = [DIR_SALIDA / "desocupados_carrera_region.csv", DIR_SALIDA / "desocupados_region_titulo.csv", DIR_SALIDA / "desocupados_validacion.csv"]
    for ruta, tabla in zip(rutas, (r, c, v)):
        tabla.to_csv(ruta, sep=";", index=False, encoding="utf-8")
        log.info("CSV generado: %s (%d filas)", ruta.name, len(tabla))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    for ruta in rutas:
        inspeccion_rigurosa(ruta)
