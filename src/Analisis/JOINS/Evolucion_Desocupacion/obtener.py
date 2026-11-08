"""
<src/Analisis/JOINS/Evolucion_Desocupacion/obtener.py>

Carga la ENE de marzo a julio de 2024 y de 2026 (comun/periodos.py), y la tabla de fuerza de trabajo por nivel,
que sirve de control para 2024.
"""

import sys
from pathlib import Path

import pandas as pd

DIR_ANALISIS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(DIR_ANALISIS.parent / "Scrapers"))
from comun.periodos import MESES_ACTUAL, MESES_CONTRASTE, RUTA_ENE_ACTUAL, RUTA_ENE_CONTRASTE  # noqa: E402

RUTA_NIVELES = DIR_ANALISIS / "JOINS" / "Fuerza_Trabajo_Region_Nivel" / "Salida" / "fuerza_trabajo_region_nivel.csv"
COLUMNAS = ["idrph", "mes", "codigo_region", "fact_cal", "cae_especifico", "cine11_1d", "estrato", "conglomerado"]


def cargar_ene() -> dict[int, pd.DataFrame]:
    """Una tabla por año, solo con sus meses de marzo a julio."""
    leer = lambda ruta, meses: pd.read_csv(ruta, sep=";", low_memory=False, usecols=COLUMNAS).query("mes in @meses")
    return {2024: leer(RUTA_ENE_CONTRASTE, MESES_CONTRASTE), 2026: leer(RUTA_ENE_ACTUAL, MESES_ACTUAL)}


def cargar_niveles() -> pd.DataFrame:
    return pd.read_csv(RUTA_NIVELES, sep=";", usecols=["nivel_titulo", "ene_tasa_nacional_nivel"]).drop_duplicates("nivel_titulo")
