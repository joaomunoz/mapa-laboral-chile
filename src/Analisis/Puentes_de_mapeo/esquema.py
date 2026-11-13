"""
<src/Analisis/Puentes_de_mapeo/esquema.py>

Single Source of Truth de los PUENTES (crosswalk) del proyecto.

Un puente = un activo de datos versionable (CSV + esquema), NO código embebido
en un procesar: así se audita, corrige y regenera sin tocar los ETL de las fuentes.

CATÁLOGO DE PUENTES
-------------------
P1 · PUENTE_ACTIVIDADES  →  Salida/P1_puente_actividades.csv            (21 filas)  ✅ construido
    Grain: 1 fila por código CAENES (1-21) ↔ sección CIIU (A-U). Relación 1:1.
    Representa: el traductor oficial entre la actividad de ENE (r_p_rev4cl_caenes)
    y la sección CIIU (actividad_ciiu) del censo → habilita comparar ambas fuentes por actividad.
    Origen: Libro de códigos ENE 2020, Anexo 5 (mapeca verbatim, no interpretada).

P2 · PUENTE_CARRERA_CASEN  →  Salida/P2_puente_carrera_casen.csv  ✅ construido (02-11-26)
    Grain: 1 fila por (e6a, carrera_normalizada) declarada en CASEN.
    Representa: el texto libre `e7` llevado a `carrera_generica` de SIES, con su método, nivel y
    estado (asignado, generico, posgrado, uniformado, no_valido, sin_asignar). Base para medir
    carrera → ocupación → actividad. Cobertura en Salida/P2_puente_carrera_casen_cobertura.csv.

P3 · CONTROL_NO_ASIGNADOS  →  Salida/P3_control_no_asignados.csv
    Grain: 1 fila por (dimension, categoria).
    Representa: si los ocupados con título y carrera asignada difieren de quienes no la tienen.

P4 · PERFIL_LABORAL_CARRERA  →  Salida/P4_perfil_laboral_carrera.csv  ✅ construido (02-11-26)
    Grain: 1 fila por (carrera_generica, dimension, categoría). Representa: dónde trabajan los
    titulados de cada carrera, según categoría en la ocupación y actividad económica. Medido en CASEN.

TIPOS: "object" textos/llaves normalizadas · "int64" enteros sin nulos (claves)
       "Int64" enteros nullable (agregados con ausencia real) · "float64" porcentajes.
LECTURA: releer con dtype=<diccionario del puente> (pandas infiere al leer CSV).
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# P1 — Actividades: CAENES (ENE, CASEN) ↔ Sección CIIU (censo)  ·  Libro códigos ENE Anexo 5
# --------------------------------------------------------------------------- #
PUENTE_ACTIVIDADES: dict[str, str] = {
    "actividad_caenes": "int64",       # Código CAENES 1-21 (rama de actividad ENE)
    "actividad_ciiu": "object",  # Letra de sección CIIU Rev.4.cl A-U (censo)
    "actividad_glosa": "object",  # Descripción oficial (Anexo 5)
    "origen": "object",      # Provenencia del dato (auditoría)
}

# --------------------------------------------------------------------------- #
# P2 · Texto de carrera en CASEN → carrera_generica de SIES
# --------------------------------------------------------------------------- #
PUENTE_CARRERA_CASEN: dict[str, str] = {
    "e6a": "int64",                     # Nivel declarado: 12 técnico, 13 profesional, 14-15 posgrado
    "carrera_normalizada": "object",    # Texto de CASEN (llave de cruce con casen_procesado)
    "texto_limpio": "object",           # Sin marcas de género ni puntuación final
    "nivel_titulo": "object",         # Catálogo usado: Tecnico o Profesional
    "carrera_generica": "object",       # Genérica SIES; NA si el estado no es asignado
    "area_cine_sies": "object",         # Área CINE más frecuente de esa genérica en SIES
    "metodo": "object",                 # Cómo se asignó (ver METODOS_P5)
    "estado": "object",                 # Resultado (ver ESTADOS_P5)
    "conflicto_nivel": "bool",          # El catálogo usado difiere del nivel declarado en e6a
    "n_personas": "int64",              # Personas de la muestra con ese texto
    "n_ocupados_titulados": "int64",    # De ellas, ocupadas con título completo
}

COBERTURA_CARRERA_CASEN: dict[str, str] = {
    "estado": "object",
    "metodo": "object",
    "n_textos": "int64",
    "n_personas": "int64",
    "pct_personas": "float64",
    "pct_ocupados_titulados_exp": "float64",  # % de ocupados con título, expandido
    "n_comparables": "int64",                 # Personas con área CINE en ambas fuentes
    "pct_acuerdo_cine": "float64",            # % de ellas donde CASEN y SIES coinciden
}

ESTADOS_P5: list[str] = ["asignado", "generico", "posgrado", "uniformado", "no_valido", "sin_asignar"]
METODOS_P5: list[str] = [
    "generica", "carrera_sies", "alias", "regla",
    "generica_segmento", "carrera_sies_segmento", "alias_segmento", "regla_segmento",
    "tipeo", "sin_metodo",
]

# --------------------------------------------------------------------------- #
# P3 · Control de sesgo de la asignación de carrera (CASEN, nacional)
# --------------------------------------------------------------------------- #
CONTROL_NO_ASIGNADOS: dict[str, str] = {
    "dimension": "object",
    "categoria": "object",
    "pct_asignados": "float64",        # Ocupados con título y carrera asignada
    "pct_no_asignados": "float64",     # Ocupados con título sin carrera asignada
    "diferencia": "float64",           # No asignados - asignados, en puntos porcentuales
}


# --------------------------------------------------------------------------- #
# P4 · Perfil laboral de cada carrera (nombres normalizados según glosarios)
# --------------------------------------------------------------------------- #
PERFIL_LABORAL_CARRERA: dict[str, str] = {
    "carrera_generica": "object",
    "nivel_titulo": "object",
    "area_cine_sies": "object",
    "dimension": "object",
    "categoria_ocupacion": "object",       # asalariado_privado, asalariado_publico, independiente u otros
    "actividad_caenes": "Int64",           # Rama de actividad económica 1-21
    "actividad_ciiu": "object",            # Sección CIIU
    "actividad_glosa": "object",
    "n_carrera": "int64",                  # Personas de la carrera con dato en esta dimensión
    "n_celda": "int64",
    "gl": "int64",
    "ocupados_expandidos": "float64",
    "pct_en_carrera": "float64",           # % de la carrera que está en esta categoría
    "pct_en_grupo": "float64",             # % que la carrera representa dentro de esta categoría
    "indice_especializacion": "float64",   # pct_en_carrera / promedio de todos los titulados; 1 = igual
    "error_estandar": "float64",           # De pct_en_carrera
    "cv_pct": "float64",
    "fiabilidad": "object",
    "pct_menores_35": "float64",           # NA si la carrera tiene menos de 60 casos de 22 a 34 años
    "n_menores_35": "int64",
}
DIMENSIONES_P9: list[str] = ["categoria_ocupacion", "actividad_economica", "categoria_actividad"]
