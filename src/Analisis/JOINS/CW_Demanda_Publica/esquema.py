"""
<src/Analisis/JOINS/CW_Demanda_Publica/esquema.py>
Actualizado 02-11-26 16:40

Single Source of Truth de la demanda pública estimada: la parte que ENADEL no ve.

vacantes_publicas_carrera_region.csv: 1 fila por (codigo_region, carrera_generica).
vacantes_publicas_validacion.csv: tasas, razón de calibración y sus márgenes.
Son ESTIMACIONES: ninguna fuente publica vacantes del sector público.
"""

VACANTES_PUBLICAS_CARRERA_REGION = {
    "codigo_region": "int64",
    "nombre_region": "object",
    "nivel_titulo": "object",
    "carrera_generica": "object",
    "vacantes_publicas": "float64",
}

VALIDACION_PUBLICA = {
    "prueba": "object",
    "grupo": "object",
    "valor": "float64",
    "descripcion": "object",
}
