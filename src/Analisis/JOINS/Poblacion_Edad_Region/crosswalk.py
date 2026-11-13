"""
<src/Analisis/JOINS/Poblacion_Edad_Region/crosswalk.py>
Personas de 15 años o más por región y tramo de edad, con su situación laboral, con el Censo 2024.
Salida: Salida/poblacion_edad_region.csv
Decisiones (aprobadas el 13-11-26):
  - Responde si el % de ocupados y la participación de cada región se deben a la edad de su población. Medido antes de
    crear la tabla: ajustando por edad con todos los tramos, 14 de 16 regiones quedan en el mismo puesto y ninguna se
    mueve más de 1.
  - Todas las edades: excluir a los de 65 o más (como el rango 18-64) dejaba fuera a 448.019 ocupados, de 3,8% a 6,3%
    de los de cada región; dejarlos sin ajustar castiga a las regiones con más personas mayores. El ajuste por edad
    evita las dos cosas.
  - Tramos 15-17 y 18-24 separados, como en Formalidad (18 es la edad mínima para trabajar sin restricciones), y 65 o
    más en un solo tramo.
  - La edad sin dato (-66) queda como su propio tramo, para cuadrar exacto con la población de cada región.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers"))
from comun.normalizador import REGIONES  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from esquema import POBLACION_EDAD_REGION  # noqa: E402
import obtener  # noqa: E402

log = logging.getLogger(__name__)
RUTA_SALIDA = Path(__file__).parent / "Salida" / "poblacion_edad_region.csv"

OCUPADO, DESOCUPADO, FUERA_FUERZA = 1, 2, 3
TRAMOS = {"15-17": (15, 17), "18-24": (18, 24), "25-34": (25, 34), "35-44": (35, 44), "45-54": (45, 54), "55-64": (55, 64), "65+": (65, 200)}
SIN_EDAD = "Sin_edad"
N_REGIONES = 16
# Medidos al aprobar la tabla: población de 15 años o más del Censo, su situación y las personas sin edad.
CHILE = {"poblacion": 15_205_784, "ocupados": 8_277_501, "desocupados": 777_920, "fuera_fuerza": 6_060_837, "sin_dato": 89_526}
SIN_EDAD_CHILE = 125_651
COLUMNAS = ["poblacion", "ocupados", "desocupados", "fuera_fuerza", "sin_dato"]


def construir(p: pd.DataFrame) -> pd.DataFrame:
    p = p.copy()
    p["tramo_edad"] = SIN_EDAD
    for tramo, (desde, hasta) in TRAMOS.items():
        p.loc[p["edad"].between(desde, hasta), "tramo_edad"] = tramo
    s = p["sit_fuerza_trabajo"]
    p["ocupados"], p["desocupados"], p["fuera_fuerza"], p["sin_dato"] = s == OCUPADO, s == DESOCUPADO, s == FUERA_FUERZA, s.isna()
    p["poblacion"] = 1
    claves = ["codigo_region", "tramo_edad"]
    t = p.groupby(claves)[COLUMNAS].sum().reset_index()
    # Todas las combinaciones, aunque alguna quede en 0, para que la tabla tenga siempre el mismo grano.
    todas = pd.MultiIndex.from_product([sorted(REGIONES), [*TRAMOS, SIN_EDAD]], names=claves).to_frame(index=False)
    t = todas.merge(t, how="left", on=claves).fillna({c: 0 for c in COLUMNAS})
    chile = t.groupby("tramo_edad", as_index=False)[COLUMNAS].sum().assign(codigo_region=pd.NA)
    t = pd.concat([t, chile], ignore_index=True)
    t["nombre_region"] = t["codigo_region"].map(REGIONES).fillna("Chile")
    t["pct_ocupados"] = (100 * t["ocupados"] / t["poblacion"]).where(t["poblacion"] > 0)
    t["tasa_participacion"] = (100 * (t["ocupados"] + t["desocupados"]) / t["poblacion"]).where(t["poblacion"] > 0)
    orden = {tr: i for i, tr in enumerate([*TRAMOS, SIN_EDAD])}
    return t.assign(_o=t["tramo_edad"].map(orden)).sort_values(["codigo_region", "_o"], na_position="first").drop(columns="_o")


def validar(t: pd.DataFrame, procesado: pd.DataFrame) -> None:
    reg = t[t["codigo_region"].notna()]
    chile = t[t["codigo_region"].isna()].set_index("tramo_edad")
    # Población y situación de cada región según el censo procesado, la misma base que el mapa.
    sit = {OCUPADO: "ocupados", DESOCUPADO: "desocupados", FUERA_FUERZA: "fuera_fuerza"}
    ref = procesado.assign(col=procesado["sit_fuerza_trabajo"].map(sit).fillna("sin_dato")).pivot_table(index="codigo_region", columns="col", values="personas", aggfunc="sum", fill_value=0)
    ref["poblacion"] = ref.sum(axis=1)
    suma = reg.groupby("codigo_region")[COLUMNAS].sum()
    suma.index = suma.index.astype(int)
    controles = {
        f"{(N_REGIONES + 1) * 8} filas con clave única": len(t) == (N_REGIONES + 1) * 8 and not t.duplicated(["codigo_region", "tramo_edad"]).any(),
        "Cada fila cuadra: población = ocupados + desocupados + fuera de la fuerza + sin dato":
            (t["poblacion"] == t["ocupados"] + t["desocupados"] + t["fuera_fuerza"] + t["sin_dato"]).all(),
        "Los tramos suman exacto la población y la situación de cada región del censo procesado":
            (suma[COLUMNAS].values == ref.loc[suma.index, COLUMNAS].values).all(),
        "Chile es la suma de las regiones": (chile[COLUMNAS].sort_index().values == reg.groupby("tramo_edad")[COLUMNAS].sum().sort_index().values).all(),
        "Chile: 15.205.784 personas, 8.277.501 ocupados, 777.920 desocupados, 6.060.837 fuera y 89.526 sin dato":
            {c: int(chile[c].sum()) for c in COLUMNAS} == CHILE,
        f"Edad sin dato: {SIN_EDAD_CHILE:,} personas en Chile".replace(",", "."): int(chile.loc[SIN_EDAD, "poblacion"]) == SIN_EDAD_CHILE,
        "Tasas entre 0 y 100": t[["pct_ocupados", "tasa_participacion"]].stack().between(0, 100).all(),
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    log.info("  [i] Chile, %% de ocupados por tramo: %s", chile["pct_ocupados"].round(1).to_dict())
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    tabla = construir(obtener.cargar_personas())
    validar(tabla, obtener.cargar_procesado())
    tabla = tabla[list(POBLACION_EDAD_REGION)].astype(POBLACION_EDAD_REGION)
    RUTA_SALIDA.parent.mkdir(exist_ok=True)
    tabla.to_csv(RUTA_SALIDA, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", RUTA_SALIDA.name, len(tabla))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(RUTA_SALIDA)
