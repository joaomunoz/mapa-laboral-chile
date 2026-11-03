"""
<src/Analisis/JOINS/CW_Competencia_Desocupados/esquema.py>

Single Source of Truth del Paso 2 del índice: desocupados titulados por región y carrera.

desocupados_carrera_region.csv: 1 fila por (codigo_region, titulo_comun, carrera_generica).
Son ESTIMACIONES sintéticas: ENE no pregunta la carrera.
desocupados_region_titulo.csv: 1 fila por (codigo_region, titulo_comun), con la medición directa
de ENE, su calidad y el valor que se reparte.
"""

DESOCUPADOS_CARRERA_REGION = {
    "codigo_region": "int64",
    "nombre_region": "object",
    "titulo_comun": "object",           # Llave P4
    "carrera_generica": "object",
    "entra_al_indice": "bool",             # True solo para pregrado terminal
    "stock_sies": "int64",              # Titulaciones 2007-2025 por sede
    "share_stock": "float64",           # Fracción de la carrera según stock dentro de la región y título
    "share_usada": "float64",           # Fracción final tras la mezcla con CASEN y la tasa de desempleo
    "origen_tasa": "object",            # propia, si difiere de su nivel; nivel en otro caso
    "tasa_desempleo_usada": "float64",  # % usado para ajustar; solo pregrado
    "origen_reparto": "object",         # stock_region, o stock_nacional si la región no tiene oferta
    "desocupados_estimados": "float64",
    "desocupados_solo_stock": "float64",  # Sensibilidad: reparto anterior
    "origen_celda": "object",           # celda_propia o mezcla_nacional
    "fiabilidad_celda": "object",       # fiable, poco_fiable o no_fiable (celda directa de ENE)
}

DESOCUPADOS_REGION_TITULO = {
    "codigo_region": "int64",
    "nombre_region": "object",
    "titulo_comun": "object",
    "n_personas": "int64",              # idrph únicos: una persona se repite hasta 4 veces en 10 meses
    "gl": "int64",
    "desocupados_directo": "float64",   # ENE, promedio trimestral
    "error_estandar": "float64",
    "cv_pct": "float64",
    "fiabilidad_celda": "object",
    "origen_celda": "object",
    "desocupados_usados": "float64",    # Lo que se reparte entre carreras
}

VALIDACION_DESOCUPADOS = {
    "prueba": "object",
    "grupo": "object",
    "valor": "float64",
    "descripcion": "object",
}

TITULOS_PREGRADO = ["Tecnico_Superior", "Profesional"]
