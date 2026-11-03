"""
<src/Analisis/Calculos_control/cobertura_enadel_ene_region_actividad/obtener.py>

Carga las entradas de la tabla de control cobertura_enadel_ene_region_actividad:
  1. src/Scrapers/ENADEL/Salida/enadel_empresas_procesado.csv
  2. src/Scrapers/ENE/Salida/ene_procesado.csv
  3. src/Analisis/Puentes_de_mapeo/Salida/P1_puente_actividades.csv (P1)
"""

import logging
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)

DIR_ACTUAL = Path(__file__).resolve().parent
DIR_ANALISIS = DIR_ACTUAL.parents[1]
DIR_SCRAPERS = DIR_ANALISIS.parent / "Scrapers"

RUTA_ENADEL = DIR_SCRAPERS / "ENADEL" / "Salida" / "enadel_empresas_procesado.csv"
RUTA_ENE = DIR_SCRAPERS / "ENE" / "Salida" / "ene_procesado.csv"
RUTA_P1 = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida" / "P1_puente_actividades.csv"

# ENADEL conserva su nombre de origen; se normaliza al leer.
COLUMNAS_ENADEL = ["idempresa_ficticio", "codigo_region", "nombre_region", "ciiu_seccion", "pond_final", "dotacion_total"]
COLUMNAS_ENE = [
    "idrph", "mes", "codigo_region", "nombre_region", "estrato", "conglomerado",
    "fact_cal", "cae_especifico", "categoria_ocupacion", "r_p_rev4cl_caenes",
]


def cargar_datos():
    """Devuelve (enadel, ene, p1); falla si falta una entrada."""
    for ruta in (RUTA_ENADEL, RUTA_ENE, RUTA_P1):
        if not ruta.exists():
            raise FileNotFoundError(f"No se encuentra: {ruta}")
    enadel = pd.read_csv(RUTA_ENADEL, sep=None, engine="python", usecols=COLUMNAS_ENADEL).rename(columns={"ciiu_seccion": "actividad_ciiu"})
    ene = pd.read_csv(RUTA_ENE, sep=";", usecols=COLUMNAS_ENE)
    p1 = pd.read_csv(RUTA_P1, sep=";", usecols=["actividad_caenes", "actividad_ciiu", "actividad_glosa"])
    log.info("  [✓] ENADEL: %d empresas | ENE: %d filas | P1: %d filas", len(enadel), len(ene), len(p1))
    return enadel, ene, p1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    cargar_datos()
