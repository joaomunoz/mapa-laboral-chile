"""
<src/Analisis/Calculos_control/ocupados_region_actividad_categoria/crosswalk.py>
Actualizado 02-11-26 16:40

Cuenta a TODOS los ocupados por región, actividad, categoría en la ocupación y nivel de título.

Salida: Salida/ocupados_region_actividad_categoria.csv

Es una tabla de control: entrega valores medidos para revisar otros cálculos y no entra a la fórmula.
Conserva cada celda, aunque tenga una sola persona encuestada, para que la suma regional dé el total
nacional (idea del usuario, 02-11-26). La fiabilidad indica cuáles pueden leerse solas.

Nivel: cine11_1d, que registra lo completado. Quien no informa cine11_1d queda en Sin_titulo, porque
no acredita un título superior; los totales por nivel lo informan por separado en el registro.
Error: linealización de Taylor del total con conglomerado y estrato, sobre todo el diseño de ENE.
"""

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import obtener
from esquema import CATEGORIA_POR_CODIGO, OCUPADOS_REGION_ACTIVIDAD_CATEGORIA

log = logging.getLogger(__name__)
RUTA = Path(__file__).parent / "Salida" / "ocupados_region_actividad_categoria.csv"
FACTOR_10_MESES, N_MINIMO, GL_MINIMO, CV_FIABLE, CV_MAXIMO = 3 / 10, 60, 9, 15.0, 30.0
MESES_JAS = ["2026-07", "2026-08", "2026-09"]
JAS_VALIDADO, INE_OFICIAL = 9_275_130, 9_274_742
PUBLICOS_CON_TITULO = 892_005


def preparar(ene: pd.DataFrame) -> pd.DataFrame:
    o = ene[ene["cae_especifico"].between(1, 7)].copy()
    o["categoria_ocupacion"] = o["categoria_ocupacion"].map(CATEGORIA_POR_CODIGO)
    if o["categoria_ocupacion"].isna().any():
        raise ValueError(f"Ocupados sin categoría asignable: {int(o['categoria_ocupacion'].isna().sum())}")
    o["nivel_titulo"] = np.select([o["cine11_1d"] == 3, o["cine11_1d"] >= 4], ["Tecnico", "Profesional"], default="Sin_titulo")
    log.info("Ocupados sin cine11_1d (quedan en Sin_titulo): %d filas", int(o["cine11_1d"].isna().sum()))
    o["actividad_caenes"] = o["r_p_rev4cl_caenes"].astype("Int64")
    o["actividad_clave"] = o["actividad_caenes"].astype("string").fillna("sin_rama")
    o["w"] = o["fact_cal"] * FACTOR_10_MESES
    o["w_jas"] = o["fact_cal"].where(o["mes"].isin(MESES_JAS), 0.0)
    return o


def cv_total(g: pd.DataFrame, psu: pd.Series) -> float:
    """Los conglomerados sin casos no aparecen en la suma, pero sí cuentan en n_h."""
    z = g.groupby(["estrato", "conglomerado"], sort=False)["w"].sum()
    h = z.groupby(level="estrato", sort=False).agg(s="sum", s2=lambda v: (v**2).sum())
    n_h = psu.reindex(h.index).to_numpy(dtype=float)
    var = np.where(n_h > 1, n_h / np.maximum(n_h - 1, 1) * (h["s2"] - h["s"]**2 / n_h), 0.0).sum()
    return 100 * np.sqrt(var) / g["w"].sum()


def clasificar(n: int, gl: int, cv: float) -> str:
    if n < N_MINIMO or gl < GL_MINIMO or cv > CV_MAXIMO:
        return "no_fiable"
    return "poco_fiable" if cv > CV_FIABLE else "fiable"


def construir(ene: pd.DataFrame, actividades: pd.DataFrame) -> pd.DataFrame:
    psu = ene[["estrato", "conglomerado"]].drop_duplicates().groupby("estrato").size()
    o = preparar(ene)
    filas = []
    for (region, nombre, actividad, categoria, nivel), g in o.groupby(["codigo_region", "nombre_region", "actividad_clave", "categoria_ocupacion", "nivel_titulo"]):
        n, gl = g["idrph"].nunique(), g["conglomerado"].nunique() - g["estrato"].nunique()
        cv = cv_total(g, psu)
        filas.append({"codigo_region": region, "nombre_region": nombre, "actividad_clave": actividad, "categoria_ocupacion": categoria, "nivel_titulo": nivel,
                      "ocupados_10_meses": g["w"].sum(), "ocupados_jas": g["w_jas"].sum(), "n_personas": n, "gl": gl, "cv_pct": cv,
                      "fiabilidad": clasificar(n, gl, cv)})
    t = pd.DataFrame(filas)
    t["actividad_caenes"] = pd.to_numeric(t["actividad_clave"], errors="coerce").astype("Int64")
    t = t.merge(actividades.astype({"actividad_caenes": "Int64"}), on="actividad_caenes", how="left")
    return t[list(OCUPADOS_REGION_ACTIVIDAD_CATEGORIA)].astype(OCUPADOS_REGION_ACTIVIDAD_CATEGORIA).sort_values(["codigo_region", "actividad_caenes", "categoria_ocupacion", "nivel_titulo"])


def validar(t: pd.DataFrame, ene: pd.DataFrame) -> None:
    """Detiene el proceso si los cuadres no se cumplen."""
    o = preparar(ene)
    claves = ["actividad_clave", "categoria_ocupacion", "nivel_titulo"]
    nacional = o.groupby(claves)["w"].sum()
    regiones = t.groupby(claves)["ocupados_10_meses"].sum()
    desde_actividades = obtener.cargar_ocupados_actividad().groupby(["codigo_region", "actividad_caenes"])["ocupados"].sum()
    esta = t.dropna(subset=["actividad_caenes"]).groupby(["codigo_region", "actividad_caenes"])["ocupados_10_meses"].sum()
    publicos = t[(t["categoria_ocupacion"] == "asalariado_publico") & (t["nivel_titulo"] != "Sin_titulo")]["ocupados_10_meses"].sum()
    jas = t["ocupados_jas"].sum()
    controles = {
        "Clave única": not t.duplicated(["codigo_region", "actividad_clave", "categoria_ocupacion", "nivel_titulo"]).any(),
        "Regiones 1-16": t["codigo_region"].nunique() == 16,
        "Regiones suman el total nacional en cada celda": np.allclose(regiones.reindex(nacional.index), nacional),
        "Total regional = total de ocupados de ENE": np.isclose(t["ocupados_10_meses"].sum(), ene.loc[ene["cae_especifico"].between(1, 7), "fact_cal"].sum() * FACTOR_10_MESES),
        "JAS reproduce la cifra validada (±1 persona)": abs(jas - JAS_VALIDADO) <= 1,
        "Calza con ocupados_region_actividad": np.allclose(esta.reindex(desde_actividades.index), desde_actividades),
        "Públicos con título = 892.005 (±1 persona)": abs(publicos - PUBLICOS_CON_TITULO) <= 1,
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    log.info("  [i] JAS %.0f; Boletín INE %d (%+.2f%%)", jas, INE_OFICIAL, 100 * (jas / INE_OFICIAL - 1))
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ene, actividades = obtener.cargar()
    tabla = construir(ene, actividades)
    validar(tabla, ene)
    RUTA.parent.mkdir(exist_ok=True)
    tabla.to_csv(RUTA, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", RUTA.name, len(tabla))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(RUTA)
