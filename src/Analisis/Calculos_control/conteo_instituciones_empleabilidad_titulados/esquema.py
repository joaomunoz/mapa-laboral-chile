"""
<src/Analisis/Calculos_control/conteo_instituciones_empleabilidad_titulados/esquema.py>
Actualizado 02-11-26 18:01

Single Source of Truth de conteo_instituciones_empleabilidad_titulados.csv.

Grano: 1 fila por carrera_generica de Empleabilidad (190). Cuenta instituciones, porque una fila de
MiFuturo es institución + carrera genérica, y en Titulados la misma combinación se repite por año,
sede y programa. Titulados usa solo pregrado que compite, salvo la columna indicada.
"""

CONTEO_INSTITUCIONES = {
    "carrera_generica": "object",
    "instituciones_empleabilidad": "int64",        # Filas de MiFuturo
    "instituciones_titulados_2021_2023": "int64",  # Mismas cohortes que la empleabilidad al 1er año
    "instituciones_titulados_todos": "int64",      # 2007-2025
    "instituciones_todas_clases_2021_2023": "int64",  # Incluye licenciaturas y otras clasificaciones
    "filas_titulados": "int64",                    # Solo informativo: no es comparable con MiFuturo
    "diferencia_2021_2023": "int64",               # Titulados 2021-2023 - Empleabilidad
    "solo_en_titulados": "int64",                  # Instituciones con títulos 2021-2023 sin fila en MiFuturo
    "solo_en_empleabilidad": "int64",              # Filas de MiFuturo sin títulos que compiten en 2021-2023
    "titulos_2021_2023": "int64",
    "pct_titulos_en_empleabilidad": "float64",     # % de esos títulos en instituciones publicadas por MiFuturo
}
