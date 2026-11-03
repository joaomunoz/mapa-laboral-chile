"""
<src/Analisis/JOINS/CW_Empleabilidad_Oferta_Titulados/esquema.py>

Single Source de Truth (SSOT) para la salida del Paso 1:
`oferta_empleabilidad_procesado.csv`
Define dtypes, nulos permitidos, reglas y validaciones rigurosas.
"""

import pandas as pd

OFERTA_EMPLEABILIDAD_ESQUEMA = {
    # Llaves y contexto temporal/geográfico
    "anio": "int64",
    "codigo_region": "int64",
    "nombre_region": "object",
    "comuna": "object",
    "codigo_institucion": "int64",
    "institucion": "object",
    "tipo_institucion": "object",
    "carrera": "object",
    "carrera_norm": "object",
    "carrera_generica": "object",
    "cine13_area": "object",
    "cine13_subarea": "object",
    "nivel_carrera": "object",
    "carrera_clasificacion_nivel_1": "object",  # Para aplicar la definición de título que compite
    "tipo_plan": "object",
    # Métricas de titulación
    "total_titulaciones": "int64",
    "titulaciones_mujeres": "int64",
    "titulaciones_hombres": "int64",
    "titulaciones_nb": "int64",
    "titulados_mayores_40": "int64",
    "titulados_menores_40": "int64",
    "edad_promedio": "float64",
    "duracion_semestres": "float64",
    # Empleabilidad adosada desde P2
    "nivel_match": "object",
    "empleabilidad_1er_anio": "float64",
    "empleabilidad_fuente": "object",
    "n_empleabilidad_asociadas": "Int64",
    "anio_ultima_titulacion": "Int64",
}

VALIDACIONES_OFERTA_EMPLEABILIDAD = [
    ("1. Sin nulos en claves principales", lambda df: df[["anio", "codigo_region", "nombre_region", "codigo_institucion", "carrera"]].notna().all().all()),
    ("2. Empleabilidad en rango [0, 100] o nula", lambda df: df["empleabilidad_1er_anio"].dropna().between(0, 100).all()),
    ("3. Coherencia en titulaciones (total = mujeres + hombres + nb)", lambda df: (df["total_titulaciones"] == (df["titulaciones_mujeres"] + df["titulaciones_hombres"] + df["titulaciones_nb"])).all()),
    ("4. Coherencia etaria (total = mayores_40 + menores_40)", lambda df: (df["total_titulaciones"] == (df["titulados_mayores_40"] + df["titulados_menores_40"])).all()),
    ("5. 16 regiones con un nombre por código", lambda df: df["codigo_region"].nunique() == 16 and df.groupby("codigo_region")["nombre_region"].nunique().eq(1).all()),
]
