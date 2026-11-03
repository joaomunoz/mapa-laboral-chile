"""
<src/Analisis/JOINS/CW_Ocupados_Carrera_Region_Actividad/crosswalk.py>
Actualizado 02-11-26 16:40

Estima cuántos titulados de cada carrera trabajan en cada actividad y región.

Entradas: stock SIES, ENE (JAS 2026), P7 y P1 (ver obtener.py).
Salida:   Salida/ocupados_carrera_region_actividad.csv

Método (estimador sintético con ajuste proporcional iterativo, IPF), por región y nivel:
  1. Filas: los ocupados ENE de la región se reparten entre carreras según el stock SIES.
  2. Semilla: cada carrera parte de su perfil nacional de P7.
  3. Peso regional: cada perfil se multiplica por el peso relativo dla actividad en la región, medido
     con TODOS los ocupados de ENE, y se reescala (idea del usuario, 02-11-26). Así la minería sube
     en Antofagasta y una carrera sin presencia en minería casi no se mueve.

Por qué no se ajusta a los ocupados con título de ENE por actividad (como el IPF anterior): la celda
región × nivel × actividad tiene una mediana de 11 personas, y ajustarse a ella empeoró las regiones
de 21,0 a 29,3 puntos. Con todos los ocupados bajó a 20,2 (ver validar_reparto.py). El peso_ene se
conserva solo para esa comparación. La tabla respeta el total ENE por región y nivel, no por actividad.

Región: la del EMPLEO (b18_region), porque esta tabla alimenta la demanda (decisión 02-11-26).

Límites: el stock usa la región de la SEDE; supone igual tasa de ocupación
entre carreras de una región y nivel; aplica a todas las carreras el mismo peso regional; las
celdas heredan la confianza de su perfil.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers"))
from comun.normalizador import REGIONES  # noqa: E402
from esquema import OCUPADOS_CARRERA_REGION_ACTIVIDAD  # noqa: E402
import obtener  # noqa: E402

log = logging.getLogger(__name__)

RUTA_SALIDA = Path(__file__).parent / "Salida" / "ocupados_carrera_region_actividad.csv"
N_MINIMO, GL_MINIMO = 60, 9
MAX_ITER, TOLERANCIA = 500, 1e-6
MARGEN_POR_DEFECTO = "ene_directo"
PESO_ENE = 0.0
RUTA_PESOS = Path(__file__).resolve().parents[2] / "Calculos_control" / "ocupados_region_actividad" / "Salida" / "ocupados_region_actividad.csv"


def margen_ene(ene: pd.DataFrame, estrategia: str) -> pd.DataFrame:
    """
    Ocupados por región, nivel y actividad.

    ene_directo: usa cada celda de ENE tal cual.
    fiabilidad:  conserva solo celdas con n >= 60 y gl >= 9; el resto de la región se reparte con
                 la mezcla nacional del nivel (estrategia (a) aprobada para el Paso 2).
    """
    o = ene.dropna(subset=["actividad_caenes"])
    claves = ["codigo_region", "nivel_titulo", "actividad_caenes"]
    m = o.groupby(claves, as_index=False).agg(
        ocupados=("fact_cal", "sum"), n=("idrph", "nunique"),
        psu=("conglomerado", "nunique"), estratos=("estrato", "nunique"),
    )
    if estrategia == "ene_directo":
        return m[claves + ["ocupados"]]
    if estrategia != "fiabilidad":
        raise ValueError(f"Estrategia desconocida: {estrategia}")

    m["fiable"] = (m["n"] >= N_MINIMO) & (m["psu"] - m["estratos"] >= GL_MINIMO)
    mezcla = o.groupby(["nivel_titulo", "actividad_caenes"])["fact_cal"].sum().rename("nacional").reset_index()
    partes = []
    for (region, nivel), g in m.groupby(["codigo_region", "nivel_titulo"]):
        fiables = g[g["fiable"]].set_index("actividad_caenes")["ocupados"]
        resto = g["ocupados"].sum() - fiables.sum()
        base = mezcla[(mezcla["nivel_titulo"] == nivel) & ~mezcla["actividad_caenes"].isin(fiables.index)].set_index("actividad_caenes")["nacional"]
        valores = pd.concat([fiables, resto * base / base.sum()]) if len(base) else fiables
        partes.append(valores.rename("ocupados").reset_index().assign(codigo_region=region, nivel_titulo=nivel))
    return pd.concat(partes, ignore_index=True)[claves + ["ocupados"]]


def ipf(semilla: np.ndarray, filas: np.ndarray, columnas: np.ndarray) -> np.ndarray:
    """Ajusta la semilla a los totales por fila y columna, conservando sus razones internas."""
    x = semilla.astype(float).copy()
    for _ in range(MAX_ITER):
        sf = x.sum(axis=1)
        x *= np.divide(filas, sf, out=np.ones_like(filas, dtype=float), where=sf > 0)[:, None]
        sc = x.sum(axis=0)
        x *= np.divide(columnas, sc, out=np.ones_like(columnas, dtype=float), where=sc > 0)
        if np.abs(x.sum(axis=1) - filas).max() < TOLERANCIA * max(filas.sum(), 1):
            break
    return x


def perfil_a_tabla(perfil: pd.DataFrame) -> pd.DataFrame:
    """Perfil de actividad de P7 como tabla carrera × CAENES, en proporciones."""
    s = perfil[perfil["dimension"] == "actividad_economica"]
    return s.pivot_table(index="carrera_generica", columns="actividad_caenes", values="pct", fill_value=0.0).reindex(columns=range(1, 22), fill_value=0.0) / 100


def cargar_pesos() -> pd.DataFrame:
    """Peso relativo región × CAENES; una actividad sin casos en la región queda en 0."""
    p = pd.read_csv(RUTA_PESOS, sep=";")
    p = p[p["base_region"] == "trabajo"]
    return p.pivot_table(index="codigo_region", columns="actividad_caenes", values="peso_relativo", fill_value=0.0).reindex(columns=range(1, 22), fill_value=0.0)


def ponderar(perfil: np.ndarray, pesos: np.ndarray) -> np.ndarray:
    """Multiplica perfiles por el peso regional y reescala; sin masa resultante conserva el original."""
    x = perfil * pesos
    suma = x.sum(axis=1, keepdims=True)
    return np.where(suma > 0, x / np.where(suma > 0, suma, 1), perfil)


def repartir(mezcla: pd.DataFrame, tabla: pd.DataFrame, margen: pd.DataFrame, carreras: pd.DataFrame,
             pesos: pd.DataFrame | None = None, peso_ene: float = PESO_ENE) -> pd.DataFrame:
    """Reparte por región y nivel. mezcla trae (codigo_region, carrera_generica, peso)."""
    base = mezcla.merge(carreras[["carrera_generica", "nivel_titulo"]], on="carrera_generica")
    filas = []
    for (region, nivel), g in base.groupby(["codigo_region", "nivel_titulo"]):
        col = margen[(margen["codigo_region"] == region) & (margen["nivel_titulo"] == nivel)].set_index("actividad_caenes")["ocupados"].reindex(range(1, 22), fill_value=0.0)
        total = col.sum()
        if total == 0:
            continue
        nombres = g["carrera_generica"].to_numpy()
        peso = g["peso"].to_numpy(dtype=float)
        fila_total = total * peso / peso.sum()
        perfil = tabla.reindex(nombres).to_numpy()
        base_perfil = ponderar(perfil, pesos.loc[region].to_numpy()) if pesos is not None else perfil
        semilla = base_perfil * fila_total[:, None]
        objetivo = (1 - peso_ene) * semilla.sum(axis=0) + peso_ene * col.to_numpy()
        ajustado = ipf(semilla, fila_total, objetivo) if peso_ene > 0 else semilla
        for i, carrera in enumerate(nombres):
            for j, actividad_caenes in enumerate(range(1, 22)):
                if ajustado[i, j] > 0:
                    filas.append((region, nivel, carrera, actividad_caenes, fila_total[i], ajustado[i, j], 100 * perfil[i, j]))
    return pd.DataFrame(filas, columns=["codigo_region", "nivel_titulo", "carrera_generica", "actividad_caenes",
                                        "ocupados_carrera_region", "ocupados_estimados", "pct_perfil_nacional"])


def construir(estrategia: str = MARGEN_POR_DEFECTO) -> pd.DataFrame:
    """Arma la tabla final con la estrategia de margen elegida."""
    stock, ene, perfil, actividades = obtener.cargar_stock(), obtener.cargar_ene(), obtener.cargar_perfil(), obtener.cargar_actividades()
    carreras = perfil[perfil["dimension"] == "actividad_economica"].drop_duplicates("carrera_generica")[
        ["carrera_generica", "nivel_titulo", "area_cine_sies", "nivel_confianza"]]
    margen = margen_ene(ene, estrategia)
    r = repartir(stock.rename(columns={"stock_sies": "peso"}), perfil_a_tabla(perfil), margen, carreras, cargar_pesos())
    r = r.merge(stock, on=["codigo_region", "carrera_generica"]).merge(
        carreras.drop(columns="nivel_titulo"), on="carrera_generica").merge(actividades, on="actividad_caenes")
    r["nombre_region"] = r["codigo_region"].map(REGIONES)
    r["pct_en_carrera_region"] = 100 * r["ocupados_estimados"] / r["ocupados_carrera_region"]
    r = r[list(OCUPADOS_CARRERA_REGION_ACTIVIDAD)].astype(OCUPADOS_CARRERA_REGION_ACTIVIDAD)
    validar(r, margen)
    return r


def validar(r: pd.DataFrame, margen: pd.DataFrame) -> None:
    """Detiene el proceso si el reparto no respeta sus totales."""
    total = r.groupby(["codigo_region", "nivel_titulo"])["ocupados_estimados"].sum().rename("est").reset_index().merge(
        margen.groupby(["codigo_region", "nivel_titulo"], as_index=False)["ocupados"].sum(), on=["codigo_region", "nivel_titulo"])
    desv_region = (total["est"] - total["ocupados"]).abs().sum() / total["ocupados"].sum()
    fila = r.groupby(["codigo_region", "carrera_generica"]).agg(est=("ocupados_estimados", "sum"), obj=("ocupados_carrera_region", "first"))
    desv_fila = (fila["est"] - fila["obj"]).abs().sum() / fila["obj"].sum()
    controles = {
        "Regiones 1-16": r["codigo_region"].nunique() == 16,
        "Clave única": not r.duplicated(["codigo_region", "carrera_generica", "actividad_caenes"]).any(),
        "Sin negativos ni nulos": (r["ocupados_estimados"] >= 0).all() and r["ocupados_estimados"].notna().all(),
        "Total por región y nivel respeta ENE (desv. < 1%)": desv_region < 0.01,
        "Total por carrera respeta el reparto (desv. < 1%)": desv_fila < 0.01,
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    log.info("  [i] Desviación: región %.4f%%, carrera %.4f%%", 100 * desv_region, 100 * desv_fila)
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    tabla = construir()
    RUTA_SALIDA.parent.mkdir(exist_ok=True)
    tabla.to_csv(RUTA_SALIDA, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", RUTA_SALIDA.name, len(tabla))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(RUTA_SALIDA)
