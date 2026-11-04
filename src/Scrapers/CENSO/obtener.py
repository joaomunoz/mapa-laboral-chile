"""
<src/Scrapers/CENSO/obtener.py>

Descarga a Entrada/ los microdatos del Censo de Población y Vivienda 2024 (INE), en formato parquet, y los
descomprime. Si los archivos ya están, no hace nada.

Por qué parquet: pesa menos que el CSV de personas por separado e incluye las tres tablas. La ubicación sale
de la lista de descargas de https://censo2024.ine.gob.cl/resultados/; la página no la muestra en su HTML.
"""

from __future__ import annotations

import logging
import zipfile
from pathlib import Path

import requests

log = logging.getLogger(__name__)

URL_ZIP = "https://storage.googleapis.com/bktdescargascenso2024/viv_hog_per_censo2024.zip"
DIR_ENTRADA = Path(__file__).parent / "Entrada"
RUTA_ZIP = DIR_ENTRADA / "viv_hog_per_censo2024.zip"
RUTA_PERSONAS = DIR_ENTRADA / "personas_censo2024.parquet"
TAMANO_BLOQUE = 1024 * 1024
TIEMPO_ESPERA = 60


def descargar(url: str, ruta: Path) -> Path:
    """Descarga un zip usando un archivo .part, para no dejar uno truncado con el nombre definitivo."""
    if ruta.exists():
        log.info("Ya existe: %s", ruta.name)
        return ruta
    ruta.parent.mkdir(parents=True, exist_ok=True)
    parcial = ruta.with_suffix(".part")
    with requests.get(url, stream=True, timeout=TIEMPO_ESPERA) as respuesta:
        respuesta.raise_for_status()
        with parcial.open("wb") as destino:
            for bloque in respuesta.iter_content(TAMANO_BLOQUE):
                destino.write(bloque)
    parcial.rename(ruta)
    log.info("Descargado: %s", ruta.name)
    return ruta


def obtener() -> Path:
    """Deja disponible el parquet de personas."""
    if RUTA_PERSONAS.exists():
        log.info("Ya existe: %s", RUTA_PERSONAS.name)
        return RUTA_PERSONAS
    with zipfile.ZipFile(descargar(URL_ZIP, RUTA_ZIP)) as archivo:
        archivo.extractall(DIR_ENTRADA)
    return RUTA_PERSONAS


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    obtener()
