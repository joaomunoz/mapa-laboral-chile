"""
<src/Analisis/Puentes_de_mapeo/P6_matriz_carrera_actividad_ocupacion.py>

Generador del P6 · MATRIZ_CARRERA_ACTIVIDAD_OCUPACION del proyecto.

Entradas: src/Scrapers/CASEN/Salida/casen_procesado.csv  (personas con educación superior)
          src/Scrapers/CASEN/Entrada/casen_2024.dta      (solo el diseño muestral completo)
          Salida/P5_puente_carrera_casen.csv             (texto → carrera_generica)
          Salida/P1_puente_actividades.csv                  (CAENES → sección CIIU)
Salidas:  Salida/P6_matriz_carrera_actividad_ocupacion.csv  (formato largo)
          Salida/P6_matriz_carrera_actividad_ocupacion_no_asignados.csv  (control de sesgo)

Mide dónde trabajan los titulados de cada carrera, a nivel nacional. Universo: ocupados con
título completo y carrera asignada en P5. Cada fila es un porcentaje dentro de la carrera, en
una de tres dimensiones: actividad_economica, grupo_ocupacion u ocupacion_actividad.

Por qué nacional: carrera × actividad × región deja celdas sin casos suficientes.

Por qué se lee el .dta: la varianza de un dominio debe considerar TODOS los conglomerados del
diseño. Con solo los que tienen titulados, los ceros desaparecen y el error queda subestimado.

Varianza: linealización de Taylor de la razón p = Y/X, con estratos varstrat y conglomerados
varunit (libro de códigos CASEN), con reemplazo en la primera etapa.
Estándar INE aplicado: no fiable si n de la carrera < 60, gl < 9 o CV > 30%; poco fiable si
CV entre 15% y 30%; fiable en otro caso. gl = conglomerados - estratos de la carrera.

Esquema: esquema.py (MATRIZ_CARRERA_ACTIVIDAD_OCUPACION, CONTROL_NO_ASIGNADOS)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from esquema import (  # noqa: E402
    CONTROL_NO_ASIGNADOS,
    DIMENSIONES_P6,
    FIABILIDADES_P6,
    MATRIZ_CARRERA_ACTIVIDAD_OCUPACION,
)

log = logging.getLogger(__name__)

DIR_SCRAPERS = Path(__file__).resolve().parents[2] / "Scrapers"
DIR_SALIDA = Path(__file__).parent / "Salida"
RUTA_CASEN = DIR_SCRAPERS / "CASEN" / "Salida" / "casen_procesado.csv"
RUTA_CRUDO = DIR_SCRAPERS / "CASEN" / "Entrada" / "casen_2024.dta"
RUTA_P5 = DIR_SALIDA / "P5_puente_carrera_casen.csv"
RUTA_P1 = DIR_SALIDA / "P1_puente_actividades.csv"

N_MINIMO, GL_MINIMO, CV_FIABLE, CV_MAXIMO = 60, 9, 15.0, 30.0

# CIUO-08 con la numeración de ENE (b1): FF.AA. es 10 aquí y 0 en CASEN.
GLOSAS_CIUO = {
    1: "Directores y gerentes", 2: "Profesionales, científicos e intelectuales",
    3: "Técnicos y profesionales de nivel medio", 4: "Personal de apoyo administrativo",
    5: "Trabajadores de servicios y vendedores", 6: "Agricultores y trabajadores calificados",
    7: "Oficiales, operarios y artesanos", 8: "Operadores de instalaciones y máquinas",
    9: "Ocupaciones elementales", 10: "Fuerzas Armadas",
}


def cargar() -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    """Une CASEN con P5 y devuelve también los conglomerados por estrato del diseño completo."""
    casen = pd.read_csv(RUTA_CASEN, sep=";", low_memory=False, dtype={"oficio4_08": "object", "rama4": "object"})
    p5 = pd.read_csv(RUTA_P5, sep=";")[["e6a", "carrera_normalizada", "carrera_generica", "nivel_titulo",
                                        "area_cine_sies", "estado"]]
    d = casen.merge(p5, on=["e6a", "carrera_normalizada"], how="left", validate="many_to_one")
    if d["estado"].isna().any():
        raise ValueError("Hay textos de CASEN que no están en P5: regenerar P5.")
    d["grupo_ocupacion"] = d["oficio1_08"].replace(0, 10).astype("Int64")
    ocupados = d[(d["activ"] == 1) & d["titulo_comun"].notna()].copy()

    diseno = pd.read_stata(RUTA_CRUDO, columns=["varstrat", "varunit"], convert_categoricals=False)
    psu_por_estrato = diseno.drop_duplicates().groupby("varstrat").size()
    log.info("Diseño: %d estratos, %d conglomerados, %d estratos con un solo conglomerado",
             len(psu_por_estrato), psu_por_estrato.sum(), int((psu_por_estrato == 1).sum()))
    return d, ocupados, psu_por_estrato


def error_estandar(x: pd.DataFrame, celda: pd.Series, p: float, total: float, psu: pd.Series) -> float:
    """
    Error estándar de p = Y/X en el dominio x, por linealización de Taylor.

    Los conglomerados sin personas del dominio tienen z = 0: no aparecen en la suma, pero sí
    cuentan en n_h. Por eso se usa la forma Σz² - (Σz)²/n_h en lugar de restar medias.
    """
    z = x["expr"].to_numpy() * (celda.to_numpy().astype(float) - p) / total
    t = pd.DataFrame({"h": x["varstrat"].to_numpy(), "u": x["varunit"].to_numpy(), "z": z})
    por_psu = t.groupby(["h", "u"], sort=False)["z"].sum().reset_index()
    por_estrato = por_psu.groupby("h", sort=False)["z"].agg(s="sum", s2=lambda v: (v**2).sum())
    n_h = psu.reindex(por_estrato.index).to_numpy().astype(float)
    # Un estrato con un solo conglomerado no permite estimar varianza: aporta 0.
    aporte = np.where(n_h > 1, n_h / np.maximum(n_h - 1, 1) * (por_estrato["s2"] - por_estrato["s"]**2 / n_h), 0.0)
    return float(np.sqrt(aporte.sum()))


def clasificar(n: int, gl: int, cv: float) -> str:
    """Aplica el estándar INE de fiabilidad a una estimación."""
    if n < N_MINIMO or gl < GL_MINIMO or not np.isfinite(cv) or cv > CV_MAXIMO:
        return "no_fiable"
    return "poco_fiable" if cv > CV_FIABLE else "fiable"


def estimar(ocupados: pd.DataFrame, psu: pd.Series, actividades: pd.DataFrame) -> pd.DataFrame:
    """Calcula porcentaje, error y fiabilidad de cada celda de las tres dimensiones."""
    asignados = ocupados[ocupados["estado"] == "asignado"]
    dimensiones = {
        "actividad_economica": ["rama1"], "grupo_ocupacion": ["grupo_ocupacion"], "ocupacion_actividad": ["grupo_ocupacion", "rama1"],
    }
    filas = []
    for (carrera, nivel, area), grupo in asignados.groupby(["carrera_generica", "nivel_titulo", "area_cine_sies"]):
        for dimension, llaves in dimensiones.items():
            x = grupo.dropna(subset=llaves)
            if x.empty:
                continue
            total = x["expr"].sum()
            n, gl = len(x), x["varunit"].nunique() - x["varstrat"].nunique()
            for valores, celda in x.groupby(llaves):
                valores = valores if isinstance(valores, tuple) else (valores,)
                pertenece = x.index.isin(celda.index)
                p = celda["expr"].sum() / total
                se = error_estandar(x, pd.Series(pertenece), p, total, psu)
                cv = 100 * se / p
                claves = dict(zip(llaves, valores))
                filas.append({
                    "carrera_generica": carrera, "nivel_titulo": nivel, "area_cine_sies": area,
                    "dimension": dimension, "actividad_caenes": claves.get("rama1"),
                    "grupo_ocupacion": claves.get("grupo_ocupacion"), "n_carrera": n, "n_celda": len(celda),
                    "gl": gl, "expandido_celda": celda["expr"].sum(), "expandido_carrera": total,
                    "pct": 100 * p, "error_estandar": 100 * se, "cv_pct": cv, "fiabilidad": clasificar(n, gl, cv),
                })
    m = pd.DataFrame(filas)
    m["actividad_caenes"] = m["actividad_caenes"].astype("Int64")
    m["grupo_ocupacion"] = m["grupo_ocupacion"].astype("Int64")
    m = m.merge(actividades, on="actividad_caenes", how="left")
    m["glosa_ocupacion"] = m["grupo_ocupacion"].map(GLOSAS_CIUO)
    m = m.sort_values(["carrera_generica", "dimension", "pct"], ascending=[True, True, False])
    return m[list(MATRIZ_CARRERA_ACTIVIDAD_OCUPACION)].astype(MATRIZ_CARRERA_ACTIVIDAD_OCUPACION)


def comparar_no_asignados(d: pd.DataFrame) -> pd.DataFrame:
    """Compara a quienes tienen carrera y a quienes no: si difieren, la matriz puede estar sesgada."""
    o = d.assign(grupo=np.where(d["estado"] == "asignado", "asignados", "no_asignados"))
    variables = {"actividad_economica": "rama1", "grupo_ocupacion": "grupo_ocupacion", "titulo": "titulo_comun",
                 "area_cine": "cinef13_area", "region": "codigo_region"}
    partes = []
    for dimension, col in variables.items():
        t = o.dropna(subset=[col]).pivot_table(index=col, columns="grupo", values="expr", aggfunc="sum", fill_value=0)
        t = 100 * t / t.sum()
        partes.append(pd.DataFrame({
            "dimension": dimension, "categoria": t.index.astype(str), "pct_asignados": t["asignados"].to_numpy(),
            "pct_no_asignados": t["no_asignados"].to_numpy(),
        }))
    r = pd.concat(partes, ignore_index=True)
    r["diferencia"] = r["pct_no_asignados"] - r["pct_asignados"]
    return r[list(CONTROL_NO_ASIGNADOS)].astype(CONTROL_NO_ASIGNADOS)


def validar(m: pd.DataFrame, ocupados: pd.DataFrame, sesgo: pd.DataFrame) -> None:
    """Detiene el proceso si los porcentajes o los totales no cuadran."""
    sumas = m.groupby(["carrera_generica", "nivel_titulo", "dimension"])["pct"].sum()
    asignados = ocupados[ocupados["estado"] == "asignado"]
    por_actividad = m[m["dimension"] == "actividad_economica"]
    controles = {
        "Dimensiones en catálogo": m["dimension"].isin(DIMENSIONES_P6).all(),
        "Fiabilidad en catálogo": m["fiabilidad"].isin(FIABILIDADES_P6).all(),
        "Porcentajes de cada carrera suman 100": np.isclose(sumas, 100).all(),
        "Celdas de actividad suman los asignados con rama": np.isclose(
            por_actividad["expandido_celda"].sum(), asignados.dropna(subset=["rama1"])["expr"].sum()),
        "Cada actividad tiene su sección CIIU": por_actividad["actividad_ciiu"].notna().all(),
        "Errores estándar positivos o nulos": (m["error_estandar"] >= 0).all(),
        "Control de sesgo suma 100 por dimensión": np.isclose(
            sesgo.groupby("dimension")[["pct_asignados", "pct_no_asignados"]].sum(), 100).all(),
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


def generar_p6() -> tuple[Path, Path]:
    """Construye, valida y exporta la matriz y su control de sesgo."""
    d, ocupados, psu = cargar()
    actividades = pd.read_csv(RUTA_P1, sep=";")[["actividad_caenes", "actividad_ciiu", "actividad_glosa"]].astype({"actividad_caenes": "Int64"})
    matriz = estimar(ocupados, psu, actividades)
    sesgo = comparar_no_asignados(ocupados)
    validar(matriz, ocupados, sesgo)
    ruta = DIR_SALIDA / "P6_matriz_carrera_actividad_ocupacion.csv"
    ruta_sesgo = DIR_SALIDA / "P6_matriz_carrera_actividad_ocupacion_no_asignados.csv"
    matriz.to_csv(ruta, sep=";", index=False, encoding="utf-8")
    sesgo.to_csv(ruta_sesgo, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", ruta.name, len(matriz))
    return ruta, ruta_sesgo


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    rutas = generar_p6()
    sys.path.insert(0, str(DIR_SCRAPERS / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    for ruta in rutas:
        inspeccion_rigurosa(ruta)
