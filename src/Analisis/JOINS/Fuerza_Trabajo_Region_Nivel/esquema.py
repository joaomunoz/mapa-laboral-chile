"""
<src/Analisis/JOINS/Fuerza_Trabajo_Region_Nivel/esquema.py>

Single Source of Truth de fuerza_trabajo_region_nivel.csv: situación laboral por región y nivel educativo.

Grano: 1 fila por (codigo_region, nivel_titulo). Son 48 filas: 16 regiones × 3 niveles.
Región: donde VIVE, salvo ocupados_trabajo. Los desocupados no tienen lugar de trabajo.
La tasa usa ocupados_residencia, para que numerador y denominador tengan la misma base.
No se abre por actividad ni carrera: un desocupado no tiene actividad registrada, y el censo no trae carrera.
"""

FUERZA_TRABAJO_REGION_NIVEL = {
    "codigo_region": "int64",
    "nombre_region": "object",
    "nivel_titulo": "object",            # Profesional, Tecnico o Sin_titulo
    "ocupados_residencia": "int64",      # Censo 2024
    "ocupados_trabajo": "int64",
    "desocupados": "int64",
    "fuera_fuerza_trabajo": "int64",
    "tasa_desocupacion": "float64",
    "tasa_nacional_nivel": "float64",
    "ene_tasa_desocupacion": "float64",  # ENE 2025-2026; contraste
    "ene_fiabilidad": "object",          # fiable, poco_fiable o no_fiable; medida sobre los desocupados
}
