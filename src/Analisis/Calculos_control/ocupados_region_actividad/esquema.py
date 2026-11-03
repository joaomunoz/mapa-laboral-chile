"""
<src/Analisis/Calculos_control/ocupados_region_actividad/esquema.py>

Single Source of Truth de ocupados_region_actividad.csv: todos los ocupados por región y actividad.

Grano: 1 fila por (base_region, codigo_region, actividad_caenes) con casos en la muestra.
base_region: residencia (donde vive) o trabajo (donde está el empleo); el reparto usa trabajo.
peso_relativo = % dla actividad en la región / % dla actividad en el país. Antofagasta tiene cerca de
5 en minería: esa actividad pesa allí 5 veces más que en el país.
"""

OCUPADOS_REGION_ACTIVIDAD = {
    "base_region": "object",        # residencia o trabajo
    "codigo_region": "int64",
    "nombre_region": "object",
    "actividad_caenes": "int64",
    "actividad_ciiu": "object",
    "actividad_glosa": "object",
    "ocupados": "float64",          # Promedio trimestral (10 meses × 3/10)
    "n_personas": "int64",          # idrph únicos
    "gl": "int64",
    "fiable_n_gl": "bool",          # n >= 60 y gl >= 9
    "pct_en_region": "float64",
    "pct_nacional": "float64",
    "peso_relativo": "float64",
}
