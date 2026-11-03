"""
<src/Analisis/JOINS/Fuerza_Trabajo_Region_Nivel/crosswalk.py>

Cuenta ocupados y desocupados por región y nivel educativo con el Censo 2024, y contrasta la tasa con ENE.

Salida: Salida/fuerza_trabajo_region_nivel.csv

Decisiones (aprobadas el 03-11-26):
  - Censo como dato principal: tiene base en todas las regiones y niveles.
  - ENE como contraste: da tasas más altas (profesionales 8,1% frente a 6,3%). Puede influir la fecha y la forma de
    preguntar, sin comprobar. Las cifras no se mezclan.
  - Fiabilidad de ENE medida sobre los desocupados, porque de ellos depende la tasa: n >= 60, gl >= 9 y CV <= 30.
  - Nivel en ENE: cine11_1d 3 es técnico; 4, 5 y 6 son profesional, igual que nivel_titulo del censo.

Varianza: linealización de Taylor con estrato y conglomerado, usando todo el diseño de ENE.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers"))
from comun.normalizador import REGIONES  # noqa: E402
from esquema import FUERZA_TRABAJO_REGION_NIVEL  # noqa: E402
import obtener  # noqa: E402

log = logging.getLogger(__name__)

RUTA_SALIDA = Path(__file__).parent / "Salida" / "fuerza_trabajo_region_nivel.csv"
OCUPADO, DESOCUPADO, FUERA = 1, 2, 3
NIVELES = ["Profesional", "Tecnico", "Sin_titulo"]
NIVEL_POR_CINE = {3: "Tecnico", 4: "Profesional", 5: "Profesional", 6: "Profesional"}
N_REGIONES = 16
FACTOR_10_MESES = 3 / 10
N_MINIMO, GL_MINIMO, CV_MAXIMO, CV_POCO_FIABLE = 60, 9, 30, 15
# Diccionario de personas del manual de microdatos Censo 2024, menos quienes no informan nivel educativo.
OCUPADOS_MANUAL, DESOCUPADOS_MANUAL = 8_277_501, 777_920
DESOCUPADOS_PROFESIONALES, DESOCUPADOS_TECNICOS = 153_695, 86_385


def tabla_censo(censo: pd.DataFrame) -> pd.DataFrame:
    c = censo.dropna(subset=["nivel_titulo"])
    cuenta = lambda datos, region: datos.groupby([region, "nivel_titulo"])["personas"].sum()
    filas = pd.MultiIndex.from_product([sorted(REGIONES), NIVELES], names=["codigo_region", "nivel_titulo"])
    t = pd.DataFrame(index=filas)
    t["ocupados_residencia"] = cuenta(c[c["sit_fuerza_trabajo"] == OCUPADO], "codigo_region")
    trabajo = c[(c["sit_fuerza_trabajo"] == OCUPADO) & c["codigo_region_trabajo"].notna()].copy()
    trabajo["codigo_region"] = trabajo["codigo_region_trabajo"].astype(int)
    t["ocupados_trabajo"] = cuenta(trabajo, "codigo_region")
    t["desocupados"] = cuenta(c[c["sit_fuerza_trabajo"] == DESOCUPADO], "codigo_region")
    t["fuera_fuerza_trabajo"] = cuenta(c[c["sit_fuerza_trabajo"] == FUERA], "codigo_region")
    t = t.fillna(0).astype(int).reset_index()
    t["tasa_desocupacion"] = 100 * t["desocupados"] / (t["ocupados_residencia"] + t["desocupados"])
    nacional = t.groupby("nivel_titulo")[["ocupados_residencia", "desocupados"]].sum()
    t["tasa_nacional_nivel"] = t["nivel_titulo"].map(100 * nacional["desocupados"] / nacional.sum(axis=1))
    t["nombre_region"] = t["codigo_region"].map(REGIONES)
    return t


def tasa_con_error(celda: pd.DataFrame, diseno: pd.DataFrame) -> tuple[float, float]:
    """Tasa de desocupación de un dominio y su coeficiente de variación."""
    peso, desocupado = celda["peso"], celda["cae_especifico"].isin([8, 9]).astype(float)
    total = peso.sum()
    tasa = (peso * desocupado).sum() / total
    if tasa == 0:
        return 0.0, np.nan
    y = celda.assign(y=peso * (desocupado - tasa) / total).groupby(["estrato", "conglomerado"], as_index=False)["y"].sum()
    g = diseno.merge(y, how="left", on=["estrato", "conglomerado"]).fillna({"y": 0.0})
    # Un estrato con un solo conglomerado no permite estimar varianza: no aporta.
    g = g[g["n_conglomerados"] > 1]
    media = g.groupby("estrato")["y"].transform("mean")
    varianza = (g["n_conglomerados"] / (g["n_conglomerados"] - 1) * (g["y"] - media) ** 2).sum()
    return 100 * tasa, 100 * varianza ** 0.5 / tasa


def clasificar(n: int, gl: int, cv: float) -> str:
    if n < N_MINIMO or gl < GL_MINIMO or not np.isfinite(cv) or cv > CV_MAXIMO:
        return "no_fiable"
    return "poco_fiable" if cv > CV_POCO_FIABLE else "fiable"


def tabla_ene(ene: pd.DataFrame) -> pd.DataFrame:
    diseno = ene[["estrato", "conglomerado"]].drop_duplicates()
    diseno = diseno.assign(n_conglomerados=diseno.groupby("estrato")["conglomerado"].transform("size"))
    e = ene[ene["cae_especifico"].between(1, 9) & ene["cine11_1d"].notna()].copy()
    e["nivel_titulo"] = e["cine11_1d"].astype(int).map(NIVEL_POR_CINE).fillna("Sin_titulo")
    e["peso"] = e["fact_cal"] * FACTOR_10_MESES
    # Cuenta a todos, sin filtro de fiabilidad: a nivel nacional hay muestra de sobra.
    nacional = e.assign(desocupado=e["cae_especifico"].isin([8, 9]) * e["peso"]).groupby("nivel_titulo")[["desocupado", "peso"]].sum()
    tasa_nacional = 100 * nacional["desocupado"] / nacional["peso"]
    filas = []
    for (region, nivel), celda in e.groupby(["codigo_region", "nivel_titulo"]):
        desocupados = celda[celda["cae_especifico"].isin([8, 9])]
        tasa, cv = tasa_con_error(celda, diseno)
        gl = desocupados["conglomerado"].nunique() - desocupados["estrato"].nunique()
        filas.append({"codigo_region": region, "nivel_titulo": nivel, "ene_tasa_desocupacion": tasa, "ene_tasa_nacional_nivel": tasa_nacional[nivel],
                      "ene_fiabilidad": clasificar(desocupados["idrph"].nunique(), gl, cv)})
    return pd.DataFrame(filas)


def validar(t: pd.DataFrame, censo: pd.DataFrame) -> None:
    """Detiene el proceso si los totales no cuadran con el censo o el manual."""
    sin_nivel = censo["nivel_titulo"].isna()
    suma_sin_nivel = lambda sit: int(censo.loc[sin_nivel & (censo["sit_fuerza_trabajo"] == sit), "personas"].sum())
    nivel = lambda n: int(t.loc[t["nivel_titulo"] == n, "desocupados"].sum())
    region_nivel = t.set_index(["codigo_region", "nivel_titulo"])
    controles = {
        "48 filas con clave única": len(t) == N_REGIONES * len(NIVELES) and not t.duplicated(["codigo_region", "nivel_titulo"]).any(),
        "Ocupados más quienes no informan nivel igual al manual": int(t["ocupados_residencia"].sum()) + suma_sin_nivel(OCUPADO) == OCUPADOS_MANUAL,
        "Desocupados más quienes no informan nivel igual al manual": int(t["desocupados"].sum()) + suma_sin_nivel(DESOCUPADO) == DESOCUPADOS_MANUAL,
        "Profesionales y técnicos desocupados como en la medición previa": nivel("Profesional") == DESOCUPADOS_PROFESIONALES and nivel("Tecnico") == DESOCUPADOS_TECNICOS,
        "Ocupados con región de trabajo no superan a los ocupados": t["ocupados_trabajo"].sum() <= t["ocupados_residencia"].sum(),
        "Tasas entre 0 y 100": t["tasa_desocupacion"].between(0, 100).all() and t["ene_tasa_desocupacion"].between(0, 100).all(),
        "Tasa nacional de ENE: profesionales 8,1 y técnicos 8,5": np.isclose(t.loc[t["nivel_titulo"] == "Profesional", "ene_tasa_nacional_nivel"].iloc[0], 8.1, atol=0.05) and np.isclose(t.loc[t["nivel_titulo"] == "Tecnico", "ene_tasa_nacional_nivel"].iloc[0], 8.5, atol=0.05),
        "Contraste con ENE completo": t["ene_fiabilidad"].notna().all(),
        "Aysén, técnicos: 372 desocupados": region_nivel.loc[(11, "Tecnico"), "desocupados"] == 372,
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    log.info("  [i] Fiabilidad ENE: %s", pd.crosstab(t["nivel_titulo"], t["ene_fiabilidad"]).to_dict("index"))
    log.info("  [i] Tasas nacionales: %s", t.drop_duplicates("nivel_titulo").set_index("nivel_titulo")["tasa_nacional_nivel"].round(1).to_dict())
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    censo = obtener.cargar_censo()
    tabla = tabla_censo(censo).merge(tabla_ene(obtener.cargar_ene()), on=["codigo_region", "nivel_titulo"], how="left", validate="one_to_one")
    validar(tabla, censo)
    tabla = tabla[list(FUERZA_TRABAJO_REGION_NIVEL)].astype(FUERZA_TRABAJO_REGION_NIVEL).sort_values(["codigo_region", "nivel_titulo"])
    RUTA_SALIDA.parent.mkdir(exist_ok=True)
    tabla.to_csv(RUTA_SALIDA, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", RUTA_SALIDA.name, len(tabla))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(RUTA_SALIDA)
