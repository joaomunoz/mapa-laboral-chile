"""
<src/Scrapers/CENSO/obtener_cartografia.py>

Deja en Entrada/cartografia/ la capa regional de la cartografía oficial del Censo 2024, que usa generar_mapa.py.
Si el archivo ya está, no hace nada.

Decisiones:
  - Separado de obtener.py: quien solo regenera el mapa necesita esta capa, no los microdatos de personas.
  - Descarga el zip completo (795 MB) aunque la capa ocupa 89 MB dentro de él: pedir solo esa parte con rangos HTTP
    ahorra datos, pero agrega código para un paso que se ejecuta rara vez.
  - Borra el zip al terminar: las otras 9 capas no se usan.
"""

from __future__ import annotations

import logging
import shutil
import zipfile
from pathlib import Path

from obtener import DIR_ENTRADA, descargar

log = logging.getLogger(__name__)

URL_ZIP = "https://storage.googleapis.com/bktdescargascenso2024/Cartografia/GEOPARQUET/Cartografia_censo2024_Pais.zip"
DIR_CARTOGRAFIA = DIR_ENTRADA / "cartografia"
RUTA_ZIP = DIR_CARTOGRAFIA / "Cartografia_censo2024_Pais.zip"
RUTA_REGIONES = DIR_CARTOGRAFIA / "Cartografia_censo2024_Pais_Regional.parquet"


def obtener_cartografia() -> Path:
    """Deja disponible la capa regional."""
    if RUTA_REGIONES.exists():
        log.info("Ya existe: %s", RUTA_REGIONES.name)
        return RUTA_REGIONES
    parcial = RUTA_REGIONES.with_suffix(".part")
    # Pasa por .part para que un corte no deje una capa truncada que la próxima ejecución daría por buena.
    with zipfile.ZipFile(descargar(URL_ZIP, RUTA_ZIP)) as archivo, archivo.open(RUTA_REGIONES.name) as origen, parcial.open("wb") as destino:
        shutil.copyfileobj(origen, destino)
    parcial.rename(RUTA_REGIONES)
    RUTA_ZIP.unlink()
    log.info("Extraída: %s", RUTA_REGIONES.name)
    return RUTA_REGIONES


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    obtener_cartografia()
