"""
<src/Analisis/JOINS/Concentracion_Region_Actividad/obtener.py>

Carga ENE y P1, y la tabla de control usada para contrastar el resultado.

ENE: los meses del contraste con el censo (comun/periodos.py).
"""

import sys
from pathlib import Path

import pandas as pd

DIR_ANALISIS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(DIR_ANALISIS.parent / "Scrapers"))
from comun.periodos import MESES_CONTRASTE, RUTA_ENE_CONTRASTE  # noqa: E402

RUTA_P1 = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida" / "P1_puente_actividades.csv"
RUTA_CONTROL = DIR_ANALISIS / "Calculos_control" / "ocupados_region_actividad" / "Salida" / "ocupados_region_actividad.csv"


def cargar_ene() -> pd.DataFrame:
    ene = pd.read_csv(RUTA_ENE_CONTRASTE, sep=";", low_memory=False,
                      usecols=["idrph", "mes", "codigo_region_trabajo", "fact_cal", "cae_especifico",
                               "r_p_rev4cl_caenes", "estrato", "conglomerado"])
    return ene[ene["mes"].isin(MESES_CONTRASTE)]


def cargar_actividades() -> pd.DataFrame:
    return pd.read_csv(RUTA_P1, sep=";")[["actividad_caenes", "actividad_ciiu", "actividad_glosa"]]


def cargar_control() -> pd.DataFrame:
    c = pd.read_csv(RUTA_CONTROL, sep=";")
    return c[c["base_region"] == "trabajo"][["codigo_region", "actividad_caenes", "ocupados"]]
