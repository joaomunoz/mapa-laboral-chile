"""
<src/Scrapers/ENADEL/esquema.py>

Definición del esquema oficial de ENADEL 2025 — Single Source of Truth.

Define las DOS tablas de salida del procesamiento:

  Tabla 1: ESQUEMA_ENADEL_EMPRESAS
    Salida: Salida/enadel_empresas_procesado.csv  (29 columnas)
    Granularidad: 1 fila por empresa (~5,576 filas).
    Contenido: identificación + diseño muestral + región + actividad CIIU
               + dotación + flujos 12m + vacantes (PER).

  Tabla 2: ESQUEMA_ENADEL_CARGOS
    Salida: Salida/enadel_cargos_procesado.csv  (17 columnas)
    Granularidad: 1 fila por empresa × origen_bloque × cargo (formato largo).
    Contenido: bloque CIUO despivotado (vacantes históricas, vacantes 2025,
               cargo clave, capacitación, tecnológico) ← materia prima del crosswalk.

Integridad referencial:
    PK de empresas: idempresa_ficticio
    FK de cargos:   idempresa_ficticio → ESQUEMA_ENADEL_EMPRESAS.idempresa_ficticio

Tipos:
    "object" : textos y códigos como string (CIUO 4 dígitos, CIIU, etiquetas)
    "int64"  : enteros sin nulos (PK, códigos de región)
    "Int64"  : enteros anulables de pandas (miden cantidades con -88 → NA)
    "float64": decimales (pesos muestrales y tasas derivadas)
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Tabla 1 — Empresas (granularidad establecimiento)
# --------------------------------------------------------------------------- #
ESQUEMA_ENADEL_EMPRESAS = {
    # Identificación y diseño muestral
    "idempresa_ficticio": "int64",    # PK — ID anónimo de empresa
    "varunit": "int64",               # Unidad de varianza (diseño muestral)
    "varstrat": "int64",              # Estrato (diseño muestral)
    "pond_final": "float64",          # Factor de expansión final
    "fpc": "float64",                 # Corrección de población finita
    # Regionalización (clave de cruce con Titulados/Empleabilidad)
    "codigo_region": "int64",         # Código región 1–16 (`reg_encuesta` del crudo)
    "nombre_region": "object",        # Nombre canónico de comun.normalizador.REGIONES
    # Actividad económica — CIIU4.CL 2012
    "ciiu_seccion": "object",         # Letra (A–S)
    "ciiu_seccion_glosa": "object",
    "ciiu_division": "object",        # 2 dígitos con cero a la izquierda
    "ciiu_division_glosa": "object",
    "ciiu_clase": "object",           # 4 dígitos
    "ciiu_clase_glosa": "object",
    # Dotación al 31-may-2025 (solo totales)
    "dotacion_total": "Int64",        # b6_1 (suma de contratos)
    "dotacion_indefinido": "Int64",   # b1_1
    "dotacion_plazo_fijo": "Int64",   # b2_1 (plazo fijo / obra y faena)
    "dotacion_aprendizaje": "Int64",  # b3_1
    "dotacion_honorarios": "Int64",   # b4_1
    "dotacion_de_palabra": "Int64",   # b5_1
    # Flujos jun-2024 → may-2025
    "renuncias_12m": "Int64",             # b7_1
    "despidos_ceses_12m": "Int64",        # b8_1
    "contrataciones_12m": "Int64",        # b9_1 (validación demanda real)
    "vacantes_no_llenadas_12m": "Int64",  # b10_1
    # Vacantes — numerador del PER
    "vacantes_actuales": "Int64",         # b11_1 (may-2025)
    "vacantes_futuras_2025": "Int64",     # b12_1
    "vacantes_futuras_2026": "Int64",     # b13_1
    "vacantes_proyectadas": "Int64",      # b11_1 + b12_1
    # Derivadas
    "tasa_rotacion": "float64",           # (renuncias + despidos) / dotacion_total
    "tasa_vacantes": "float64",           # vacantes_proyectadas / dotacion_total
}

# --------------------------------------------------------------------------- #
# Tabla 2 — Cargos/ocupaciones en formato largo (materia prima del crosswalk)
# --------------------------------------------------------------------------- #
ESQUEMA_ENADEL_CARGOS = {
    # Claves
    "idempresa_ficticio": "int64",    # FK → ESQUEMA_ENADEL_EMPRESAS
    # Contexto regional y sectorial (heredado de la empresa)
    "codigo_region": "int64",
    "nombre_region": "object",
    "ciiu_division": "object",
    "ciiu_division_glosa": "object",
    "pond_final": "float64",          # Peso muestral (expansión de la demanda)
    # Estructura del despivote
    "origen_bloque": "object",        # vacante_historica | vacante_2025 |
                                      # cargo_clave | cargo_capacitacion |
                                      # cargo_tecnologico
    "posicion": "Int64",              # Índice n dentro del bloque (1..7 / 1..3)
    # Clasificación ocupacional — CIUO-08
    "ciuo_08": "object",              # Código 4 dígitos como string ("2141")
    "ciuo_nivel_2": "object",         # Subgrupo 2 dígitos (fallback crosswalk)
    "ciuo_nivel_1": "object",         # Gran grupo 1 dígito (fallback profundo)
    "ciuo_glosa": "object",           # Etiqueta oficial del CIUO
    "puesto_estandarizado": "object",  # Nombre estándar del puesto
    # Requisitos del cargo
    "nivel_educacional": "object",    # Etiqueta alineada a niveles SIES
    "experiencia_anios": "Int64",     # Años de experiencia requeridos
    # Resultado de la contratación (solo bloque vacante_historica / c1)
    "logro_contratar": "Int64",       # 1=Sí, 2=No (nullable)
    "cantidad_contratada": "Int64",   # Vacantes efectivamente cubiertas
}

# --------------------------------------------------------------------------- #
# Mapeo de tablas → archivo de salida
# --------------------------------------------------------------------------- #
TABLAS_ENADEL = {
    "empresas": {
        "esquema": ESQUEMA_ENADEL_EMPRESAS,
        "archivo_salida": "enadel_empresas_procesado.csv",
        "granularidad": "1 fila por empresa",
    },
    "cargos": {
        "esquema": ESQUEMA_ENADEL_CARGOS,
        "archivo_salida": "enadel_cargos_procesado.csv",
        "granularidad": "1 fila por empresa × bloque × cargo",
    },
}
