"""
<src/Analisis/JOINS/Formalidad_Ocupados/crosswalk.py>

Mide cómo trabajan los ocupados según la ENE de marzo a julio de 2026: asalariado o independiente, y formal o informal.

Salida: Salida/formalidad_ocupados.csv

Decisiones (aprobadas el 08-11-26):
  - Dos ejes y no tres grupos: independiente es un tipo de trabajo y formal o informal una condición; un
    independiente puede ser formal o informal.
  - Solo ENE 2026: las ocupadas informales de 2024 no reproducen el boletín del INE (ver ENE/procesar.py), así que
    no hay evolución de la informalidad. El Censo no mide formalidad.
  - Los mismos meses que la evolución de la desocupación (comun/periodos.py), para que ambas secciones hablen del
    mismo periodo.
  - Independiente = empleador o cuenta propia (CISE 1-2). Asalariado = privado, público y servicio doméstico (3-6).
    Familiar no remunerado (7) aparte; en la ENE es siempre informal.
  - Ocupados sin rama o sin nivel informado quedan fuera de esas filas, pero cuentan en Chile y en su región.

Varianza: linealización de Taylor con estrato y conglomerado, usando todo el diseño (igual que Evolucion_Desocupacion).
Fiabilidad de cada cifra medida sobre su numerador: n >= 60, gl >= 9 y CV <= 30 (poco fiable si CV > 15).
Familiar no remunerado lleva su propia fiabilidad (08-11-26): es la casilla más chica del reparto, y el mapa la muestra
solo donde es fiable. Las otras cuatro casillas se controlan en Chile y los niveles, que es donde el mapa las muestra.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers"))
from comun.normalizador import REGIONES  # noqa: E402
from comun.periodos import FACTOR_CONTRASTE, MESES_ACTUAL  # noqa: E402
from esquema import FORMALIDAD_OCUPADOS  # noqa: E402
import obtener  # noqa: E402

log = logging.getLogger(__name__)

RUTA_SALIDA = Path(__file__).parent / "Salida" / "formalidad_ocupados.csv"
FACTOR = 3 / len(MESES_ACTUAL)  # Cada mes es un tercio de la población: 5 meses x 3/5 = promedio trimestral
NIVEL_POR_CINE = {3: "Tecnico", 4: "Profesional", 5: "Profesional", 6: "Profesional"}  # Igual que Evolucion_Desocupacion
NIVELES = ["Profesional", "Tecnico", "Sin_titulo"]
NOMBRE_NIVEL = {"Profesional": "Profesional", "Tecnico": "Técnico", "Sin_titulo": "Sin título superior"}
TIPO_POR_CISE = {1: "independiente", 2: "independiente", 3: "asalariado", 4: "asalariado", 5: "asalariado", 6: "asalariado", 7: "familiar"}
FORMAL, INFORMAL = 1, 2
N_MINIMO, GL_MINIMO, CV_MAXIMO, CV_POCO_FIABLE = 60, 9, 30, 15
N_REGIONES, N_ACTIVIDADES = 16, 21
INFORMALIDAD_CHILE = 26.6  # Medida al proponer la sección (08-11-26)


def diseno(ene: pd.DataFrame) -> pd.DataFrame:
    d = ene[["estrato", "conglomerado"]].drop_duplicates()
    return d.assign(n_conglomerados=d.groupby("estrato")["conglomerado"].transform("size"))


def proporcion(celda: pd.DataFrame, indicador: str, dis: pd.DataFrame) -> tuple[float, float, str]:
    """% de la celda con el indicador, su CV y su fiabilidad (misma fórmula que Evolucion_Desocupacion)."""
    peso, y = celda["fact_cal"], celda[indicador].astype(float)
    total = peso.sum()
    p = (peso * y).sum() / total
    if p == 0:
        return 0.0, np.nan, "no_fiable"
    z = celda.assign(z=peso * (y - p) / total).groupby(["estrato", "conglomerado"], as_index=False)["z"].sum()
    g = dis.merge(z, how="left", on=["estrato", "conglomerado"]).fillna({"z": 0.0})
    g = g[g["n_conglomerados"] > 1]  # Un estrato con un solo conglomerado no permite estimar varianza
    media = g.groupby("estrato")["z"].transform("mean")
    cv = 100 * (g["n_conglomerados"] / (g["n_conglomerados"] - 1) * (g["z"] - media) ** 2).sum() ** 0.5 / p
    con = celda[celda[indicador]]
    n, gl = con["idrph"].nunique(), con["conglomerado"].nunique() - con["estrato"].nunique()
    fiabilidad = "no_fiable" if n < N_MINIMO or gl < GL_MINIMO or not np.isfinite(cv) or cv > CV_MAXIMO else "poco_fiable" if cv > CV_POCO_FIABLE else "fiable"
    return 100 * p, cv, fiabilidad


def preparar(ene: pd.DataFrame, puente: pd.DataFrame) -> pd.DataFrame:
    o = ene[ene["cae_especifico"].between(1, 7)].copy()
    o["tipo"] = o["categoria_ocupacion"].map(TIPO_POR_CISE)
    o["informal"] = o["ocup_form"] == INFORMAL
    o["independiente"] = o["tipo"] == "independiente"
    o["familiar"] = o["tipo"] == "familiar"
    for tipo in ("asalariado", "independiente"):
        for condicion, codigo in (("formal", FORMAL), ("informal", INFORMAL)):
            o[f"{tipo}_{condicion}"] = (o["tipo"] == tipo) & (o["ocup_form"] == codigo)
    o["nivel_titulo"] = o["cine11_1d"].map(lambda c: NIVEL_POR_CINE.get(int(c), "Sin_titulo") if pd.notna(c) else None)
    return o.merge(puente, how="left", left_on="r_p_rev4cl_caenes", right_on="actividad_caenes")


def medir(celda: pd.DataFrame, dis: pd.DataFrame) -> dict:
    peso = celda["fact_cal"]
    reparto = lambda tipo, formal: 100 * peso[(celda["tipo"] == tipo) & (celda["ocup_form"] == formal)].sum() / peso.sum()
    tasa, cv_t, f_t = proporcion(celda, "informal", dis)
    ind, cv_i, f_i = proporcion(celda, "independiente", dis)
    _, cv_f, f_f = proporcion(celda, "familiar", dis)
    return {"ocupados": int(round(peso.sum() * FACTOR)), "n_ocupados": celda["idrph"].nunique(),
            "pct_asalariado_formal": reparto("asalariado", FORMAL), "pct_asalariado_informal": reparto("asalariado", INFORMAL),
            "pct_independiente_formal": reparto("independiente", FORMAL), "pct_independiente_informal": reparto("independiente", INFORMAL),
            "pct_familiar": 100 * peso[celda["tipo"] == "familiar"].sum() / peso.sum(),
            "tasa_informalidad": tasa, "cv_informalidad": cv_t, "pct_independientes": ind, "cv_independientes": cv_i,
            "cv_familiar": cv_f, "fiabilidad_informalidad": f_t, "fiabilidad_independientes": f_i, "fiabilidad_familiar": f_f}


def construir(ene: pd.DataFrame, puente: pd.DataFrame) -> pd.DataFrame:
    dis, o = diseno(ene), preparar(ene, puente)
    vacio = {"codigo_region": None, "nivel_titulo": "Todos", "actividad_ciiu": None}
    dominios = ([({"ambito": "chile", **vacio, "nombre": "Chile"}, o)]
                + [({"ambito": "nivel", **vacio, "nivel_titulo": n, "nombre": NOMBRE_NIVEL[n]}, o[o["nivel_titulo"] == n]) for n in NIVELES]
                + [({"ambito": "region", **vacio, "codigo_region": r, "nombre": REGIONES[r]}, o[o["codigo_region"] == r]) for r in range(1, N_REGIONES + 1)]
                + [({"ambito": "actividad", **vacio, "actividad_ciiu": f.actividad_ciiu, "nombre": f.actividad_glosa}, o[o["actividad_ciiu"] == f.actividad_ciiu])
                   for f in puente.sort_values("actividad_ciiu").itertuples()])
    filas = [{**clave, **medir(celda, dis)} for clave, celda in dominios]
    return pd.DataFrame(filas)[list(FORMALIDAD_OCUPADOS)].astype(FORMALIDAD_OCUPADOS)


def casillas_fiables(ene: pd.DataFrame, puente: pd.DataFrame) -> bool:
    """Las cuatro casillas asalariado o independiente por formal o informal son fiables en Chile y en cada nivel."""
    dis, o = diseno(ene), preparar(ene, puente)
    celdas = [o] + [o[o["nivel_titulo"] == n] for n in NIVELES]
    return all(proporcion(c, f"{tipo}_{cond}", dis)[2] == "fiable" for c in celdas
               for tipo in ("asalariado", "independiente") for cond in ("formal", "informal"))


def validar(t: pd.DataFrame, ene: pd.DataFrame, casillas_ok: bool) -> None:
    """Detiene el proceso si la tabla no cuadra consigo misma o con su periodo."""
    chile = t[t["ambito"] == "chile"].iloc[0]
    sin_rama = int(round(ene.loc[ene["cae_especifico"].between(1, 7) & ene["r_p_rev4cl_caenes"].isna(), "fact_cal"].sum() * FACTOR))
    repartos = ["pct_asalariado_formal", "pct_asalariado_informal", "pct_independiente_formal", "pct_independiente_informal", "pct_familiar"]
    region = t[t["ambito"] == "region"]
    controles = {
        "41 filas con clave única": len(t) == 1 + len(NIVELES) + N_REGIONES + N_ACTIVIDADES
            and not t.duplicated(["ambito", "codigo_region", "nivel_titulo", "actividad_ciiu"]).any(),
        "Solo los 5 meses de 2026": sorted(ene["mes"].unique()) == MESES_ACTUAL,
        "Los cinco repartos suman 100 en cada fila": np.allclose(t[repartos].sum(axis=1), 100),
        "Informalidad = asalariado informal + independiente informal + familiar": np.allclose(t["tasa_informalidad"], t["pct_asalariado_informal"] + t["pct_independiente_informal"] + t["pct_familiar"]),
        "Independientes = independiente formal + informal": np.allclose(t["pct_independientes"], t["pct_independiente_formal"] + t["pct_independiente_informal"]),
        "Las 16 regiones suman Chile (±16 por redondeo)": abs(region["ocupados"].sum() - chile["ocupados"]) <= N_REGIONES,
        "Las actividades y los sin rama suman Chile (±21 por redondeo)": abs(t.loc[t["ambito"] == "actividad", "ocupados"].sum() + sin_rama - chile["ocupados"]) <= N_ACTIVIDADES,
        f"Chile: {INFORMALIDAD_CHILE}% de informalidad": round(chile["tasa_informalidad"], 1) == INFORMALIDAD_CHILE,
        "Chile, niveles y regiones: ambas cifras fiables": (t.loc[t["ambito"].isin(["chile", "nivel", "region"]), ["fiabilidad_informalidad", "fiabilidad_independientes"]] == "fiable").all().all(),
        "Chile y niveles: las cuatro casillas asalariado o independiente por formal o informal son fiables": casillas_ok,
        "Familiar fiable en Chile": chile["fiabilidad_familiar"] == "fiable",
        "El factor coincide con el del contraste (mismo largo de ventana)": FACTOR == FACTOR_CONTRASTE,
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    act = t[t["ambito"] == "actividad"]
    log.info("  [i] Ocupados sin rama: %s", f"{sin_rama:,}")
    log.info("  [i] Familiar fiable en: %s", t.loc[t["fiabilidad_familiar"] == "fiable", "nombre"].tolist())
    for col in ("fiabilidad_informalidad", "fiabilidad_independientes"):
        log.info("  [i] %s en actividades: %s; no fiables: %s", col, act[col].value_counts().to_dict(), act.loc[act[col] != "fiable", "actividad_ciiu"].tolist())
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ene = obtener.cargar_ene()
    puente = obtener.cargar_puente()
    tabla = construir(ene, puente)
    validar(tabla, ene, casillas_fiables(ene, puente))
    RUTA_SALIDA.parent.mkdir(exist_ok=True)
    tabla.to_csv(RUTA_SALIDA, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", RUTA_SALIDA.name, len(tabla))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(RUTA_SALIDA)
