"""
<src/Scrapers/ENE/esquema.py>

Definición del esquema oficial de ENE 2026 — Single Source of Truth.

Define la ÚNICA tabla de salida del procesamiento:

  ESQUEMA_ENE
    Salida: Salida/ene_procesado.csv  (30 columnas)
    Granularidad: 1 fila por ENTREVISTA única = (idrph, ano_encuesta, mes_encuesta).
    Contenido: microdatos (NO agregados) de las 8 bases mensuales 2026 unificadas,
               con clave de período `mes` para análisis por mes/region.

CONTEXTO METODOLÓGICO (clave para no malinterpretar la tabla):
  * Los 8 archivos CSV de Entrada/2026/ son TRIMESTRES MÓVILES SOLAPADOS:
    el archivo "ene-2026-K-*.csv" contiene los meses {K-1, K, K+1}
    (K=1 = trimestre dic/ene/feb, por lo que contiene el mes 12 de 2025).
  * Misma entrevista aparece en hasta 3 archivos con CONTENIDO IDÉNTICO
    pero con `fact_cal` recalibrado distinto (verificado: 100% igualdad en
    edad/sexo/región/nivel/cae/b1; 0% igualdad en fact_cal).
  * Crudo = 782,303 filas → tras deduplicar = 324,054 entrevistas únicas.
  * NUNCA sumar meses en bruto: duplicaría hasta 3 veces cada entrevista.

DEDUPLICACIÓN (implementada en procesar.py):
  Clave: (idrph, ano_encuesta, mes_encuesta)
  Política del peso = "CENTRAL": de entre los archivos que contienen una
  entrevista, conservar `fact_cal` del archivo cuyo mes_central coincide con
  mes_encuesta (o el primero disponible en los extremos: dic-2025 solo está en
  archivo 1, sep-2026 solo en el 8).
  Validación empírica vs "verdad" (archivo del propio trimestre):
    central : desviación regional máxima ≤ 1.75%, promedio 0.64%, 0–3/16 regiones >1%
    first   : ≤ 4.02%, promedio 1.06%, hasta 9/16 regiones >1%
    last    : ≤ 4.34%, promedio 1.13%, hasta 8/16 regiones >1%

PANEL Y ESCALA DE `fact_cal` (verificado empíricamente, NO es un peso mensual):
  * Cadencia de entrevista: cada persona es entrevistada cada 3 MESES
    (huecos observados: 160,236 de 160,838 = 3 meses; 5,281 = 6; 321 = 9).
  * Meses consecutivos son cohortes DISJUNTAS: 0% de personas compartidas
    entre cualquier par de meses vecinos (2025-12→2026-09).
  * Por tanto: TRES meses consecutivos = 1 entrevista por persona =
    población completa. sum(fact_cal) de un archivo/trimestre ≈ población:
    archivo 01 (dic-ene-feb) = 20.27M total / 16.62M con edad ≥15
    (Chile 2026: 20.15M total, PEP ≈16.9M).
  * UN solo mes = cohorte de ~1/3 de la población ⇒ sum(fact_cal) mensual
    ≈ 6.6-6.9M (≈ población/3). REGLA DE USO:
      - NIVELES (poblaciones, conteos ponderados): agrupar 3 meses
        consecutivos (= trimestre móvil oficial) o multiplicar el mes ×3.
      - TASAS/PROPORCIONES: cualquier agrupación sirve (la escala cancela).

VALIDACIÓN CONTRA EL DATO OFICIAL (Boletín INE n°336, 29-10-2026, JAS 2026):
    indicador            INE oficial      nuestra salida      desv.
    fuerza de trabajo    10,282,718       10,282,930         0.00%
    ocupadas              9,274,742        9,275,130         0.00%
    desocupadas           1,007,976        1,007,799        -0.02%
    inactivas             6,416,440        6,421,373         0.08%
    ocupadas informales   2,451,443        2,452,190         0.03%
    tasa desocupación          9.8%            9.80%        exacta
    tasa participación         61.6%           61.56%        exacta
    tasa de ocupación          55.5%           55.53%        exacta
  → la unificación + deduplicación + política central reproducen la estadística
    oficial; procesar.py ejecuta este chequeo como validación 9.

PESO EXPANSIVO:
  `fact_cal` = factor calibrado (Censo 2017), único factor vigente desde NDE 2019,
  calibrado al TRIMESTRE MÓVIL (ver PANEL Y ESCALA arriba).
  En crudo viene como object con COMA decimal ("195,01134908538") → procesar.py
  lo convierte a float64. Diseño muestral: conglomerado (UPM) + estrato + fact_cal.

TIPOS:
  "object"  : textos y códigos con cero a la izquierda (cine11_2d) o derivados (mes, nombre_region)
  "int64"   : enteros crudos sin nulos (claves)
  "Int64"   : enteros nullable de pandas (toleran nulos y sentinelas convertidas a NA)
  "float64" : numéricos con decimales (fact_cal)

LECTURA DE LA SALIDA (importante): el CSV es texto, así que pandas infiere
int64/float64 al releer. Siempre releer con los tipos del esquema:
    pd.read_csv("Salida/ene_procesado.csv", sep=";", dtype=ESQUEMA_ENE)
(si no, `cine11_2d` pierde el cero a la izquierda —en el archivo está como
"01" y un lector numérico lo vuelve 1.0—).
El módulo comun/inspect_data.py ya aplica este dtype automáticamente.

SENTINELAS (ver SENTINELAS): valores "sin información"/"no sabe"/"no responde"
del libro de códigos se convierten a NA (np.nan) en procesar.py, para que los
agregados no los contengan como ceros ni como categorías válidas.

REGIÓN DE RESIDENCIA Y DE TRABAJO (decisión 02-11-26):
  codigo_region es donde VIVE la persona y codigo_region_trabajo donde está su empleo (b18_region del
  cuestionario; 99,93% válido entre ocupados). Difieren en 3,9% de los ocupados, pero en 37,4% en
  minería. El empleo se ubica donde está el trabajo; desocupados y población, donde viven.

NIVEL EDUCATIVO Y TITULACIÓN (decisión 01-11-26, verificado en los 8 CSV crudos):
  * `nivel` registra el nivel más alto CURSADO, no si se tituló. Sin
    `termino_nivel` no se puede comparar con titulados SIES: en JAS 2026 no
    terminó el 34% de nivel=9 ni el 40% de nivel=7.
    Para contar a quienes tienen el título, filtrar termino_nivel == 1.
  * SIGNIFICADO REAL DE `nivel` 7-9 (las etiquetas del libro de códigos son
    legado y engañan: NO miden tipo de institución). Inferido de los microdatos
    cruzando edu2 (tipo de título) × curso (años aprobados); patrón determinístico
    en el 100% de los casos, no documentado por el INE:
      7 "Centro formación técnica" = título TÉCNICO (edu2=12) con 1-2 años aprobados
      8 "Instituto profesional"    = título TÉCNICO (edu2=12) con 3 años aprobados
      9 "Universitario"            = título PROFESIONAL (edu2=13) de CUALQUIER
                                     institución (incluye profesionales de IP)
    Por eso el nivel 8 casi nunca figura "no terminado" (0.3%): quien aprobó 3 años
    de técnico casi siempre lo terminó. No es error de codificación.
    Llave de cruce correcta con SIES = TIPO DE TÍTULO, no institución.
  * Descartadas `edu3` y `edu2` del cuestionario 2020:
      - edu3 == termino_nivel en el 100% de los casos → redundante.
      - edu2 queda determinado por `nivel` (7 y 8 → 12 técnico, 9 → 13 profesional,
        10/11/12 → 14/15/16) → no agrega información; `nivel` es más rica porque
        además separa al técnico por años aprobados (7 vs 8).
  * `cine11_1d` registra el nivel más alto COMPLETADO (escala INE 0-6: 3 técnico
    superior, 4 profesional/postítulo, 5 magíster, 6 doctorado). Verificado:
    nivel 9 no terminado → 2 (media); magíster no terminado → 4 (profesional).
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# 1. ESQUEMA DE SALIDA — orden canónico de columnas de ene_procesado.csv
# ---------------------------------------------------------------------------
ESQUEMA_ENE: dict[str, str] = {
    # --- A. Clave de la entrevista y período (4) ---------------------------
    "idrph": "int64",            # Identificador único de persona (libro de códigos)
    "ano_encuesta": "int64",     # Año de la entrevista (2025 solo para dic-2025)
    "mes_encuesta": "int64",     # Mes de la entrevista (1-12)
    "mes": "object",             # DERIVADA: período "AAAA-MM" (ej. "2026-03") = clave de análisis temporal

    # --- B. Geografía y diseño muestral (7) --------------------------------
    "codigo_region": "Int64",    # Región de RESIDENCIA 1-16 (Anexo 1); columna `region` del crudo; 0 nulos
    "codigo_region_trabajo": "Int64",  # Región del EMPLEO; `b18_region` del crudo; solo ocupados; 88/99 → NA
    "nombre_region": "object",   # DERIVADA: nombre canónico de comun.normalizador.REGIONES
    "tipo": "Int64",             # Estrato: 1 Ciudad, 3 Rural (2 RAU descontinuado desde EFM 2022)
    "estrato": "Int64",          # Estrato muestral (para estimación diseñada)
    "conglomerado": "Int64",     # UPM / conglomerado (para estimación diseñada)
    "fact_cal": "float64",       # Peso calibrado (Censo 2017); coma decimal → float

    # --- C. Demografía y formación (7) -------------------------------------
    "sexo": "Int64",             # 1 Hombre, 2 Mujer
    "edad": "Int64",             # 0-120 años en semana de referencia
    "nivel": "Int64",            # Nivel educ. más alto aprobado 0-14 (88/99 → NA)
    "termino_nivel": "Int64",    # ¿Terminó ese nivel? 1 Sí, 2 No (88/99 → NA); 1 = titulado en ed. superior
    "estudia_actual": "Int64",   # 1 Sí, 2 No (88 → NA); oferta educativa vigente
    "cine11_1d": "Int64",        # Nivel CINE 2011 1 dígito 0-6 (9 = sin clasif. → NA)
    "cine11_2d": "object",       # Subárea CINE 2011 2 dígitos, string con cero ("01"); 98/99 → NA

    # --- D. Condición de actividad (3) -------------------------------------
    "activ": "Int64",            # 1 Ocupado, 2 Desocupado, 3 FFDD (NA = menores de 15)
    "cae_general": "Int64",      # CAE general 0-9 (0 = menor de 15; 1-3 ocup., 4-5 desocup., 6-9 inactivos)
    "cae_especifico": "Int64",   # CAE específico 0-28: base de indicadores oficiales
                                 #   ocupados 1-7 | desocupados 8-9 | FT 1-9

    # --- E. Ocupación, empleador y formalidad (8) --------------------------
    "b1": "Int64",               # Gran grupo ocupación CIUO-08 (1-10); 999 → NA; solo ocupados (~56% nulos)
    "ciso1": "Int64",            # CISO-18 nivel 1: 1 Independiente, 2 Dependiente (solo ocupados)
    "ciso2": "Int64",            # CISO-18 nivel 2: 1 Empleador … 7 Familiar no remunerado (solo ocupados)
    "categoria_ocupacion": "Int64",  # CISE-93 categoría 1-7; 0 = no corresponde → NA
    "ocup_form": "Int64",        # Formalidad: 1 Formal, 2 Informal (solo ocupados)
    "sector": "Int64",           # Sector institucional: 1 Formal, 2 Informal, 3 Hogares empleadores; 999 → NA
    "r_p_rev4cl_caenes": "Int64",  # Rama de actividad CAENES 1-21 (Anexo 5); 999 → NA (solo ocupados)
    "habituales": "Int64",       # Horas habituales semanales 1-168 (solo ocupados)
    "tpi": "Int64",              # Ocupado a tiempo parcial involuntario: 0 No, 1 Sí (≤30h y disponible)
}

# ---------------------------------------------------------------------------
# 2. CLAVE PRIMARIA
# ---------------------------------------------------------------------------
CLAVE_ENE: list[str] = ["idrph", "ano_encuesta", "mes_encuesta"]
# Unicidad verificada en los 8 archivos crudos y tras la deduplicación global.
# id_identificacion (35,197 p/archivo) es el ID del HOGAR, no de la persona: NO es PK.

# ---------------------------------------------------------------------------
# 3. PROYECCIÓN DE LECTURA (usecols= en procesar.py)
# ---------------------------------------------------------------------------
# Columnas a leer del CSV crudo (separador ";"): todas las de ESQUEMA_ENE que
# vienen del archivo + "mes_central" (solo para VALIDAR que el archivo K tiene
# mes_central == K; no se exporta, porque tras deduplicar cada entrevista puede
# provenir de un archivo con otro mes_central).
COLUMNAS_ENTRADA: list[str] = [
    c for c in ESQUEMA_ENE if c not in ("mes", "codigo_region", "nombre_region", "codigo_region_trabajo")
] + ["region", "b18_region", "mes_central"]

# ---------------------------------------------------------------------------
# 4. SENTINELAS → NA
# ---------------------------------------------------------------------------
# Valor del libro de códigos que significa "sin información"/"no sabe"/
# "no responde"/"no corresponde" y que se convierte a NA (np.nan) en procesar.py.
SENTINELAS: dict[str, list[int]] = {
    "nivel": [88, 99],              # No sabe / No responde
    "codigo_region_trabajo": [88, 99],
    "termino_nivel": [88, 99],
    "estudia_actual": [88, 99],
    "cine11_1d": [9],               # Sin clasificación
    "categoria_ocupacion": [0],     # 0 = no corresponde (no ocupados)
    "b1": [999],                    # Sin información
    "sector": [999],
    "r_p_rev4cl_caenes": [999],
}
# cine11_2d (object): se mapean explícitamente ["98", "99"] → NA en procesar.py
# (se maneja aparte por ser string con cero a la izquierda, no numérico).
SENTINELAS_CINE11_2D: list[str] = ["98", "99"]

# ---------------------------------------------------------------------------
# 5. REGLAS DE VALIDACIÓN (ejecutadas tras procesar; procesar.py falla si violan)
# ---------------------------------------------------------------------------
VALIDACIONES: list[str] = [
    "1. dtype de cada columna == ESQUEMA_ENE[col] tras reindex(columns=ESQUEMA_ENE)",
    "2. (idrph, ano_encuesta, mes_encuesta) es única → 0 duplicados",
    "3. len(filas) == 324,054 entrevistas únicas (782,303 crudas - 458,249 duplicadas)",
    "4. mes ∈ {2025-12} ∪ {2026-01 … 2026-09} (10 meses) y coincide con ano/mes_encuesta",
    "5. codigo_region ∈ 1..16 sin nulos; nombre_region coincide con comun.REGIONES",
    "6. fact_cal > 0 sin nulos",
    "7. sin valores sentinelas residuales en las columnas de SENTINELAS",
    "8. activ=1 ⟹ b1 no nulo salvo b1=999 original (control de cobertura ocupados)",
    "9. Trimestre móvil 2026-07..09 reproduce el Boletín INE n°336: ocupadas,",
    "    fuerza de trabajo, desocupadas, inactivas e informales con desviación ≤0.5%,",
    "    y tasa de desocupación = 9.8% (recetas §7 del libro de códigos: cae_especifico)",
    "10. Cohortes disjuntas: 0% de idrph compartidos entre meses consecutivos",
    "     (consistente con la cadencia de entrevista cada 3 meses)",
    "NOTA: para NIVELES se agrupan 3 meses consecutivos (o mes ×3); ver PANEL Y ESCALA.",
]
