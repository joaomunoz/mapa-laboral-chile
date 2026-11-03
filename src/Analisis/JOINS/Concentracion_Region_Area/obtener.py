"""
<src/Analisis/JOINS/Concentracion_Region_Area/obtener.py>

Carga CASEN, su diseño muestral completo, P5 y las áreas de la tabla 2.
"""

from pathlib import Path

import pandas as pd

DIR_ANALISIS = Path(__file__).resolve().parents[2]
DIR_SCRAPERS = DIR_ANALISIS.parent / "Scrapers"
RUTA_P5 = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida" / "P5_puente_carrera_casen.csv"
RUTA_AREAS = DIR_ANALISIS / "JOINS" / "Areas_Por_Actividad" / "Salida" / "areas_por_actividad.csv"


def cargar_casen() -> pd.DataFrame:
    c = pd.read_csv(DIR_SCRAPERS / "CASEN" / "Salida" / "casen_procesado.csv", sep=";", low_memory=False,
                    usecols=["codigo_region", "nombre_region", "e6a", "carrera_normalizada", "titulo_comun",
                             "cinef13_area", "expr", "varstrat", "varunit"])
    return c[c["titulo_comun"].notna()]


def cargar_diseno() -> pd.DataFrame:
    """Todos los conglomerados de la encuesta, no solo los que tienen titulados."""
    d = pd.read_stata(DIR_SCRAPERS / "CASEN" / "Entrada" / "casen_2024.dta", columns=["varstrat", "varunit"], convert_categoricals=False)
    return d.drop_duplicates()


def cargar_puente_carrera() -> pd.DataFrame:
    p = pd.read_csv(RUTA_P5, sep=";")
    return p[p["estado"] == "asignado"][["e6a", "carrera_normalizada", "area_cine_sies"]]


def cargar_areas_tabla_2() -> set[str]:
    return set(pd.read_csv(RUTA_AREAS, sep=";", usecols=["area_cine"])["area_cine"])
