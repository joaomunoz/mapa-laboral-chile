"""
<src/Analisis/Calculos_control/cobertura_enadel_ene_region_actividad/crosswalk.py>

Compara la dotación de ENADEL con los asalariados privados de la ENE por región y actividad,
y exporta Salida/cobertura_enadel_ene_region_actividad.csv con su reporte de inspección.
Indica dónde se puede confiar en ENADEL como medida del mercado privado.
"""

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from esquema import (
    COBERTURA_ESQUEMA,
    GL_MINIMO_ENE,
    N_MINIMO_EMPRESAS,
    N_MINIMO_ENE,
    PCT_TOP1_MAXIMO,
    VALIDACIONES_COBERTURA,
)
from obtener import DIR_ACTUAL, DIR_SCRAPERS, cargar_datos

log = logging.getLogger(__name__)

MESES_JAS = ["2026-07", "2026-08", "2026-09"]
ASALARIADO_PRIVADO = 3  # categoria_ocupacion, libro de códigos ENE


def calcular(enadel: pd.DataFrame, ene: pd.DataFrame, p1: pd.DataFrame) -> pd.DataFrame:
    # Grilla completa: un cruce simple perdería las celdas presentes en una sola fuente.
    regiones = ene[["codigo_region", "nombre_region"]].drop_duplicates()
    grilla = regiones.merge(p1, how="cross")

    enadel = enadel.assign(expandido=enadel["dotacion_total"] * enadel["pond_final"])
    secciones_enadel = set(enadel["actividad_ciiu"])
    lado_enadel = (
        enadel.groupby(["codigo_region", "actividad_ciiu"])
        .agg(
            dotacion=("expandido", "sum"),
            mayor_empresa=("expandido", "max"),
            n_empresas_enadel=("idempresa_ficticio", "nunique"),
        )
        .reset_index()
    )

    privados = ene[
        ene["mes"].isin(MESES_JAS)
        & ene["cae_especifico"].between(1, 7)
        & ene["categoria_ocupacion"].eq(ASALARIADO_PRIVADO)
    ]
    sin_rama = privados["r_p_rev4cl_caenes"].isna()
    log.info("Asalariados privados JAS 2026: %s | sin rama: %s personas",
             f"{privados['fact_cal'].sum():,.0f}", f"{privados.loc[sin_rama, 'fact_cal'].sum():,.0f}")
    privados = privados[~sin_rama].assign(actividad_caenes=lambda d: d["r_p_rev4cl_caenes"].astype(int))
    lado_ene = (
        privados.groupby(["codigo_region", "actividad_caenes"])
        .agg(
            expandido=("fact_cal", "sum"),
            n_personas_ene=("idrph", "nunique"),
            conglomerados=("conglomerado", "nunique"),
            estratos=("estrato", "nunique"),
        )
        .reset_index()
    )
    lado_ene["gl_ene"] = lado_ene["conglomerados"] - lado_ene["estratos"]

    df = grilla.merge(lado_enadel, on=["codigo_region", "actividad_ciiu"], how="left")
    df = df.merge(lado_ene, on=["codigo_region", "actividad_caenes"], how="left")

    # Actividad encuestado sin empresas en la región = 0; actividad no encuestado = NA.
    df["actividad_en_enadel"] = df["actividad_ciiu"].isin(secciones_enadel)
    for columna in ("dotacion", "n_empresas_enadel"):
        df[columna] = df[columna].fillna(0).where(df["actividad_en_enadel"])
    for columna in ("expandido", "n_personas_ene", "gl_ene"):
        df[columna] = df[columna].fillna(0)

    df["pct_top1_empresa"] = (100 * df["mayor_empresa"] / df["dotacion"].where(df["dotacion"] > 0)).round(2)
    df["razon_cobertura"] = (df["dotacion"] / df["expandido"].where(df["expandido"] > 0)).round(3)
    df["dotacion_enadel"] = df["dotacion"].round().astype("Int64")
    df["n_empresas_enadel"] = df["n_empresas_enadel"].astype("Int64")
    df["asalariados_privados_ene"] = df["expandido"].round().astype("int64")
    df["n_personas_ene"] = df["n_personas_ene"].astype("int64")
    df["gl_ene"] = df["gl_ene"].astype("int64")

    suficiente = (
        (df["n_personas_ene"] >= N_MINIMO_ENE)
        & (df["gl_ene"] >= GL_MINIMO_ENE)
        & (df["n_empresas_enadel"].fillna(0) >= N_MINIMO_EMPRESAS)
    )
    concentrada = df["pct_top1_empresa"] > PCT_TOP1_MAXIMO
    df["lectura"] = np.select(
        [~df["actividad_en_enadel"], ~suficiente, concentrada],
        ["actividad_fuera_de_enadel", "muestra_insuficiente", "concentrada"],
        default="comparable",
    )

    # Control contable contra ambas fuentes: la grilla no puede crear ni perder personas.
    dif_enadel = abs(df["dotacion"].sum() - enadel["expandido"].sum())
    dif_ene = abs(df["expandido"].sum() - privados["fact_cal"].sum())
    if dif_enadel > 1 or dif_ene > 1:
        raise ValueError(f"La tabla no cuadra: ENADEL {dif_enadel:,.1f}, ENE {dif_ene:,.1f}")
    log.info("  [✓] Control contable: cuadra con ENADEL (dif. %.4f) y ENE (dif. %.4f)", dif_enadel, dif_ene)

    return df[list(COBERTURA_ESQUEMA)].astype(COBERTURA_ESQUEMA).sort_values(["codigo_region", "actividad_caenes"])


def ejecutar() -> Path:
    log.info("=== Control: cobertura_enadel_ene_region_actividad ===")
    df = calcular(*cargar_datos())

    for descripcion, regla in VALIDACIONES_COBERTURA:
        valido = bool(regla(df))
        log.info("  [%s] %s", "✓" if valido else "✗", descripcion)
        if not valido:
            raise ValueError(f"Validación fallida: {descripcion}")

    ruta = DIR_ACTUAL / "Salida" / "cobertura_enadel_ene_region_actividad.csv"
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
