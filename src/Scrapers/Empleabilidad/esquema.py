"""
<src/Scrapers/Empleabilidad/esquema.py>

Definición del esquema oficial para la tabla procesada de Empleabilidad (MiFuturo).
Empleabilidad como float (porcentaje, ej. 88.4), ingresos y percentiles como enteros (int64).
"""

from __future__ import annotations

# Diccionario de tipos de datos oficiales por columna
ESQUEMA_EMPLEABILIDAD = {
    "id_institucion": "int64",
    "institucion": "object",
    "tipo_institucion": "object",
    "carrera": "object",
    "carrera_generica": "object",
    "regiones_sede": "object",
    "empleabilidad_1er_anio": "float64",
    "empleabilidad_2do_anio": "float64",
    "ingreso_medio_1er_anio": "Int64",  # Int64 nullable de pandas para tolerar nulos
    "ingreso_medio_2do_anio": "Int64",
    "ingreso_medio_3er_anio": "Int64",
    "ingreso_medio_4to_anio": "Int64",
    "ingreso_medio_5to_anio": "Int64",
    "percentil_10_anio_1": "Int64",
    "percentil_25_anio_1": "Int64",
    "percentil_50_anio_1": "Int64",
    "percentil_75_anio_1": "Int64",
    "percentil_90_anio_1": "Int64",
    "percentil_10_anio_5": "Int64",
    "percentil_25_anio_5": "Int64",
    "percentil_50_anio_5": "Int64",
    "percentil_75_anio_5": "Int64",
    "percentil_90_anio_5": "Int64",
}
