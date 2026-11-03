"""
<src/Analisis/JOINS/CW_Demanda_Jubilacion/crosswalk.py>

Paso 3 del índice: estima cuántos cupos deja la jubilación cada año, por carrera y región.

Salidas: Salida/jubilacion_carrera_region.csv, Salida/jubilacion_region_titulo.csv y
         Salida/jubilacion_validacion.csv

Unidad: flujo ANUAL, igual que Titulados (decisión 02-11-26).

Cuántos salen (ENE, 10 meses × 3/10):
  - Base: salidas efectivas. Por tramos de 5 años desde los 50, por nivel y sexo, población × caída de
    la tasa de ocupación / 5. Se usan tasas y no personas porque las cohortes jóvenes con título son
    más grandes: comparar personas confundiría expansión educativa con jubilación.
  - Sensibilidad: quienes llegarán a la edad legal en 5 años (mujeres 55-59, hombres 60-64), / 5.
    Sobrestima, porque muchos siguen trabajando después de esa edad.

Dónde (región de TRABAJO, decisión 02-11-26): según quienes están a 5 años de la edad legal. Una celda no fiable se reemplaza por los
ocupados con título de la región × la proporción nacional, y se conserva el total nacional.

Qué carreras: según CASEN, no SIES. El stock de SIES parte en 2007 y casi no ve a los mayores: al
predecir una mitad de la muestra con la otra, usar el stock da 38-44 puntos y CASEN da 26-28. El peso
de cada carrera = sus ocupados en CASEN × su proporción cerca de la edad legal (propia con 30 casos;
si no, de su área y nivel, o de su nivel). La región se incorpora con la distribución territorial de
la carrera en la tabla de ocupados. Una carrera sin ocupados en CASEN queda en 0.

Límites: las tasas por edad son de un corte transversal, no siguen personas; a diferencia del Paso 4,
incluye sector público. Parte de las vacantes de ENADEL pueden ser reemplazos de jubilados: el
posible doble conteo se resuelve en el Paso 5.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers"))
from comun.normalizador import REGIONES  # noqa: E402
from esquema import JUBILACION_CARRERA_REGION, JUBILACION_REGION_TITULO, VALIDACION_JUBILACION  # noqa: E402
import obtener  # noqa: E402

log = logging.getLogger(__name__)

DIR_SALIDA = Path(__file__).parent / "Salida"
FACTOR_10_MESES, ANIOS_VENTANA = 3 / 10, 5
TRAMOS = [50, 55, 60, 65, 70, 75, 80]
N_MINIMO, GL_MINIMO, CV_MAXIMO, MIN_CERCA = 60, 9, 30.0, 30
NIVELES = ("Tecnico", "Profesional")
PARTICIONES = 30


def es_cerca(sexo: pd.Series, edad: pd.Series) -> pd.Series:
    """A 5 años de la edad legal de jubilación: 60 mujeres y 65 hombres."""
    return ((sexo == 2) & edad.between(55, 59)) | ((sexo == 1) & edad.between(60, 64))


def salidas_nacionales(t: pd.DataFrame) -> pd.Series:
    """Salidas efectivas por año y nivel, sumando por sexo la caída de la tasa de ocupación."""
    x = t[t["edad"] >= TRAMOS[0]].copy()
    x["tramo"] = pd.cut(x["edad"], TRAMOS + [130], right=False, labels=TRAMOS).astype(int)
    x["w"] = x["fact_cal"] * FACTOR_10_MESES
    salida = {}
    for nivel, g in x.groupby("nivel_titulo"):
        total = 0.0
        for _, s in g.groupby("sexo"):
            pob = s.groupby("tramo")["w"].sum().reindex(TRAMOS, fill_value=0.0)
            tasa = (s[s["ocupado"]].groupby("tramo")["w"].sum().reindex(TRAMOS, fill_value=0.0) / pob).fillna(0.0)
            total += sum(pob[a] * max(tasa[a] - tasa[b], 0.0) for a, b in zip(TRAMOS, TRAMOS[1:])) / ANIOS_VENTANA
        salida[nivel] = total
    return pd.Series(salida)


def celdas_region(t: pd.DataFrame, psu: pd.Series, salidas: pd.Series) -> pd.DataFrame:
    """Personas cerca de la edad legal por región y nivel; asigna las salidas anuales a cada región."""
    o = t[t["ocupado"]].copy()
    # El cupo se abre donde está el empleo; sin ese dato (0,07%), donde vive la persona.
    o["codigo_region"] = o["codigo_region_trabajo"].fillna(o["codigo_region"]).astype(int)
    o["w"] = o["fact_cal"] * FACTOR_10_MESES
    o["cerca"] = es_cerca(o["sexo"], o["edad"])
    filas = []
    for (region, nivel), g in o.groupby(["codigo_region", "nivel_titulo"]):
        c = g[g["cerca"]]
        z = c.groupby(["estrato", "conglomerado"], sort=False)["w"].sum()
        h = z.groupby(level="estrato", sort=False).agg(s="sum", s2=lambda v: (v**2).sum())
        n_h = psu.reindex(h.index).to_numpy(dtype=float)
        var = np.where(n_h > 1, n_h / np.maximum(n_h - 1, 1) * (h["s2"] - h["s"]**2 / n_h), 0.0).sum()
        total = c["w"].sum()
        filas.append({"codigo_region": region, "nivel_titulo": nivel, "n_personas": c["idrph"].nunique(),
                      "gl": c["conglomerado"].nunique() - c["estrato"].nunique(), "cerca_directo": total,
                      "cv_pct": 100 * np.sqrt(var) / total if total else np.nan, "ocupados": g["w"].sum()})
    c = pd.DataFrame(filas)
    fiable = (c["n_personas"] >= N_MINIMO) & (c["gl"] >= GL_MINIMO) & (c["cv_pct"] <= CV_MAXIMO)
    c["origen_celda"] = np.where(fiable, "celda_propia", "ocupados_x_nacional")
    prop = c.groupby("nivel_titulo")["cerca_directo"].sum() / c.groupby("nivel_titulo")["ocupados"].sum()
    c["cerca_usados"] = np.where(fiable, c["cerca_directo"], c["ocupados"] * c["nivel_titulo"].map(prop))
    # Reemplazar celdas puede mover el total nacional, que sí está bien medido: se reescala.
    objetivo = c.groupby("nivel_titulo")["cerca_directo"].sum()
    c["cerca_usados"] *= c["nivel_titulo"].map(objetivo / c.groupby("nivel_titulo")["cerca_usados"].sum())
    parte = c["cerca_usados"] / c["nivel_titulo"].map(objetivo)
    c["jubilaciones_anuales"] = parte * c["nivel_titulo"].map(salidas)
    c["jubilaciones_edad_legal"] = c["cerca_usados"] / ANIOS_VENTANA
    c["nombre_region"] = c["codigo_region"].map(REGIONES)
    return c[list(JUBILACION_REGION_TITULO)].astype(JUBILACION_REGION_TITULO)


def proporcion_cerca(d: pd.DataFrame) -> pd.DataFrame:
    """Proporción de cada carrera cerca de la edad legal, con herencia si tiene pocos casos."""
    medida = lambda g: pd.Series({"n": g["cerca"].sum(), "q": g.loc[g["cerca"], "expr"].sum() / g["expr"].sum()})
    propia = d.groupby("carrera_generica").apply(medida, include_groups=False)
    area = d.groupby(["nivel_titulo", "area_cine_sies"]).apply(medida, include_groups=False)
    nivel = d.groupby("nivel_titulo").apply(medida, include_groups=False)
    filas = []
    for f in d[["carrera_generica", "nivel_titulo", "area_cine_sies"]].drop_duplicates().itertuples(index=False):
        a = area.loc[(f.nivel_titulo, f.area_cine_sies)]
        if propia.loc[f.carrera_generica, "n"] >= MIN_CERCA:
            q, origen = propia.loc[f.carrera_generica, "q"], "propia"
        elif a["n"] >= MIN_CERCA:
            q, origen = a["q"], "area_nivel"
        else:
            q, origen = nivel.loc[f.nivel_titulo, "q"], "nivel"
        filas.append({"carrera_generica": f.carrera_generica, "nivel_titulo": f.nivel_titulo, "q": q, "origen_propension": origen})
    return pd.DataFrame(filas).set_index("carrera_generica")


def mezcla_carreras(d: pd.DataFrame) -> pd.DataFrame:
    """Peso nacional de cada carrera dentro de las jubilaciones de su nivel."""
    q = proporcion_cerca(d)
    q["peso"] = d.groupby("carrera_generica")["expr"].sum().reindex(q.index) * q["q"]
    q["mezcla"] = q["peso"] / q.groupby("nivel_titulo")["peso"].transform("sum")
    return q


def repartir(celdas: pd.DataFrame, mezcla: pd.DataFrame, ocupados: pd.DataFrame) -> pd.DataFrame:
    """Reparte cada celda con la mezcla nacional, modulada por la presencia regional de la carrera."""
    o = ocupados.groupby(["codigo_region", "carrera_generica"], as_index=False)["ocupados_estimados"].sum()
    nacional = o.groupby("carrera_generica")["ocupados_estimados"].sum()
    o["territorial"] = o["ocupados_estimados"] / o["carrera_generica"].map(nacional)
    partes = []
    for f in celdas.itertuples(index=False):
        m = mezcla[mezcla["nivel_titulo"] == f.nivel_titulo][["mezcla", "origen_propension"]].copy()
        m["territorial"] = o[o["codigo_region"] == f.codigo_region].set_index("carrera_generica")["territorial"].reindex(m.index).fillna(0.0)
        m["cuota"] = m["mezcla"] * m["territorial"]
        if m["cuota"].sum() == 0:
            m["cuota"] = m["mezcla"]
        s = m["cuota"] / m["cuota"].sum()
        partes.append(pd.DataFrame({"codigo_region": f.codigo_region, "nombre_region": f.nombre_region, "nivel_titulo": f.nivel_titulo,
                                    "carrera_generica": m.index, "origen_propension": m["origen_propension"].to_numpy(),
                                    "jubilaciones_anuales": f.jubilaciones_anuales * s.to_numpy(),
                                    "jubilaciones_edad_legal": f.jubilaciones_edad_legal * s.to_numpy()}))
    r = pd.concat(partes, ignore_index=True)
    r = r[r["jubilaciones_anuales"] > 0]
    return r[list(JUBILACION_CARRERA_REGION)].astype(JUBILACION_CARRERA_REGION)


def disimilitud(a: pd.Series, b: pd.Series) -> float:
    i = a.index.union(b.index)
    a, b = a.reindex(i, fill_value=0.0), b.reindex(i, fill_value=0.0)
    return float(50 * (a / a.sum() - b / b.sum()).abs().sum())


def validacion(d: pd.DataFrame, ocupados: pd.DataFrame, salidas: pd.Series, celdas: pd.DataFrame) -> pd.DataFrame:
    """Predice una mitad de la muestra con la otra y deja constancia de los totales."""
    filas = []
    agregar = lambda p, g, v, t: filas.append({"prueba": p, "grupo": g, "valor": float(v), "descripcion": t})
    stock = ocupados.groupby(["nivel_titulo", "carrera_generica"])["ocupados_estimados"].sum()
    rng = np.random.default_rng(2026)
    u = d["varunit"].unique()
    res = {(n, v): [] for n in NIVELES for v in ("stock_sies", "casen")}
    for _ in range(PARTICIONES):
        elegidos = set(rng.choice(u, len(u) // 2, replace=False))
        a, b = d[d["varunit"].isin(elegidos)], d[~d["varunit"].isin(elegidos)]
        m = mezcla_carreras(a)
        for n in NIVELES:
            real = b[b["cerca"] & (b["nivel_titulo"] == n)].groupby("carrera_generica")["expr"].sum()
            res[(n, "stock_sies")].append(disimilitud(real, stock[n]))
            res[(n, "casen")].append(disimilitud(real, m.loc[m["nivel_titulo"] == n, "mezcla"]))
    for (n, v), valores in res.items():
        agregar(f"mitades_{v}", n, np.mean(valores), f"Disimilitud promedio en {PARTICIONES} particiones")
    for n in NIVELES:
        agregar("salidas_efectivas_anuales", n, salidas[n], "Por caída de la tasa de ocupación")
        agregar("llegan_edad_legal_anual", n, celdas.loc[celdas["nivel_titulo"] == n, "jubilaciones_edad_legal"].sum(), "A 5 años de la edad legal, / 5")
    return pd.DataFrame(filas)[list(VALIDACION_JUBILACION)].astype(VALIDACION_JUBILACION)


def validar(r: pd.DataFrame, c: pd.DataFrame, salidas: pd.Series) -> None:
    por_celda = r.groupby(["codigo_region", "nivel_titulo"])["jubilaciones_anuales"].sum().reset_index().merge(c, on=["codigo_region", "nivel_titulo"])
    controles = {
        "Clave única": not r.duplicated(["codigo_region", "carrera_generica"]).any(),
        "Regiones 1-16": r["codigo_region"].nunique() == 16,
        "Regiones conservan el total nacional": np.isclose(c.groupby("nivel_titulo")["jubilaciones_anuales"].sum().reindex(salidas.index), salidas).all(),
        "Reparto conserva cada celda": np.isclose(por_celda["jubilaciones_anuales_x"], por_celda["jubilaciones_anuales_y"]).all(),
        "Salidas efectivas no superan a la edad legal": (salidas <= c.groupby("nivel_titulo")["jubilaciones_edad_legal"].sum().reindex(salidas.index)).all(),
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    if not all(controles.values()):
        raise ValueError("Validaciones fallidas en el Paso 3")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    t, psu = obtener.cargar_ene()
    salidas = salidas_nacionales(t)
    c = celdas_region(t, psu, salidas)
    d = obtener.cargar_casen()
    d["cerca"] = es_cerca(d["sexo"], d["edad"])
    ocupados = obtener.cargar_ocupados()
    r = repartir(c, mezcla_carreras(d), ocupados)
    validar(r, c, salidas)
    v = validacion(d, ocupados, salidas, c)
    DIR_SALIDA.mkdir(exist_ok=True)
    rutas = [(DIR_SALIDA / "jubilacion_carrera_region.csv", r), (DIR_SALIDA / "jubilacion_region_titulo.csv", c), (DIR_SALIDA / "jubilacion_validacion.csv", v)]
    for ruta, tabla in rutas:
        tabla.to_csv(ruta, sep=";", index=False, encoding="utf-8")
        log.info("CSV generado: %s (%d filas)", ruta.name, len(tabla))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    for ruta, _ in rutas:
        inspeccion_rigurosa(ruta)
