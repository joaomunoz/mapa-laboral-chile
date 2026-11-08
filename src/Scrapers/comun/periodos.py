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

NOMBRES_MES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
               "noviembre", "diciembre"]


def texto_meses(meses: list[str]) -> str:
    """'marzo a julio de 2024' desde ['2024-03', ..., '2024-07']: el texto sale de los meses y no puede quedar distinto."""
    (a1, m1), (a2, m2) = (map(int, meses[0].split("-")), map(int, meses[-1].split("-")))
    inicio = NOMBRES_MES[m1 - 1] + ("" if a1 == a2 else f" de {a1}")
    return f"{inicio} a {NOMBRES_MES[m2 - 1]} de {a2}"


RUTA_ENE_CONTRASTE = Path(__file__).resolve().parents[1] / "ENE" / "Salida" / "ene_procesado_2024.csv"
MESES_CONTRASTE = ["2024-03", "2024-04", "2024-05", "2024-06", "2024-07"]
FACTOR_CONTRASTE = 3 / len(MESES_CONTRASTE)
TEXTO_CONTRASTE = texto_meses(MESES_CONTRASTE)

# Cuadre con INE: el trimestre de ese periodo que reproduce ENE/procesar.py (Boletín INE n°310, 29-08-2024).
MESES_BOLETIN_CONTRASTE = ["2024-05", "2024-06", "2024-07"]
OCUPADOS_INE_CONTRASTE = 9_257_480

# Evolución (fase 4, 08-11-26): la misma ventana de meses en 2026, para medir el cambio ENE contra ENE sin que
# influya la estacionalidad. Es la última ventana completa de marzo a julio que tiene la ENE procesada.
RUTA_ENE_ACTUAL = Path(__file__).resolve().parents[1] / "ENE" / "Salida" / "ene_procesado.csv"
MESES_ACTUAL = ["2026-03", "2026-04", "2026-05", "2026-06", "2026-07"]
TEXTO_ACTUAL = texto_meses(MESES_ACTUAL)

# Los dos periodos deben tener los mismos meses del año: si no, la estacionalidad contaría como cambio.
if [m[5:] for m in MESES_CONTRASTE] != [m[5:] for m in MESES_ACTUAL]:
    raise ValueError("La evolución exige los mismos meses del año en ambos periodos")
TEXTO_EVOLUCION = f"{TEXTO_CONTRASTE[:TEXTO_CONTRASTE.rindex(' de ')]} de {MESES_CONTRASTE[0][:4]} y de {MESES_ACTUAL[0][:4]}"
