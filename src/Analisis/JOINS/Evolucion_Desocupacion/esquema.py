"""
<src/Analisis/JOINS/Evolucion_Desocupacion/esquema.py>

Single Source of Truth de evolucion_desocupacion.csv: cambio de la tasa de desocupación entre marzo a julio de
2024 (los meses del Censo) y los mismos meses de 2026, medido ENE contra ENE.

Grano: 1 fila por (codigo_region, nivel_titulo). Son 20 filas: Chile, las 16 regiones y Chile por nivel de título.
Región: donde VIVE la persona, igual que la tasa del censo. Región por nivel queda fuera: con 5 meses pocas
regiones tienen muestra para un nivel, y un cambio suma el error de dos años.
"""

EVOLUCION_DESOCUPACION = {
    "codigo_region": "Int64",          # Vacío para Chile
    "nombre_region": "object",         # "Chile" o el nombre de la región
    "nivel_titulo": "object",          # Todos, Profesional, Tecnico o Sin_titulo
    "tasa_2024": "float64",            # Marzo a julio de 2024 (%)
    "cv_2024": "float64",
    "n_desocupados_2024": "int64",     # idrph únicos en la muestra
    "tasa_2026": "float64",            # Marzo a julio de 2026 (%)
    "cv_2026": "float64",
    "n_desocupados_2026": "int64",
    "diferencia_pp": "float64",        # tasa_2026 - tasa_2024
    "diferencia_min": "float64",       # Rango 95%; trata los dos años como muestras independientes
    "diferencia_max": "float64",
    "fiabilidad": "object",            # fiable, poco_fiable o no_fiable: la peor de los dos años
    "lectura": "object",               # sube, baja, sin_cambio_claro o no_fiable
}
