"""
<src/Analisis/JOINS/Poblacion_Edad_Region/obtener.py>

Carga los microdatos de personas del Censo 2024 con la edad, con la misma preparación que el censo procesado, y el
censo procesado, contra el que se cuadra la población de cada región.

Reutiliza la carga de Fuerza_Trabajo_Titulo_Edad (por su ruta), que ya prepara las personas igual que CENSO/procesar.py:
así las dos tablas por edad parten de las mismas personas.
"""

import importlib.util
from pathlib import Path

import pandas as pd

DIR_JOINS = Path(__file__).resolve().parents[1]
RUTA_PROCESADO = DIR_JOINS.parents[1] / "Scrapers" / "CENSO" / "Salida" / "censo_procesado.csv"


def _obtener_titulo_edad():
    spec = importlib.util.spec_from_file_location("obtener_titulo_edad", DIR_JOINS / "Fuerza_Trabajo_Titulo_Edad" / "obtener.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def cargar_personas() -> pd.DataFrame:
    """Personas de 15 años o más, con región de residencia, edad y situación laboral."""
    return _obtener_titulo_edad().cargar_personas()[["codigo_region", "edad", "sit_fuerza_trabajo"]]


def cargar_procesado() -> pd.DataFrame:
    return pd.read_csv(RUTA_PROCESADO, sep=";", usecols=["codigo_region", "sit_fuerza_trabajo", "personas"])
