"""
<src/Analisis/Archivo/CW_Ocupados_Carrera_Region_Actividad/validar_reparto.py>

Evalúa si el reparto predice lo que no vio.

Salida: Salida/ocupados_carrera_region_actividad_validacion.csv

Prueba 1, región oculta: el perfil se recalcula sin la región evaluada y se compara con lo que
CASEN mide directamente allí, por carrera (con al menos 30 casos en esa región) y por total de
actividad. Ocultarla evita que la Región Metropolitana, que pesa la mitad del país, se prediga a
sí misma. ajuste_ene_NNN indica cuánto del total ENE de titulados por actividad se incorpora (000
es el perfil nacional solo); peso_actividad_elegido es el método que usa crosswalk.py.
Prueba 2, ocupación: predice el gran grupo con stock y perfil, y lo compara con b1 de ENE, que
no se usa en el reparto. Es la prueba que no pasó el piloto de P3.
Prueba 3, mezcla: compara la mezcla de carreras de SIES (por sede) con la de CASEN (residencia).

Disimilitud = puntos de 100 que habría que mover para igualar dos repartos. El "piso de ruido"
indica cuánto daría una predicción perfecta, porque la medición directa también tiene error
(remuestreo de personas, que ignora conglomerados y por lo tanto es un mínimo).
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

DIR = Path(__file__).resolve().parent
DIR_PUENTES = DIR.parents[1] / "Puentes_de_mapeo"
sys.path.insert(0, str(DIR))
import crosswalk  # noqa: E402
import obtener  # noqa: E402
from esquema import VALIDACION_REPARTO  # noqa: E402

# Los dos módulos se llaman esquema: P7 debe resolver el suyo.
del sys.modules["esquema"]
sys.path.insert(0, str(DIR_PUENTES))
import P7_perfil_carrera_actividad_ocupacion as p7  # noqa: E402

log = logging.getLogger(__name__)
RUTA = DIR / "Salida" / "ocupados_carrera_region_actividad_validacion.csv"
N_DIRECTO = 30
ACTIVIDADES = range(1, 22)
REMUESTREOS = 200
PESOS_ENE = (0.0, 0.25, 0.5, 0.75, 1.0)


def disimilitud(a: np.ndarray, b: np.ndarray) -> float:
    return 50 * np.abs(a - b).sum()


def resumir(prueba: str, df: pd.DataFrame) -> list[dict]:
    """Resume por variante en total, RM y resto de regiones."""
    filas = []
    for (variante), g in df.groupby("variante"):
        for grupo, x in (("total", g), ("metropolitana", g[g["codigo_region"] == 13]), ("otras_regiones", g[g["codigo_region"] != 13])):
            if len(x):
                filas.append({"prueba": prueba, "variante": variante, "grupo": grupo, "n_comparaciones": len(x),
                              "disimilitud_media": np.average(x["d"], weights=x["peso"]), "disimilitud_mediana": x["d"].median()})
    return filas


def region_oculta(o: pd.DataFrame, cat: pd.DataFrame, stock: pd.DataFrame, ene: pd.DataFrame) -> list[dict]:
    """Prueba 1: compara cada variante contra CASEN en la región, por carrera y por total de actividad."""
    rng = np.random.default_rng(2026)
    margenes = {e: crosswalk.margen_ene(ene, e) for e in ("ene_directo", "fiabilidad")}
    carreras_nivel = cat.set_index("carrera_generica")["nivel_titulo"]
    pesos_regionales = crosswalk.cargar_pesos()
    filas, totales = [], []
    for region in sorted(o["codigo_region"].unique()):
        resto = o[o["codigo_region"] != region]
        directa = o[(o["codigo_region"] == region) & o["actividad_caenes"].notna() & o["carrera_generica"].isin(carreras_nivel.index)]
        tabla = crosswalk.perfil_a_tabla(p7.perfiles(resto, cat))
        st = stock[stock["codigo_region"] == region].rename(columns={"stock_sies": "peso"})
        mezcla_casen = directa.groupby("carrera_generica", as_index=False)["expr"].sum().rename(columns={"expr": "peso"}).assign(codigo_region=region)
        variantes = [(f"ajuste_ene_{int(100 * lam):03d}", st, "ene_directo", lam, None) for lam in PESOS_ENE]
        variantes += [("ajuste_ene_100_con_fiabilidad", st, "fiabilidad", 1.0, None),
                      ("peso_actividad_elegido", st, "ene_directo", 0.0, pesos_regionales),
                      ("peso_actividad_mezcla_casen", mezcla_casen, "ene_directo", 0.0, pesos_regionales)]
        pred, ag = {}, {}
        for nombre, mezcla, margen, lam, pes in variantes:
            r = crosswalk.repartir(mezcla, tabla, margenes[margen][margenes[margen]["codigo_region"] == region], cat, pes, lam)
            t = r.pivot_table(index="carrera_generica", columns="actividad_caenes", values="ocupados_estimados", fill_value=0.0).reindex(columns=ACTIVIDADES, fill_value=0.0)
            pred[nombre] = t.div(t.sum(axis=1), axis=0)
            ag[nombre] = r.groupby(["nivel_titulo", "actividad_caenes"])["ocupados_estimados"].sum()
        margen = margenes["ene_directo"]
        margen = margen[margen["codigo_region"] == region]

        for nivel in ("Tecnico", "Profesional"):
            x = directa[directa["carrera_generica"].map(carreras_nivel) == nivel]
            real = x.groupby("actividad_caenes")["expr"].sum().reindex(ACTIVIDADES, fill_value=0.0).to_numpy(dtype=float)
            comun = {"codigo_region": region, "peso": real.sum()}
            real = real / real.sum()
            enes = margen[margen["nivel_titulo"] == nivel].set_index("actividad_caenes")["ocupados"].reindex(ACTIVIDADES, fill_value=0.0).to_numpy(dtype=float)
            totales.append({**comun, "variante": "ene_directo", "d": disimilitud(real, enes / enes.sum())})
            for nombre, serie in ag.items():
                a = serie[nivel].reindex(ACTIVIDADES, fill_value=0.0).to_numpy(dtype=float)
                totales.append({**comun, "variante": nombre, "d": disimilitud(real, a / a.sum())})

        for carrera, g in directa.groupby("carrera_generica"):
            if len(g) < N_DIRECTO:
                continue
            real = g.groupby("actividad_caenes")["expr"].sum().reindex(ACTIVIDADES, fill_value=0.0).to_numpy(dtype=float)
            real = real / real.sum()
            comun = {"codigo_region": region, "carrera": carrera, "peso": g["expr"].sum()}
            indep = margen[margen["nivel_titulo"] == carreras_nivel[carrera]].set_index("actividad_caenes")["ocupados"].reindex(ACTIVIDADES, fill_value=0.0).to_numpy(dtype=float)
            filas.append({**comun, "variante": "actividad_igual_para_todas", "d": disimilitud(real, indep / indep.sum())})
            for nombre, t in pred.items():
                if carrera in t.index:
                    filas.append({**comun, "variante": nombre, "d": disimilitud(real, t.loc[carrera].to_numpy(dtype=float))})
            pesos = g["expr"].to_numpy(dtype=float)
            sect = g["actividad_caenes"].to_numpy(dtype=int) - 1
            ruido = []
            for _ in range(REMUESTREOS):
                i = rng.integers(0, len(g), len(g))
                m = np.bincount(sect[i], weights=pesos[i], minlength=21)
                ruido.append(disimilitud(real, m / m.sum()))
            filas.append({**comun, "variante": "piso_de_ruido", "d": float(np.mean(ruido))})
    return resumir("region_oculta_por_carrera", pd.DataFrame(filas)) + resumir("region_oculta_total_actividad", pd.DataFrame(totales))


def ocupacion(stock: pd.DataFrame, perfil: pd.DataFrame, cat: pd.DataFrame, ene: pd.DataFrame) -> list[dict]:
    """Prueba 2: gran grupo predicho frente a b1 de ENE, por nivel y región."""
    p = perfil[perfil["dimension"] == "grupo_ocupacion"][["carrera_generica", "grupo_ocupacion", "pct"]]
    x = stock.merge(cat[["carrera_generica", "nivel_titulo"]], on="carrera_generica").merge(p, on="carrera_generica")
    x["pred"] = x["stock_sies"] * x["pct"] / 100
    filas = []
    grupos = range(1, 11)
    e = ene.dropna(subset=["b1"])
    nac = x.groupby(["nivel_titulo", "grupo_ocupacion"])["pred"].sum()
    enen = e.groupby(["nivel_titulo", "b1"])["fact_cal"].sum()
    salida = []
    for nivel in ("Tecnico", "Profesional"):
        a = nac[nivel].reindex(grupos, fill_value=0.0).to_numpy(dtype=float)
        b = enen[nivel].reindex(grupos, fill_value=0.0).to_numpy(dtype=float)
        a, b = a / a.sum(), b / b.sum()
        salida.append({"prueba": "grupo_ocupacion", "variante": "perfil_p7", "grupo": f"nacional_{nivel}", "n_comparaciones": 1,
                       "disimilitud_media": disimilitud(a, b), "disimilitud_mediana": disimilitud(a, b)})
        log.info("  Ocupación %s: predicho %s | ENE %s", nivel, np.round(100 * a, 1).tolist(), np.round(100 * b, 1).tolist())
        for region in sorted(x["codigo_region"].unique()):
            a = x[(x["codigo_region"] == region) & (x["nivel_titulo"] == nivel)].groupby("grupo_ocupacion")["pred"].sum().reindex(grupos, fill_value=0.0).to_numpy(dtype=float)
            b_s = e[(e["codigo_region"] == region) & (e["nivel_titulo"] == nivel)].groupby("b1")["fact_cal"].sum().reindex(grupos, fill_value=0.0)
            if a.sum() and b_s.sum():
                filas.append({"codigo_region": region, "variante": f"perfil_p7_{nivel}", "peso": b_s.sum(),
                              "d": disimilitud(a / a.sum(), b_s.to_numpy(dtype=float) / b_s.sum())})
    return salida + resumir("grupo_ocupacion", pd.DataFrame(filas))


def mezcla_carreras(o: pd.DataFrame, stock: pd.DataFrame, cat: pd.DataFrame) -> list[dict]:
    """Prueba 3: ¿el stock por sede representa las carreras de quienes residen en la región?"""
    filas = []
    nacional = stock.groupby("carrera_generica")["stock_sies"].sum()
    for region in sorted(o["codigo_region"].unique()):
        aqui = o[o["codigo_region"] == region].groupby("carrera_generica")["expr"].sum()
        sede = stock[stock["codigo_region"] == region].set_index("carrera_generica")["stock_sies"]
        todas = aqui.index.union(sede.index).union(nacional.index)
        c = aqui.reindex(todas, fill_value=0.0).to_numpy(dtype=float)
        for variante, serie in (("stock_de_la_region", sede), ("stock_nacional", nacional)):
            s = serie.reindex(todas, fill_value=0.0).to_numpy(dtype=float)
            filas.append({"codigo_region": region, "variante": variante, "peso": aqui.sum(),
                          "d": disimilitud(c / c.sum(), s / s.sum())})
    return resumir("mezcla_carreras", pd.DataFrame(filas))


def validar_reparto() -> Path:
    o = p7.cargar_ocupados()
    perfil, stock, ene = obtener.cargar_perfil(), obtener.cargar_stock(), obtener.cargar_ene()
    cat = perfil[perfil["dimension"] == "actividad_economica"].drop_duplicates("carrera_generica")[["carrera_generica", "nivel_titulo", "area_cine_sies"]]
    filas = region_oculta(o, cat, stock, ene) + ocupacion(stock, perfil, cat, ene) + mezcla_carreras(o, stock, cat)
    tabla = pd.DataFrame(filas)[list(VALIDACION_REPARTO)].astype(VALIDACION_REPARTO)
    tabla.to_csv(RUTA, sep=";", index=False, encoding="utf-8")
    return RUTA


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ruta = validar_reparto()
    sys.path.insert(0, str(DIR.parents[2] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(ruta)
