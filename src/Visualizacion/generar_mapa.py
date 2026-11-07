"""
<src/Visualizacion/generar_mapa.py>

Genera el mapa interactivo: una sola página HTML, sin servidor ni dependencias externas.

Entradas: tablas de Analisis/JOINS y la capa regional de la cartografía del Censo 2024.
Salida:   docs/index.html, en la carpeta del resultado y no en src/: es lo que se publica
Ejecutar: .venv/bin/python src/Visualizacion/generar_mapa.py (requiere geopandas y pyarrow)

Este archivo solo ordena los pasos: cargar, armar datos y geometría, validar y escribir. Cada paso vive en su módulo:
  config.py      rutas y constantes
  carga.py       lectura de las entradas y escritura de la página
  datos.py       JSON que lee la página
  indicadores.py cálculos: tramo del CL, resúmenes, sexo y nivel de estudios
  geometria.py   bordes de las regiones en SVG
  formato.py     cómo se escriben cifras y nombres
  controles.py   controles que detienen la generación
"""

from __future__ import annotations

import json
import logging

from config import RUTA_SALIDA
from geometria import construir_geometria
from carga import cargar_tablas, escribir_pagina, leer_plantilla, leer_regiones
from datos import construir_datos
from controles import validar

log = logging.getLogger(__name__)


def armar_pagina(datos: dict, geo: dict) -> str:
    geometria = {k: geo[k] for k in ("ancho", "alto", "trazados")}
    return leer_plantilla().replace("__DATOS__", json.dumps(datos, ensure_ascii=False)).replace("__GEO__", json.dumps(geometria))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    datos, geo = construir_datos(cargar_tablas()), construir_geometria(leer_regiones())
    html = armar_pagina(datos, geo)
    validar(datos, geo, html)
    escribir_pagina(html)
    log.info("HTML generado: %s (%.0f KB, %d carreras)", RUTA_SALIDA, RUTA_SALIDA.stat().st_size / 1024, len(datos["fichas"]))
