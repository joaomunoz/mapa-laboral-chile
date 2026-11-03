"""
<src/Scrapers/Titulados/obtener.py>

Módulo de extracción de datos de Titulados desde mifuturo.cl.
Descarga a la carpeta Entrada/ solo la base histórica oficial:
  Base Titulados histórica (ej. 2007-2025) → titulados_<anio_inicio>_<anio_fin>.xlsx

La base anual (TITULADO_<anio>_web_...) NO se descarga: auditoría 01-11-26
verificó que es idéntica al último año de la histórica (mismas 15,469 filas,
329,011 titulaciones y códigos de programa). Descargarla solo duplicaba datos
en Entrada/ sin aportar información, y procesar.py lee únicamente la histórica.

La detección es dinámica (scraping del HTML), por lo que resiste
actualizaciones de URLs con fechas cambiantes en mifuturo.cl.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

# URL oficial de la página fuente
URL_BASE = "https://www.mifuturo.cl/bases-de-datos-titulados/"

# Carpeta Entrada/ del scraper de Titulados
DIR_ENTRADA = Path(__file__).parent / "Entrada"

# Patrón de la base histórica en los href: TITULADO_2007-2025_web_...
# (el rango de años exige el guion, así que nunca calza con la base anual).
PATRON_HISTORICA = re.compile(r"TITULADO_(\d{4})-(\d{4})_web_", re.IGNORECASE)


def _obtener_enlaces(url: str) -> list[str]:
    """Extrae todos los href de enlaces .xlsx desde la página fuente."""
    log.info(f"Descargando página: {url}")
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    enlaces = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".xlsx") or ".xlsx" in href.lower():
            # Completar URL relativa
            if not href.startswith("http"):
                href = "https://www.mifuturo.cl" + href if href.startswith("/") else url.rstrip("/") + "/" + href
            enlaces.append(href)
    return enlaces


def _descargar_archivo(url_archivo: str, destino: Path) -> Path:
    """Descarga un archivo desde una URL y lo guarda en la ruta destino."""
    log.info(f"Descargando: {url_archivo}")
    resp = requests.get(url_archivo, timeout=120)
    resp.raise_for_status()
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(resp.content)
    log.info(f"Guardado en: {destino} ({len(resp.content):,} bytes)")
    return destino


def obtener_titulados() -> Path:
    """
    Descarga la base histórica de titulados desde mifuturo.cl.

    Returns:
        Ruta del archivo descargado, ej. Path(".../Entrada/titulados_2007_2025.xlsx").

    Raises:
        RuntimeError: si la página no publica ninguna base histórica. Se falla
        en vez de solo advertir porque procesar.py no tiene otra entrada posible.
    """
    enlaces = _obtener_enlaces(URL_BASE)
    log.info(f"Se encontraron {len(enlaces)} enlaces .xlsx en la página.")

    # Si la página llegara a publicar varias históricas, se elige la de rango
    # más amplio (año inicial menor, año final mayor): es la que contiene a las demás.
    candidatas = [
        (int(m.group(1)), int(m.group(2)), enlace)
        for enlace in enlaces
        if (m := PATRON_HISTORICA.search(enlace))
    ]
    if not candidatas:
        raise RuntimeError(f"No se encontró la base histórica de titulados en {URL_BASE}")
    if len(candidatas) > 1:
        log.warning(f"Se encontraron {len(candidatas)} bases históricas; se usa la de rango más amplio.")

    anio_ini, anio_fin, enlace = min(candidatas, key=lambda c: (c[0], -c[1]))
    destino = DIR_ENTRADA / f"titulados_{anio_ini}_{anio_fin}.xlsx"
    return _descargar_archivo(enlace, destino)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ruta = obtener_titulados()
    print("\n=== Archivo descargado ===")
    print(f"  [historica] → {ruta}")
