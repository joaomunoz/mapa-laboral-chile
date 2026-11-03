"""
<src/Analisis/JOINS/Carreras_Por_Actividad/obtener.py>

Carga P9, P5, CASEN con su diseño muestral, MiFuturo y Titulados.
"""

from pathlib import Path

import pandas as pd

DIR_ANALISIS = Path(__file__).resolve().parents[2]
DIR_SCRAPERS = DIR_ANALISIS.parent / "Scrapers"
RUTA_P9 = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida" / "P9_perfil_laboral_carrera.csv"
RUTA_P5 = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida" / "P5_puente_carrera_casen.csv"
CLASES_QUE_COMPITEN = ["Técnico de Nivel Superior", "Profesional Con Licenciatura", "Profesional Sin Licenciatura"]


def cargar_perfil() -> pd.DataFrame:
    p = pd.read_csv(RUTA_P9, sep=";")
    return p[p["dimension"] == "actividad_economica"]


def cargar_casen() -> pd.DataFrame:
    """Titulados con carrera asignada y condición de actividad, con la llave de P5."""
    c = pd.read_csv(DIR_SCRAPERS / "CASEN" / "Salida" / "casen_procesado.csv", sep=";", low_memory=False,
                    usecols=["e6a", "carrera_normalizada", "titulo_comun", "activ", "edad", "expr", "varstrat", "varunit"])
    p = pd.read_csv(RUTA_P5, sep=";")
    p = p[p["estado"] == "asignado"][["e6a", "carrera_normalizada", "carrera_generica"]]
    return c[c["titulo_comun"].notna() & c["activ"].notna()].merge(p, on=["e6a", "carrera_normalizada"], validate="many_to_one")


def cargar_diseno() -> pd.DataFrame:
    """Todos los conglomerados de la encuesta, no solo los que tienen titulados."""
    d = pd.read_stata(DIR_SCRAPERS / "CASEN" / "Entrada" / "casen_2024.dta", columns=["varstrat", "varunit"], convert_categoricals=False)
    return d.drop_duplicates()


def cargar_mifuturo() -> pd.DataFrame:
    return pd.read_csv(DIR_SCRAPERS / "Empleabilidad" / "Salida" / "empleabilidad_procesado.csv", sep=";",
                       usecols=["id_institucion", "carrera_generica", "empleabilidad_1er_anio",
                                "ingreso_medio_1er_anio", "ingreso_medio_5to_anio"])


def cargar_titulados() -> pd.DataFrame:
    t = pd.read_csv(DIR_SCRAPERS / "Titulados" / "Salida" / "titulados_procesado.csv", sep=";", low_memory=False,
                    usecols=["anio", "codigo_institucion", "carrera_generica", "carrera_clasificacion_nivel_1", "total_titulaciones"])
    return t[t["carrera_clasificacion_nivel_1"].isin(CLASES_QUE_COMPITEN)]
