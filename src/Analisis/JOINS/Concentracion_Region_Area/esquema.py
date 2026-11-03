"""
<src/Analisis/JOINS/Concentracion_Region_Area/esquema.py>

Single Source of Truth de concentracion_region_area.csv: qué áreas de estudio concentra cada región.

Grano: 1 fila por (codigo_region, area_cine). Son 160 filas: se conservan las combinaciones sin casos, para
que el mapa las muestre como "sin muestra".
Región: donde VIVE el titulado, porque CASEN no informa la región de trabajo. No se debe leer como lugar de
empleo ni mezclar con concentracion_region_actividad.csv, que sí usa la región de trabajo.
peso_relativo: cuántas veces pesa el área en la región respecto del país.
"""

CONCENTRACION_REGION_AREA = {
    "codigo_region": "int64",
    "nombre_region": "object",
    "area_cine": "object",       # Nombre usado en cine13_area de Titulados
    "titulados": "float64",
    "n_personas": "int64",
    "gl": "int64",
    "cv_pct": "float64",         # CV de titulados; vacío sin casos
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
