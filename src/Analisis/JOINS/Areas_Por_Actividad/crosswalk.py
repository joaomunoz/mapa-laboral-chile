"""
<src/Analisis/JOINS/Areas_Por_Actividad/crosswalk.py>
Actualizado 02-11-26 21:22

Mide qué áreas de estudio se vinculan a cada actividad económica, a nivel nacional.

Salida: Salida/areas_por_actividad.csv

Decisiones:
  - Nivel nacional: la región de CASEN es la de residencia, así que no se puede leer como lugar de trabajo.
  - Área según cinef13_area, no según la carrera asignada en P5: cubre a casi todos los titulados, mientras
    que P5 deja fuera a quienes no se asignan a una carrera.
  - Nombre del área: CASEN solo trae el código. Se toma el nombre más frecuente en P5 para cada código, y se
    exige que exista en Titulados. No hay tabla oficial de equivalencia.

Varianza: linealización de Taylor con varstrat y varunit, usando todo el diseño de la encuesta.
Filtro: n >= 60, gl >= 9 y CV <= 30 (poco fiable si CV > 15), igual que en los puentes.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from esquema import AREAS_POR_ACTIVIDAD
import obtener

log = logging.getLogger(__name__)

RUTA_SALIDA = Path(__file__).parent / "Salida" / "areas_por_actividad.csv"
N_MINIMO, GL_MINIMO, CV_MAXIMO, CV_POCO_FIABLE = 60, 9, 30, 15
Z_95 = 1.96
N_ACTIVIDADES, N_AREAS = 21, 10
COINCIDENCIA_MINIMA, COBERTURA_MINIMA = 0.98, 0.99


def varianza_total(valores: pd.Series, datos: pd.DataFrame, diseno: pd.DataFrame) -> float:
    """Varianza de un total: suma por conglomerado y compara dentro de cada estrato."""
    suma = datos.assign(y=valores).groupby(["varstrat", "varunit"], as_index=False)["y"].sum()
    g = diseno.merge(suma, how="left", on=["varstrat", "varunit"]).fillna({"y": 0.0})
    # Un estrato con un solo conglomerado no permite estimar varianza: no aporta.
    multiples = g[g["n_conglomerados"] > 1]
    media = multiples.groupby("varstrat")["y"].transform("mean")
    h = multiples["n_conglomerados"]
    return float((h / (h - 1) * (multiples["y"] - media) ** 2).sum())


def proporcion(dominio: pd.DataFrame, en_celda: pd.Series, diseno: pd.DataFrame) -> tuple[float, float, float]:
    """Proporción dentro de un dominio, en %, con su rango 95%."""
    total = dominio["expr"].sum()
    p = dominio.loc[en_celda, "expr"].sum() / total
    ee = varianza_total(dominio["expr"] * (en_celda.astype(float) - p) / total, dominio, diseno) ** 0.5
    return 100 * p, 100 * max(p - Z_95 * ee, 0), 100 * min(p + Z_95 * ee, 1)


def clasificar(n: int, gl: int, cv: float) -> str:
    if n < N_MINIMO or gl < GL_MINIMO or not np.isfinite(cv) or cv > CV_MAXIMO:
        return "no_fiable"
    return "poco_fiable" if cv > CV_POCO_FIABLE else "fiable"


def nombres_de_area(casen: pd.DataFrame, puente: pd.DataFrame) -> tuple[pd.Series, float]:
    """Asigna a cada código de área su nombre más frecuente en P5, e informa cuánto coinciden."""
    c = casen.dropna(subset=["cinef13_area"]).merge(puente, on=["e6a", "carrera_normalizada"], how="inner", validate="many_to_one")
    nombres = c.groupby("cinef13_area")["area_cine_sies"].agg(lambda s: s.value_counts().index[0])
    return nombres, float((c["area_cine_sies"] == c["cinef13_area"].map(nombres)).mean())


def construir(casen: pd.DataFrame, diseno: pd.DataFrame, actividades: pd.DataFrame, nombres: pd.Series) -> pd.DataFrame:
    diseno = diseno.assign(n_conglomerados=diseno.groupby("varstrat")["varunit"].transform("size"))
    o = casen[casen["titulo_comun"].notna() & (casen["activ"] == 1)].dropna(subset=["rama1", "cinef13_area"]).copy()
    o["actividad_caenes"] = o["rama1"].astype(int)
    o["area_cine"] = o["cinef13_area"].map(nombres)
    filas = []
    for actividad in range(1, N_ACTIVIDADES + 1):
        en_actividad = o[o["actividad_caenes"] == actividad]
        for area in nombres:
            en_area = o[o["area_cine"] == area]
            celda = en_actividad[en_actividad["area_cine"] == area]
            fila = {"actividad_caenes": actividad, "area_cine": area}
            if celda.empty:
                filas.append(fila | {"ocupados_titulados": 0.0, "n_personas": 0, "gl": 0, "cv_pct": np.nan,
                                     "pct_en_actividad": 0.0, "pct_en_actividad_min": np.nan, "pct_en_actividad_max": np.nan,
                                     "pct_en_area": 0.0, "pct_en_area_min": np.nan, "pct_en_area_max": np.nan, "fiabilidad": "no_fiable"})
                continue
            total = celda["expr"].sum()
            cv = 100 * varianza_total(celda["expr"], celda, diseno) ** 0.5 / total
            gl = celda["varunit"].nunique() - celda["varstrat"].nunique()
            pa, pa_min, pa_max = proporcion(en_actividad, en_actividad["area_cine"] == area, diseno)
            pr, pr_min, pr_max = proporcion(en_area, en_area["actividad_caenes"] == actividad, diseno)
            filas.append(fila | {"ocupados_titulados": total, "n_personas": len(celda), "gl": gl, "cv_pct": cv,
                                 "pct_en_actividad": pa, "pct_en_actividad_min": pa_min, "pct_en_actividad_max": pa_max,
                                 "pct_en_area": pr, "pct_en_area_min": pr_min, "pct_en_area_max": pr_max,
                                 "fiabilidad": clasificar(len(celda), gl, cv)})
    t = pd.DataFrame(filas).merge(actividades, on="actividad_caenes", validate="many_to_one")
    return (t[list(AREAS_POR_ACTIVIDAD)].astype(AREAS_POR_ACTIVIDAD)
            .sort_values(["actividad_caenes", "ocupados_titulados"], ascending=[True, False]).reset_index(drop=True))


def validar(t: pd.DataFrame, casen: pd.DataFrame, nombres: pd.Series, coincidencia: float, areas_titulados: set[str]) -> None:
    """Detiene el proceso si la tabla no cuadra con CASEN o si las áreas no calzan con Titulados."""
    ocupados = casen[casen["titulo_comun"].notna() & (casen["activ"] == 1)]
    validos = ocupados.dropna(subset=["rama1", "cinef13_area"])
    cobertura = validos["expr"].sum() / ocupados["expr"].sum()
    por_actividad = t.groupby("actividad_caenes")["pct_en_actividad"].sum()
    por_area = t.groupby("area_cine")["pct_en_area"].sum()
    con_casos = t[t["n_personas"] > 0]
    controles = {
        "210 filas con clave única": len(t) == N_ACTIVIDADES * N_AREAS and not t.duplicated(["actividad_caenes", "area_cine"]).any(),
        "10 áreas distintas, todas presentes en Titulados": nombres.nunique() == N_AREAS and set(nombres) <= areas_titulados,
        "Código y nombre de área coinciden en al menos 98%": coincidencia >= COINCIDENCIA_MINIMA,
        "Actividad y área cubren al menos 99% de los titulados ocupados": cobertura >= COBERTURA_MINIMA,
        "Ocupados iguales a CASEN": np.isclose(t["ocupados_titulados"].sum(), validos["expr"].sum()),
        "pct_en_actividad suma 100 en cada actividad con casos": np.isclose(por_actividad[por_actividad > 0], 100).all(),
        "pct_en_area suma 100 en cada área": np.isclose(por_area, 100).all(),
        "El valor queda dentro de su rango": ((con_casos["pct_en_actividad_min"] <= con_casos["pct_en_actividad"]) & (con_casos["pct_en_actividad"] <= con_casos["pct_en_actividad_max"])
                                              & (con_casos["pct_en_area_min"] <= con_casos["pct_en_area"]) & (con_casos["pct_en_area"] <= con_casos["pct_en_area_max"])).all(),
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    log.info("  [i] Titulados ocupados: %.0f; cobertura %.2f%%; coincidencia de áreas %.2f%%", validos["expr"].sum(), 100 * cobertura, 100 * coincidencia)
    log.info("  [i] Fiabilidad: %s; sin casos: %d", t["fiabilidad"].value_counts().to_dict(), (t["n_personas"] == 0).sum())
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    casen = obtener.cargar_casen()
    nombres, coincidencia = nombres_de_area(casen[casen["titulo_comun"].notna()], obtener.cargar_puente_carrera())
    tabla = construir(casen, obtener.cargar_diseno(), obtener.cargar_actividades(), nombres)
    validar(tabla, casen, nombres, coincidencia, obtener.cargar_areas_titulados())
    RUTA_SALIDA.parent.mkdir(exist_ok=True)
    tabla.to_csv(RUTA_SALIDA, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", RUTA_SALIDA.name, len(tabla))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(RUTA_SALIDA)
