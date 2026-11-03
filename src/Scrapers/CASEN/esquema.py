"""
<src/Scrapers/CASEN/esquema.py>

Definición del esquema de CASEN 2024 — Single Source of Truth.

Salida: Salida/casen_procesado.csv
Granularidad: 1 fila por PERSONA (folio, id_persona) que asiste o asistió a educación superior.
Universo: e6a 12-15 (61,070 personas). Coincide exacto con quienes tienen `e7` (nombre de la
carrera); es la única población que aporta al vínculo carrera → ocupación → sector.

UNIVERSO Y TÍTULO (verificado en los microdatos, 02-11-26):
  * e6c_completo está vacío para quienes siguen asistiendo (asiste == 1): no cuentan como
    titulados. Por eso `titulo_comun` solo se asigna con e6c_completo == 1 y queda NA si no
    terminó o sigue estudiando (13,555 + 7,342 personas). Se conservan esas filas porque el
    puente e7 → carrera_generica aprovecha todos los textos.
  * titulo_comun usa el catálogo común de títulos del proyecto. CASEN no distingue postítulo.
  * Magíster y doctorado: `e7` suele nombrar el pregrado; solo 18-24% de esos textos menciona
    un posgrado (medido 02-11-26).

PESO Y DISEÑO:
  * `expr` viene como int16: sumarlo sin convertir DESBORDA en groupby y da porcentajes
    absurdos (error real detectado 02-11-26). Se exporta float64.
  * Es factor REGIONAL, único y anual (no se reescala como fact_cal de ENE).
  * Varianza: usar varstrat + varunit (libro de códigos).

REPRESENTATIVIDAD: nacional, urbano/rural y regional. Terreno 01-nov-2024 a 02-feb-2025.
Carrera × sector × región NO es estimable con precisión: la celda queda sin casos suficientes.

COMPATIBILIDAD CON OTRAS FUENTES:
  * codigo_region: viene de `region` (misma numeración que comun.REGIONES).
    NO usar `region_geo`: sigue orden geográfico y cruzaría regiones equivocadas.
  * rama1: CAENES 1-21, igual que r_p_rev4cl_caenes de ENE.
  * oficio1_08: CIUO-08 0-9, con 0 = FF.AA. En ENE ese grupo es b1 == 10; armonizar al cruzar.

PRIVACIDAD: se excluyen los textos libres o9a, o9b, o24, e9nom y e9dir (ocupación descrita,
nombres y direcciones de establecimientos). No hacen falta aquí y pueden identificar personas.

LECTURA: pd.read_csv("Salida/casen_procesado.csv", sep=";", dtype=ESQUEMA_CASEN)
(sin dtype, oficio4_08 y rama4 pierden el cero a la izquierda).
"""

from __future__ import annotations

# Orden canónico de columnas de casen_procesado.csv.
ESQUEMA_CASEN: dict[str, str] = {
    # --- A. Identificación (2) ---
    "folio": "int64",              # Hogar
    "id_persona": "int64",         # Persona dentro del hogar
    # --- B. Geografía y diseño muestral (6) ---
    "codigo_region": "int64",      # `region` del crudo, 1-16
    "nombre_region": "object",     # DERIVADA: comun.normalizador.REGIONES
    "area": "int64",               # 1 Urbano, 2 Rural
    "expr": "float64",             # Factor de expansión regional (int16 en crudo)
    "varstrat": "int64",           # Estrato de varianza
    "varunit": "int64",            # Conglomerado de varianza
    # --- C. Demografía (2) ---
    "edad": "int64",
    "sexo": "int64",               # 1 Hombre, 2 Mujer
    # --- D. Educación (9) ---
    "asiste": "int64",             # 1 Sí, 2 No
    "e6a": "int64",                # 12 Técnico, 13 Profesional, 14 Magíster, 15 Doctorado
    "e6c_completo": "Int64",       # 1 Sí, 2 No; NA si sigue asistiendo
    "titulo_comun": "object",      # DERIVADA: título común; NA si no tiene el título
    "e7": "object",                # Nombre de la carrera, tal como se declaró
    "carrera_normalizada": "object",  # DERIVADA: e7 sin tildes, en mayúsculas
    "cinef13_area": "Int64",       # CINE-F campo amplio 1-10
    "cinef13_subarea": "Int64",    # CINE-F campo específico 1-27
    "e8": "Int64",                 # Institución: 1 CFT, 2 IP, 3-4 U. privada, 5 Estatal, 6 otro, 7 extranjera
    # --- E. Trabajo (7) ---
    "activ": "Int64",              # 1 Ocupado, 2 Desocupado, 3 Inactivo; NA menores de 15
    "o15": "Int64",                # Categoría: 3 público, 4 empresa pública, 5 privado, 1-2 independiente...
    "oficio1_08": "Int64",         # CIUO-08 1 dígito, 0 = FF.AA.
    "oficio4_08": "object",        # CIUO-08 4 dígitos, string con cero
    "rama1": "Int64",              # CAENES 1-21
    "rama4": "object",             # CAENES 4 dígitos, string con cero
    "yoprcor": "float64",          # Ingreso de la ocupación principal corregido
}

CLAVE_CASEN: list[str] = ["folio", "id_persona"]

# Columnas leídas del .dta: las del esquema que vienen del crudo, más `region`.
COLUMNAS_ENTRADA: list[str] = [
    c for c in ESQUEMA_CASEN
    if c not in ("codigo_region", "nombre_region", "titulo_comun", "carrera_normalizada")
] + ["region"]

# Códigos "No responde", "No sabe" y "Glosa no permite clasificación" → NA.
SENTINELAS: list[int] = [-66, -88, -99]
COLUMNAS_CON_SENTINELAS: list[str] = [
    "cinef13_area", "cinef13_subarea", "e8", "oficio1_08", "oficio4_08", "rama1", "rama4",
]

TITULO_POR_E6A: dict[int, str] = {
    12: "Tecnico_Superior", 13: "Profesional", 14: "Magister", 15: "Doctorado",
}

# Textos libres que nunca deben llegar a la salida (se valida en procesar.py).
TEXTOS_EXCLUIDOS: list[str] = ["o9a", "o9b", "o24", "e9nom", "e9dir"]
