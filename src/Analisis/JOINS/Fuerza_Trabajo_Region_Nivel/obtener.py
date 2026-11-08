"""
<src/Analisis/JOINS/Fuerza_Trabajo_Region_Nivel/obtener.py>

Carga el censo procesado y las columnas de ENE necesarias para el contraste.

ENE: los meses del contraste con el censo (comun/periodos.py).
"""

import sys
from pathlib import Path

import pandas as pd

DIR_SCRAPERS = Path(__file__).resolve().parents[3] / "Scrapers"
sys.path.insert(0, str(DIR_SCRAPERS))
from comun.periodos import MESES_CONTRASTE, RUTA_ENE_CONTRASTE  # noqa: E402


def cargar_censo() -> pd.DataFrame:
    return pd.read_csv(DIR_SCRAPERS / "CENSO" / "Salida" / "censo_procesado.csv", sep=";")


def cargar_ene() -> pd.DataFrame:
    ene = pd.read_csv(RUTA_ENE_CONTRASTE, sep=";", low_memory=False,
                      usecols=["idrph", "mes", "codigo_region", "fact_cal", "cae_especifico", "cine11_1d", "estrato", "conglomerado"])
    return ene[ene["mes"].isin(MESES_CONTRASTE)]
