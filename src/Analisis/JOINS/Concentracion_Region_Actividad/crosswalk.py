"""
<src/Analisis/JOINS/Concentracion_Region_Actividad/crosswalk.py>

Mide qué actividades económicas concentra cada región con ENE, con su margen de error. Es el contraste de la
tabla del censo (Concentracion_Region_Actividad_Censo), que es la capa principal del mapa.

Salida: Salida/concentracion_region_actividad.csv

Decisiones (aprobadas el 02-11-26):
  - Todos los ocupados: describen mejor la economía regional y dan más casos que usar solo titulados.
  - Periodo (08-11-26): los meses del censo, marzo a julio de 2024 (comun/periodos.py), para que la diferencia
    entre fuentes no se deba a la fecha. Antes usaba 10 meses de 2025-2026. El cuadre con INE se hace sobre
    mayo a julio de 2024.
  - Quien no informa región de trabajo o actividad queda fuera: asignarle una región sería un supuesto, y
    así la tabla coincide con la de control.

Varianza: linealización de Taylor con estrato y conglomerado. Se usa todo el diseño de ENE, incluso los
conglomerados sin casos en la celda; omitirlos subestimaría el error.
Filtro: n >= 60, gl >= 9 y CV <= 30 (poco fiable si CV > 15), igual que en los puentes.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers"))
from comun.normalizador import REGIONES  # noqa: E402
from comun.periodos import FACTOR_CONTRASTE, MESES_BOLETIN_CONTRASTE, OCUPADOS_INE_CONTRASTE  # noqa: E402
from esquema import CONCENTRACION_REGION_ACTIVIDAD  # noqa: E402
import obtener  # noqa: E402

log = logging.getLogger(__name__)

RUTA_SALIDA = Path(__file__).parent / "Salida" / "concentracion_region_actividad.csv"
N_MINIMO, GL_MINIMO, CV_MAXIMO, CV_POCO_FIABLE = 60, 9, 30, 15
Z_95 = 1.96
TOLERANCIA_INE = 0.001
COBERTURA_MINIMA = 0.99
N_REGIONES, N_ACTIVIDADES = 16, 21


def varianza_total(valores: pd.Series, datos: pd.DataFrame, diseno: pd.DataFrame) -> float:
    """Varianza de un total: suma por conglomerado y compara dentro de cada estrato."""
    suma = datos.assign(y=valores).groupby(["estrato", "conglomerado"], as_index=False)["y"].sum()
    g = diseno.merge(suma, how="left", on=["estrato", "conglomerado"]).fillna({"y": 0.0})
    # Un estrato con un solo conglomerado no permite estimar varianza: no aporta.
    multiples = g[g["n_conglomerados"] > 1]
    media = multiples.groupby("estrato")["y"].transform("mean")
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


def construir(ene: pd.DataFrame, actividades: pd.DataFrame) -> pd.DataFrame:
    diseno = ene[["estrato", "conglomerado"]].drop_duplicates()
    diseno = diseno.assign(n_conglomerados=diseno.groupby("estrato")["conglomerado"].transform("size"))

    o = ene[ene["cae_especifico"].between(1, 7)].dropna(subset=["codigo_region_trabajo", "r_p_rev4cl_caenes"]).copy()
    o["codigo_region"] = o["codigo_region_trabajo"].astype(int)
    o["actividad_caenes"] = o["r_p_rev4cl_caenes"].astype(int)
    o["peso"] = o["fact_cal"] * FACTOR_CONTRASTE
    pct_nacional = 100 * o.groupby("actividad_caenes")["peso"].sum() / o["peso"].sum()

    filas = []
    for region, en_region in o.groupby("codigo_region"):
        total_region = en_region["peso"].sum()
        for actividad in range(1, N_ACTIVIDADES + 1):
            celda = en_region[en_region["actividad_caenes"] == actividad]
            fila = {"codigo_region": region, "actividad_caenes": actividad, "pct_nacional": pct_nacional.get(actividad, np.nan)}
            if celda.empty:
                filas.append(fila | {"ocupados": 0.0, "n_personas": 0, "gl": 0, "cv_pct": np.nan, "pct_en_region": 0.0,
                                     "pct_min": np.nan, "pct_max": np.nan, "peso_relativo": 0.0, "peso_min": np.nan,
                                     "peso_max": np.nan, "fiabilidad": "no_fiable", "lectura": "sin_muestra"})
                continue
            ocupados = celda["peso"].sum()
            cv = 100 * varianza_total(celda["peso"], celda, diseno) ** 0.5 / ocupados
            p = ocupados / total_region
            en_actividad = (en_region["actividad_caenes"] == actividad).astype(float)
            ee = varianza_total(en_region["peso"] * (en_actividad - p) / total_region, en_region, diseno) ** 0.5
            pct, pct_min, pct_max = 100 * p, 100 * max(p - Z_95 * ee, 0), 100 * min(p + Z_95 * ee, 1)
            nac = fila["pct_nacional"]
            n = celda["idrph"].nunique()
            gl = celda["conglomerado"].nunique() - celda["estrato"].nunique()
            fiabilidad = clasificar(n, gl, cv)
            filas.append(fila | {"ocupados": ocupados, "n_personas": n, "gl": gl, "cv_pct": cv, "pct_en_region": pct,
                                 "pct_min": pct_min, "pct_max": pct_max, "peso_relativo": pct / nac, "peso_min": pct_min / nac,
                                 "peso_max": pct_max / nac, "fiabilidad": fiabilidad,
                                 "lectura": leer(fiabilidad, pct_min / nac, pct_max / nac)})
    t = pd.DataFrame(filas).merge(actividades, on="actividad_caenes", validate="many_to_one")
    t["nombre_region"] = t["codigo_region"].map(REGIONES)
    return (t[list(CONCENTRACION_REGION_ACTIVIDAD)].astype(CONCENTRACION_REGION_ACTIVIDAD)
            .sort_values(["codigo_region", "actividad_caenes"]).reset_index(drop=True))


def validar(t: pd.DataFrame, ene: pd.DataFrame, control: pd.DataFrame) -> None:
    """Detiene el proceso si la tabla no cuadra con INE ni con la tabla de control."""
    trim = ene[ene["mes"].isin(MESES_BOLETIN_CONTRASTE) & ene["cae_especifico"].between(1, 7)]
    trim_validos = trim.dropna(subset=["codigo_region_trabajo", "r_p_rev4cl_caenes"])
    total_trim, validos_trim = trim["fact_cal"].sum(), trim_validos["fact_cal"].sum()
    comparacion = t[t["n_personas"] > 0].merge(control, on=["codigo_region", "actividad_caenes"], how="outer", suffixes=("", "_control"), indicator=True)
    con_casos = t[t["n_personas"] > 0]
    lecturas_ok = (t.loc[t["fiabilidad"] == "no_fiable", "lectura"] == "sin_muestra").all() and (t.loc[t["fiabilidad"] != "no_fiable", "lectura"] != "sin_muestra").all()
    controles = {
        "336 filas con clave única": len(t) == N_REGIONES * N_ACTIVIDADES and not t.duplicated(["codigo_region", "actividad_caenes"]).any(),
        "Actividades y regiones con nombre": t[["nombre_region", "actividad_ciiu", "actividad_glosa"]].notna().all().all(),
        "Ocupados de mayo a julio de 2024 cuadran con INE (desv. < 0,1%)": abs(total_trim / OCUPADOS_INE_CONTRASTE - 1) < TOLERANCIA_INE,
        "Región y actividad cubren al menos 99% del trimestre": validos_trim / total_trim >= COBERTURA_MINIMA,
        "pct_en_region suma 100 en cada región": np.isclose(t.groupby("codigo_region")["pct_en_region"].sum(), 100).all(),
        "pct_nacional suma 100 por región": np.isclose(t.groupby("codigo_region")["pct_nacional"].sum(), 100).all(),
        "El valor queda dentro de su rango": ((con_casos["pct_min"] <= con_casos["pct_en_region"]) & (con_casos["pct_en_region"] <= con_casos["pct_max"])).all(),
        "Ocupados iguales a la tabla de control": (comparacion["_merge"] == "both").all() and np.isclose(comparacion["ocupados"], comparacion["ocupados_control"]).all(),
        "Lectura coherente con fiabilidad": lecturas_ok,
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    log.info("  [i] Mayo a julio de 2024: %.0f ocupados frente a %d de INE (%.3f%%); con región y actividad %.0f (%.2f%%)",
             total_trim, OCUPADOS_INE_CONTRASTE, 100 * (total_trim / OCUPADOS_INE_CONTRASTE - 1), validos_trim, 100 * validos_trim / total_trim)
    log.info("  [i] Lectura: %s", t["lectura"].value_counts().to_dict())
    log.info("  [i] Sin casos en la encuesta: %d", (t["n_personas"] == 0).sum())
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ene = obtener.cargar_ene()
    tabla = construir(ene, obtener.cargar_actividades())
    validar(tabla, ene, obtener.cargar_control())
    RUTA_SALIDA.parent.mkdir(exist_ok=True)
    tabla.to_csv(RUTA_SALIDA, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", RUTA_SALIDA.name, len(tabla))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(RUTA_SALIDA)
