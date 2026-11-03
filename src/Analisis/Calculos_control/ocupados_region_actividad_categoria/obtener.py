"""
<src/Analisis/Calculos_control/ocupados_region_actividad_categoria/obtener.py>

Carga ENE y P1 para contar a los ocupados por región, actividad, categoría en la ocupación y nivel.
"""

from pathlib import Path

import pandas as pd

DIR_ANALISIS = Path(__file__).resolve().parents[2]
RUTA_ENE = DIR_ANALISIS.parent / "Scrapers" / "ENE" / "Salida" / "ene_procesado.csv"
RUTA_P1 = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida" / "P1_puente_actividades.csv"
RUTA_OCUPADOS_ACTIVIDAD = DIR_ANALISIS / "Calculos_control" / "ocupados_region_actividad" / "Salida" / "ocupados_region_actividad.csv"


def cargar() -> tuple[pd.DataFrame, pd.DataFrame]:
    ene = pd.read_csv(RUTA_ENE, sep=";", low_memory=False,
                      usecols=["idrph", "mes", "codigo_region", "nombre_region", "fact_cal", "cae_especifico", "cine11_1d",
                               "categoria_ocupacion", "r_p_rev4cl_caenes", "estrato", "conglomerado"])
    return ene, pd.read_csv(RUTA_P1, sep=";")[["actividad_caenes", "actividad_ciiu", "actividad_glosa"]]


def cargar_ocupados_actividad() -> pd.DataFrame:
    t = pd.read_csv(RUTA_OCUPADOS_ACTIVIDAD, sep=";")
    return t[t["base_region"] == "residencia"]
