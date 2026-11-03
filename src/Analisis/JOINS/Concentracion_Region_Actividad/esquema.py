"""
<src/Analisis/JOINS/Concentracion_Region_Actividad/esquema.py>

Single Source of Truth de concentracion_region_actividad.csv: qué actividades económicas concentra cada región.

Grano: 1 fila por (codigo_region, actividad_caenes). Son 336 filas: se conservan las 11 combinaciones sin
casos en la encuesta, para que el mapa las muestre como "sin muestra" y no como si no existieran.
Región: donde está el TRABAJO. Población: todos los ocupados, no solo titulados.
peso_relativo: cuántas veces pesa la actividad en la región respecto del país.
"""

CONCENTRACION_REGION_ACTIVIDAD = {
    "codigo_region": "int64",
    "nombre_region": "object",
    "actividad_caenes": "int64",
    "actividad_ciiu": "object",
    "actividad_glosa": "object",
    "ocupados": "float64",       # Promedio trimestral (10 meses × 3/10)
    "n_personas": "int64",       # idrph únicos
    "gl": "int64",
    "cv_pct": "float64",         # CV de ocupados; vacío sin casos
    "pct_en_region": "float64",
    "pct_min": "float64",        # Rango 95%
    "pct_max": "float64",
    "pct_nacional": "float64",
    "peso_relativo": "float64",
    "peso_min": "float64",       # Rango 95%; trata pct_nacional como fijo
    "peso_max": "float64",
    "fiabilidad": "object",      # fiable, poco_fiable o no_fiable
    "lectura": "object",         # concentra, similar, bajo_lo_nacional o sin_muestra
}
