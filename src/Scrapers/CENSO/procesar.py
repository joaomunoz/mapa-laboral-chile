"""
<src/Scrapers/CENSO/procesar.py>

Resume los microdatos del Censo 2024 en una tabla agregada por región, actividad y nivel.

Entrada: Entrada/personas_censo2024.parquet (requiere pyarrow: ejecutar con .venv/bin/python)
Salida:  Salida/censo_procesado.csv

Decisiones (aprobadas el 02-11-26):
  - Quien trabaja en varias comunas queda sin región de trabajo, igual que en la matriz de conmutación del
    INE. Asignarle su región de residencia supondría que trabaja ahí. Afecta sobre todo a Transporte y
    Construcción, y p44_lug_trab permite medirlo.
  - Región de trabajo: según el manual, se obtiene del código de comuna dividido por 1.000. Se exige un código
    de comuna: con p44 = 3, los códigos menores son -99; con p44 = 4 son continentes y con p44 = 5, el 998.
  - Se excluyen las variables sensibles: el mapa no las necesita.

Los totales de control vienen del diccionario del manual de microdatos del INE.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comun.normalizador import REGIONES  # noqa: E402
sys.path.insert(0, str(Path(__file__).parent))
from esquema import ESQUEMA_CENSO  # noqa: E402
import obtener  # noqa: E402

log = logging.getLogger(__name__)

RUTA_SALIDA = Path(__file__).parent / "Salida" / "censo_procesado.csv"
COLUMNAS_ENTRADA = ["region", "sit_fuerza_trabajo", "cod_caenes", "cine11", "p44_lug_trab", "p44_lug_trab_esp"]
SIN_RESPUESTA = -99
ACTIVIDAD_SIN_DATO = ["999", "-99"]
P44_EN_CHILE = [1, 2, 3]
P44_VARIAS_COMUNAS = 5
CODIGO_COMUNA_MINIMO, DIVISOR_COMUNA = 1000, 1000
NIVEL_POR_CINE = {8: "Tecnico", 9: "Profesional", 10: "Profesional", 11: "Profesional"}
CLAVES = [c for c in ESQUEMA_CENSO if c not in ("nombre_region", "personas")]
N_REGIONES = 16
# Diccionario de personas del manual de microdatos Censo 2024.
TOTALES_MANUAL = {"personas_15_o_mas": 15_205_784, "ocupados": 8_277_501, "desocupados": 777_920, "fuera_fuerza": 6_060_837,
                  "sit_sin_respuesta": 89_526, "mineria": 275_517, "varias_comunas": 460_346}


def preparar(crudo: pd.DataFrame) -> pd.DataFrame:
    """Normaliza códigos y nombres, y deja una fila por persona de 15 años o más."""
    d = crudo[crudo["sit_fuerza_trabajo"].notna()].copy()
    en_chile = d["p44_lug_trab"].isin(P44_EN_CHILE) & (d["p44_lug_trab_esp"] >= CODIGO_COMUNA_MINIMO)
    d["codigo_region_trabajo"] = np.where(en_chile, np.trunc(d["p44_lug_trab_esp"] / DIVISOR_COMUNA), np.nan)
    d["codigo_region"] = d["region"]
    d["actividad_ciiu"] = d["cod_caenes"].where(~d["cod_caenes"].isin(ACTIVIDAD_SIN_DATO))
    d["nivel_titulo"] = d["cine11"].map(NIVEL_POR_CINE).fillna("Sin_titulo").where(d["cine11"] != SIN_RESPUESTA)
    for columna in ["sit_fuerza_trabajo", "p44_lug_trab"]:
        d[columna] = d[columna].where(d[columna] != SIN_RESPUESTA)
    return d


def agregar(d: pd.DataFrame) -> pd.DataFrame:
    """Suma personas por combinación, conservando las columnas vacías como un grupo más."""
    t = d.groupby(CLAVES, dropna=False).size().rename("personas").reset_index()
    t["nombre_region"] = t["codigo_region"].map(REGIONES)
    return t[list(ESQUEMA_CENSO)].astype(ESQUEMA_CENSO).sort_values(CLAVES).reset_index(drop=True)


def validar(t: pd.DataFrame) -> None:
    """Detiene el proceso si la tabla no reproduce los totales del INE o rompe la regla de región de trabajo."""
    suma = lambda filtro: int(t.loc[filtro, "personas"].sum())
    sit = t["sit_fuerza_trabajo"]
    ocupados = sit == 1
    sin_region = t["codigo_region_trabajo"].isna()
    misma_comuna = t["p44_lug_trab"].isin([1, 2]).fillna(False)
    controles = {
        "Clave única": not t.duplicated(CLAVES, keep=False).any(),
        "Regiones 1-16 con nombre": t["codigo_region"].nunique() == N_REGIONES and t["nombre_region"].notna().all(),
        "Región de trabajo entre 1 y 16": t["codigo_region_trabajo"].dropna().between(1, N_REGIONES).all(),
        "Total de 15 años o más igual al manual": int(t["personas"].sum()) == TOTALES_MANUAL["personas_15_o_mas"],
        "Ocupados iguales al manual": suma(ocupados) == TOTALES_MANUAL["ocupados"],
        "Desocupados iguales al manual": suma(sit == 2) == TOTALES_MANUAL["desocupados"],
        "Fuera de la fuerza de trabajo igual al manual": suma(sit == 3) == TOTALES_MANUAL["fuera_fuerza"],
        "Sin respuesta igual al manual": suma(sit.isna()) == TOTALES_MANUAL["sit_sin_respuesta"],
        "Minería igual al manual": suma(t["actividad_ciiu"] == "B") == TOTALES_MANUAL["mineria"],
        "Varias comunas iguales al manual": suma(t["p44_lug_trab"] == P44_VARIAS_COMUNAS) == TOTALES_MANUAL["varias_comunas"],
        "Solo los ocupados tienen actividad y región de trabajo": t.loc[~ocupados.fillna(False), ["actividad_ciiu", "codigo_region_trabajo"]].isna().all().all(),
        "Quien trabaja en su comuna tiene región igual a la de residencia": (t.loc[misma_comuna, "codigo_region_trabajo"] == t.loc[misma_comuna, "codigo_region"]).all(),
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    log.info("  [i] Ocupados con región de trabajo: %d (%.2f%%); con región y actividad: %d (%.2f%%)",
             suma(ocupados & ~sin_region), 100 * suma(ocupados & ~sin_region) / suma(ocupados),
             suma(ocupados & ~sin_region & t["actividad_ciiu"].notna()), 100 * suma(ocupados & ~sin_region & t["actividad_ciiu"].notna()) / suma(ocupados))
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


def procesar_censo() -> Path:
    crudo = pd.read_parquet(obtener.obtener(), columns=COLUMNAS_ENTRADA)
    tabla = agregar(preparar(crudo))
    validar(tabla)
    RUTA_SALIDA.parent.mkdir(exist_ok=True)
    tabla.to_csv(RUTA_SALIDA, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", RUTA_SALIDA.name, len(tabla))
    return RUTA_SALIDA


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ruta = procesar_censo()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(ruta)
