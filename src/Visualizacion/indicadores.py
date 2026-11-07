"""
<src/Visualizacion/indicadores.py>

Cálculos del mapa a partir de las tablas. Por ahora, el tramo de color del CL.

Va aparte porque lo usan el armado de los datos y los controles: si viviera en generar_mapa.py, los controles
tendrían que importar el punto de entrada.
"""

from __future__ import annotations

import pandas as pd

from config import CLASE_NEUTRA, CORTES_AZUL, CORTES_ROJO, DECIMALES_CL


def clase_color(peso: float) -> int | None:
    """Tramo de color del CL publicado, con 2 decimales; usa las mismas comparaciones que la lectura. Vacío si no hay dato."""
    if pd.isna(peso):
        return None
    peso = round(float(peso), DECIMALES_CL)
    if peso <= CORTES_AZUL[2]:
        return sum(peso > c for c in CORTES_AZUL[:2])
    if peso < CORTES_ROJO[0]:
        return CLASE_NEUTRA
    return CLASE_NEUTRA + 1 + sum(peso >= c for c in CORTES_ROJO[1:])
