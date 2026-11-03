"""
<src/Analisis/JOINS/CW_Ocupados_Carrera_Region_Actividad/esquema.py>

Single Source of Truth del reparto de titulados ocupados por región, carrera y actividad.

Grano: 1 fila por (codigo_region, carrera_generica, actividad_caenes) con estimación positiva.
Son ESTIMACIONES sintéticas, no mediciones: ninguna encuesta mide esta celda.
"""

OCUPADOS_CARRERA_REGION_ACTIVIDAD = {
    "codigo_region": "int64",          # Región del empleo
    "nombre_region": "object",
    "nivel_titulo": "object",        # Tecnico o Profesional (incluye posgrado)
    "carrera_generica": "object",
    "area_cine_sies": "object",
    "nivel_confianza": "object",       # Origen del perfil (P7)
    "actividad_caenes": "int64",
    "actividad_ciiu": "object",
    "actividad_glosa": "object",
    "stock_sies": "int64",             # Titulaciones 2007-2025 por sede en la región
    "ocupados_carrera_region": "float64",  # Ocupados ENE repartidos según el stock
    "ocupados_estimados": "float64",   # Estimación de la celda tras el ajuste parcial
    "pct_en_carrera_region": "float64",
    "pct_perfil_nacional": "float64",  # Perfil de P7 antes del ajuste regional
}

VALIDACION_REPARTO = {
    "prueba": "object",
    "variante": "object",
    "grupo": "object",
    "n_comparaciones": "int64",
    "disimilitud_media": "float64",    # Puntos de 100 que habría que mover para igualar repartos
    "disimilitud_mediana": "float64",
}
