"""
<src/Scrapers/comun/periodos.py>

Periodo de la ENE con que se contrasta el Censo 2024. Vive en un solo lugar para que las tablas de contraste
no puedan quedar con meses distintos.

Decisión (estrategia de consistencia temporal, 07-11-26): el contraste usa los mismos meses del censo, que
pregunta por la "semana pasada" entre marzo y julio de 2024. Así una diferencia entre fuentes no se puede deber
a la fecha. El cambio en el tiempo se mide ENE contra ENE, nunca censo menos ENE.

Escala: cada mes de la ENE es un tercio de la población (ver ENE/esquema.py, PANEL Y ESCALA). Sumar 5 meses
y multiplicar por 3/5 da el promedio trimestral, comparable con las cifras de los boletines.
"""

from pathlib import Path

RUTA_ENE_CONTRASTE = Path(__file__).resolve().parents[1] / "ENE" / "Salida" / "ene_procesado_2024.csv"
MESES_CONTRASTE = ["2024-03", "2024-04", "2024-05", "2024-06", "2024-07"]
FACTOR_CONTRASTE = 3 / len(MESES_CONTRASTE)
TEXTO_CONTRASTE = "marzo a julio de 2024"

# Cuadre con INE: el trimestre de ese periodo que reproduce ENE/procesar.py (Boletín INE n°310, 29-08-2024).
MESES_BOLETIN_CONTRASTE = ["2024-05", "2024-06", "2024-07"]
OCUPADOS_INE_CONTRASTE = 9_257_480

# Evolución (fase 4, 08-11-26): la misma ventana de meses en 2026, para medir el cambio ENE contra ENE sin que
# influya la estacionalidad. Es la última ventana completa de marzo a julio que tiene la ENE procesada.
RUTA_ENE_ACTUAL = Path(__file__).resolve().parents[1] / "ENE" / "Salida" / "ene_procesado.csv"
MESES_ACTUAL = ["2026-03", "2026-04", "2026-05", "2026-06", "2026-07"]
TEXTO_ACTUAL = "marzo a julio de 2026"
