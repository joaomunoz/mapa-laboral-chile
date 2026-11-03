"""
<src/Analisis/Calculos_control/conteo_instituciones_empleabilidad_titulados/obtener.py>
Actualizado 02-11-26 18:01

Carga Titulados y Empleabilidad procesados, las dos fuentes que se comparan.
"""

from pathlib import Path

import pandas as pd

DIR_SCRAPERS = Path(__file__).resolve().parents[3] / "Scrapers"


def cargar() -> tuple[pd.DataFrame, pd.DataFrame]:
    tit = pd.read_csv(DIR_SCRAPERS / "Titulados" / "Salida" / "titulados_procesado.csv", sep=";", low_memory=False,
                      usecols=["anio", "codigo_institucion", "carrera_generica", "carrera_clasificacion_nivel_1", "total_titulaciones"])
    emp = pd.read_csv(DIR_SCRAPERS / "Empleabilidad" / "Salida" / "empleabilidad_procesado.csv", sep=";",
                      usecols=["id_institucion", "carrera_generica"])
    return tit, emp
