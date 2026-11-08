"""
<src/Scrapers/ENE/obtener.py>

Módulo de extracción de microdatos ENE (Encuesta Nacional de Empleo) del INE.

Fuente: https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/ocupacion-y-desocupacion

Estrategia de extracción (verificada empíricamente):

  El sitio del INE NO sirve los enlaces de descarga en el HTML inicial.
  Se carga dinámicamente mediante una cascada de AJAX (jQuery) que navega
  una estructura de carpetas Sitefinity. La secuencia real es:

  Nivel 1 - Página principal:
      GET a la página oficial. Se extrae el atributo `data-folder` del
      bloque <div> que contiene el texto "BASES DE DATOS" (GUID de carpeta).

  Nivel 2 - Subcarpetas:
      POST a `/hijosCarpeta/` con `idFolder={GUID_BD}` → devuelve JSON con
      las subcarpetas (Libro de Códigos, Bases anualizadas, 2026, 2025, ...).
      Se busca la carpeta cuyo `Titulo` coincida con el año objetivo.

  Nivel 3 - Archivos:
      POST a `/getArchivos/` con `idFolder={GUID_AÑO}` → devuelve JSON con
      los archivos (.CSV y .DTA) del año. Se filtran solo los `.CSV`.

  Nivel 4 - Descarga idempotente:
      Cada CSV se descarga a Entrada/{AÑO}/, omitiendo los que ya existen.
      Los archivos pesan ~36-38 MB, se usa stream=True.

Nota sobre URLs: el endpoint devuelve URLs con prefijo `http:`, pero el
JavaScript del INE las reemplaza por `https:`. Este script aplica el mismo
reemplazo antes de descargar.

Lo que NO hace este script (responsabilidad de procesar.py):
  - Detectar encoding del CSV (probablemente Latin-1 o CP1252).
  - Concatenar los múltiples archivos en uno consolidado.
  - Aplicar filtros de población, regiones o factores de expansión.
  - Ninguna transformación de datos.

Salida: Entrada/{AÑO}/ene-{AÑO}-{MM}-{siglas}.csv  (crudos, sin transformar)
"""

from __future__ import annotations

import json
import logging
import re
import sys
import time
from pathlib import Path

import requests

# Cabecera estándar del proyecto: ruta del script y fecha de actualización.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comun.normalizador import normalizar_texto  # noqa: E402

log = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Configuración
# --------------------------------------------------------------------------- #
URL_BASE_INE = (
    "https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/ocupacion-y-desocupacion"
)
URL_HIJOS = f"{URL_BASE_INE}/hijosCarpeta/"
URL_ARCHIVOS = f"{URL_BASE_INE}/getArchivos/"

DIR_ENTRADA = Path(__file__).parent / "Entrada"

ANIO_OBJETIVO = 2026

# Texto exacto del nodo de navegación que contiene la carpeta "BASES DE DATOS".
NOMBRE_CARPETA_BASES = "BASES DE DATOS"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": URL_BASE_INE,
}

# Pausa entre peticiones para no saturar el servidor del INE.
PAUSA_SEG = 0.5


def _sesion() -> requests.Session:
    """Sesión HTTP con headers compartidos."""
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


# --------------------------------------------------------------------------- #
# Nivel 1 - Descubrir GUID de "BASES DE DATOS" desde el HTML principal
# --------------------------------------------------------------------------- #
def _obtener_guid_bases(s: requests.Session) -> str:
    """
    Extrae el data-folder (GUID) del nodo 'BASES DE DATOS' en la navegación principal.

    El HTML contiene líneas como:
        <div class="navPrincipalDescargas" data-folder="83b8e18c-...">
            <em class="fas fa-database"></em>BASES DE DATOS</div>

    Returns:
        GUID (UUID) de la carpeta Sitefinity de Bases de Datos.
    """
    log.info("Obteniendo GUID de '%s' desde la página principal...", NOMBRE_CARPETA_BASES)
    resp = s.get(URL_BASE_INE, timeout=60)
    resp.raise_for_status()

    # Buscar data-folder seguido inmediatamente por el ícono y texto de la carpeta.
    # Se restringe el rango entre > y </div> para no cruzar nodos hermanos.
    patron = re.compile(
        r'data-folder="([0-9a-f\-]{36})"[^>]*>'
        r'[^<]*<em[^>]*>[^<]*</em>\s*BASES\s+DE\s+DATOS',
        re.IGNORECASE,
    )
    m = patron.search(resp.text)
    if not m:
        raise RuntimeError(
            f"No se encontró el nodo '{NOMBRE_CARPETA_BASES}' en la página del INE. "
            f"Verificar que la estructura del sitio no haya cambiado."
        )

    guid = m.group(1)
    log.info("GUID de '%s': %s", NOMBRE_CARPETA_BASES, guid)
    return guid


# --------------------------------------------------------------------------- #
# Nivel 2 - Obtener subcarpetas (años)
# --------------------------------------------------------------------------- #
def _obtener_subcarpetas(s: requests.Session, guid: str) -> list[dict]:
    """
    Consulta las subcarpetas de una carpeta vía AJAX.

    Returns:
        Lista de dicts con claves: Titulo, Id, ParentId.
    """
    log.info("Consultando subcarpetas de: %s", guid)
    resp = s.post(URL_HIJOS, data={"idFolder": guid}, timeout=30)
    resp.raise_for_status()

    data = resp.json()
    carpetas = data.get("folder", [])
    log.info("Subcarpetas encontradas: %d", len(carpetas))
    for c in carpetas:
        log.info("  → %s (%s)", c.get("Titulo", "?"), c.get("Id", "?")[:8])
    return carpetas


# --------------------------------------------------------------------------- #
# Nivel 3 - Obtener archivos de una carpeta
# --------------------------------------------------------------------------- #
def _obtener_archivos(s: requests.Session, guid: str) -> list[dict]:
    """
    Consulta los archivos de una carpeta vía AJAX.

    Returns:
        Lista de dicts con claves: Titulo, Url, Tipo, Peso, etc.
    """
    log.info("Consultando archivos de: %s", guid)
    resp = s.post(URL_ARCHIVOS, data={"idFolder": guid}, timeout=30)
    resp.raise_for_status()

    data = resp.json()
    archivos = data.get("documento", [])
    log.info("Archivos encontrados: %d", len(archivos))
    return archivos


# --------------------------------------------------------------------------- #
# Nivel 4 - Descarga idempotente
# --------------------------------------------------------------------------- #
def descargar_archivos(
    s: requests.Session,
    enlaces_csv: list[dict],
    anio: int,
) -> list[Path]:
    """
    Descarga cada CSV a Entrada/{anio}/, omitiendo los que ya existen.

    Args:
        s: Sesión HTTP activa.
        enlaces_csv: Lista de dicts con 'nombre' y 'url' (ya con https://).
        anio: Año objetivo (para la subcarpeta).

    Returns:
        Lista de rutas de archivos disponibles localmente.
    """
    dir_destino = DIR_ENTRADA / str(anio)
    dir_destino.mkdir(parents=True, exist_ok=True)
    log.info("Directorio destino: %s", dir_destino)

    rutas: list[Path] = []

    for i, enlace in enumerate(enlaces_csv, start=1):
        ruta_local = dir_destino / enlace["nombre"]

        # Idempotencia: si ya existe, omitir
        if ruta_local.exists():
            peso_mb = ruta_local.stat().st_size / (1024 * 1024)
            log.info("[%d/%d] Ya descargado: %s (%.1f MB)",
                     i, len(enlaces_csv), enlace["nombre"], peso_mb)
            rutas.append(ruta_local)
            continue

        log.info("[%d/%d] Descargando: %s", i, len(enlaces_csv), enlace["nombre"])
        try:
            resp = s.get(enlace["url"], stream=True, timeout=300)
            resp.raise_for_status()

            total_bytes = 0
            with open(ruta_local, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
                    total_bytes += len(chunk)

            peso_mb = total_bytes / (1024 * 1024)
            log.info("  ✓ Descargado: %.1f MB", peso_mb)
            rutas.append(ruta_local)

        except Exception as exc:  # noqa: BLE001 - no tumbar el pipeline por un archivo
            log.error("  ✗ Error descargando %s: %s", enlace["nombre"], exc)
            if ruta_local.exists():
                ruta_local.unlink()

        time.sleep(PAUSA_SEG)

    return rutas


# --------------------------------------------------------------------------- #
# Orquestador
# --------------------------------------------------------------------------- #
def obtener_ene(anio: int = ANIO_OBJETIVO) -> list[Path]:
    """
    Descarga los microdatos ENE del INE a Entrada/{anio}/.

    Flujo:
        1. GET página principal → GUID de 'BASES DE DATOS'
        2. POST hijosCarpeta → GUID del año {anio}
        3. POST getArchivos → lista de archivos del año
        4. Filtrar solo .CSV y descargar a Entrada/{anio}/

    Args:
        anio: Año objetivo (defecto 2026).

    Returns:
        Lista de rutas de archivos CSV disponibles localmente.
    """
    s = _sesion()

    # Nivel 1: GUID de Bases de Datos
    guid_bd = _obtener_guid_bases(s)
    time.sleep(PAUSA_SEG)

    # Nivel 2: buscar carpeta del año
    carpetas = _obtener_subcarpetas(s, guid_bd)
    carpeta_anio = next(
        (c for c in carpetas if c.get("Titulo", "").strip() == str(anio)),
        None,
    )
    if carpeta_anio is None:
        titulos = [c.get("Titulo", "?") for c in carpetas]
        raise RuntimeError(
            f"No se encontró la carpeta '{anio}' en Bases de Datos. "
            f"Carpetas disponibles: {titulos}"
        )
    guid_anio = carpeta_anio["Id"]
    log.info("Carpeta '%s' encontrada: %s", anio, guid_anio)
    time.sleep(PAUSA_SEG)

    # Nivel 3: listar archivos del año
    archivos = _obtener_archivos(s, guid_anio)
    time.sleep(PAUSA_SEG)

    # Filtrar solo CSV y preparar URLs con https://
    enlaces_csv: list[dict] = []
    for arch in archivos:
        tipo = arch.get("Tipo", "").upper()
        if ".CSV" not in tipo:
            continue

        url = arch.get("Url", "")
        # El INE devuelve http:// pero el sitio usa https://
        url = url.replace("http://", "https://")

        # Extraer nombre del archivo de la URL
        nombre = url.split("?")[0].split("/")[-1]

        enlaces_csv.append({
            "nombre": nombre,
            "url": url,
            "titulo": arch.get("Titulo", ""),
            "peso_bytes": int(arch.get("Peso", 0)),
        })

    # Ordenar por mes descendente (más reciente primero)
    def _extraer_mes(nombre: str) -> int:
        m = re.search(r'-\d{4}-(\d{2})-', nombre)
        return int(m.group(1)) if m else 0

    enlaces_csv.sort(key=lambda x: _extraer_mes(x["nombre"]), reverse=True)

    log.info("CSVs filtrados para %d: %d de %d archivos totales",
             anio, len(enlaces_csv), len(archivos))
    for e in enlaces_csv:
        peso_mb = e["peso_bytes"] / (1024 * 1024)
        log.info("  → %s (%.1f MB)", e["nombre"], peso_mb)

    if not enlaces_csv:
        raise RuntimeError(f"No se encontraron archivos CSV para {anio}.")

    # Nivel 4: descargar
    rutas = descargar_archivos(s, enlaces_csv, anio)

    # Resumen
    log.info("=== Resumen ENE %d ===", anio)
    log.info("  Enlaces CSV encontrados : %d", len(enlaces_csv))
    log.info("  Archivos disponibles    : %d", len(rutas))
    log.info("  Directorio              : %s", DIR_ENTRADA / str(anio))

    return rutas


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    # Año como argumento (python obtener.py 2024): el contraste con el Censo usa 2024 y el resto, 2026.
    anio = int(sys.argv[1]) if len(sys.argv) > 1 else ANIO_OBJETIVO
    rutas = obtener_ene(anio)

    print(f"\n=== ENE INE — Microdescarga {anio} ===")
    print(f"Archivos en Entrada/{anio}/:")
    total_mb = 0
    for ruta in sorted(rutas):
        peso_mb = ruta.stat().st_size / (1024 * 1024)
        total_mb += peso_mb
        print(f"  {ruta.name:30s}  {peso_mb:6.1f} MB")
    print(f"\nTotal: {len(rutas)} archivos ({total_mb:.1f} MB)")
