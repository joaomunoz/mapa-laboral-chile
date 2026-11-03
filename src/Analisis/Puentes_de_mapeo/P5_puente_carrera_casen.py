"""
<src/Analisis/Puentes_de_mapeo/P5_puente_carrera_casen.py>
Actualizado 02-11-26 16:40

Generador del P5 · PUENTE_CARRERA_CASEN del proyecto.

Entradas: src/Scrapers/CASEN/Salida/casen_procesado.csv       (61,070 personas)
          src/Scrapers/Titulados/Salida/titulados_procesado.csv (catálogo SIES)
Salidas:  Salida/P5_puente_carrera_casen.csv            (1 fila por e6a × texto declarado)
          Salida/P5_puente_carrera_casen_cobertura.csv  (resumen por método)

Lleva el texto libre `e7` a `carrera_generica` de SIES para poder medir carrera → actividad.

Por qué el catálogo depende del nivel: "ENFERMERIA" declarado por un técnico (e6a 12) es
TECNICO EN ENFERMERIA, no la carrera profesional. Un título explícito en el texto prevalece
sobre e6a y queda marcado en `conflicto_nivel`. e6a 14-15 usa el catálogo profesional porque
e7 suele nombrar el pregrado (solo 18-24% de esos textos menciona un posgrado).

Por qué esta cascada: va de lo más seguro a lo menos seguro, y el método queda en cada fila
para poder excluirlo. El parecido de texto solo corrige errores de tipeo: con un umbral bajo
"PROFESOR DE EDUCACION BASICA" caía en "PEDAGOGIA EN EDUCACION FISICA", y esa confusión no la
detecta la validación CINE porque ambas son del área Educación. "INGENIERIA CIVIL" sin
especialidad se mantiene en la genérica amplia que usa SIES: su destino laboral es disperso
y asignarla a obras civiles sería inventar el dato.

Lo que no se puede asignar queda con su estado (generico, posgrado, uniformado, no_valido o
sin_asignar) en vez de forzarse a una carrera.

Validación independiente: cinef13_area lo codificó MDSF sin usar este puente, y su catálogo
de áreas es el mismo de SIES (cine13_area).

Esquema: esquema.py (PUENTE_CARRERA_CASEN, COBERTURA_CARRERA_CASEN)
"""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz, process

DIR_SCRAPERS = Path(__file__).resolve().parents[2] / "Scrapers"
sys.path.insert(0, str(DIR_SCRAPERS))
from comun.normalizador import normalizar_texto  # noqa: E402

from esquema import COBERTURA_CARRERA_CASEN, ESTADOS_P5, METODOS_P5, PUENTE_CARRERA_CASEN  # noqa: E402

log = logging.getLogger(__name__)

RUTA_CASEN = DIR_SCRAPERS / "CASEN" / "Salida" / "casen_procesado.csv"
RUTA_TITULADOS = DIR_SCRAPERS / "Titulados" / "Salida" / "titulados_procesado.csv"
DIR_SALIDA = Path(__file__).parent / "Salida"

CLASES_TECNICO = {"Técnico de Nivel Superior"}
CLASES_PROFESIONAL = {
    "Profesional Con Licenciatura", "Profesional Sin Licenciatura",
    "Licenciatura No Conducente a Título",
}
# Un nombre de SIES solo identifica su genérica si esta concentra casi todas sus titulaciones.
PARTICIPACION_MINIMA = 0.8
# Umbral de tipeo: bajo este valor el parecido ya confunde carreras distintas.
UMBRAL_TIPEO = 94
# Bajo este acuerdo con CINE, algo está mal en la cascada y no debe publicarse.
ACUERDO_CINE_MINIMO = 95.0

AREAS_CINE = {
    1: "Salud y Bienestar", 2: "Ingeniería, Industria y Construcción", 3: "Educación",
    4: "Servicios", 5: "Administración de Empresas y Derecho",
    6: "Ciencias Sociales, Periodismo e Información",
    7: "Ciencias naturales, matemáticas y estadística",
    8: "Agricultura, Silvicultura, Pesca y Veterinaria",
    9: "Tecnología de la Información y la Comunicación (TIC)", 10: "Artes y Humanidades",
}

# Incluye respuestas que no son carreras; algunas parecen restos de un corrector automático.
NO_VALIDOS = re.compile(
    r"^(NO SABE|NO RECUERDA|NO LO RECUERDA|NO RESPONDE|NINGUNA?|SIN INFORMACION)\b"
    r"|\bTEXTO\b|^POR FAVOR\b"
)
UNIFORMADOS = re.compile(
    r"\b(CARABINEROS?|SUBOFICIAL|OFICIAL|EJERCITO|ARMADA|GENDARMERIA|GENDARME|"
    r"FUERZA AEREA|POLICIA DE INVESTIGACIONES|CADETE)\b"
)
POSGRADOS = re.compile(r"^(MAGISTER|MASTER|MAESTRIA|DOCTORADO|DOCTOR|DIPLOMADO|POSTITULO|POSTGRADO|POSGRADO)\b")
GENERICOS = {
    "PEDAGOGIA", "PROFESOR", "PROFESOR DE ESTADO", "PROFESORADO", "EDUCACION", "DOCENTE",
    "INGENIERIA", "INGENIERIA EN EJECUCION", "INGENIERIA DE EJECUCION", "ADMINISTRACION",
    "LICENCIATURA", "TECNICO", "TECNICO SUPERIOR", "TECNICO DE NIVEL SUPERIOR",
    "TECNICO NIVEL SUPERIOR", "CIENCIAS", "UNIVERSITARIA", "UNIVERSIDAD",
}

# Docentes: se declaran de muchas formas, pero la especialidad identifica la genérica.
# El orden importa: una mención (BASICA CON MENCION EN MATEMATICAS) no cambia la especialidad.
INICIO_DOCENTE = re.compile(r"^(PROFESOR|PROFESORADO|PEDAGOGIA|EDUCADOR|DOCENTE|EDUCACION|PARVULARIA)\b")
ESPECIALIDADES_DOCENTES = [
    (r"PARVUL", "PEDAGOGIA EN EDUCACION DE PARVULOS"),
    (r"DIFERENCIAL|ESPECIAL", "PEDAGOGIA EN EDUCACION DIFERENCIAL"),
    (r"\bBASIC[AO]\b", "PEDAGOGIA EN EDUCACION BASICA"),
    (r"EDUCACION FISICA", "PEDAGOGIA EN EDUCACION FISICA"),
    (r"HISTORIA|CIENCIAS SOCIALES", "PEDAGOGIA EN HISTORIA, GEOGRAFIA Y CIENCIAS SOCIALES"),
    (r"MATEMATICA", "PEDAGOGIA EN MATEMATICAS Y COMPUTACION"),
    (r"INGLES|IDIOMA|FRANCES|ALEMAN", "PEDAGOGIA EN IDIOMAS"),
    (r"LENGUAJE|CASTELLANO|LENGUA|LITERATURA", "PEDAGOGIA EN LENGUAJE, COMUNICACION Y/O CASTELLANO"),
    (r"RELIGION|FILOSOFIA|TEOLOGIA", "PEDAGOGIA EN FILOSOFIA Y RELIGION"),
    (r"\bARTES?\b|MUSICA", "PEDAGOGIA EN ARTES Y MUSICA"),
    (r"BIOLOGIA|QUIMICA|\bFISICA\b|CIENCIAS", "PEDAGOGIA EN CIENCIAS"),
    (r"TECNICO PROFESIONAL", "PEDAGOGIA EN EDUCACION TECNICO PROFESIONAL"),
    (r"ENSENANZA MEDIA|EDUCACION MEDIA", "PEDAGOGIA EN EDUCACION MEDIA"),
]

# Oficios y nombres frecuentes que no aparecen tal cual en SIES. Revisados uno a uno contra
# los textos más comunes sin asignar; agregar aquí, no relajar UMBRAL_TIPEO.
ALIAS_PROFESIONAL = {
    "ABOGADO": "DERECHO", "LEYES": "DERECHO", "CIENCIAS JURIDICAS": "DERECHO",
    "FONOAUDIOLOGO": "FONOAUDIOLOGIA", "PSICOLOGO": "PSICOLOGIA", "KINESIOLOGO": "KINESIOLOGIA",
    "VETERINARIA": "MEDICINA VETERINARIA", "VETERINARIO": "MEDICINA VETERINARIA",
    "MEDICO VETERINARIO": "MEDICINA VETERINARIA",
    "NUTRICION": "NUTRICION Y DIETETICA", "NUTRICIONISTA": "NUTRICION Y DIETETICA",
    "ENFERMERO": "ENFERMERIA", "ENFERMERO UNIVERSITARIO": "ENFERMERIA",
    "ENFERMERIA UNIVERSITARIA": "ENFERMERIA",
    "TECNOLOGO MEDICO": "TECNOLOGIA MEDICA", "TERAPEUTA OCUPACIONAL": "TERAPIA OCUPACIONAL",
    "INGENIERIA AGRONOMO": "AGRONOMIA", "INGENIERIA AGRONOMA": "AGRONOMIA",
    "INGENIERIA AGRONOMICA": "AGRONOMIA", "INGENIERIA EN AGRONOMIA": "AGRONOMIA",
    "CONTABILIDAD": "CONTADOR AUDITOR", "CONTADOR": "CONTADOR AUDITOR",
    "CONTADURIA PUBLICA": "CONTADOR AUDITOR", "CONTADOR PUBLICO": "CONTADOR AUDITOR",
    "MEDICINA GENERAL": "MEDICINA", "MEDICO": "MEDICINA", "MEDICO CIRUJANO": "MEDICINA",
    "MATRONA": "OBSTETRICIA Y PUERICULTURA", "MATRON": "OBSTETRICIA Y PUERICULTURA",
    "QUIMICO FARMACEUTICO": "QUIMICA Y FARMACIA", "QUIMICA FARMACEUTICA": "QUIMICA Y FARMACIA",
    "FARMACIA": "QUIMICA Y FARMACIA",
    "CIRUJANO DENTISTA": "ODONTOLOGIA", "ODONTOLOGO": "ODONTOLOGIA", "DENTISTA": "ODONTOLOGIA",
    "PERIODISTA": "PERIODISMO", "PSICOPEDAGOGO": "PSICOPEDAGOGIA", "ARQUITECTO": "ARQUITECTURA",
    "PUBLICISTA": "PUBLICIDAD", "TRABAJADOR SOCIAL": "TRABAJO SOCIAL",
    "PREVENCION DE RIESGOS": "INGENIERIA EN PREVENCION DE RIESGOS",
    "PREVENCIONISTA DE RIESGOS": "INGENIERIA EN PREVENCION DE RIESGOS",
    "INGENIERIA EN PREVENCION": "INGENIERIA EN PREVENCION DE RIESGOS",
    "INGENIERIA EN CONSTRUCCION CIVIL": "INGENIERIA EN CONSTRUCCION",
    "INGENIERIA EN AUTOMATIZACION": "INGENIERIA EN AUTOMATIZACION, INSTRUMENTACION Y CONTROL",
    "INGENIERIA EN SISTEMAS": "INGENIERIA EN COMPUTACION E INFORMATICA",
    "INGENIERIA DE SISTEMAS": "INGENIERIA EN COMPUTACION E INFORMATICA",
    "INFORMATICA": "INGENIERIA EN COMPUTACION E INFORMATICA",
    "INGENIERIA EN MINERIA": "INGENIERIA EN MINAS",
    "INGENIERIA METALURGICA": "INGENIERIA EN METALURGIA", "INGENIERIA QUIMICO": "INGENIERIA EN QUIMICA",
    "INGENIERIA AUTOMOTRIZ": "INGENIERIA EN MECANICA AUTOMOTRIZ",
    "ECONOMIA": "INGENIERIA COMERCIAL", "COMERCIO EXTERIOR": "INGENIERIA EN COMERCIO EXTERIOR",
    "TURISMO": "ADMINISTRACION TURISTICA Y HOTELERA",
    "ADMINISTRACION HOTELERA": "ADMINISTRACION TURISTICA Y HOTELERA",
    "RECURSOS HUMANOS": "INGENIERIA EN RECURSOS HUMANOS",
    "LICENCIATURA EN ADMINISTRACION": "ADMINISTRACION DE EMPRESAS E ING. ASOCIADAS",
    "ADMINISTRADOR DE EMPRESA": "ADMINISTRACION DE EMPRESAS E ING. ASOCIADAS",
    "ADMINISTRADOR DE EMPRESAS": "ADMINISTRACION DE EMPRESAS E ING. ASOCIADAS",
    "GASTRONOMIA": "ADMINISTRACION GASTRONOMICA", "SICOPEDAGOGIA": "PSICOPEDAGOGIA",
    "INGENIERIA QUIMICA": "INGENIERIA EN QUIMICA", "INGENIERIA LOGISTICA": "INGENIERIA EN LOGISTICA",
    "INGENIERIA EN REDES": "INGENIERIA EN CONECTIVIDAD Y REDES",
    "INGENIERIA EN RRHH": "INGENIERIA EN RECURSOS HUMANOS",
    "INGENIERIA EN PESCA": "INGENIERIA EN ACUICULTURA Y PESCA",
    "INGENIERIA ACUICOLA": "INGENIERIA EN ACUICULTURA Y PESCA",
    "LICENCIATURA EN PSICOLOGIA": "PSICOLOGIA", "PSICOLOGIA CLINICA": "PSICOLOGIA",
    "CONTADURIA": "CONTADOR AUDITOR", "CONTADOR AUDITOR PUBLICO": "CONTADOR AUDITOR",
    "BIOQUIMICO": "BIOQUIMICA", "SOCIOLOGO": "SOCIOLOGIA", "DERECHOS": "DERECHO",
    "ENFERMERIA PROFESIONAL": "ENFERMERIA", "BIOLOGO MARINO": "BIOLOGIA MARINA Y ECOLOGIA MARINA",
    "ORIENTADOR FAMILIAR": "ORIENTACION FAMILIAR Y RELACIONES HUMANAS",
    "TRADUCTOR BILINGUE": "TRADUCCION E INTERPRETACION",
}
ALIAS_TECNICO = {
    "PARAMEDICO": "TECNICO EN ENFERMERIA", "AUXILIAR PARAMEDICO": "TECNICO EN ENFERMERIA",
    "AUXILIAR DE ENFERMERIA": "TECNICO EN ENFERMERIA", "ENFERMERIA (TENS)": "TECNICO EN ENFERMERIA",
    "CONTADOR": "TECNICO EN CONTABILIDAD GENERAL", "CONTADOR GENERAL": "TECNICO EN CONTABILIDAD GENERAL",
    "ELECTRONICO": "TECNICO EN ELECTRONICA Y ELECTRONICA INDUSTRIAL",
    "AUTOMOTRIZ": "TECNICO EN MECANICA AUTOMOTRIZ",
    "ELECTRICIDAD AUTOMOTRIZ": "TECNICO EN MECANICA AUTOMOTRIZ",
    "DIBUJANTE TECNICO": "TECNICO EN DIBUJO TECNICO",
    "DIFERENCIAL": "TECNICO ASISTENTE DEL EDUCADOR DIFERENCIAL",
    "EDUCADOR DIFERENCIAL": "TECNICO ASISTENTE DEL EDUCADOR DIFERENCIAL",
    "LABORATORIO DENTAL": "TECNICO LABORATORISTA DENTAL",
    "ESTILISTA": "TECNICO EN PELUQUERIA Y ESTETICA", "ESTILISTA PROFESIONAL": "TECNICO EN PELUQUERIA Y ESTETICA",
    "ESTETICA": "TECNICO EN PELUQUERIA Y ESTETICA", "ESTETICA PROFESIONAL": "TECNICO EN PELUQUERIA Y ESTETICA",
    "COSMETOLOGO": "TECNICO EN PELUQUERIA Y ESTETICA",
    "INFORMATICO": "TECNICO EN COMPUTACION E INFORMATICA",
    "PROGRAMADOR": "TECNICO EN ANALISIS DE SISTEMAS",
    "PROGRAMADOR EN COMPUTACION": "TECNICO EN ANALISIS DE SISTEMAS",
    "PROGRAMADOR DE COMPUTACION": "TECNICO EN ANALISIS DE SISTEMAS",
    "ANALISTA EN PROGRAMACION": "TECNICO EN ANALISIS DE SISTEMAS",
    "FARMACEUTICO": "TECNICO EN FARMACIA", "AUXILIAR DE FARMACIA": "TECNICO EN FARMACIA",
    "MINA": "TECNICO EN MINERIA", "METALURGICO": "TECNICO EN METALURGIA",
    "ARSENAL QUIRURGICO": "TECNICO EN ARSENALERIA QUIRURGICA",
    "CHEF": "TECNICO EN GASTRONOMIA Y COCINA", "CHEF PROFESIONAL": "TECNICO EN GASTRONOMIA Y COCINA",
    "FOTOGRAFIA PROFESIONAL": "TECNICO EN FOTOGRAFIA", "MASOTERAPEUTA": "TECNICO EN MASOTERAPIA",
    "ADMINISTRADOR DE EMPRESAS": "TECNICO EN ADMINISTRACION DE EMPRESAS",
    "ADMINISTRADOR PUBLICO": "TECNICO EN ADMINISTRACION PUBLICA O MUNICIPAL",
    "REDES": "TECNICO EN ADMINISTRACION DE REDES Y SOPORTE",
    "SOCIAL": "TECNICO EN SERVICIO SOCIAL", "TRABAJADOR SOCIAL": "TECNICO EN SERVICIO SOCIAL",
    "PREVENCION": "TECNICO EN PREVENCION DE RIESGOS",
    "DISENADOR GRAFICO": "TECNICO EN DISENO GRAFICO", "PERITO AGRICOLA": "TECNICO AGROPECUARIO",
    "ELECTROMECANICO": "TECNICO EN ELECTROMECANICA", "MECANICO AUTOMOTRIZ": "TECNICO EN MECANICA AUTOMOTRIZ",
    "CHEF INTERNACIONAL": "TECNICO EN GASTRONOMIA Y COCINA",
}


def limpiar(texto: str) -> str:
    """Quita marcas de género y puntuación final, y unifica abreviaturas y oficios."""
    t = normalizar_texto(texto)
    t = re.sub(r"\((A|O|AS|OS|ES)\)", "", t)
    t = re.sub(r"^(TEC|TNS|TENS|TIENES)\b\.?(?= )", "TECNICO", t)
    t = re.sub(r"\bING\b\.?", "INGENIERIA", t)
    t = re.sub(r"\bINGENIERO\b", "INGENIERIA", t)
    t = re.sub(r"\bLICENCIADO\b", "LICENCIATURA", t)
    return re.sub(r"\s+", " ", t).strip(" .,:;-")


def sin_prefijo_tecnico(texto: str) -> str:
    """Reduce el título técnico a su especialidad: en el catálogo técnico el prefijo no distingue."""
    return re.sub(r"^TECNICO( DE NIVEL SUPERIOR| NIVEL SUPERIOR| SUPERIOR| UNIVERSITARIO)?( EN| DE)? ", "", texto)


def primer_segmento(texto: str) -> str:
    """Conserva el primer título cuando se declaran varios o se agrega una mención."""
    return re.split(r",|:|;|\.| CON MENCION| MENCION| Y MAGISTER| CON MAGISTER| ESPECIALIDAD", texto)[0].strip()


def construir_catalogos(tit: pd.DataFrame) -> tuple[dict, dict[str, str]]:
    """Arma por nivel los nombres de genérica y de carrera SIES que identifican una genérica."""
    tit = tit.assign(generica=tit["carrera_generica"].map(normalizar_texto))
    catalogos = {}
    for nivel, clases in (("Tecnico", CLASES_TECNICO), ("Profesional", CLASES_PROFESIONAL)):
        x = tit[tit["carrera_clasificacion_nivel_1"].isin(clases)].copy()
        clave = limpiar if nivel == "Profesional" else (lambda s: sin_prefijo_tecnico(limpiar(s)))
        x["clave"] = x["carrera"].map(clave)
        pesos = x.groupby(["clave", "generica"], as_index=False)["total_titulaciones"].sum()
        pesos["part"] = pesos["total_titulaciones"] / pesos.groupby("clave")["total_titulaciones"].transform("sum")
        unicas = pesos[pesos["part"] >= PARTICIPACION_MINIMA]
        genericas = {clave(g): g for g in x["generica"].unique()}
        carreras = dict(zip(unicas["clave"], unicas["generica"]))
        catalogos[nivel] = {
            "genericas": genericas, "carreras": carreras,
            "alias": ALIAS_TECNICO if nivel == "Tecnico" else ALIAS_PROFESIONAL,
            "clave": clave, "nombres": sorted(set(genericas) | set(carreras)),
        }
    areas = tit.groupby("generica")["cine13_area"].agg(lambda s: s.value_counts().index[0]).to_dict()
    return catalogos, areas


def por_regla(nivel: str, clave: str) -> str | None:
    """Reglas por patrón para oficios que se declaran de muchas formas."""
    if nivel == "Profesional":
        if INICIO_DOCENTE.match(clave):
            for patron, generica in ESPECIALIDADES_DOCENTES:
                if re.search(patron, clave):
                    return generica
        return None
    if "PARVUL" in clave:
        return "TECNICO ASISTENTE DEL EDUCADOR DE PARVULOS"
    if re.match(r"(SECRETARI|ASISTENTE EJECUTIV)", clave):
        if "COMPUTA" in clave:
            return "SECRETARIADO COMPUTACIONAL"
        return "SECRETARIADO BILINGUE" if "BILINGUE" in clave else "SECRETARIADO EJECUTIVO"
    return None


def buscar(cat: dict, nivel: str, clave: str, con_tipeo: bool) -> tuple[str | None, str]:
    """Aplica la cascada a un nivel y devuelve (genérica, método)."""
    for texto, sufijo in ((clave, ""), (primer_segmento(clave), "_segmento")):
        if texto in cat["genericas"]:
            return cat["genericas"][texto], f"generica{sufijo}"
        if texto in cat["carreras"]:
            return cat["carreras"][texto], f"carrera_sies{sufijo}"
        if texto in cat["alias"]:
            return cat["alias"][texto], f"alias{sufijo}"
        regla = por_regla(nivel, texto)
        if regla:
            return regla, f"regla{sufijo}"
    if con_tipeo:
        texto = primer_segmento(clave)
        parecido = process.extractOne(texto, cat["nombres"], scorer=fuzz.ratio, score_cutoff=UMBRAL_TIPEO)
        # Misma inicial: "GASTRONOMIA" se parece a "ASTRONOMIA" en 95%, y son carreras distintas.
        if parecido and parecido[0][:1] == texto[:1]:
            nombre = parecido[0]
            return cat["genericas"].get(nombre) or cat["carreras"][nombre], "tipeo"
    return None, "sin_metodo"


def resolver(texto: str, e6a: int, catalogos: dict) -> dict:
    """Clasifica un texto declarado: primero descarta lo que no es una carrera asignable."""
    limpio = limpiar(texto)
    esperado = "Tecnico" if e6a == 12 else "Profesional"
    salida = {"texto_limpio": limpio, "nivel_titulo": esperado, "carrera_generica": pd.NA,
              "metodo": "sin_metodo", "conflicto_nivel": False}
    if not limpio or NO_VALIDOS.search(limpio):
        return {**salida, "estado": "no_valido"}
    if UNIFORMADOS.search(limpio):
        return {**salida, "estado": "uniformado"}
    if POSGRADOS.match(limpio):
        return {**salida, "estado": "posgrado"}
    if limpio in GENERICOS:
        return {**salida, "estado": "generico"}

    # El título explícito prevalece sobre e6a: la persona nombró qué estudió.
    if limpio.startswith("TECNICO"):
        nivel = "Tecnico"
    elif re.match(r"^(INGENIERIA|PEDAGOGIA|LICENCIATURA)\b", limpio):
        nivel = "Profesional"
    else:
        nivel = esperado

    otro = "Profesional" if nivel == "Tecnico" else "Tecnico"
    for candidato, con_tipeo in ((nivel, True), (otro, False)):
        clave = catalogos[candidato]["clave"](limpio)
        generica, metodo = buscar(catalogos[candidato], candidato, clave, con_tipeo)
        if generica:
            return {**salida, "nivel_titulo": candidato, "carrera_generica": generica, "metodo": metodo,
                    "conflicto_nivel": candidato != esperado, "estado": "asignado"}
    return {**salida, "nivel_titulo": nivel, "estado": "sin_asignar"}


def construir(casen: pd.DataFrame, catalogos: dict, areas: dict[str, str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Resuelve cada par (e6a, texto) una vez y lo agrega con personas, expansión y acuerdo CINE."""
    pares = casen[["e6a", "carrera_normalizada"]].drop_duplicates()
    filas = [resolver(t, e, catalogos) for e, t in pares.itertuples(index=False)]
    puente = pd.concat([pares.reset_index(drop=True), pd.DataFrame(filas)], axis=1)

    d = casen.merge(puente, on=["e6a", "carrera_normalizada"], validate="many_to_one")
    d["ocupado_titulado"] = (d["activ"] == 1) & d["titulo_comun"].notna()
    d["area_casen"] = d["cinef13_area"].map(AREAS_CINE)
    d["area_sies"] = d["carrera_generica"].map(areas)
    d["comparable"] = d["area_casen"].notna() & d["area_sies"].notna()
    d["acuerdo"] = d["comparable"] & (d["area_casen"] == d["area_sies"])

    conteos = d.groupby(["e6a", "carrera_normalizada"], as_index=False).agg(
        n_personas=("expr", "size"), n_ocupados_titulados=("ocupado_titulado", "sum"),
    )
    puente = puente.merge(conteos, on=["e6a", "carrera_normalizada"])
    puente["area_cine_sies"] = puente["carrera_generica"].map(areas)
    puente = puente.sort_values(["n_personas", "carrera_normalizada"], ascending=[False, True])
    puente = puente[list(PUENTE_CARRERA_CASEN)].astype(PUENTE_CARRERA_CASEN)

    ocup = d[d["ocupado_titulado"]]
    resumen = d.groupby(["estado", "metodo"], as_index=False).agg(
        n_personas=("expr", "size"), n_comparables=("comparable", "sum"), n_acuerdo=("acuerdo", "sum"),
    )
    textos = puente.groupby(["estado", "metodo"], as_index=False).size().rename(columns={"size": "n_textos"})
    exp = ocup.groupby(["estado", "metodo"], as_index=False)["expr"].sum().rename(columns={"expr": "exp_ocupados"})
    resumen = resumen.merge(textos, on=["estado", "metodo"]).merge(exp, on=["estado", "metodo"], how="left")
    resumen["pct_personas"] = 100 * resumen["n_personas"] / len(d)
    resumen["pct_ocupados_titulados_exp"] = 100 * resumen["exp_ocupados"].fillna(0) / ocup["expr"].sum()
    resumen["pct_acuerdo_cine"] = (100 * resumen["n_acuerdo"] / resumen["n_comparables"]).where(resumen["n_comparables"] > 0)
    resumen = resumen.sort_values("n_personas", ascending=False)
    resumen = resumen[list(COBERTURA_CARRERA_CASEN)].astype(COBERTURA_CARRERA_CASEN)
    return puente, resumen


def validar(puente: pd.DataFrame, resumen: pd.DataFrame, catalogos: dict, n_personas: int) -> None:
    """Detiene el proceso si el puente es incoherente o pierde acuerdo con CINE."""
    asignado = puente["estado"] == "asignado"
    validas = {g for c in catalogos.values() for g in c["genericas"].values()}
    comp, acu = resumen["n_comparables"].sum(), None
    acuerdo = resumen.dropna(subset=["pct_acuerdo_cine"])
    acu = (acuerdo["pct_acuerdo_cine"] * acuerdo["n_comparables"]).sum() / comp
    controles = {
        "Clave (e6a, texto) única": not puente.duplicated(["e6a", "carrera_normalizada"]).any(),
        "Conserva a todas las personas": puente["n_personas"].sum() == n_personas,
        "Estados en catálogo": puente["estado"].isin(ESTADOS_P5).all(),
        "Métodos en catálogo": puente["metodo"].isin(METODOS_P5).all(),
        "Genérica solo si está asignado": puente["carrera_generica"].notna().eq(asignado).all(),
        "Genéricas existen en SIES": puente.loc[asignado, "carrera_generica"].isin(validas).all(),
        f"Acuerdo CINE ≥ {ACUERDO_CINE_MINIMO}%": acu >= ACUERDO_CINE_MINIMO,
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    log.info("  [i] Acuerdo CINE global: %.1f%% sobre %d personas comparables", acu, comp)
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


def generar_p5() -> tuple[Path, Path]:
    """Construye, valida y exporta P5 y su cobertura."""
    sys.path.insert(0, str(DIR_SCRAPERS / "CASEN"))
    casen = pd.read_csv(RUTA_CASEN, sep=";", low_memory=False,
                        dtype={"carrera_normalizada": "object"})
    tit = pd.read_csv(RUTA_TITULADOS, sep=";", low_memory=False,
                      usecols=["carrera", "carrera_generica", "carrera_clasificacion_nivel_1",
                               "cine13_area", "total_titulaciones"])
    catalogos, areas = construir_catalogos(tit)
    puente, resumen = construir(casen, catalogos, areas)
    validar(puente, resumen, catalogos, len(casen))

    DIR_SALIDA.mkdir(parents=True, exist_ok=True)
    ruta_puente = DIR_SALIDA / "P5_puente_carrera_casen.csv"
    ruta_resumen = DIR_SALIDA / "P5_puente_carrera_casen_cobertura.csv"
    puente.to_csv(ruta_puente, sep=";", index=False, encoding="utf-8")
    resumen.to_csv(ruta_resumen, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", ruta_puente.name, len(puente))
    return ruta_puente, ruta_resumen


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    rutas = generar_p5()
    sys.path.insert(0, str(DIR_SCRAPERS / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    for ruta in rutas:
        inspeccion_rigurosa(ruta)
