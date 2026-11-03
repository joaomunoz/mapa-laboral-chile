"""
<src/Analisis/Puentes_de_mapeo/P8_razon_empleo_carrera.py>
Actualizado 02-11-26 16:40

Generador del P8 · RAZON_EMPLEO_CARRERA del proyecto.

Entradas: src/Scrapers/CASEN/Salida/casen_procesado.csv, src/Scrapers/CASEN/Entrada/casen_2024.dta
          (diseño completo) y Salida/P5_puente_carrera_casen.csv
Salida:   Salida/P8_razon_empleo_carrera.csv

Por cada 10 titulados de 22 a 54 años de una carrera: cuántos están ocupados, desocupados e
inactivos, a nivel nacional, más la tasa de desempleo con su error según el diseño muestral.

Es un indicador para mostrar JUNTO al índice, no dentro de la fórmula (decisión 02-11-26). Mide
algo distinto a MiFuturo, y al usarla para repartir desocupados empeoró el Paso 2: la mitad de
la muestra predijo peor a la otra mitad (23,3 con stock frente a 24,6 con razón, profesionales).
La fiabilidad se evalúa sobre la tasa de desempleo, que es el dato más ruidoso de la fila.

Esquema: esquema.py (RAZON_EMPLEO_CARRERA)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from esquema import RAZON_EMPLEO_CARRERA  # noqa: E402
from P6_matriz_carrera_actividad_ocupacion import clasificar, error_estandar  # noqa: E402

log = logging.getLogger(__name__)

DIR_SCRAPERS = Path(__file__).resolve().parents[2] / "Scrapers"
DIR_SALIDA = Path(__file__).parent / "Salida"
EDAD_MIN, EDAD_MAX = 22, 54


def cargar() -> tuple[pd.DataFrame, pd.Series]:
    """Personas con título, carrera asignada y condición de actividad, y el diseño completo."""
    ruta = DIR_SCRAPERS / "CASEN" / "Salida" / "casen_procesado.csv"
    c = pd.read_csv(ruta, sep=";", low_memory=False, usecols=["e6a", "carrera_normalizada", "activ", "titulo_comun", "expr", "edad", "varstrat", "varunit"])
    p5 = pd.read_csv(DIR_SALIDA / "P5_puente_carrera_casen.csv", sep=";")[["e6a", "carrera_normalizada", "carrera_generica", "nivel_titulo", "estado"]]
    d = c.merge(p5, on=["e6a", "carrera_normalizada"], validate="many_to_one")
    d = d[d["titulo_comun"].notna() & (d["estado"] == "asignado") & d["edad"].between(EDAD_MIN, EDAD_MAX) & d["activ"].notna()]
    diseno = pd.read_stata(DIR_SCRAPERS / "CASEN" / "Entrada" / "casen_2024.dta", columns=["varstrat", "varunit"], convert_categoricals=False)
    return d, diseno.drop_duplicates().groupby("varstrat").size()


def construir(d: pd.DataFrame, psu: pd.Series) -> pd.DataFrame:
    filas = []
    for (carrera, nivel), x in d.groupby(["carrera_generica", "nivel_titulo"]):
        a = x[x["activ"].isin([1, 2])]
        total = x["expr"].sum()
        por_10 = {k: 10 * x.loc[x["activ"] == v, "expr"].sum() / total for k, v in (("ocupados_por_10", 1), ("desocupados_por_10", 2), ("inactivos_por_10", 3))}
        fila = {"carrera_generica": carrera, "nivel_titulo": nivel, "n_titulados": len(x), "n_activos": len(a),
                "n_desocupados": int((a["activ"] == 2).sum()), **por_10}
        if a.empty:
            fila |= {"gl": 0, "tasa_desempleo_pct": np.nan, "error_estandar": np.nan, "cv_pct": np.nan, "fiabilidad": "no_fiable"}
        else:
            base = a["expr"].sum()
            u = a.loc[a["activ"] == 2, "expr"].sum() / base
            se = error_estandar(a, pd.Series((a["activ"] == 2).to_numpy()), u, base, psu)
            gl = a["varunit"].nunique() - a["varstrat"].nunique()
            cv = 100 * se / u if u > 0 else np.inf
            fila |= {"gl": gl, "tasa_desempleo_pct": 100 * u, "error_estandar": 100 * se,
                     "cv_pct": cv if np.isfinite(cv) else np.nan, "fiabilidad": clasificar(len(a), gl, cv)}
        filas.append(fila)
    return pd.DataFrame(filas)[list(RAZON_EMPLEO_CARRERA)].astype(RAZON_EMPLEO_CARRERA)


def validar(t: pd.DataFrame) -> None:
    suma = t[["ocupados_por_10", "desocupados_por_10", "inactivos_por_10"]].sum(axis=1)
    controles = {"Clave única": t["carrera_generica"].is_unique, "Cada fila suma 10": np.isclose(suma, 10).all(),
                 "Activos no superan a titulados": (t["n_activos"] <= t["n_titulados"]).all()}
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    if not all(controles.values()):
        raise ValueError("Validaciones fallidas en P8")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    tabla = construir(*cargar())
    validar(tabla)
    ruta = DIR_SALIDA / "P8_razon_empleo_carrera.csv"
    tabla.to_csv(ruta, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", ruta.name, len(tabla))
    sys.path.insert(0, str(DIR_SCRAPERS / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(ruta)
