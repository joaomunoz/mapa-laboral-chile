"""
<src/Analisis/JOINS/Carreras_Por_Actividad/esquema.py>

Single Source of Truth de carreras_por_actividad.csv: qué carreras se vinculan a cada actividad económica.

Grano: 1 fila por (carrera_generica, actividad_caenes) con casos en CASEN, a nivel nacional.
afinidad:
  afin: pct_en_carrera >= 10, indice_especializacion >= 2 y fiabilidad aceptable.
  indicio_sin_muestra: cumple ambos umbrales con muestra insuficiente, pero con al menos 10 casos. No es un dato firme.
  indicio_debil: cumple ambos umbrales con menos de 10 casos. Se conserva, pero no se muestra.
  no_afin: no cumple los umbrales.
Los datos de MiFuturo y Titulados son de la carrera y se repiten en todas sus filas.
"""

CARRERAS_POR_ACTIVIDAD = {
    "actividad_caenes": "int64",
    "actividad_ciiu": "object",
    "actividad_glosa": "object",
    "carrera_generica": "object",
    "nivel_titulo": "object",
    "area_cine": "object",
    "pct_en_carrera": "float64",
    "pct_en_carrera_min": "float64",      # Rango 95%
    "pct_en_carrera_max": "float64",
    "ocupados_titulados": "float64",      # Titulados de la carrera en la actividad, a nivel nacional
    "indice_especializacion": "float64",
    "n_carrera": "int64",
    "n_celda": "int64",
    "cv_pct": "float64",
    "fiabilidad": "object",               # fiable, poco_fiable o no_fiable
    "afinidad": "object",                 # afin, indicio_sin_muestra, indicio_debil o no_afin
    "titulados_2025": "int64",            # Títulos de pregrado terminal entregados en 2025
    "empleabilidad_1er_anio": "float64",
    "ingreso_medio_1er_anio": "float64",  # Vacío si MiFuturo no lo informa
    "ingreso_medio_5to_anio": "float64",
    "n_instituciones": "int64",           # Instituciones que respaldan el dato de MiFuturo
    "pct_institucion_principal": "float64",  # % de títulos 2021-2023 de la institución más grande; vacío sin títulos
    "alerta_pocas_instituciones": "bool",    # 1 o 2 instituciones: el dato describe más a ellas que a la carrera
}
