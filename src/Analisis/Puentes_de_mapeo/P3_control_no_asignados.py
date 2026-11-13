"""
<src/Analisis/Puentes_de_mapeo/P3_control_no_asignados.py>

Generador del control de sesgo de P3, y fuente de las funciones de error y fiabilidad que usa P4.

Entradas: src/Scrapers/CASEN/Salida/casen_procesado.csv  (personas con educación superior)
          Salida/P2_puente_carrera_casen.csv             (texto → carrera_generica)
Salida:   Salida/P3_control_no_asignados.csv

Compara a los ocupados con título que tienen carrera asignada con quienes no la tienen: si difieren,
lo medido por carrera puede estar sesgado.

La matriz carrera × actividad × ocupación se retiró porque ninguna tabla la leía: P4 mide el perfil por su
cuenta. Se recupera con (la ruta lleva P6, el nombre que tenía este puente hasta el 13-11-26): git show e1a7160:src/Analisis/Puentes_de_mapeo/Salida/P6_matriz_carrera_actividad_ocupacion.csv

Varianza: linealización de Taylor de la razón p = Y/X, con estratos varstrat y conglomerados
varunit (libro de códigos CASEN), con reemplazo en la primera etapa.
Estándar INE aplicado: no fiable si n de la carrera < 60, gl < 9 o CV > 30%; poco fiable si
CV entre 15% y 30%; fiable en otro caso. gl = conglomerados - estratos de la carrera.

Esquema: esquema.py (CONTROL_NO_ASIGNADOS)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from esquema import CONTROL_NO_ASIGNADOS  # noqa: E402

log = logging.getLogger(__name__)

DIR_SCRAPERS = Path(__file__).resolve().parents[2] / "Scrapers"
DIR_SALIDA = Path(__file__).parent / "Salida"
RUTA_CASEN = DIR_SCRAPERS / "CASEN" / "Salida" / "casen_procesado.csv"
RUTA_P2 = DIR_SALIDA / "P2_puente_carrera_casen.csv"

N_MINIMO, GL_MINIMO, CV_FIABLE, CV_MAXIMO = 60, 9, 15.0, 30.0


def cargar() -> pd.DataFrame:
    """Une CASEN con P2 y devuelve a los ocupados con título."""
    casen = pd.read_csv(RUTA_CASEN, sep=";", low_memory=False, dtype={"oficio4_08": "object", "rama4": "object"})
    p5 = pd.read_csv(RUTA_P2, sep=";")[["e6a", "carrera_normalizada", "estado"]]
    d = casen.merge(p5, on=["e6a", "carrera_normalizada"], how="left", validate="many_to_one")
    if d["estado"].isna().any():
        raise ValueError("Hay textos de CASEN que no están en P2: regenerar P2.")
    # CIUO-08 con la numeración de ENE (b1): FF.AA. es 10 aquí y 0 en CASEN.
    d["grupo_ocupacion"] = d["oficio1_08"].replace(0, 10).astype("Int64")
    return d[(d["activ"] == 1) & d["titulo_comun"].notna()].copy()


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


def comparar_no_asignados(d: pd.DataFrame) -> pd.DataFrame:
    """Compara a quienes tienen carrera y a quienes no: si difieren, lo medido por carrera puede estar sesgado."""
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


def validar(sesgo: pd.DataFrame) -> None:
    """Detiene el proceso si los porcentajes no cuadran."""
    if not np.isclose(sesgo.groupby("dimension")[["pct_asignados", "pct_no_asignados"]].sum(), 100).all():
        raise ValueError("El control de sesgo no suma 100 por dimensión")
    log.info("  [✓] Control de sesgo suma 100 por dimensión")


def generar_p6() -> Path:
    """Construye, valida y exporta el control de sesgo."""
    sesgo = comparar_no_asignados(cargar())
    validar(sesgo)
    ruta = DIR_SALIDA / "P3_control_no_asignados.csv"
    sesgo.to_csv(ruta, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", ruta.name, len(sesgo))
    return ruta


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ruta = generar_p6()
    sys.path.insert(0, str(DIR_SCRAPERS / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(ruta)
