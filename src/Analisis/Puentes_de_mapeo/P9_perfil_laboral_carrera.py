"""
<src/Analisis/Puentes_de_mapeo/P9_perfil_laboral_carrera.py>
Actualizado 02-11-26 16:40

Generador del P9 · PERFIL_LABORAL_CARRERA del proyecto.

Entradas: src/Scrapers/CASEN/Salida/casen_procesado.csv, src/Scrapers/CASEN/Entrada/casen_2024.dta
          (diseño completo), Salida/P5_puente_carrera_casen.csv y Salida/P1_puente_actividades.csv
Salida:   Salida/P9_perfil_laboral_carrera.csv

Dónde trabajan los titulados de cada carrera, a nivel nacional. Es el indicador más directo del
proyecto, porque CASEN mide carrera y trabajo en la misma persona: no hay reparto ni estimación sintética.
Son personas que trabajan hoy, de todas las edades, no recién contratadas.

Dimensiones, con los nombres de los glosarios:
  categoria_ocupacion  asalariado privado, asalariado público, independiente u otros
  actividad_economica  rama CAENES, como minería, finanzas o agricultura
  categoria_actividad  las dos juntas

FF.AA. y del Orden van en asalariado_publico, igual que en ENE (decisión 02-11-26): son funcionarios
públicos, y así los públicos con título difieren 0,8% entre CASEN y ENE, frente a 4,8% al separarlas.

Se conservan todas las filas con su fiabilidad, aunque tengan una persona encuestada. Una celda
ausente significa sin casos en la muestra, no cero. pct_menores_35 usa solo edades de 22 a 34 y queda
vacío si la carrera no tiene 60 casos en ese grupo.

Esquema: esquema.py (PERFIL_LABORAL_CARRERA)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from esquema import DIMENSIONES_P9, PERFIL_LABORAL_CARRERA  # noqa: E402
from P6_matriz_carrera_actividad_ocupacion import clasificar, error_estandar  # noqa: E402

log = logging.getLogger(__name__)

DIR_SCRAPERS = Path(__file__).resolve().parents[2] / "Scrapers"
DIR_SALIDA = Path(__file__).parent / "Salida"
N_JOVENES, EDAD_MIN_JOVEN, EDAD_MAX_JOVEN = 60, 22, 34
CATEGORIAS = {5: "asalariado_privado", 3: "asalariado_publico", 4: "asalariado_publico", 8: "asalariado_publico",
              1: "independiente", 2: "independiente", 6: "otros", 7: "otros", 9: "otros"}
LLAVES = {"categoria_ocupacion": ["categoria_ocupacion"], "actividad_economica": ["actividad_caenes"],
          "categoria_actividad": ["categoria_ocupacion", "actividad_caenes"]}


def cargar() -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    c = pd.read_csv(DIR_SCRAPERS / "CASEN" / "Salida" / "casen_procesado.csv", sep=";", low_memory=False,
                    usecols=["e6a", "carrera_normalizada", "activ", "titulo_comun", "o15", "rama1", "edad", "expr", "varstrat", "varunit"])
    p5 = pd.read_csv(DIR_SALIDA / "P5_puente_carrera_casen.csv", sep=";")[["e6a", "carrera_normalizada", "carrera_generica", "nivel_titulo", "area_cine_sies", "estado"]]
    d = c.merge(p5, on=["e6a", "carrera_normalizada"], validate="many_to_one")
    d = d[(d["activ"] == 1) & d["titulo_comun"].notna() & (d["estado"] == "asignado") & d["o15"].notna()].copy()
    d["categoria_ocupacion"] = d["o15"].astype(int).map(CATEGORIAS)
    d["actividad_caenes"] = d["rama1"].astype("Int64")
    diseno = pd.read_stata(DIR_SCRAPERS / "CASEN" / "Entrada" / "casen_2024.dta", columns=["varstrat", "varunit"], convert_categoricals=False)
    actividades = pd.read_csv(DIR_SALIDA / "P1_puente_actividades.csv", sep=";")[["actividad_caenes", "actividad_ciiu", "actividad_glosa"]].astype({"actividad_caenes": "Int64"})
    return d, diseno.drop_duplicates().groupby("varstrat").size(), actividades


def construir(d: pd.DataFrame, psu: pd.Series, actividades: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for dimension, llaves in LLAVES.items():
        base = d.dropna(subset=llaves)
        total_general = base["expr"].sum()
        grupo_total = base.groupby(llaves)["expr"].sum()
        for (carrera, nivel, area), x in base.groupby(["carrera_generica", "nivel_titulo", "area_cine_sies"]):
            total, n = x["expr"].sum(), len(x)
            gl = x["varunit"].nunique() - x["varstrat"].nunique()
            jov = x[x["edad"].between(EDAD_MIN_JOVEN, EDAD_MAX_JOVEN)]
            for valores, celda in x.groupby(llaves):
                valores = valores if isinstance(valores, tuple) else (valores,)
                claves = dict(zip(llaves, valores))
                p = celda["expr"].sum() / total
                se = error_estandar(x, pd.Series(x.index.isin(celda.index)), p, total, psu)
                cv = 100 * se / p
                referencia = grupo_total.loc[valores if len(valores) > 1 else valores[0]] / total_general
                joven = np.nan
                if len(jov) >= N_JOVENES:
                    mascara = np.logical_and.reduce([jov[k] == v for k, v in claves.items()])
                    joven = 100 * jov.loc[mascara, "expr"].sum() / jov["expr"].sum()
                filas.append({"carrera_generica": carrera, "nivel_titulo": nivel, "area_cine_sies": area, "dimension": dimension,
                              "categoria_ocupacion": claves.get("categoria_ocupacion"), "actividad_caenes": claves.get("actividad_caenes"),
                              "n_carrera": n, "n_celda": len(celda), "gl": gl, "ocupados_expandidos": celda["expr"].sum(), "pct_en_carrera": 100 * p,
                              "pct_en_grupo": 100 * celda["expr"].sum() / grupo_total.loc[valores if len(valores) > 1 else valores[0]],
                              "indice_especializacion": p / referencia, "error_estandar": 100 * se, "cv_pct": cv, "fiabilidad": clasificar(n, gl, cv),
                              "pct_menores_35": joven, "n_menores_35": len(jov)})
    t = pd.DataFrame(filas)
    t["actividad_caenes"] = t["actividad_caenes"].astype("Int64")
    t = t.merge(actividades, on="actividad_caenes", how="left")
    return t[list(PERFIL_LABORAL_CARRERA)].astype(PERFIL_LABORAL_CARRERA).sort_values(["carrera_generica", "dimension", "pct_en_carrera"], ascending=[True, True, False])


def validar(t: pd.DataFrame, d: pd.DataFrame) -> None:
    """Contrasta la tabla con conteos directos sobre los datos, hechos por otro camino."""
    cat = t[t["dimension"] == "categoria_ocupacion"]
    directa = d.groupby("categoria_ocupacion")["expr"].sum()
    desde = cat.groupby("categoria_ocupacion")["ocupados_expandidos"].sum()
    publicos = d[d["o15"].isin([3, 4, 8])]["expr"].sum()
    sin_ffaa = d[d["o15"].isin([3, 4])]["expr"].sum()
    contador = cat[cat["carrera_generica"] == "CONTADOR AUDITOR"].set_index("categoria_ocupacion")["pct_en_carrera"]
    sumas = t.groupby(["carrera_generica", "dimension"])["pct_en_carrera"].sum()
    grupos = t.groupby(["dimension", "categoria_ocupacion", "actividad_caenes"], dropna=False)["pct_en_grupo"].sum()
    controles = {
        "Dimensiones en catálogo": t["dimension"].isin(DIMENSIONES_P9).all(),
        "Clave única": not t.duplicated(["carrera_generica", "dimension", "categoria_ocupacion", "actividad_caenes"]).any(),
        "pct_en_carrera suma 100 por carrera y dimensión": np.isclose(sumas, 100).all(),
        "pct_en_grupo suma 100 en cada grupo": np.isclose(grupos, 100).all(),
        "Categorías suman el total de cada carrera": np.allclose(desde.reindex(directa.index), directa),
        "Públicos asignados incluyen FF.AA. (conteo directo)": np.isclose(desde["asalariado_publico"], publicos) and publicos > sin_ffaa,
        "Sin FF.AA. reproduce la medición previa (766.253)": abs(sin_ffaa - 766_253) <= 1,
        "Contador privado reproduce 64,5% e independiente 20,4%": round(contador["asalariado_privado"], 1) == 64.5 and round(contador["independiente"], 1) == 20.4,
        "Cada actividad tiene su sección CIIU": t.loc[t["actividad_caenes"].notna(), "actividad_ciiu"].notna().all(),
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    d, psu, actividades = cargar()
    tabla = construir(d, psu, actividades)
    validar(tabla, d)
    ruta = DIR_SALIDA / "P9_perfil_laboral_carrera.csv"
    tabla.to_csv(ruta, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", ruta.name, len(tabla))
    sys.path.insert(0, str(DIR_SCRAPERS / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(ruta)
