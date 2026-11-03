"""
<src/Analisis/Archivo/CW_Demanda_Empresarial/esquema.py>

Single Source of Truth del Paso 4 del índice: vacantes proyectadas para titulados.

vacantes_carrera_region.csv: 1 fila por (codigo_region, carrera_generica); es la que entra al índice.
vacantes_carrera_region_actividad.csv: el mismo dato abierto por actividad.
vacantes_region_actividad.csv: vacantes de ENADEL por región y actividad, con su calidad.
Son ESTIMACIONES sintéticas: ENADEL no pregunta qué carrera se busca.
"""

VACANTES_CARRERA_REGION = {
    "codigo_region": "int64",
    "nombre_region": "object",
    "nivel_titulo": "object",
    "carrera_generica": "object",
    "nivel_confianza": "object",            # Origen del perfil (P7)
    "pct_asalariado_privado": "float64",    # % de la carrera en empleo privado; NA si n < 60 en CASEN
    "vacantes_estimadas": "float64",        # Valor base
    "vacantes_sin_winsorizar": "float64",   # Sensibilidad: sin tope a empresas influyentes
    "vacantes_con_menciones": "float64",    # Sensibilidad: nivel exigido según cargos de 2025 (c3)
}

VACANTES_CARRERA_REGION_ACTIVIDAD = {
    "codigo_region": "int64",
    "nombre_region": "object",
    "nivel_titulo": "object",
    "carrera_generica": "object",
    "actividad_ciiu": "object",
    "vacantes_estimadas": "float64",
}

VACANTES_REGION_ACTIVIDAD = {
    "codigo_region": "int64",
    "nombre_region": "object",
    "actividad_ciiu": "object",
    "n_empresas": "int64",
    "vacantes_sin_winsorizar": "float64",
    "vacantes_directo": "float64",     # Con tope a empresas influyentes
    "pct_empresa_mayor": "float64",
    "cv_pct": "float64",
    "celda_fiable": "bool",
    "origen_celda": "object",          # celda_propia o mezcla_nacional_ponderada
    "vacantes_usadas": "float64",
}

VALIDACION_VACANTES = {
    "prueba": "object",
    "grupo": "object",
    "valor": "float64",
    "descripcion": "object",
}
