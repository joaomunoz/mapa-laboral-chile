"""
<src/Analisis/Calculos_control/titulados_ocupados_region_actividad/crosswalk.py>
Actualizado 02-11-26 16:40

Calcula cuántos titulados trabajan en cada región y actividad (CAENES), por tipo de título,
y exporta Salida/titulados_ocupados_region_actividad.csv con su reporte de inspección.
Es la base del control del reparto por actividad: mide directamente, sin asignar carreras.
"""

import logging
import sys
from pathlib import Path

import pandas as pd

from esquema import (
    GL_MINIMO,
    N_MINIMO,
    TITULADOS_OCUPADOS_ESQUEMA,
    VALIDACIONES_TITULADOS_OCUPADOS,
)
from obtener import DIR_ACTUAL, DIR_SCRAPERS, cargar_datos

log = logging.getLogger(__name__)

MESES_JAS = ["2026-07", "2026-08", "2026-09"]
TIPO_TITULO = {3: "Tecnico", 4: "Profesional", 5: "Postgrado", 6: "Postgrado"}


def calcular(ene: pd.DataFrame, p1: pd.DataFrame) -> pd.DataFrame:
    ocupados = ene[ene["mes"].isin(MESES_JAS) & ene["cae_especifico"].between(1, 7)]
    titulados = ocupados[ocupados["cine11_1d"].ge(3)].copy()
    total = titulados["fact_cal"].sum()

    # Quien no declara rama no se puede ubicar en una actividad: se reporta, no se imputa.
    sin_rama = titulados["r_p_rev4cl_caenes"].isna()
    log.info("Titulados ocupados %s: %s | sin rama: %d filas = %s personas (%.2f%%)", "JAS 2026",
             f"{total:,.0f}", sin_rama.sum(), f"{titulados.loc[sin_rama, 'fact_cal'].sum():,.0f}",
             100 * titulados.loc[sin_rama, "fact_cal"].sum() / total)
    titulados = titulados[~sin_rama].copy()
    titulados["actividad_caenes"] = titulados["r_p_rev4cl_caenes"].astype(int)
    titulados["nivel_titulo"] = titulados["cine11_1d"].astype(int).map(TIPO_TITULO)

    df = (
        titulados.groupby(["codigo_region", "nombre_region", "actividad_caenes", "nivel_titulo"])
        .agg(
            expandido=("fact_cal", "sum"),
            n_personas=("idrph", "nunique"),
            conglomerados=("conglomerado", "nunique"),
            estratos=("estrato", "nunique"),
        )
        .reset_index()
    )
    df["gl"] = df["conglomerados"] - df["estratos"]
    df["fiable_n_gl"] = (df["n_personas"] >= N_MINIMO) & (df["gl"] >= GL_MINIMO)
    df["titulados_ocupados"] = df["expandido"].round().astype("int64")
    df["pct_en_region"] = (100 * df["expandido"] / df.groupby("codigo_region")["expandido"].transform("sum")).round(2)
    df["pct_en_actividad"] = (100 * df["expandido"] / df.groupby("actividad_caenes")["expandido"].transform("sum")).round(2)
    df = df.merge(p1, on="actividad_caenes", how="left", validate="many_to_one")

    # Control contable: lo exportado debe cuadrar con la población de partida.
    diferencia = abs(df["expandido"].sum() - titulados["fact_cal"].sum())
    if diferencia > 1:
        raise ValueError(f"La tabla no cuadra con la población de partida: diferencia {diferencia:,.1f}")
    log.info("  [✓] Control contable: la tabla cuadra con la población (diferencia %.4f)", diferencia)

    columnas = list(TITULADOS_OCUPADOS_ESQUEMA)
    return df[columnas].astype(TITULADOS_OCUPADOS_ESQUEMA).sort_values(["codigo_region", "actividad_caenes", "nivel_titulo"])


def ejecutar() -> Path:
    log.info("=== Control: titulados_ocupados_region_actividad ===")
    df = calcular(*cargar_datos())

    for descripcion, regla in VALIDACIONES_TITULADOS_OCUPADOS:
        valido = bool(regla(df))
        log.info("  [%s] %s", "✓" if valido else "✗", descripcion)
        if not valido:
            raise ValueError(f"Validación fallida: {descripcion}")

    ruta = DIR_ACTUAL / "Salida" / "titulados_ocupados_region_actividad.csv"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False, sep=";", encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", ruta.name, len(df))

    # Reporte obligatorio para toda tabla generada (regla del proyecto).
    sys.path.insert(0, str(DIR_SCRAPERS / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(ruta)
    return ruta


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ejecutar()
