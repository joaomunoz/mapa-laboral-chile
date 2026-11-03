"""
<src/Analisis/Puentes_de_mapeo/P4_puente_niveles_educativos.py>

Generador del P4 · PUENTE_NIVELES_EDUCATIVOS (v2) del proyecto.

Propósito:
  Homologar el nivel educativo entre las 3 fuentes con una LLAVE COMÚN de tipo de título
  (`titulo_comun`):
    1. ENE (INE): `nivel` (0 a 14) y `cine11_1d` (escala INE 0-6).
    2. SIES Titulados: `carrera_clasificacion_nivel_1` (9 categorías).
    3. ENADEL (SENCE): nivel educacional requerido por vacante (`c1_c`/`c3_c`, códigos 0-7).

Por qué tipo de título y no institución (auditoría ENE 01-11-26): en los microdatos,
`nivel` 7 = técnico con 1-2 años aprobados, 8 = técnico con 3 años, 9 = profesional de
CUALQUIER institución (patrón determinístico edu2 × curso en el 100% de los casos).
Las glosas "CFT"/"IP"/"Universitario" son legado del INE y no identifican la institución.
Con esta llave desaparece el ambiguo `Tecnico_o_Profesional` de la v1.

`cine11_1d` registra el nivel más alto COMPLETADO (ej. nivel 9 no terminado → 2), por eso
en P4 se informa el valor que toma cuando el nivel está completo.

Salida:
  Salida/P4_puente_niveles_educativos.csv (15 filas, una por código de nivel ENE)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

from esquema import PUENTE_NIVELES_EDUCATIVOS, SIES_EXCLUIDAS_P4, TITULOS_COMUNES  # noqa: E402

log = logging.getLogger(__name__)

DIR_SCRAPERS = Path(__file__).resolve().parents[2] / "Scrapers"
RUTA_TITULADOS = DIR_SCRAPERS / "Titulados" / "Salida" / "titulados_procesado.csv"
RUTA_ENADEL_CARGOS = DIR_SCRAPERS / "ENADEL" / "Salida" / "enadel_cargos_procesado.csv"
DIR_SALIDA = Path(__file__).parent / "Salida"
SEPARADOR_SALIDA = ";"
SEP_LISTA = " | "  # separador de varias categorías SIES dentro de una celda

ORIGEN = "INE Libro Códigos 2020 + microdatos ENE 2026 / SIES Glosario 2007-2025 / ENADEL 2025"

# Códigos ENADEL (libro de códigos, c1_c/c3_c) → texto exacto de enadel_cargos_procesado.
ENADEL = {
    0: "Sin exigencia de educación formal",
    1: "Educación básica",
    2: "Educación media Científico humanista",
    3: "Educación media Técnico profesional",
    4: "Técnico superior",
    5: "Profesional",
    6: "Profesional con Magíster",
    7: "Profesional con Doctorado",
}


def _fila(nivel, glosa, significado, cine, titulo, sies, enadel):
    return {
        "ene_nivel": nivel,
        "glosa_ene_nivel": glosa,
        "significado_ene": significado,
        "cine11_1d": cine,
        "titulo_comun": titulo,
        "sies_clasificacion_nivel_1": SEP_LISTA.join(sies) if sies else pd.NA,
        "enadel_codigo": enadel,
        "enadel_nivel_educacional": ENADEL[enadel],
        "origen": ORIGEN,
    }


# cine11_1d = valor observado en ene_procesado cuando el nivel está completo (moda).
TABLA_NIVELES: list[dict] = [
    _fila(0, "Nunca estudió", "Sin educación formal", 0, "No_superior", None, 0),
    _fila(1, "Sala cuna", "Preescolar", 0, "No_superior", None, 0),
    _fila(2, "Kínder", "Preescolar", 0, "No_superior", None, 0),
    _fila(3, "Básica o primaria", "Básica", 1, "No_superior", None, 1),
    _fila(4, "Media común", "Media científico-humanista", 2, "No_superior", None, 2),
    _fila(5, "Media técnico profesional", "Media técnico-profesional", 2, "No_superior", None, 3),
    _fila(6, "Humanidades", "Media sistema antiguo", 2, "No_superior", None, 2),
    _fila(7, "Centro formación técnica",
          "Título técnico (edu2=12) con 1-2 años aprobados; NO identifica CFT",
          3, "Tecnico_Superior", ["Técnico de Nivel Superior"], 4),
    _fila(8, "Instituto profesional",
          "Título técnico (edu2=12) con 3 años aprobados; NO identifica IP",
          3, "Tecnico_Superior", ["Técnico de Nivel Superior"], 4),
    _fila(9, "Universitario",
          "Título profesional (edu2=13) de cualquier institución, incluye profesionales de IP",
          4, "Profesional", ["Profesional Con Licenciatura", "Profesional Sin Licenciatura"], 5),
    # ENE 10 incluye diplomados de ≥1 semestre (edu2=14). ENADEL no tiene nivel de postítulo:
    # se usa "Profesional" (5), el requisito más cercano.
    _fila(10, "Post títulos", "Diplomado o postítulo de ≥1 semestre (edu2=14)", 4, "Postitulo",
          ["Postítulo", "Especialidad Médica u Odontológica", "Diplomado (desde un semestre)"], 5),
    _fila(11, "Magíster", "Magíster (edu2=15)", 5, "Magister", ["Magister"], 6),
    _fila(12, "Doctorado", "Doctorado (edu2=16)", 6, "Doctorado", ["Doctorado"], 7),
    _fila(13, "Educación diferencial", "Educación especial", pd.NA, "No_superior", None, 0),
    # INE (edu2=11) lo clasifica como técnica/normalista del sistema antiguo, no superior;
    # cine11_1d observado 1-2. Además queda fuera del rango etario del índice (22-54).
    _fila(14, "Normalista", "Normalista sistema antiguo (edu2=11), no superior", 2, "No_superior", None, 3),
]


def validar(df: pd.DataFrame) -> None:
    """Ejecuta las 5 validaciones de esquema.VALIDACIONES['P4_puente_niveles_educativos']; falla si alguna no se cumple."""
    log.info("=== Validaciones P4_puente_niveles_educativos (%d filas) ===", len(df))
    resultados = []

    ok1 = len(df) == 15 and df["ene_nivel"].is_unique and set(df["ene_nivel"]) == set(range(15))
    resultados.append(("1. 15 filas con códigos ENE 0 a 14 únicos", ok1, ""))

    nulos = int(df[["ene_nivel", "titulo_comun"]].isna().sum().sum())
    fuera = sorted(set(df["titulo_comun"]) - set(TITULOS_COMUNES))
    resultados.append(("2. titulo_comun sin nulos y en catálogo", nulos == 0 and not fuera,
                       f"{nulos} nulos, fuera de catálogo: {fuera}"))

    # 3. Contra los datos reales: las categorías citadas existen y, con las excluidas, cubren todo.
    sies_real = set(pd.read_csv(RUTA_TITULADOS, sep=";", usecols=["carrera_clasificacion_nivel_1"])
                    ["carrera_clasificacion_nivel_1"].dropna())
    sies_p4 = {c for v in df["sies_clasificacion_nivel_1"].dropna() for c in v.split(SEP_LISTA)}
    inexistentes = sorted(sies_p4 - sies_real)
    sin_cubrir = sorted(sies_real - sies_p4 - set(SIES_EXCLUIDAS_P4))
    resultados.append(("3. Categorías SIES existen y cubren el 100%", not inexistentes and not sin_cubrir,
                       f"inexistentes: {inexistentes}, sin cubrir: {sin_cubrir}"))

    enadel_real = set(pd.read_csv(RUTA_ENADEL_CARGOS, sep=None, engine="python",
                                  usecols=["nivel_educacional"])["nivel_educacional"].dropna())
    enadel_inex = sorted(set(df["enadel_nivel_educacional"]) - enadel_real)
    resultados.append(("4. Textos ENADEL existen en enadel_cargos_procesado", not enadel_inex,
                       f"inexistentes: {enadel_inex}"))

    sup = df[df["titulo_comun"] != "No_superior"]
    n_cod = sup.groupby("titulo_comun")["enadel_codigo"].nunique()
    resultados.append(("5. Cada título superior tiene un único enadel_codigo", bool((n_cod == 1).all()),
                       n_cod.to_dict()))

    for nombre, ok, detalle in resultados:
        log.info("  [%s] %-52s %s", "✓" if ok else "✗", nombre, "" if ok else detalle)
    fallidas = [n for n, ok, _ in resultados if not ok]
    if fallidas:
        raise ValueError(f"P4: validaciones fallidas: {fallidas}")


def generar_puente_p4() -> Path:
    log.info("Generando P4_puente_niveles_educativos (v2)...")
    df = pd.DataFrame(TABLA_NIVELES)
    df = df[list(PUENTE_NIVELES_EDUCATIVOS)].astype(PUENTE_NIVELES_EDUCATIVOS)

    validar(df)

    DIR_SALIDA.mkdir(parents=True, exist_ok=True)
    ruta_salida = DIR_SALIDA / "P4_puente_niveles_educativos.csv"
    df.to_csv(ruta_salida, sep=SEPARADOR_SALIDA, index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas, %.1f KB)", ruta_salida.name, len(df), ruta_salida.stat().st_size / 1024)

    # Reporte de inspección obligatorio para toda tabla generada (regla del proyecto).
    sys.path.insert(0, str(DIR_SCRAPERS / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(ruta_salida)

    return ruta_salida


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    generar_puente_p4()
