"""
<src/Analisis/Calculos_control/ocupados_region_actividad/obtener.py>
Actualizado 02-11-26 16:40

Carga ENE y P1 para contar todos los ocupados por región y actividad.
"""

from pathlib import Path

import pandas as pd

DIR_ANALISIS = Path(__file__).resolve().parents[2]
RUTA_ENE = DIR_ANALISIS.parent / "Scrapers" / "ENE" / "Salida" / "ene_procesado.csv"
RUTA_P1 = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida" / "P1_puente_actividades.csv"


def cargar() -> tuple[pd.DataFrame, pd.DataFrame]:
    ene = pd.read_csv(RUTA_ENE, sep=";", low_memory=False,
                      usecols=["idrph", "codigo_region", "codigo_region_trabajo", "fact_cal", "cae_especifico",
                               "r_p_rev4cl_caenes", "estrato", "conglomerado"])
    return ene, pd.read_csv(RUTA_P1, sep=";")[["actividad_caenes", "actividad_ciiu", "actividad_glosa"]]
