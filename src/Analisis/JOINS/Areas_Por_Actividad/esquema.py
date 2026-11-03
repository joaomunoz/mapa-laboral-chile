"""
<src/Analisis/JOINS/Areas_Por_Actividad/esquema.py>
Actualizado 02-11-26 21:22

Single Source of Truth de areas_por_actividad.csv: qué áreas de estudio se vinculan a cada actividad económica.

Grano: 1 fila por (actividad_caenes, area_cine), a nivel nacional. Son 210 filas: se conservan las
combinaciones sin casos, para distinguir "sin muestra" de un dato ausente por error.
Población: titulados ocupados de CASEN.
pct_en_actividad: de los titulados de la actividad, % que viene de esta área.
pct_en_area: de los titulados del área, % que trabaja en esta actividad.
"""

AREAS_POR_ACTIVIDAD = {
    "actividad_caenes": "int64",
    "actividad_ciiu": "object",
    "actividad_glosa": "object",
    "area_cine": "object",            # Nombre usado en cine13_area de Titulados
    "ocupados_titulados": "float64",
    "n_personas": "int64",
    "gl": "int64",
    "cv_pct": "float64",              # CV de ocupados_titulados; vacío sin casos
    "pct_en_actividad": "float64",
    "pct_en_actividad_min": "float64",  # Rango 95%
    "pct_en_actividad_max": "float64",
    "pct_en_area": "float64",
    "pct_en_area_min": "float64",     # Rango 95%
    "pct_en_area_max": "float64",
    "fiabilidad": "object",           # fiable, poco_fiable o no_fiable
}
