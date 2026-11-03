"""
<src/Analisis/Puentes_de_mapeo/P7_perfil_carrera_actividad_ocupacion.py>
Actualizado 02-11-26 16:40

Generador del P7 · PERFIL_CARRERA_ACTIVIDAD_OCUPACION del proyecto.

Entradas: src/Scrapers/CASEN/Salida/casen_procesado.csv
          src/Scrapers/Titulados/Salida/titulados_procesado.csv
          Salida/P5_puente_carrera_casen.csv
Salida:   Salida/P7_perfil_carrera_actividad_ocupacion.csv

Entrega el perfil que usará el índice para cada carrera de pregrado que compite, reemplazando a
P3 (decisión 02-11-26). A diferencia de P6, que publica lo medido carrera por carrera, aquí
toda carrera tiene un perfil y su nivel de confianza dice de dónde viene:

    A_propia     la carrera cumple n >= 60 y gl >= 9
    B_area_nivel hereda de su área CINE y nivel, que cumplen el mínimo
    C_nivel      hereda del total de su nivel (técnico o profesional)

Se hereda en vez de usar pocos casos: un perfil con 20 personas refleja a esas personas, no a
la carrera. El costo es que dos carreras B de la misma área quedan con igual perfil, por eso
el nivel se conserva y debe llegar hasta el índice.

Base: todos los titulados ocupados. El perfil de menores de 35 va como sensibilidad, porque
filtrar por edad reduce todavía más la muestra (decisión 02-11-26). Solo para carreras A.

Esquema: esquema.py (PERFIL_CARRERA_ACTIVIDAD_OCUPACION)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from esquema import NIVELES_CONFIANZA_P7, PERFIL_CARRERA_ACTIVIDAD_OCUPACION  # noqa: E402

log = logging.getLogger(__name__)

DIR_SCRAPERS = Path(__file__).resolve().parents[2] / "Scrapers"
DIR_SALIDA = Path(__file__).parent / "Salida"
RUTA_CASEN = DIR_SCRAPERS / "CASEN" / "Salida" / "casen_procesado.csv"
RUTA_TITULADOS = DIR_SCRAPERS / "Titulados" / "Salida" / "titulados_procesado.csv"
RUTA_P5 = DIR_SALIDA / "P5_puente_carrera_casen.csv"

N_MINIMO, GL_MINIMO, EDAD_JOVEN = 60, 9, 35
CLASES_POR_NIVEL = {
    "Tecnico": ["Técnico de Nivel Superior"],
    "Profesional": ["Profesional Con Licenciatura", "Profesional Sin Licenciatura"],
}
DIMENSIONES = {"actividad_economica": "actividad_caenes", "grupo_ocupacion": "grupo_ocupacion"}


def cargar_ocupados() -> pd.DataFrame:
    """Ocupados con título y carrera asignada, con CIUO en numeración ENE y dimensión actividad_caenes."""
    casen = pd.read_csv(RUTA_CASEN, sep=";", low_memory=False, dtype={"oficio4_08": "object", "rama4": "object"})
    p5 = pd.read_csv(RUTA_P5, sep=";")[["e6a", "carrera_normalizada", "carrera_generica", "estado"]]
    d = casen.merge(p5, on=["e6a", "carrera_normalizada"], validate="many_to_one")
    o = d[(d["activ"] == 1) & d["titulo_comun"].notna() & (d["estado"] == "asignado")].copy()
    o["actividad_caenes"] = o["rama1"].astype("Int64")
    o["grupo_ocupacion"] = o["oficio1_08"].replace(0, 10).astype("Int64")
    return o


def catalogo_carreras(tit: pd.DataFrame) -> pd.DataFrame:
    """Carreras de pregrado que compiten en SIES, con un solo nivel y su área más frecuente."""
    partes = []
    for nivel, clases in CLASES_POR_NIVEL.items():
        x = tit[tit["carrera_clasificacion_nivel_1"].isin(clases)]
        areas = x.groupby(["carrera_generica", "cine13_area"])["total_titulaciones"].sum().reset_index()
        areas = areas.sort_values("total_titulaciones", ascending=False).drop_duplicates("carrera_generica")
        partes.append(areas.assign(nivel_titulo=nivel).rename(columns={"cine13_area": "area_cine_sies"}))
    cat = pd.concat(partes)[["carrera_generica", "nivel_titulo", "area_cine_sies"]]
    if cat["carrera_generica"].duplicated().any():
        raise ValueError("Una carrera genérica aparece en ambos niveles: el perfil sería ambiguo.")
    return cat


def repartir(x: pd.DataFrame, col: str) -> pd.Series:
    """Porcentaje expandido por categoría; vacío si el grupo no tiene datos."""
    s = x.dropna(subset=[col]).groupby(col)["expr"].sum()
    return 100 * s / s.sum() if s.sum() > 0 else s


def suficiente(x: pd.DataFrame) -> tuple[bool, int, int]:
    """Aplica el mínimo del estándar: 60 casos y 9 grados de libertad."""
    n, gl = len(x), x["varunit"].nunique() - x["varstrat"].nunique()
    return n >= N_MINIMO and gl >= GL_MINIMO, n, gl


def perfiles(o: pd.DataFrame, catalogo: pd.DataFrame) -> pd.DataFrame:
    """Asigna a cada carrera su perfil según la jerarquía A → B → C, en cada dimensión."""
    o = o.merge(catalogo, on="carrera_generica", how="inner")
    filas = []
    for fila in catalogo.itertuples(index=False):
        propia = o[o["carrera_generica"] == fila.carrera_generica]
        area = o[(o["area_cine_sies"] == fila.area_cine_sies) & (o["nivel_titulo"] == fila.nivel_titulo)]
        nivel = o[o["nivel_titulo"] == fila.nivel_titulo]
        for dimension, col in DIMENSIONES.items():
            for confianza, grupo in (("A_propia", propia), ("B_area_nivel", area), ("C_nivel", nivel)):
                base = grupo.dropna(subset=[col])
                ok, n, gl = suficiente(base)
                if ok or confianza == "C_nivel":
                    break
            pct = repartir(base, col)
            jovenes = repartir(propia[propia["edad"] < EDAD_JOVEN], col) if confianza == "A_propia" else pd.Series(dtype=float)
            n_jov = int(propia[propia["edad"] < EDAD_JOVEN][col].notna().sum()) if confianza == "A_propia" else 0
            for categoria, valor in pct.items():
                filas.append({
                    "carrera_generica": fila.carrera_generica, "nivel_titulo": fila.nivel_titulo,
                    "area_cine_sies": fila.area_cine_sies, "dimension": dimension,
                    "actividad_caenes": categoria if dimension == "actividad_economica" else pd.NA,
                    "grupo_ocupacion": categoria if dimension == "grupo_ocupacion" else pd.NA,
                    "pct": valor, "nivel_confianza": confianza, "n_perfil": n, "gl_perfil": gl,
                    "pct_menores_35": jovenes.get(categoria, 0.0) if confianza == "A_propia" else np.nan,
                    "n_menores_35": n_jov if confianza == "A_propia" else pd.NA,
                })
    return pd.DataFrame(filas)[list(PERFIL_CARRERA_ACTIVIDAD_OCUPACION)].astype(PERFIL_CARRERA_ACTIVIDAD_OCUPACION)


def validar(p: pd.DataFrame, catalogo: pd.DataFrame) -> None:
    """Detiene el proceso si falta una carrera o un perfil no suma 100."""
    sumas = p.groupby(["carrera_generica", "dimension"])["pct"].sum()
    controles = {
        "Todas las carreras tienen perfil en ambas dimensiones": len(sumas) == 2 * len(catalogo),
        "Cada perfil suma 100": np.isclose(sumas, 100).all(),
        "Nivel de confianza en catálogo": p["nivel_confianza"].isin(NIVELES_CONFIANZA_P7).all(),
        "Clave única": not p.duplicated(["carrera_generica", "dimension", "actividad_caenes", "grupo_ocupacion"]).any(),
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


def generar_p7() -> Path:
    """Construye, valida y exporta P7."""
    tit = pd.read_csv(RUTA_TITULADOS, sep=";", low_memory=False,
                      usecols=["carrera_generica", "carrera_clasificacion_nivel_1", "cine13_area", "total_titulaciones"])
    catalogo = catalogo_carreras(tit)
    perfil = perfiles(cargar_ocupados(), catalogo)
    validar(perfil, catalogo)
    ruta = DIR_SALIDA / "P7_perfil_carrera_actividad_ocupacion.csv"
    perfil.to_csv(ruta, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", ruta.name, len(perfil))
    return ruta


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ruta = generar_p7()
    sys.path.insert(0, str(DIR_SCRAPERS / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(ruta)
