"""
<src/Analisis/JOINS/Indice_Cupos/esquema.py>

Single Source of Truth del Paso 5: índice por carrera, región y a nivel nacional.

indice_cupos_carrera_region.csv: 1 fila por (codigo_region, carrera_generica).
indice_cupos_carrera_nacional.csv: 1 fila por carrera_generica. Es la lectura más sólida.
índice = empleabilidad × (jubilaciones + vacantes privadas + públicas) / (titulados 2025 + desocupados), en %.
Es un índice comparativo: no es una probabilidad y puede superar 100.
"""

INDICE_CARRERA_REGION = {
    "codigo_region": "int64",
    "nombre_region": "object",
    "nivel_titulo": "object",
    "carrera_generica": "object",
    "area_cine_sies": "object",
    "empleabilidad_pct": "float64",
    "origen_empleabilidad": "object",     # medida o heredada_area_nivel
    "jubilaciones_anuales": "float64",
    "vacantes_proyectadas": "float64",
    "vacantes_publicas": "float64",       # Estimadas: ENADEL no ve el sector público
    "titulados_2025": "int64",
    "desocupados": "float64",
    "cupos_por_100": "float64",           # (J + V + Vpub) / (T + D) × 100, sin empleabilidad
    "indice_cupos": "float64",                 # Valor principal, con vacantes públicas (decisión 02-11-26)
    "indice_solo_privado": "float64",        # Solo vacantes de empresas privadas (ENADEL)
    "indice_sin_doble_conteo": "float64",    # Sensibilidad: solo jubilaciones fuera del empleo privado
    "indice_vacantes_menciones": "float64",  # Sensibilidad: parte con título según cargos 2025
    "indice_edad_legal": "float64",          # Sensibilidad: quienes llegan a la edad legal
    "indice_titulados_3_anios": "float64",   # Sensibilidad: promedio de titulados 2023-2025
    "indice_publico_sin_jubilacion": "float64",  # Solo vacantes privadas y públicas: evita doble conteo
    "pct_asalariado_privado": "float64",  # Alerta: bajo = ENADEL ve poco de la carrera
    "nivel_confianza_perfil": "object",   # P7
    "fiabilidad_desocupados": "object",   # Paso 2
    "confianza_indice": "object",            # alta, media o baja
    "alerta_empleo_publico": "bool",      # Menos de 50% de empleo privado: la demanda es en parte estimada
    "supera_100": "bool",
}

INDICE_CARRERA_NACIONAL = {
    "nivel_titulo": "object",
    "carrera_generica": "object",
    "area_cine_sies": "object",
    "empleabilidad_pct": "float64",
    "origen_empleabilidad": "object",
    "jubilaciones_anuales": "float64",
    "vacantes_proyectadas": "float64",
    "vacantes_publicas": "float64",       # Estimadas: ENADEL no ve el sector público
    "titulados_2025": "int64",
    "desocupados": "float64",
    "cupos_por_100": "float64",
    "indice_cupos": "float64",
    "indice_solo_privado": "float64",
    "indice_sin_doble_conteo": "float64",
    "indice_vacantes_menciones": "float64",
    "indice_edad_legal": "float64",
    "indice_titulados_3_anios": "float64",
    "indice_publico_sin_jubilacion": "float64",
    "pct_asalariado_privado": "float64",
    "nivel_confianza_perfil": "object",
    "confianza_indice": "object",
    "ocupados_por_10": "float64",         # P8: indicador junto al índice, no dentro de la fórmula
    "desocupados_por_10": "float64",
    "inactivos_por_10": "float64",
    "fiabilidad_razon_empleo": "object",
    "alerta_empleo_publico": "bool",      # Menos de 50% de empleo privado: la demanda es en parte estimada
    "supera_100": "bool",
}

VALIDACION_INDICE = {
    "prueba": "object",
    "grupo": "object",
    "valor": "float64",
    "descripcion": "object",
}
