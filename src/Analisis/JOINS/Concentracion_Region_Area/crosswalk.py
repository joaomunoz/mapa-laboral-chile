"""
<src/Analisis/JOINS/Concentracion_Region_Area/crosswalk.py>

Mide qué áreas de estudio concentra cada región. Es la capa secundaria del mapa.

Salida: Salida/concentracion_region_area.csv

Decisiones (aprobadas el 02-11-26):
  - Se compara el peso del área dentro de cada región con su peso nacional. Contar personas no sirve: la
    Metropolitana ganaría en todas las áreas solo por ser la más poblada.
  - Región de residencia: es la única que informa CASEN. Por eso esta capa dice dónde viven los titulados.

Varianza: linealización de Taylor con varstrat y varunit, usando todo el diseño de la encuesta.
Filtro: n >= 60, gl >= 9 y CV <= 30 (poco fiable si CV > 15), igual que en los puentes.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from esquema import CONCENTRACION_REGION_AREA
import obtener

log = logging.getLogger(__name__)

RUTA_SALIDA = Path(__file__).parent / "Salida" / "concentracion_region_area.csv"
N_MINIMO, GL_MINIMO, CV_MAXIMO, CV_POCO_FIABLE = 60, 9, 30, 15
Z_95 = 1.96
N_REGIONES, N_AREAS = 16, 10
COBERTURA_MINIMA = 0.99


def varianza_total(valores: pd.Series, datos: pd.DataFrame, diseno: pd.DataFrame) -> float:
    """Varianza de un total: suma por conglomerado y compara dentro de cada estrato."""
    suma = datos.assign(y=valores).groupby(["varstrat", "varunit"], as_index=False)["y"].sum()
    g = diseno.merge(suma, how="left", on=["varstrat", "varunit"]).fillna({"y": 0.0})
    # Un estrato con un solo conglomerado no permite estimar varianza: no aporta.
    multiples = g[g["n_conglomerados"] > 1]
    media = multiples.groupby("varstrat")["y"].transform("mean")
    h = multiples["n_conglomerados"]
    return float((h / (h - 1) * (multiples["y"] - media) ** 2).sum())


def clasificar(n: int, gl: int, cv: float) -> str:
    if n < N_MINIMO or gl < GL_MINIMO or not np.isfinite(cv) or cv > CV_MAXIMO:
        return "no_fiable"
    return "poco_fiable" if cv > CV_POCO_FIABLE else "fiable"


def leer(fiabilidad: str, peso_min: float, peso_max: float) -> str:
    if fiabilidad == "no_fiable":
        return "sin_muestra"
    if peso_min > 1:
        return "concentra"
    return "bajo_lo_nacional" if peso_max < 1 else "similar"


def nombres_de_area(casen: pd.DataFrame, puente: pd.DataFrame) -> pd.Series:
    """Asigna a cada código de área su nombre más frecuente en P5, igual que en la tabla 2."""
    c = casen.dropna(subset=["cinef13_area"]).merge(puente, on=["e6a", "carrera_normalizada"], how="inner", validate="many_to_one")
    return c.groupby("cinef13_area")["area_cine_sies"].agg(lambda s: s.value_counts().index[0])


def construir(casen: pd.DataFrame, diseno: pd.DataFrame, nombres: pd.Series) -> pd.DataFrame:
    diseno = diseno.assign(n_conglomerados=diseno.groupby("varstrat")["varunit"].transform("size"))
    t = casen.dropna(subset=["cinef13_area"]).copy()
    t["area_cine"] = t["cinef13_area"].map(nombres)
    pct_nacional = 100 * t.groupby("area_cine")["expr"].sum() / t["expr"].sum()
    filas = []
    for (region, nombre), en_region in t.groupby(["codigo_region", "nombre_region"]):
        total_region = en_region["expr"].sum()
        for area in nombres:
            celda = en_region[en_region["area_cine"] == area]
            nac = pct_nacional[area]
            fila = {"codigo_region": region, "nombre_region": nombre, "area_cine": area, "pct_nacional": nac}
            if celda.empty:
                filas.append(fila | {"titulados": 0.0, "n_personas": 0, "gl": 0, "cv_pct": np.nan, "pct_en_region": 0.0, "pct_min": np.nan,
                                     "pct_max": np.nan, "peso_relativo": 0.0, "peso_min": np.nan, "peso_max": np.nan,
                                     "fiabilidad": "no_fiable", "lectura": "sin_muestra"})
                continue
            titulados = celda["expr"].sum()
            cv = 100 * varianza_total(celda["expr"], celda, diseno) ** 0.5 / titulados
            p = titulados / total_region
            en_celda = (en_region["area_cine"] == area).astype(float)
            ee = varianza_total(en_region["expr"] * (en_celda - p) / total_region, en_region, diseno) ** 0.5
            pct, pct_min, pct_max = 100 * p, 100 * max(p - Z_95 * ee, 0), 100 * min(p + Z_95 * ee, 1)
            gl = celda["varunit"].nunique() - celda["varstrat"].nunique()
            fiabilidad = clasificar(len(celda), gl, cv)
            filas.append(fila | {"titulados": titulados, "n_personas": len(celda), "gl": gl, "cv_pct": cv, "pct_en_region": pct,
                                 "pct_min": pct_min, "pct_max": pct_max, "peso_relativo": pct / nac, "peso_min": pct_min / nac,
                                 "peso_max": pct_max / nac, "fiabilidad": fiabilidad, "lectura": leer(fiabilidad, pct_min / nac, pct_max / nac)})
    return (pd.DataFrame(filas)[list(CONCENTRACION_REGION_AREA)].astype(CONCENTRACION_REGION_AREA)
            .sort_values(["codigo_region", "area_cine"]).reset_index(drop=True))


def validar(t: pd.DataFrame, casen: pd.DataFrame, areas_tabla_2: set[str]) -> None:
    """Detiene el proceso si la tabla no cuadra con CASEN o usa áreas distintas a la tabla 2."""
    validos = casen.dropna(subset=["cinef13_area"])
    cobertura = validos["expr"].sum() / casen["expr"].sum()
    con_casos = t[t["n_personas"] > 0]
    controles = {
        "160 filas con clave única": len(t) == N_REGIONES * N_AREAS and not t.duplicated(["codigo_region", "area_cine"]).any(),
        "Mismas áreas que la tabla 2": set(t["area_cine"]) == areas_tabla_2,
        "El área cubre al menos 99% de los titulados": cobertura >= COBERTURA_MINIMA,
        "Titulados iguales a CASEN": np.isclose(t["titulados"].sum(), validos["expr"].sum()),
        "pct_en_region suma 100 en cada región": np.isclose(t.groupby("codigo_region")["pct_en_region"].sum(), 100).all(),
        "pct_nacional suma 100 en cada región": np.isclose(t.groupby("codigo_region")["pct_nacional"].sum(), 100).all(),
        "El valor queda dentro de su rango": ((con_casos["pct_min"] <= con_casos["pct_en_region"]) & (con_casos["pct_en_region"] <= con_casos["pct_max"])).all(),
        "Lectura coherente con fiabilidad": (t["lectura"].eq("sin_muestra") == t["fiabilidad"].eq("no_fiable")).all(),
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    log.info("  [i] Titulados: %.0f; cobertura %.2f%%", validos["expr"].sum(), 100 * cobertura)
    log.info("  [i] Fiabilidad: %s; sin casos: %d", t["fiabilidad"].value_counts().to_dict(), (t["n_personas"] == 0).sum())
    log.info("  [i] Lectura: %s", t["lectura"].value_counts().to_dict())
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    casen = obtener.cargar_casen()
    nombres = nombres_de_area(casen, obtener.cargar_puente_carrera())
    tabla = construir(casen, obtener.cargar_diseno(), nombres)
    validar(tabla, casen, obtener.cargar_areas_tabla_2())
    RUTA_SALIDA.parent.mkdir(exist_ok=True)
    tabla.to_csv(RUTA_SALIDA, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", RUTA_SALIDA.name, len(tabla))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(RUTA_SALIDA)
