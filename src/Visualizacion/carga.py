"""
<src/Visualizacion/carga.py>

Lectura de las entradas y escritura de la página. Es el único módulo que toca archivos, salvo el control que compara
con los microdatos del Censo cuando están disponibles (controles.py).
"""

from __future__ import annotations

import geopandas as gpd
import pandas as pd

from config import (
    RUTA_AREAS, RUTA_CARRERAS, RUTA_CENSO, RUTA_CENSO_PROCESADO, RUTA_CENSO_SEXO, RUTA_NIVELES, RUTA_PLANTILLA,
    RUTA_REGIONES, RUTA_SALIDA,
)


def cargar_tablas() -> dict[str, pd.DataFrame]:
    """Tablas del Censo y de los cruces que arman los datos de la página."""
    rutas = {"censo": RUTA_CENSO, "procesado": RUTA_CENSO_PROCESADO, "por_sexo": RUTA_CENSO_SEXO, "areas": RUTA_AREAS,
             "carreras": RUTA_CARRERAS, "niveles": RUTA_NIVELES}
    return {nombre: pd.read_csv(ruta, sep=";") for nombre, ruta in rutas.items()}


def leer_regiones() -> gpd.GeoDataFrame:
    return gpd.read_parquet(RUTA_REGIONES).set_geometry("SHAPE")


def leer_plantilla() -> str:
    return RUTA_PLANTILLA.read_text(encoding="utf-8")


def escribir_pagina(html: str) -> None:
    RUTA_SALIDA.parent.mkdir(exist_ok=True)
    RUTA_SALIDA.write_text(html, encoding="utf-8")
