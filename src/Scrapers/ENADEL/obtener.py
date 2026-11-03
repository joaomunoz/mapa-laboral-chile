"""
<src/Scrapers/ENADEL/obtener.py>
Actualizado 29-10-26 20:35

Módulo de extracción de microdatos ENADEL (Encuesta Nacional de Demanda Laboral)
de la Subsecretaría del Trabajo.

Fuente: https://www.subtrab.gob.cl/enadel/

Estrategia de extracción (verificada empíricamente):

  La página es WordPress estático (plugin Download Monitor). Los enlaces de
  descarga están directamente en el HTML, sin JavaScript ni AJAX.

  Nivel 1 - Descubrimiento dinámico de enlace:
      GET a la página oficial de ENADEL. Se extraen todos los hrefs y se
      filtra el que contenga "FORMATO-CSV-ENADEL" y termine en ".zip".
      La URL contiene la fecha de publicación (/2026/08/), que cambiará
      cuando publiquen nueva versión → no se hardcodea.

  Nivel 2 - Descarga idempotente del ZIP:
      Si el ZIP ya existe en Entrada/, se omite. Si no, se descarga con
      stream=True y se escribe al disco.

  Nivel 3 - Descompresión idempotente:
      Se extraen los CSVs del ZIP a Entrada/. Si los CSVs ya existen
      extraídos, se omite. El ZIP se conserva como respaldo crudo.

Formatos disponibles en la página (se descarta Stata y R):
  - FORMATO-CSV-ENADEL.zip   ← este scraper
  - FORMATO-STATA-ENADEL.zip
  - FORMATO-RDATA-ENADEL.zip

Lo que NO hace este script (responsabilidad de procesar.py):
  - Leer ni transformar los CSVs extraídos.
  - Detectar encoding, separador ni tipado de columnas.
  - Ninguna transformación de datos.

Salida: Entrada/FORMATO-CSV-ENADEL.zip + CSVs extraídos en Entrada/
"""

from __future__ import annotations

import logging
import re
import sys
import time
import zipfile
from pathlib import Path
from urllib.parse import urlparse

import requests

# Cabecera estándar del proyecto: ruta del script y fecha de actualización.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comun.normalizador import normalizar_texto  # noqa: E402

log = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Configuración
# --------------------------------------------------------------------------- #
URL_PAGINA = "https://www.subtrab.gob.cl/enadel/"

DIR_ENTRADA = Path(__file__).parent / "Entrada"

# Patrón para identificar el enlace de descarga del formato CSV.
# La URL real es: .../wp-content/uploads/{AAAA}/{MM}/FORMATO-CSV-ENADEL.zip
PATRON_ZIP_CSV = re.compile(
    r'href="([^"]*FORMATO-CSV-ENADEL[^"]*\.zip[^"]*)"',
    re.IGNORECASE,
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
}


def _sesion() -> requests.Session:
    """Sesión HTTP con headers compartidos."""
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


# --------------------------------------------------------------------------- #
# Nivel 1 - Descubrir enlace de descarga
# --------------------------------------------------------------------------- #
def descubrir_enlace_zip(s: requests.Session) -> str:
    """
    Extrae dinámicamente el enlace del ZIP con formato CSV desde la página de ENADEL.

    Returns:
        URL limpia del ZIP (sin query params).
    """
    log.info("Conectando a: %s", URL_PAGINA)
    resp = s.get(URL_PAGINA, timeout=60)
    resp.raise_for_status()
    log.info("Página descargada: %.1f MB", len(resp.content) / (1024 * 1024))

    # Buscar el href del ZIP CSV (puede haber varios, tomar el primero)
    m = PATRON_ZIP_CSV.search(resp.text)
    if not m:
        raise RuntimeError(
            "No se encontró enlace FORMATO-CSV-ENADEL.zip en la página. "
            "Verificar que la estructura del sitio no haya cambiado."
        )

    url_cruda = m.group(1).replace("&amp;", "&")

    # Limpiar query params si existen
    parsed = urlparse(url_cruda)
    url_limpia = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    # Extraer nombre del archivo
    nombre = Path(parsed.path).name

    log.info("Enlace ZIP descubierto: %s", nombre)
    log.info("URL: %s", url_limpia)
    return url_limpia


# --------------------------------------------------------------------------- #
# Nivel 2 - Descarga idempotente del ZIP
# --------------------------------------------------------------------------- #
def descargar_zip(s: requests.Session, url: str) -> Path:
    """
    Descarga el ZIP a Entrada/ si no existe previamente.

    Returns:
        Ruta local del ZIP.
    """
    DIR_ENTRADA.mkdir(parents=True, exist_ok=True)
    nombre_zip = Path(urlparse(url).path).name
    ruta_zip = DIR_ENTRADA / nombre_zip

    if ruta_zip.exists():
        peso_mb = ruta_zip.stat().st_size / (1024 * 1024)
        log.info("ZIP ya descargado: %s (%.1f MB)", nombre_zip, peso_mb)
        return ruta_zip

    log.info("Descargando: %s", nombre_zip)
    try:
        resp = s.get(url, stream=True, timeout=300)
        resp.raise_for_status()

        total_bytes = 0
        with open(ruta_zip, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
                total_bytes += len(chunk)

        peso_mb = total_bytes / (1024 * 1024)
        log.info("✓ ZIP descargado: %.1f MB", peso_mb)

    except Exception as exc:  # noqa: BLE001
        if ruta_zip.exists():
            ruta_zip.unlink()
        raise RuntimeError(f"Error descargando ZIP: {exc}") from exc

    return ruta_zip


# --------------------------------------------------------------------------- #
# Nivel 3 - Descompresión idempotente
# --------------------------------------------------------------------------- #
def extraer_zip(ruta_zip: Path) -> list[Path]:
    """
    Extrae los contenidos del ZIP a Entrada/, omitiendo archivos ya extraídos.

    Returns:
        Lista de rutas de archivos extraídos (incluye los preexistentes).
    """
    log.info("Extrayendo: %s", ruta_zip.name)

    rutas: list[Path] = []
    extraidos_nuevos = 0

    try:
        with zipfile.ZipFile(ruta_zip, "r") as zf:
            for info in zf.infolist():
                # Evitar path traversal (seguridad básica)
                destino = DIR_ENTRADA / info.filename
                if not destino.resolve().is_relative_to(DIR_ENTRADA.resolve()):
                    log.warning("Ruta insegura omitida: %s", info.filename)
                    continue

                # Si ya existe, omitir
                if destino.exists():
                    rutas.append(destino)
                    continue

                # Extraer
                destino.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info) as src, open(destino, "wb") as dst:
                    dst.write(src.read())
                rutas.append(destino)
                extraidos_nuevos += 1

    except zipfile.BadZipFile as exc:
        raise RuntimeError(f"ZIP corrupto o inválido: {ruta_zip.name}") from exc

    log.info("Extracción completada: %d archivos nuevos, %d total",
             extraidos_nuevos, len(rutas))
    return rutas


# --------------------------------------------------------------------------- #
# Orquestador
# --------------------------------------------------------------------------- #
def obtener_enadel() -> list[Path]:
    """
    Descarga y extrae los microdatos ENADEL en Entrada/.

    Returns:
        Lista de rutas de archivos (ZIP + CSVs extraídos).
    """
    s = _sesion()

    # Nivel 1: descubrir enlace
    url_zip = descubrir_enlace_zip(s)
    time.sleep(0.5)

    # Nivel 2: descargar ZIP
    ruta_zip = descargar_zip(s, url_zip)
    time.sleep(0.5)

    # Nivel 3: extraer CSVs
    rutas_extraidas = extraer_zip(ruta_zip)

    # Resumen
    log.info("=== Resumen ENADEL ===")
    log.info("  ZIP : %s (%.1f MB)", ruta_zip.name,
             ruta_zip.stat().st_size / (1024 * 1024))
    log.info("  Archivos extraídos: %d", len(rutas_extraidas))
    log.info("  Directorio: %s", DIR_ENTRADA)

    return [ruta_zip] + rutas_extraidas


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    rutas = obtener_enadel()

    print("\n=== ENADEL — Microdescarga ===")
    print(f"Archivos en Entrada/:")
    for ruta in sorted(rutas):
        if ruta.is_file():
            peso_mb = ruta.stat().st_size / (1024 * 1024)
            print(f"  {ruta.name:45s}  {peso_mb:6.1f} MB")
    print(f"\nTotal: {len([r for r in rutas if r.is_file()])} archivos")
