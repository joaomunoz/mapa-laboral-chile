"""
<src/Scrapers/CASEN/obtener.py>
Actualizado 02-11-26 03:00

Módulo de extracción de la Encuesta CASEN (Ministerio de Desarrollo Social y Familia).
Descarga a Entrada/ los microdatos de la versión más reciente publicada, en formato Stata.

Por qué CASEN (decisión 02-11-26): es la única fuente con campo de estudio, ocupación y
sector de actividad en la misma persona, lo que permite medir el vínculo carrera → ocupación
→ sector que ENE y ENADEL no entregan. Es la quinta fuente oficial del proyecto.

Detección dinámica: el año se toma del menú de encuestas de la página oficial, de modo que
una versión nueva (CASEN 2026, en levantamiento) se detecta sin cambiar el código.

Se descarga .dta y no .RData porque pandas lo lee sin dependencias nuevas, aunque pesa más
(1.6 GB frente a 47 MB). La descarga es idempotente, se reanuda tras un corte de conexión
y usa un archivo .part para nunca dejar una base truncada con el nombre definitivo.
"""

from __future__ import annotations

import logging
import re
import time
from pathlib import Path

import requests

log = logging.getLogger(__name__)

URL_BASE = "https://observatorio.ministeriodesarrollosocial.gob.cl"
# Cualquier página de encuesta trae el menú completo de versiones.
URL_INDICE = f"{URL_BASE}/encuesta-casen-2024"
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/124.0"}
DIR_ENTRADA = Path(__file__).parent / "Entrada"
BLOQUE_BYTES = 8 * 1024 * 1024
MAX_INTENTOS_SIN_AVANCE = 5
ESPERA_REINTENTO_S = 5


def detectar_anio_vigente() -> int:
    """Devuelve el año más reciente del menú cuya base .dta esté publicada."""
    html = requests.get(URL_INDICE, headers=HEADERS, timeout=60)
    html.raise_for_status()
    anios = sorted({int(a) for a in re.findall(r"encuesta-casen-(\d{4})", html.text)}, reverse=True)
    if not anios:
        raise RuntimeError(f"No se encontraron versiones de CASEN en {URL_INDICE}")
    for anio in anios:
        if requests.head(_url_base_datos(anio), headers=HEADERS, timeout=60, allow_redirects=True).ok:
            log.info("Versiones en el menú: %s | vigente con base publicada: %d", anios[:4], anio)
            return anio
    raise RuntimeError("Ninguna versión de CASEN tiene su base .dta publicada")


def _url_base_datos(anio: int) -> str:
    return f"{URL_BASE}/storage/docs/casen/{anio}/casen_{anio}.dta"


def _tamano(ruta: Path) -> int:
    return ruta.stat().st_size if ruta.exists() else 0


def descargar(anio: int) -> Path:
    """Descarga la base del año indicado; omite si ya existe con el tamaño correcto."""
    url = _url_base_datos(anio)
    destino = DIR_ENTRADA / f"casen_{anio}.dta"
    esperado = int(requests.head(url, headers=HEADERS, timeout=60, allow_redirects=True).headers["Content-Length"])

    if destino.exists() and destino.stat().st_size == esperado:
        log.info("Ya descargada: %s (%.2f GB)", destino.name, esperado / 1024**3)
        return destino

    DIR_ENTRADA.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_suffix(".dta.part")
    log.info("Descargando %s (%.2f GB)...", url, esperado / 1024**3)

    # El servidor corta las conexiones largas: se reanuda desde lo ya escrito en vez de reiniciar.
    # Los intentos sin avance se cuentan aparte para no reintentar para siempre ante una caída real.
    sin_avance = 0
    while _tamano(parcial) < esperado:
        inicio = _tamano(parcial)
        try:
            cabecera = {**HEADERS, "Range": f"bytes={inicio}-"}
            with requests.get(url, headers=cabecera, timeout=120, stream=True) as resp:
                resp.raise_for_status()
                if inicio and resp.status_code != 206:
                    raise RuntimeError(f"El servidor no permite reanudar (HTTP {resp.status_code})")
                with open(parcial, "ab") as archivo:
                    for bloque in resp.iter_content(BLOQUE_BYTES):
                        archivo.write(bloque)
        except requests.RequestException as exc:
            log.warning("Conexión cortada en %.1f%%: %s", 100 * _tamano(parcial) / esperado, type(exc).__name__)
        sin_avance = 0 if _tamano(parcial) > inicio else sin_avance + 1
        if sin_avance >= MAX_INTENTOS_SIN_AVANCE:
            raise RuntimeError(f"Sin avance tras {sin_avance} intentos en {parcial}")
        if _tamano(parcial) < esperado:
            time.sleep(ESPERA_REINTENTO_S)

    obtenido = parcial.stat().st_size
    if obtenido != esperado:
        raise RuntimeError(f"Tamaño inesperado: {obtenido:,} de {esperado:,} bytes en {parcial}")
    parcial.rename(destino)
    log.info("Guardado: %s", destino)
    return destino


def obtener_casen() -> Path:
    return descargar(detectar_anio_vigente())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    print(f"=== Base descargada: {obtener_casen()}")
