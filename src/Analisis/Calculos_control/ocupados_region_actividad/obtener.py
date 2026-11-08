"""
<src/Analisis/Calculos_control/ocupados_region_actividad/obtener.py>

Carga ENE y P1 para contar todos los ocupados por región y actividad.

ENE: los meses del contraste con el censo (comun/periodos.py).
"""

import sys
from pathlib import Path

import pandas as pd

DIR_ANALISIS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(DIR_ANALISIS.parent / "Scrapers"))
from comun.periodos import MESES_CONTRASTE, RUTA_ENE_CONTRASTE  # noqa: E402

RUTA_P1 = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida" / "P1_puente_actividades.csv"


def cargar() -> tuple[pd.DataFrame, pd.DataFrame]:
    ene = pd.read_csv(RUTA_ENE_CONTRASTE, sep=";", low_memory=False,
                      usecols=["idrph", "mes", "codigo_region", "codigo_region_trabajo", "fact_cal", "cae_especifico",
                               "r_p_rev4cl_caenes", "estrato", "conglomerado"])
    return ene[ene["mes"].isin(MESES_CONTRASTE)], pd.read_csv(RUTA_P1, sep=";")[["actividad_caenes", "actividad_ciiu", "actividad_glosa"]]
