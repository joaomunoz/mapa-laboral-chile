"""
<src/Analisis/JOINS/Areas_Por_Actividad/obtener.py>

Carga CASEN, su diseño muestral completo, P1, P5 y las áreas de Titulados.
"""

from pathlib import Path

import pandas as pd

DIR_ANALISIS = Path(__file__).resolve().parents[2]
DIR_SCRAPERS = DIR_ANALISIS.parent / "Scrapers"
DIR_PUENTES = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida"


def cargar_casen() -> pd.DataFrame:
    return pd.read_csv(DIR_SCRAPERS / "CASEN" / "Salida" / "casen_procesado.csv", sep=";", low_memory=False,
                       usecols=["e6a", "carrera_normalizada", "titulo_comun", "activ", "rama1", "cinef13_area",
                                "expr", "varstrat", "varunit"])


def cargar_diseno() -> pd.DataFrame:
    """Todos los conglomerados de la encuesta, no solo los que tienen titulados."""
    d = pd.read_stata(DIR_SCRAPERS / "CASEN" / "Entrada" / "casen_2024.dta", columns=["varstrat", "varunit"], convert_categoricals=False)
    return d.drop_duplicates()


def cargar_actividades() -> pd.DataFrame:
    return pd.read_csv(DIR_PUENTES / "P1_puente_actividades.csv", sep=";")[["actividad_caenes", "actividad_ciiu", "actividad_glosa"]]


def cargar_puente_carrera() -> pd.DataFrame:
    p = pd.read_csv(DIR_PUENTES / "P5_puente_carrera_casen.csv", sep=";")
    return p[p["estado"] == "asignado"][["e6a", "carrera_normalizada", "area_cine_sies"]]


def cargar_areas_titulados() -> set[str]:
    t = pd.read_csv(DIR_SCRAPERS / "Titulados" / "Salida" / "titulados_procesado.csv", sep=";", usecols=["cine13_area"])
    return set(t["cine13_area"].unique())
