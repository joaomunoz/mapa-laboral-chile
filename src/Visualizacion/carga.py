"""
<src/Visualizacion/carga.py>

Lectura de las entradas y escritura de la página. Es el único módulo que toca archivos, salvo el control que compara
con los microdatos del Censo cuando están disponibles (controles.py).
"""

from __future__ import annotations

import re

import geopandas as gpd
import pandas as pd

from config import (
    ARCHIVOS_CSS, ARCHIVOS_JS, DIR_WEB,
    RUTA_AREAS, RUTA_CARRERAS, RUTA_CENSO, RUTA_CENSO_PROCESADO, RUTA_CENSO_SEXO, RUTA_EVOLUCION, RUTA_FORMALIDAD, RUTA_NIVELES, RUTA_PLANTILLA, RUTA_TITULO_EDAD,
    RUTA_REGIONES, RUTA_SALIDA,
)


def cargar_tablas() -> dict[str, pd.DataFrame]:
    """Tablas del Censo y de los cruces que arman los datos de la página."""
    rutas = {"censo": RUTA_CENSO, "procesado": RUTA_CENSO_PROCESADO, "por_sexo": RUTA_CENSO_SEXO, "areas": RUTA_AREAS,
             "carreras": RUTA_CARRERAS, "niveles": RUTA_NIVELES, "evolucion": RUTA_EVOLUCION, "formalidad": RUTA_FORMALIDAD,
             "titulo_edad": RUTA_TITULO_EDAD}
    return {nombre: pd.read_csv(ruta, sep=";") for nombre, ruta in rutas.items()}


def leer_regiones() -> gpd.GeoDataFrame:
    return gpd.read_parquet(RUTA_REGIONES).set_geometry("SHAPE")


def leer_fuente(ruta: str) -> str:
    """Archivo de web/ sin su cabecera: la ruta de la cabecera sirve a quien edita, no a quien abre el mapa."""
    return re.sub(r"\A/\*.*?\*/\n", "", (DIR_WEB / ruta).read_text(encoding="utf-8"), count=1, flags=re.S)


def leer_codigo_js() -> dict[str, str]:
    return {ruta: leer_fuente(ruta) for ruta in ARCHIVOS_JS}


def archivos_web_sin_listar() -> list[str]:
    """Archivos de css/ y js/ que no están en ARCHIVOS_CSS ni ARCHIVOS_JS: no llegarían a la página."""
    en_disco = {p.relative_to(DIR_WEB).as_posix() for p in DIR_WEB.rglob("*") if p.suffix in (".css", ".js")}
    return sorted(en_disco - set(ARCHIVOS_CSS) - set(ARCHIVOS_JS))


def leer_plantilla() -> str:
    """index.html con los estilos y el código ya insertados; los datos se insertan después, en generar_mapa.py."""
    estilos = "".join(leer_fuente(r) for r in ARCHIVOS_CSS)
    codigo = "".join(leer_codigo_js().values())
    return RUTA_PLANTILLA.read_text(encoding="utf-8").replace("__ESTILOS__", estilos, 1).replace("__CODIGO__", codigo, 1)


def escribir_pagina(html: str) -> None:
    RUTA_SALIDA.parent.mkdir(exist_ok=True)
    RUTA_SALIDA.write_text(html, encoding="utf-8")
