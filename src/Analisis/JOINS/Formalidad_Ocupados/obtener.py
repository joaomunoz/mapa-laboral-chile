"""
<src/Analisis/JOINS/Formalidad_Ocupados/obtener.py>

Carga la ENE de marzo a julio de 2026 (comun/periodos.py) y el puente de actividades CAENES ↔ CIIU.
"""

import sys
from pathlib import Path

import pandas as pd

DIR_ANALISIS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(DIR_ANALISIS.parent / "Scrapers"))
from comun.periodos import MESES_ACTUAL, RUTA_ENE_ACTUAL  # noqa: E402

RUTA_PUENTE = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida" / "P1_puente_actividades.csv"
COLUMNAS = ["idrph", "mes", "codigo_region", "fact_cal", "cae_especifico", "cine11_1d", "categoria_ocupacion", "ocup_form",
            "r_p_rev4cl_caenes", "estrato", "conglomerado", "edad"]


def cargar_ene() -> pd.DataFrame:
    return pd.read_csv(RUTA_ENE_ACTUAL, sep=";", low_memory=False, usecols=COLUMNAS).query("mes in @MESES_ACTUAL")


def cargar_puente() -> pd.DataFrame:
    return pd.read_csv(RUTA_PUENTE, sep=";", usecols=["actividad_caenes", "actividad_ciiu", "actividad_glosa"])
