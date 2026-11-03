"""
<src/Analisis/JOINS/Concentracion_Region_Actividad_Censo/obtener.py>
Actualizado 03-11-26 12:29

Carga el censo procesado, P1 y la tabla de concentración calculada con ENE.
"""

from pathlib import Path

import pandas as pd

DIR_ANALISIS = Path(__file__).resolve().parents[2]
RUTA_CENSO = DIR_ANALISIS.parent / "Scrapers" / "CENSO" / "Salida" / "censo_procesado.csv"
RUTA_P1 = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida" / "P1_puente_actividades.csv"
RUTA_ENE = DIR_ANALISIS / "JOINS" / "Concentracion_Region_Actividad" / "Salida" / "concentracion_region_actividad.csv"


def cargar_censo() -> pd.DataFrame:
    return pd.read_csv(RUTA_CENSO, sep=";")


def cargar_actividades() -> pd.DataFrame:
    return pd.read_csv(RUTA_P1, sep=";")[["actividad_caenes", "actividad_ciiu", "actividad_glosa"]]


def cargar_ene() -> pd.DataFrame:
    return pd.read_csv(RUTA_ENE, sep=";", usecols=["codigo_region", "actividad_caenes", "ocupados", "pct_nacional", "peso_relativo", "lectura"])
