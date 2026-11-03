"""
<src/Analisis/JOINS/Fuerza_Trabajo_Region_Nivel/obtener.py>

Carga el censo procesado y las columnas de ENE necesarias para el contraste.
"""

from pathlib import Path

import pandas as pd

DIR_SCRAPERS = Path(__file__).resolve().parents[3] / "Scrapers"


def cargar_censo() -> pd.DataFrame:
    return pd.read_csv(DIR_SCRAPERS / "CENSO" / "Salida" / "censo_procesado.csv", sep=";")


def cargar_ene() -> pd.DataFrame:
    return pd.read_csv(DIR_SCRAPERS / "ENE" / "Salida" / "ene_procesado.csv", sep=";", low_memory=False,
                       usecols=["idrph", "codigo_region", "fact_cal", "cae_especifico", "cine11_1d", "estrato", "conglomerado"])
