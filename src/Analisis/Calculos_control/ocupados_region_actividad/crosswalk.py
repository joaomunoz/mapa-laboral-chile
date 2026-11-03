"""
<src/Analisis/Calculos_control/ocupados_region_actividad/crosswalk.py>
Actualizado 02-11-26 16:40

Calcula cuántos ocupados tiene cada actividad en cada región, con todos los niveles educativos.

Salida: Salida/ocupados_region_actividad.csv, con dos versiones: por residencia y por región de trabajo

Por qué todos y no solo titulados: la celda típica con 10 meses tiene 167 personas frente a 45
de titulados, y mide igual de bien el peso dla actividad (idea del usuario, 02-11-26). Con ella, el
reparto carrera × actividad mejoró en la prueba de región oculta. Alimenta a
JOINS/CW_Ocupados_Carrera_Region_Actividad.
"""

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers"))
from comun.normalizador import REGIONES  # noqa: E402
import obtener  # noqa: E402
from esquema import OCUPADOS_REGION_ACTIVIDAD  # noqa: E402

log = logging.getLogger(__name__)
RUTA = Path(__file__).parent / "Salida" / "ocupados_region_actividad.csv"
FACTOR_10_MESES, N_MINIMO, GL_MINIMO = 3 / 10, 60, 9


def por_base(o: pd.DataFrame, base: str, col: str) -> pd.DataFrame:
    """Calcula la tabla para una definición de región; quien no informa región de trabajo queda fuera."""
    x = o.dropna(subset=[col]).assign(codigo_region=lambda d: d[col].astype(int))
    t = x.groupby(["codigo_region", "actividad_caenes"], as_index=False).agg(
        suma=("fact_cal", "sum"), n_personas=("idrph", "nunique"), psu=("conglomerado", "nunique"), h=("estrato", "nunique"))
    t["ocupados"] = t["suma"] * FACTOR_10_MESES
    t["gl"] = t["psu"] - t["h"]
    t["fiable_n_gl"] = (t["n_personas"] >= N_MINIMO) & (t["gl"] >= GL_MINIMO)
    t["pct_en_region"] = 100 * t["ocupados"] / t.groupby("codigo_region")["ocupados"].transform("sum")
    t["pct_nacional"] = 100 * t.groupby("actividad_caenes")["ocupados"].transform("sum") / t["ocupados"].sum()
    t["peso_relativo"] = t["pct_en_region"] / t["pct_nacional"]
    return t.assign(base_region=base)


def construir() -> pd.DataFrame:
    ene, actividades = obtener.cargar()
    o = ene[ene["cae_especifico"].between(1, 7)].dropna(subset=["r_p_rev4cl_caenes"]).rename(columns={"r_p_rev4cl_caenes": "actividad_caenes"})
    t = pd.concat([por_base(o, "residencia", "codigo_region"), por_base(o, "trabajo", "codigo_region_trabajo")], ignore_index=True)
    t["nombre_region"] = t["codigo_region"].map(REGIONES)
    t = t.merge(actividades, on="actividad_caenes")
    return t[list(OCUPADOS_REGION_ACTIVIDAD)].astype(OCUPADOS_REGION_ACTIVIDAD).sort_values(["base_region", "codigo_region", "actividad_caenes"])


def validar(t: pd.DataFrame) -> None:
    res, tra = t[t["base_region"] == "residencia"], t[t["base_region"] == "trabajo"]
    controles = {"Clave única": not t.duplicated(["base_region", "codigo_region", "actividad_caenes"]).any(),
                 "Regiones 1-16 en ambas bases": res["codigo_region"].nunique() == 16 and tra["codigo_region"].nunique() == 16,
                 "pct_en_region suma 100": np.isclose(t.groupby(["base_region", "codigo_region"])["pct_en_region"].sum(), 100).all(),
                 "Pesos relativos positivos": (t["peso_relativo"] > 0).all(), "Total entre 9 y 10 millones": 9e6 < res["ocupados"].sum() < 1e7,
                 "Región de trabajo cubre 99% de los ocupados": tra["ocupados"].sum() >= 0.99 * res["ocupados"].sum()}
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    if not all(controles.values()):
        raise ValueError("Validaciones fallidas")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    tabla = construir()
    validar(tabla)
    RUTA.parent.mkdir(exist_ok=True)
    tabla.to_csv(RUTA, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas, %.0f ocupados)", RUTA.name, len(tabla), tabla.loc[tabla["base_region"] == "residencia", "ocupados"].sum())
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(RUTA)
