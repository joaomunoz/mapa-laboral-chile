"""
<src/Analisis/Calculos_control/titulados_ocupados_region_actividad/obtener.py>
Actualizado 02-11-26 16:40

Carga las entradas de la tabla de control titulados_ocupados_region_actividad:
  1. src/Scrapers/ENE/Salida/ene_procesado.csv
  2. src/Analisis/Puentes_de_mapeo/Salida/P1_puente_actividades.csv (P1)
"""

import logging
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)

DIR_ACTUAL = Path(__file__).resolve().parent
DIR_ANALISIS = DIR_ACTUAL.parents[1]
DIR_SCRAPERS = DIR_ANALISIS.parent / "Scrapers"

RUTA_ENE = DIR_SCRAPERS / "ENE" / "Salida" / "ene_procesado.csv"
RUTA_P1 = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida" / "P1_puente_actividades.csv"

COLUMNAS_ENE = [
    "idrph", "mes", "codigo_region", "nombre_region", "estrato", "conglomerado",
    "fact_cal", "cine11_1d", "cae_especifico", "r_p_rev4cl_caenes",
]


def cargar_datos():
    """Devuelve (ene, p1); falla si falta una entrada."""
    for ruta in (RUTA_ENE, RUTA_P1):
        if not ruta.exists():
            raise FileNotFoundError(f"No se encuentra: {ruta}")
    ene = pd.read_csv(RUTA_ENE, sep=";", usecols=COLUMNAS_ENE)
    p1 = pd.read_csv(RUTA_P1, sep=";", usecols=["actividad_caenes", "actividad_ciiu", "actividad_glosa"])
    log.info("  [✓] ENE: %d filas | P1: %d filas", len(ene), len(p1))
    return ene, p1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    cargar_datos()
