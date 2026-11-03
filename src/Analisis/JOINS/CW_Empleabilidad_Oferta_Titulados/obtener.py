"""
<src/Analisis/JOINS/CW_Empleabilidad_Oferta_Titulados/obtener.py>
Actualizado 02-11-26 16:40

Módulo de obtención y verificación para el Paso 1 del índice:
Carga y valida los datasets de entrada:
  1. src/Scrapers/Titulados/Salida/titulados_procesado.csv
  2. src/Analisis/Puentes_de_mapeo/Salida/P2_puente_llaves_carrera.csv
"""

import logging
from pathlib import Path
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

DIR_ACTUAL = Path(__file__).resolve().parent
DIR_ANALISIS = DIR_ACTUAL.parents[1]
DIR_SCRAPERS = DIR_ANALISIS.parents[0] / "Scrapers"

RUTA_TITULADOS = DIR_SCRAPERS / "Titulados" / "Salida" / "titulados_procesado.csv"
RUTA_PUENTE_P2 = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida" / "P2_puente_llaves_carrera.csv"


def cargar_datos_paso1():
    """Carga y valida la existencia de los datasets de Titulados y Puente P2."""
    log.info("Iniciando carga de datos para CW_Empleabilidad_Oferta_Titulados...")

    if not RUTA_TITULADOS.exists():
        raise FileNotFoundError(f"No se encuentra el archivo de titulados en: {RUTA_TITULADOS}")
    if not RUTA_PUENTE_P2.exists():
        raise FileNotFoundError(f"No se encuentra el puente P2 en: {RUTA_PUENTE_P2}")

    df_titulados = pd.read_csv(RUTA_TITULADOS, sep=";", dtype={"codigo_institucion": "int64"})
    df_p2 = pd.read_csv(RUTA_PUENTE_P2, sep=";", dtype={"id_institucion": "int64"})

    log.info("  [✓] Titulados cargados: %d filas, %d columnas", len(df_titulados), len(df_titulados.columns))
    log.info("  [✓] Puente P2 cargado: %d filas, %d columnas", len(df_p2), len(df_p2.columns))

    return df_titulados, df_p2


if __name__ == "__main__":
    t, p = cargar_datos_paso1()
    print("Obtención completada con éxito.")
