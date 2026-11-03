"""
<src/Analisis/Puentes_de_mapeo/esquema.py>
Actualizado 02-11-26 17:28

Single Source of Truth de los PUENTES (crosswalk) del proyecto.

Un puente = un activo de datos versionable (CSV + esquema), NO código embebido
en un procesar: así se audita, corrige y regenera sin tocar los ETL de las fuentes.

CATÁLOGO DE PUENTES
-------------------
P1 · PUENTE_ACTIVIDADES  →  Salida/P1_puente_actividades.csv            (21 filas)  ✅ construido
    Grain: 1 fila por código CAENES (1-21) ↔ sección CIIU (A-U). Relación 1:1.
    Representa: el traductor oficial entre la actividad de ENE (r_p_rev4cl_caenes)
    y la actividad de ENADEL (actividad_ciiu) → habilita el cruce ENE ⋈ ENADEL por actividad.
    Origen: Libro de códigos ENE 2020, Anexo 5 (mapeca verbatim, no interpretada).

P2 · PUENTE_LLAVES_CARRERA  →  Salida/P2_puente_llaves_carrera.csv  (8,623 filas)  ✅ construido
    Grain: 1 fila por llave única (id_institucion, carrera_norm) del unión
    Titulados ∪ Empleabilidad.
    Representa: la relación directa Titulados ⋈ Empleabilidad resuelta en 3 niveles
    de fallback y con trazabilidad de cobertura en AMBAS direcciones:
      nivel_match:  exacto   → existe fila MiFuturo con esa institución+carrera
                    generica → media de las carreras MiFuturo de esa institución
                               con la misma carrera_generica
                    nacional → media nacional de esa carrera_generica
                    ninguno  → la carrera no tiene dato de empleabilidad
    Caché del índice: aporta EMPLEABILIDAD_A1 (columna base de la fórmula) anclada
    a la oferta de titulados, más el potencial de recambio (mayores_40).

P3 · RETIRADO (02-11-26)
    Lista candidata carrera ↔ ocupación que no pasó la validación; la reemplazaron P6 y P7.
    El número no se reutiliza para mantener las referencias del historial.

P4 · PUENTE_NIVELES_EDUCATIVOS  →  Salida/P4_puente_niveles_educativos.csv  (15 filas)  ✅ v2 (01-11-26)
    Grain: 1 fila por nivel educativo oficial ENE (0 a 14) ↔ CINE 2011 ↔ SIES Titulados ↔ ENADEL.
    Representa: el estándar de homologación de nivel de formación entre oferta (Titulados),
    demanda empresarial (vacantes ENADEL) y población desocupada/fuerza de trabajo (ENE).
    Llave común = `titulo_comun` (TIPO DE TÍTULO), no tipo de institución: auditoría ENE
    01-11-26 mostró que `nivel` 7/8 = técnico (1-2 / 3 años aprobados) y 9 = profesional de
    cualquier institución; las glosas "CFT"/"IP"/"Universitario" son legado del INE.
    v1 → v2: `nivel_agrupado` (con el ambiguo Tecnico_o_Profesional) → `titulo_comun`;
    `sies_nivel_carrera` (nivel 2) → `sies_clasificacion_nivel_1` (nivel 1, que separa
    diplomados y licenciaturas no conducentes); se agrega `enadel_codigo` (0-7).

TIPOS: "object" textos/llaves normalizadas · "int64" enteros sin nulos (claves)
       "Int64" enteros nullable (agregados con ausencia real) · "float64" porcentajes.
LECTURA: releer con dtype=<diccionario del puente> (pandas infiere al leer CSV).
P5 · PUENTE_CARRERA_CASEN  →  Salida/P5_puente_carrera_casen.csv  ✅ construido (02-11-26)
    Grain: 1 fila por (e6a, carrera_normalizada) declarada en CASEN.
    Representa: el texto libre `e7` llevado a `carrera_generica` de SIES, con su método, nivel y
    estado (asignado, generico, posgrado, uniformado, no_valido, sin_asignar). Base para medir
    carrera → ocupación → actividad. Cobertura en Salida/P5_puente_carrera_casen_cobertura.csv.

P6 · MATRIZ_CARRERA_ACTIVIDAD_OCUPACION  →  Salida/P6_matriz_carrera_actividad_ocupacion.csv  ✅ construido (02-11-26)
    Grain: 1 fila por (carrera_generica, dimension, actividad_caenes, grupo_ocupacion), con celdas observadas.
    Representa: dónde trabajan los titulados de cada carrera a nivel nacional (CASEN 2024), con
    error estándar según el diseño muestral y fiabilidad INE. Sin región: esa mezcla se combina
    después con los totales regionales de ENE.

P7 · PERFIL_CARRERA_ACTIVIDAD_OCUPACION  →  Salida/P7_perfil_carrera_actividad_ocupacion.csv  ✅ construido (02-11-26)
    Grain: 1 fila por (carrera_generica, dimension, categoría). Reemplaza a P3 en el índice.
    Representa: el perfil que usa cada carrera de pregrado, propio o heredado, con su nivel de
    confianza (A_propia, B_area_nivel, C_nivel) y el perfil de menores de 35 como sensibilidad.

P8 · RAZON_EMPLEO_CARRERA  →  Salida/P8_razon_empleo_carrera.csv  ✅ construido (02-11-26)
    Grain: 1 fila por carrera_generica. Representa: por cada 10 titulados de 22 a 54 años, cuántos
    están ocupados, desocupados e inactivos. Indicador junto al índice, no dentro de la fórmula.

P9 · PERFIL_LABORAL_CARRERA  →  Salida/P9_perfil_laboral_carrera.csv  ✅ construido (02-11-26)
    Grain: 1 fila por (carrera_generica, dimension, categoría). Representa: dónde trabajan los
    titulados de cada carrera, según categoría en la ocupación y actividad económica. Medido en CASEN.

"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# P1 — Actividades: CAENES (ENE) ↔ Sección CIIU (ENADEL)  ·  Libro códigos ENE Anexo 5
# --------------------------------------------------------------------------- #
PUENTE_ACTIVIDADES: dict[str, str] = {
    "actividad_caenes": "int64",       # Código CAENES 1-21 (rama de actividad ENE)
    "actividad_ciiu": "object",  # Letra de sección CIIU Rev.4.cl A-U (ENADEL)
    "actividad_glosa": "object",  # Descripción oficial (Anexo 5)
    "origen": "object",      # Provenencia del dato (auditoría)
}

# --------------------------------------------------------------------------- #
# P2 — Llaves de carrera: Titulados ⋈ Empleabilidad con fallback de 3 niveles
# --------------------------------------------------------------------------- #
PUENTE_LLAVES_CARRERA: dict[str, str] = {
    # --- Llave y contexto de la carrera ---
    "id_institucion": "int64",          # Código SIES/MiFuturo (105 códigos cruzan 1:1)
    "institucion": "object",            # Nombre canónico (lado disponible)
    "tipo_institucion": "object",       # Universidad / IP / CFT / etc.
    "carrera": "object",                # Nombre original (lado disponible)
    "carrera_norm": "object",           # LLAVE normalizada (sin tildes/mayúsculas)
    "carrera_generica": "object",       # Genérica (lado Titulados si existe, si no MiFuturo)
    "cine13_area": "object",            # CINE 2013 área (solo lado Titulados; NA si no)
    "cine13_subarea": "object",         # CINE 2013 subárea
    "nivel_carrera": "object",          # Profesional / Técnico / etc.

    # --- Resultado del cruce (lo que "representa" la fila) ---
    "origen": "object",                 # ambos | solo_titulados | solo_empleabilidad
    "nivel_match": "object",            # exacto | generica | nacional | ninguno (ver catálogos abajo)
    "empleabilidad_1er_anio": "float64",  # EMPLEABILIDAD_A1 del índice (% 0-100) resuelta al nivel del match; NA si ninguno
    "empleabilidad_fuente": "object",   # exacto | media_institucion_generica | media_nacional | sin_dato
    "n_empleabilidad_asociadas": "Int64",  # Filas MiFuturo que respaldan el valor (1 si exacto)

    # --- Oferta de titulados (lado Titulados; 0 = sin titulaciones 2007-2025) ---
    "titulaciones_total": "Int64",      # Suma histórica de titulaciones 2007-2025 de la llave
    "titulaciones_ult_anio": "Int64",   # Titulaciones del último año del dataset (2025)
    "titulados_mayores_40": "Int64",    # Potencial de recambio/jubilación (numerador índice)
    "n_regiones_titulados": "Int64",    # Regiones donde hay titulados de esta llave
    "anio_ultima_titulacion": "Int64",  # Año más reciente con titulados (NA si nunca)
}

# Catálogos de validación (dominios) de P2
ORIGEN_LLAVES: list[str] = ["ambos", "solo_titulados", "solo_empleabilidad"]
NIVELES_MATCH: list[str] = ["exacto", "generica", "nacional", "ninguno"]
FUENTES_EMPLEABILIDAD: list[str] = [
    "exacto", "media_institucion_generica", "media_nacional", "sin_dato",
]

# --------------------------------------------------------------------------- #
# P4 — Niveles Educativos: SIES (Titulados) ↔ ENE (INE) ↔ ENADEL (SENCE)
# --------------------------------------------------------------------------- #
PUENTE_NIVELES_EDUCATIVOS: dict[str, str] = {
    "ene_nivel": "int64",               # Código nivel ENE (0 a 14)
    "glosa_ene_nivel": "object",        # Glosa oficial ENE (legado: CFT/IP/Univ NO son institución)
    "significado_ene": "object",        # Contenido real verificado en microdatos (edu2 × curso)
    "cine11_1d": "Int64",               # CINE 2011 (escala INE 0-6) cuando el nivel está COMPLETO
    "titulo_comun": "object",           # LLAVE COMÚN del índice (ver TITULOS_COMUNES)
    "sies_clasificacion_nivel_1": "object",  # Categorías SIES `carrera_clasificacion_nivel_1` (sep. " | ")
    "enadel_codigo": "Int64",           # Código ENADEL c1_c/c3_c (0-7)
    "enadel_nivel_educacional": "object",  # Texto ENADEL tal como aparece en enadel_cargos_procesado
    "origen": "object",                 # Procedencia
}

# Catálogo de la llave común. "No_superior" agrupa 0-6, 13 y 14: el índice solo cruza
# educación superior, pero se conserva el mapeo ENADEL de esas filas para el Paso 4.
TITULOS_COMUNES: list[str] = [
    "No_superior", "Tecnico_Superior", "Profesional", "Postitulo", "Magister", "Doctorado",
]

# Categorías SIES que P4 deja FUERA a propósito (definición "título que compite", 01-11-26):
# grado intermedio, no es un título con el que se compite en el mercado laboral.
SIES_EXCLUIDAS_P4: list[str] = ["Licenciatura No Conducente a Título"]

# --------------------------------------------------------------------------- #
# Validaciones por puente
# --------------------------------------------------------------------------- #
VALIDACIONES: dict[str, list[str]] = {
    "P1_puente_actividades": [
        "1. 21 filas; actividad_caenes ∈ 1..21 sin duplicados; actividad_ciiu ∈ A..U sin duplicados (1:1)",
        "2. Sin nulos en ninguna columna",
    ],
    "P2_puente_llaves_carrera": [
        "1. PK (id_institucion, carrera_norm) única → 0 duplicados",
        "2. origen ∈ catálogo ORIGEN_LLAVES; nivel_match ∈ NIVELES_MATCH",
        "3. empleabilidad_1er_anio ∈ [0,100]; NA ⇔ empleabilidad_fuente = sin_dato",
        "4. nivel_match exacto ⇒ empleabilidad_fuente = exacto y n_empleabilidad_asociadas = 1",
        "5. titulaciones_total ≥ titulados_mayores_40; orig=solo_empleabilidad ⇒ titulaciones_total=0",
        "6. Cobertura bidireccional reportada: % filas Empleabilidad resueltas y",
        "    % de titulados (volumen) con empleabilidad resuelta",
    ],
    "P4_puente_niveles_educativos": [
        "1. 15 filas (códigos ENE 0 a 14 únicos)",
        "2. Sin nulos en ene_nivel y titulo_comun; titulo_comun ∈ TITULOS_COMUNES",
        "3. Categorías SIES citadas existen en titulados_procesado y, junto a",
        "   SIES_EXCLUIDAS_P4, cubren el 100% de carrera_clasificacion_nivel_1",
        "4. enadel_nivel_educacional ⊂ valores de enadel_cargos_procesado",
        "5. Cada titulo_comun superior tiene exactamente un enadel_codigo",
    ],
}

# --------------------------------------------------------------------------- #
# P5 · Texto de carrera en CASEN → carrera_generica de SIES
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
# P6 · Matriz carrera → actividad y ocupación (CASEN, nacional)
# --------------------------------------------------------------------------- #
MATRIZ_CARRERA_ACTIVIDAD_OCUPACION: dict[str, str] = {
    "carrera_generica": "object",
    "nivel_titulo": "object",        # Tecnico o Profesional (catálogo de P5)
    "area_cine_sies": "object",
    "dimension": "object",             # actividad_economica, grupo_ocupacion u ocupacion_actividad
    "actividad_caenes": "Int64",                 # CAENES 1-21; NA en dimension = grupo_ocupacion
    "actividad_ciiu": "object",          # Sección CIIU (P1), para cruzar con ENADEL
    "actividad_glosa": "object",
    "grupo_ocupacion": "Int64",        # CIUO-08 con numeración ENE (10 = FF.AA.); NA en dimension = actividad_economica
    "glosa_ocupacion": "object",
    "n_carrera": "int64",              # Personas de la carrera con dato en esta dimensión
    "n_celda": "int64",                # Personas de la celda
    "gl": "int64",                     # Conglomerados - estratos de la carrera
    "expandido_celda": "float64",
    "expandido_carrera": "float64",
    "pct": "float64",                  # % dentro de la carrera
    "error_estandar": "float64",       # En puntos porcentuales
    "cv_pct": "float64",               # Coeficiente de variación de pct
    "fiabilidad": "object",            # fiable, poco_fiable o no_fiable (estándar INE)
}

CONTROL_NO_ASIGNADOS: dict[str, str] = {
    "dimension": "object",
    "categoria": "object",
    "pct_asignados": "float64",        # Ocupados con título y carrera asignada
    "pct_no_asignados": "float64",     # Ocupados con título sin carrera asignada
    "diferencia": "float64",           # No asignados - asignados, en puntos porcentuales
}

DIMENSIONES_P6: list[str] = ["actividad_economica", "grupo_ocupacion", "ocupacion_actividad"]
FIABILIDADES_P6: list[str] = ["fiable", "poco_fiable", "no_fiable"]

# --------------------------------------------------------------------------- #
# P7 · Perfil que usa el índice para cada carrera
# --------------------------------------------------------------------------- #
PERFIL_CARRERA_ACTIVIDAD_OCUPACION: dict[str, str] = {
    "carrera_generica": "object",
    "nivel_titulo": "object",       # Tecnico o Profesional
    "area_cine_sies": "object",
    "dimension": "object",            # actividad_economica o grupo_ocupacion
    "actividad_caenes": "Int64",                # NA en dimension = grupo_ocupacion
    "grupo_ocupacion": "Int64",       # Numeración ENE; NA en dimension = actividad_economica
    "pct": "float64",                 # % del perfil usado
    "nivel_confianza": "object",      # Ver NIVELES_CONFIANZA_P7
    "n_perfil": "int64",              # Personas del grupo del que sale el perfil
    "gl_perfil": "int64",
    "pct_menores_35": "float64",      # Sensibilidad; solo carreras A_propia
    "n_menores_35": "Int64",
}
NIVELES_CONFIANZA_P7: list[str] = ["A_propia", "B_area_nivel", "C_nivel"]

# --------------------------------------------------------------------------- #
# P8 · Razón de empleo por carrera
# --------------------------------------------------------------------------- #
RAZON_EMPLEO_CARRERA: dict[str, str] = {
    "carrera_generica": "object",
    "nivel_titulo": "object",
    "n_titulados": "int64",
    "n_activos": "int64",
    "n_desocupados": "int64",
    "gl": "int64",
    "ocupados_por_10": "float64",
    "desocupados_por_10": "float64",
    "inactivos_por_10": "float64",
    "tasa_desempleo_pct": "float64",   # Desocupados / activos
    "error_estandar": "float64",
    "cv_pct": "float64",
    "fiabilidad": "object",
}

# --------------------------------------------------------------------------- #
# P9 · Perfil laboral de cada carrera (nombres normalizados según glosarios)
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
