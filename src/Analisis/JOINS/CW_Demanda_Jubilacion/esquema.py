"""
<src/Analisis/JOINS/CW_Demanda_Jubilacion/esquema.py>
Actualizado 02-11-26 16:40

Single Source of Truth del Paso 3 del índice: vacantes por jubilación al año.

jubilacion_carrera_region.csv: 1 fila por (codigo_region, carrera_generica); entra al índice.
jubilacion_region_titulo.csv: 1 fila por (codigo_region, nivel_titulo), con su calidad.
Son ESTIMACIONES sintéticas: ENE no trae carrera y CASEN no alcanza por región.
"""

JUBILACION_CARRERA_REGION = {
    "codigo_region": "int64",
    "nombre_region": "object",
    "nivel_titulo": "object",
    "carrera_generica": "object",
    "origen_propension": "object",       # propia, area_nivel o nivel: de dónde sale el peso de mayores
    "jubilaciones_anuales": "float64",   # Valor base: salidas efectivas del trabajo
    "jubilaciones_edad_legal": "float64",  # Sensibilidad: quienes llegan a la edad legal
}

JUBILACION_REGION_TITULO = {
    "codigo_region": "int64",
    "nombre_region": "object",
    "nivel_titulo": "object",
    "n_personas": "int64",               # Ocupados a 5 años de la edad legal, idrph únicos
    "gl": "int64",
    "cerca_directo": "float64",          # Medición directa de ENE
    "cv_pct": "float64",
    "origen_celda": "object",            # celda_propia u ocupados_x_nacional
    "cerca_usados": "float64",
    "jubilaciones_anuales": "float64",
    "jubilaciones_edad_legal": "float64",
}

VALIDACION_JUBILACION = {
    "prueba": "object",
    "grupo": "object",
    "valor": "float64",
    "descripcion": "object",
}
