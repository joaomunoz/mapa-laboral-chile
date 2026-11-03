"""
<src/Analisis/JOINS/Carreras_Por_Actividad/obtener.py>
Actualizado 02-11-26 21:37

Carga P9, MiFuturo y Titulados.
"""

from pathlib import Path

import pandas as pd

DIR_ANALISIS = Path(__file__).resolve().parents[2]
DIR_SCRAPERS = DIR_ANALISIS.parent / "Scrapers"
RUTA_P9 = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida" / "P9_perfil_laboral_carrera.csv"
CLASES_QUE_COMPITEN = ["Técnico de Nivel Superior", "Profesional Con Licenciatura", "Profesional Sin Licenciatura"]


def cargar_perfil() -> pd.DataFrame:
    p = pd.read_csv(RUTA_P9, sep=";")
    return p[p["dimension"] == "actividad_economica"]


def cargar_mifuturo() -> pd.DataFrame:
    return pd.read_csv(DIR_SCRAPERS / "Empleabilidad" / "Salida" / "empleabilidad_procesado.csv", sep=";",
                       usecols=["id_institucion", "carrera_generica", "empleabilidad_1er_anio",
                                "ingreso_medio_1er_anio", "ingreso_medio_5to_anio"])


def cargar_titulados() -> pd.DataFrame:
    t = pd.read_csv(DIR_SCRAPERS / "Titulados" / "Salida" / "titulados_procesado.csv", sep=";", low_memory=False,
                    usecols=["anio", "codigo_institucion", "carrera_generica", "carrera_clasificacion_nivel_1", "total_titulaciones"])
    return t[t["carrera_clasificacion_nivel_1"].isin(CLASES_QUE_COMPITEN)]
