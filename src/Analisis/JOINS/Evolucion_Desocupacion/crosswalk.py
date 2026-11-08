"""
<src/Analisis/JOINS/Evolucion_Desocupacion/crosswalk.py>

Mide cómo cambió la tasa de desocupación entre marzo a julio de 2024 y los mismos meses de 2026, con ENE.

Salida: Salida/evolucion_desocupacion.csv

Decisiones (aprobadas el 08-11-26):
  - ENE contra ENE, nunca censo menos ENE: dos fuentes distintas difieren también por cómo preguntan.
  - Los mismos meses en ambos años (comun/periodos.py), para que la estacionalidad no cuente como cambio.
  - Solo la tasa de desocupación: es lo que responde la pregunta del mapa.
  - Chile, regiones y Chile por nivel de título. Región por nivel queda fuera por falta de muestra.
  - Los dos años se tratan como muestras independientes: entre ambos pasan 24 meses y una vivienda deja la
    muestra antes. Si se repiten conglomerados, la covarianza es positiva y el rango real sería más angosto;
    el que se publica es prudente.
  - "sube" o "baja" solo si el rango entero queda sobre o bajo cero, con el valor redondeado a 1 decimal que
    se publica (la misma regla del peso relativo en el mapa).

Varianza: linealización de Taylor con estrato y conglomerado, usando todo el diseño de cada año.
Fiabilidad de cada año medida sobre los desocupados: n >= 60, gl >= 9 y CV <= 30 (poco fiable si CV > 15).
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers"))
from comun.normalizador import REGIONES  # noqa: E402
from comun.periodos import MESES_ACTUAL, MESES_CONTRASTE  # noqa: E402
from esquema import EVOLUCION_DESOCUPACION  # noqa: E402
import obtener  # noqa: E402

log = logging.getLogger(__name__)

RUTA_SALIDA = Path(__file__).parent / "Salida" / "evolucion_desocupacion.csv"
ANIOS = (2024, 2026)
NIVEL_POR_CINE = {3: "Tecnico", 4: "Profesional", 5: "Profesional", 6: "Profesional"}  # Igual que Fuerza_Trabajo_Region_Nivel
NIVELES = ["Profesional", "Tecnico", "Sin_titulo"]
N_MINIMO, GL_MINIMO, CV_MAXIMO, CV_POCO_FIABLE = 60, 9, 30, 15
ORDEN_FIABILIDAD = ["fiable", "poco_fiable", "no_fiable"]
Z_95 = 1.96
DECIMALES = 1
N_REGIONES = 16


def diseno(ene: pd.DataFrame) -> pd.DataFrame:
    d = ene[["estrato", "conglomerado"]].drop_duplicates()
    return d.assign(n_conglomerados=d.groupby("estrato")["conglomerado"].transform("size"))


def tasa_con_error(celda: pd.DataFrame, dis: pd.DataFrame) -> tuple[float, float]:
    """Tasa de desocupación de un dominio y su coeficiente de variación (misma fórmula que Fuerza_Trabajo_Region_Nivel)."""
    peso, desocupado = celda["fact_cal"], celda["cae_especifico"].isin([8, 9]).astype(float)
    total = peso.sum()
    tasa = (peso * desocupado).sum() / total
    if tasa == 0:
        return 0.0, np.nan
    y = celda.assign(y=peso * (desocupado - tasa) / total).groupby(["estrato", "conglomerado"], as_index=False)["y"].sum()
    g = dis.merge(y, how="left", on=["estrato", "conglomerado"]).fillna({"y": 0.0})
    # Un estrato con un solo conglomerado no permite estimar varianza: no aporta.
    g = g[g["n_conglomerados"] > 1]
    media = g.groupby("estrato")["y"].transform("mean")
    varianza = (g["n_conglomerados"] / (g["n_conglomerados"] - 1) * (g["y"] - media) ** 2).sum()
    return 100 * tasa, 100 * varianza ** 0.5 / tasa


def clasificar(n: int, gl: int, cv: float) -> str:
    if n < N_MINIMO or gl < GL_MINIMO or not np.isfinite(cv) or cv > CV_MAXIMO:
        return "no_fiable"
    return "poco_fiable" if cv > CV_POCO_FIABLE else "fiable"


def medir(celda: pd.DataFrame, dis: pd.DataFrame) -> dict:
    tasa, cv = tasa_con_error(celda, dis)
    desocupados = celda[celda["cae_especifico"].isin([8, 9])]
    n = desocupados["idrph"].nunique()
    gl = desocupados["conglomerado"].nunique() - desocupados["estrato"].nunique()
    return {"tasa": tasa, "cv": cv, "n": n, "fiabilidad": clasificar(n, gl, cv)}


def leer(fiabilidad: str, minimo: float, maximo: float) -> str:
    if fiabilidad == "no_fiable":
        return "no_fiable"
    if round(minimo, DECIMALES) > 0:
        return "sube"
    return "baja" if round(maximo, DECIMALES) < 0 else "sin_cambio_claro"


def construir(ene: dict[int, pd.DataFrame]) -> pd.DataFrame:
    fuerza, disenos = {}, {}
    for anio, e in ene.items():
        disenos[anio] = diseno(e)
        f = e[e["cae_especifico"].between(1, 9)].copy()
        f["nivel_titulo"] = f["cine11_1d"].map(lambda c: NIVEL_POR_CINE.get(int(c), "Sin_titulo") if pd.notna(c) else None)
        fuerza[anio] = f
    dominios = ([(None, "Chile", "Todos", lambda f: f)]
                + [(r, REGIONES[r], "Todos", lambda f, r=r: f[f["codigo_region"] == r]) for r in range(1, N_REGIONES + 1)]
                + [(None, "Chile", n, lambda f, n=n: f[f["nivel_titulo"] == n]) for n in NIVELES])
    filas = []
    for region, nombre, nivel, filtro in dominios:
        m = {anio: medir(filtro(fuerza[anio]), disenos[anio]) for anio in ANIOS}
        dif = m[2026]["tasa"] - m[2024]["tasa"]
        ee = np.hypot(*(m[a]["tasa"] * m[a]["cv"] / 100 for a in ANIOS))
        fiabilidad = max((m[a]["fiabilidad"] for a in ANIOS), key=ORDEN_FIABILIDAD.index)
        minimo, maximo = dif - Z_95 * ee, dif + Z_95 * ee
        filas.append({"codigo_region": region, "nombre_region": nombre, "nivel_titulo": nivel,
                      "tasa_2024": m[2024]["tasa"], "cv_2024": m[2024]["cv"], "n_desocupados_2024": m[2024]["n"],
                      "tasa_2026": m[2026]["tasa"], "cv_2026": m[2026]["cv"], "n_desocupados_2026": m[2026]["n"],
                      "diferencia_pp": dif, "diferencia_min": minimo, "diferencia_max": maximo,
                      "fiabilidad": fiabilidad, "lectura": leer(fiabilidad, minimo, maximo)})
    return pd.DataFrame(filas)[list(EVOLUCION_DESOCUPACION)].astype(EVOLUCION_DESOCUPACION)


def validar(t: pd.DataFrame, ene: dict[int, pd.DataFrame], niveles: pd.DataFrame) -> None:
    """Detiene el proceso si la tabla no cuadra con sus periodos o con la tabla de fuerza de trabajo."""
    chile = t[t["codigo_region"].isna() & (t["nivel_titulo"] == "Todos")].iloc[0]
    por_nivel = t[t["codigo_region"].isna() & (t["nivel_titulo"] != "Todos")].merge(niveles, on="nivel_titulo")
    controles = {
        "20 filas con clave única": len(t) == 1 + N_REGIONES + len(NIVELES) and not t.duplicated(["codigo_region", "nivel_titulo"]).any(),
        "Cada año tiene sus 5 meses": sorted(ene[2024]["mes"].unique()) == MESES_CONTRASTE and sorted(ene[2026]["mes"].unique()) == MESES_ACTUAL,
        "Tasas entre 0 y 100": t[["tasa_2024", "tasa_2026"]].stack().between(0, 100).all(),
        "Diferencia igual a 2026 menos 2024": np.allclose(t["diferencia_pp"], t["tasa_2026"] - t["tasa_2024"]),
        "La diferencia queda dentro de su rango": ((t["diferencia_min"] <= t["diferencia_pp"]) & (t["diferencia_pp"] <= t["diferencia_max"])).all(),
        "2024 por nivel igual a Fuerza_Trabajo_Region_Nivel": len(por_nivel) == len(NIVELES) and np.allclose(por_nivel["tasa_2024"], por_nivel["ene_tasa_nacional_nivel"]),
        "Chile: 8,6% en 2024 y 9,5% en 2026, sube": round(chile["tasa_2024"], 1) == 8.6 and round(chile["tasa_2026"], 1) == 9.5 and chile["lectura"] == "sube",
        "Las 20 cifras son fiables": (t["fiabilidad"] == "fiable").all(),
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    log.info("  [i] Lectura: %s", t["lectura"].value_counts().to_dict())
    log.info("  [i] Regiones que suben: %s", t.loc[t["codigo_region"].notna() & (t["lectura"] == "sube"), "nombre_region"].tolist())
    log.info("  [i] Regiones que bajan: %s", t.loc[t["codigo_region"].notna() & (t["lectura"] == "baja"), "nombre_region"].tolist())
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ene = obtener.cargar_ene()
    tabla = construir(ene)
    validar(tabla, ene, obtener.cargar_niveles())
    RUTA_SALIDA.parent.mkdir(exist_ok=True)
    tabla.to_csv(RUTA_SALIDA, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", RUTA_SALIDA.name, len(tabla))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(RUTA_SALIDA)
