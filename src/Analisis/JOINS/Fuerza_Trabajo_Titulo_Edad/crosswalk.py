"""
<src/Analisis/JOINS/Fuerza_Trabajo_Titulo_Edad/crosswalk.py>

Desocupación con y sin título técnico o profesional por región y tramo de edad, con el Censo 2024.

Salida: Salida/fuerza_trabajo_titulo_edad.csv

Decisiones (aprobadas el 11-11-26):
  - Responde si la ventaja del título en la desocupación ("16 de 16 regiones") se mantiene a igual edad. Medido
    antes de crear la tabla: sí, en los 4 tramos de 25 a 64 de las 16 regiones; ajustada por edad, la brecha de
    Chile casi no cambia (3,0 a 2,9 puntos con todas las edades).
  - Dos grupos y no tres niveles: es la comparación de la tarjeta y de "Estudios y trabajo".
  - Tramos de 10 años como en Formalidad; 15-24 y 65 o más se publican, pero la comparación usa de 25 a 64: de 15
    a 24 los titulados recién buscan su primer trabajo y la relación se invierte, y desde 65 hay pocos activos.
  - La edad sin dato (-66) queda como su propio tramo, para cuadrar exacto con la tabla por región y nivel.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers"))
from comun.normalizador import REGIONES  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent))
from esquema import FUERZA_TRABAJO_TITULO_EDAD  # noqa: E402
import obtener  # noqa: E402

log = logging.getLogger(__name__)

RUTA_SALIDA = Path(__file__).parent / "Salida" / "fuerza_trabajo_titulo_edad.csv"
OCUPADO, DESOCUPADO = 1, 2
CON_TITULO = ["Tecnico", "Profesional"]
TRAMOS = {"15-24": (15, 24), "25-34": (25, 34), "35-44": (35, 44), "45-54": (45, 54), "55-64": (55, 64), "65+": (65, 200)}
SIN_EDAD = "Sin_edad"
TRAMOS_COMPARACION = ["25-34", "35-44", "45-54", "55-64"]
N_REGIONES = 16
SIN_EDAD_CHILE = 68_783  # Activos con nivel informado y edad -66, medido al aprobar la tabla


def construir(p: pd.DataFrame) -> pd.DataFrame:
    a = p[p["nivel_titulo"].notna() & p["sit_fuerza_trabajo"].isin([OCUPADO, DESOCUPADO])].copy()
    a["con_titulo"] = a["nivel_titulo"].isin(CON_TITULO)
    a["tramo_edad"] = SIN_EDAD
    for tramo, (desde, hasta) in TRAMOS.items():
        a.loc[a["edad"].between(desde, hasta), "tramo_edad"] = tramo
    a["ocupados"] = a["sit_fuerza_trabajo"] == OCUPADO
    a["desocupados"] = a["sit_fuerza_trabajo"] == DESOCUPADO
    claves = ["codigo_region", "con_titulo", "tramo_edad"]
    t = a.groupby(claves)[["ocupados", "desocupados"]].sum().reset_index()
    # Todas las combinaciones, aunque alguna quede en 0, para que la tabla tenga siempre el mismo grano.
    todas = pd.MultiIndex.from_product([sorted(REGIONES), [False, True], [*TRAMOS, SIN_EDAD]], names=claves).to_frame(index=False)
    t = todas.merge(t, how="left", on=claves).fillna({"ocupados": 0, "desocupados": 0})
    chile = t.groupby(["con_titulo", "tramo_edad"], as_index=False)[["ocupados", "desocupados"]].sum().assign(codigo_region=pd.NA)
    t = pd.concat([t, chile], ignore_index=True)
    t["nombre_region"] = t["codigo_region"].map(REGIONES).fillna("Chile")
    activos = t["ocupados"] + t["desocupados"]
    t["tasa_desocupacion"] = (100 * t["desocupados"] / activos).where(activos > 0)
    orden = {tr: i for i, tr in enumerate([*TRAMOS, SIN_EDAD])}
    return t.assign(_o=t["tramo_edad"].map(orden)).sort_values(["codigo_region", "con_titulo", "_o"], na_position="first").drop(columns="_o")


def validar(t: pd.DataFrame, niveles: pd.DataFrame) -> None:
    reg = t[t["codigo_region"].notna()]
    suma = reg.groupby(["codigo_region", "con_titulo"])[["ocupados", "desocupados"]].sum()
    ref = niveles.assign(con_titulo=niveles["nivel_titulo"].isin(CON_TITULO)).groupby(["codigo_region", "con_titulo"])[["ocupados_residencia", "desocupados"]].sum()
    ref.index = ref.index.set_levels(ref.index.levels[0].astype("Int64"), level=0)
    comp = (lambda tr: reg[reg["tramo_edad"].isin(tr)].pivot_table(index=["codigo_region", "tramo_edad"], columns="con_titulo", values="tasa_desocupacion"))
    c = comp(TRAMOS_COMPARACION)
    chile = t[t["codigo_region"].isna()].set_index(["con_titulo", "tramo_edad"])
    controles = {
        f"{(N_REGIONES + 1) * 2 * 7} filas con clave única": len(t) == (N_REGIONES + 1) * 2 * 7 and not t.duplicated(["codigo_region", "con_titulo", "tramo_edad"]).any(),
        "Los tramos suman exacto la tabla por región y nivel (ocupados por residencia y desocupados)":
            (suma["ocupados"].values == ref.loc[suma.index, "ocupados_residencia"].values).all() and (suma["desocupados"].values == ref.loc[suma.index, "desocupados"].values).all(),
        "Chile es la suma de las regiones": (chile[["ocupados", "desocupados"]].sort_index().values == reg.groupby(["con_titulo", "tramo_edad"])[["ocupados", "desocupados"]].sum().sort_index().values).all(),
        f"Edad sin dato: {SIN_EDAD_CHILE:,} activos en Chile".replace(",", "."): int(chile.xs(SIN_EDAD, level="tramo_edad")[["ocupados", "desocupados"]].sum().sum()) == SIN_EDAD_CHILE,
        "En las 16 regiones y en cada tramo de 25 a 64, menor desocupación con título": len(c) == N_REGIONES * 4 and (c[True] < c[False]).all(),
        "Tasas entre 0 y 100": t["tasa_desocupacion"].dropna().between(0, 100).all(),
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    sin_edad = reg[reg["tramo_edad"] == SIN_EDAD].groupby("codigo_region")[["ocupados", "desocupados"]].sum().sum(axis=1) / reg.groupby("codigo_region")[["ocupados", "desocupados"]].sum().sum(axis=1)
    log.info("  [i] %% de activos sin edad por región (mayores): %s", (100 * sin_edad).round(1).sort_values(ascending=False).head(3).to_dict())
    log.info("  [i] Chile, tasa con/sin título por tramo: %s", chile["tasa_desocupacion"].round(1).unstack(level="con_titulo").to_dict("index"))
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    tabla = construir(obtener.cargar_personas())
    validar(tabla, obtener.cargar_niveles())
    tabla = tabla[list(FUERZA_TRABAJO_TITULO_EDAD)].astype(FUERZA_TRABAJO_TITULO_EDAD)
    RUTA_SALIDA.parent.mkdir(exist_ok=True)
    tabla.to_csv(RUTA_SALIDA, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", RUTA_SALIDA.name, len(tabla))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(RUTA_SALIDA)
