"""
<src/Analisis/JOINS/Concentracion_Region_Actividad/obtener.py>
Actualizado 02-11-26 21:14

Carga ENE y P1, y la tabla de control usada para contrastar el resultado.
"""

from pathlib import Path

import pandas as pd

DIR_ANALISIS = Path(__file__).resolve().parents[2]
RUTA_ENE = DIR_ANALISIS.parent / "Scrapers" / "ENE" / "Salida" / "ene_procesado.csv"
RUTA_P1 = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida" / "P1_puente_actividades.csv"
RUTA_CONTROL = DIR_ANALISIS / "Calculos_control" / "ocupados_region_actividad" / "Salida" / "ocupados_region_actividad.csv"


def cargar_ene() -> pd.DataFrame:
    return pd.read_csv(RUTA_ENE, sep=";", low_memory=False,
                       usecols=["idrph", "mes", "codigo_region_trabajo", "fact_cal", "cae_especifico",
                                "r_p_rev4cl_caenes", "estrato", "conglomerado"])


def cargar_actividades() -> pd.DataFrame:
    return pd.read_csv(RUTA_P1, sep=";")[["actividad_caenes", "actividad_ciiu", "actividad_glosa"]]


def cargar_control() -> pd.DataFrame:
    c = pd.read_csv(RUTA_CONTROL, sep=";")
    return c[c["base_region"] == "trabajo"][["codigo_region", "actividad_caenes", "ocupados"]]
