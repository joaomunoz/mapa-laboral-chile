"""
<src/Analisis/JOINS/Concentracion_Region_Actividad_Censo/crosswalk.py>

Mide qué actividades concentra cada región con el Censo 2024, y la contrasta con ENE de los mismos meses del
censo, marzo a julio de 2024 (comun/periodos.py; hasta el 08-11-26 era ENE 2025-2026).

Salida: Salida/concentracion_region_actividad_censo.csv

Decisiones (aprobadas el 03-11-26):
  - Censo como capa principal: cubre todas las regiones y actividades, mientras ENE deja sin muestra 112 de 336.
    ENE se conserva como contraste, sin mezclar sus cifras con las del censo.
  - Lectura por umbrales: sin error de muestreo no sirve la regla de ENE, que comparaba un rango con 1.
    concentra desde 1,2 veces y bajo_lo_nacional hasta 0,8. Son criterios de trabajo, no un estándar externo.
  - Los umbrales se aplican al peso redondeado a 2 decimales, la cifra que se publica (06-11-26). Más precisión
    sería falsa: solo los ocupados sin región de trabajo mueven el peso más que eso. Con el valor completo, un
    0,8008 quedaba como similar aunque se lea 0,80. peso_relativo se guarda completo.
  - base_pequena bajo 60 personas: un peso relativo con tan pocas personas no describe a la región.
  - U queda fuera de la lista del mapa: son unas 2.800 personas, y hacía que la Metropolitana apareciera
    concentrando embajadas y organismos internacionales en lugar de Finanzas.
  - Alerta: el peso nacional de algunas actividades difiere mucho entre fuentes. En Minería, el censo calza con
    las mediciones de alcance amplio y ENE queda por debajo, quizá por cómo clasifica a los contratistas.
    La causa no está comprobada. Con los mismos meses del censo la diferencia sigue (08-11-26): Minería pesa
    3,63% en el censo y 1,54% en ENE de marzo a julio de 2024 (1,67% en ENE 2025-2026), así que la fecha no la
    explica. Las seis actividades con alerta son las mismas con ambos periodos.
  - U también queda con alerta desde el 08-11-26 (0,04% en el censo y 0,02% en ENE). No cambia el mapa: U no
    se muestra.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers"))
from comun.normalizador import REGIONES  # noqa: E402
from esquema import CONCENTRACION_REGION_ACTIVIDAD_CENSO  # noqa: E402
import obtener  # noqa: E402

log = logging.getLogger(__name__)

RUTA_SALIDA = Path(__file__).parent / "Salida" / "concentracion_region_actividad_censo.csv"
UMBRAL_CONCENTRA, UMBRAL_BAJO, BASE_MINIMA = 1.2, 0.8, 60
DECIMALES_PESO = 2   # Los umbrales se comparan con el peso publicado, no con el completo.
RAZON_FUENTES = 1.3
ACTIVIDADES_FUERA_DEL_MAPA = ["U"]
OCUPADO = 1
N_REGIONES, N_ACTIVIDADES = 16, 21
ACTIVIDADES_CON_ALERTA = {"B", "D", "N", "O", "P", "Q", "U"}
OCUPADOS_VALIDOS_ESPERADOS = 7_395_105  # Medido en la auditoría de censo_procesado.csv


def construir(censo: pd.DataFrame, actividades: pd.DataFrame, ene: pd.DataFrame) -> pd.DataFrame:
    ocupados = censo[censo["sit_fuerza_trabajo"] == OCUPADO]
    validos = ocupados.dropna(subset=["codigo_region_trabajo", "actividad_ciiu"])
    t = (validos.groupby(["codigo_region_trabajo", "actividad_ciiu"], as_index=False)["personas"].sum()
         .rename(columns={"codigo_region_trabajo": "codigo_region", "personas": "ocupados"}))
    t["codigo_region"] = t["codigo_region"].astype(int)
    t = t.merge(actividades, on="actividad_ciiu", how="left", validate="many_to_one")
    t["nombre_region"] = t["codigo_region"].map(REGIONES)
    t["pct_en_region"] = 100 * t["ocupados"] / t.groupby("codigo_region")["ocupados"].transform("sum")
    t["pct_nacional"] = 100 * t.groupby("actividad_ciiu")["ocupados"].transform("sum") / t["ocupados"].sum()
    t["peso_relativo"] = t["pct_en_region"] / t["pct_nacional"]
    # round() de Python, el mismo que usa el mapa: np.round puede diferir en el último decimal.
    publicado = t["peso_relativo"].map(lambda v: round(v, DECIMALES_PESO))
    t["lectura"] = np.select([t["ocupados"] < BASE_MINIMA, publicado >= UMBRAL_CONCENTRA, publicado <= UMBRAL_BAJO],
                             ["base_pequena", "concentra", "bajo_lo_nacional"], "similar")
    t["pct_poblacion_15_mas"] = 100 * t["ocupados"] / t["codigo_region"].map(censo.groupby("codigo_region")["personas"].sum())
    con_actividad = ocupados.dropna(subset=["actividad_ciiu"])
    sin_region = con_actividad[con_actividad["codigo_region_trabajo"].isna()].groupby("actividad_ciiu")["personas"].sum()
    t["pct_sin_region_trabajo"] = 100 * t["actividad_ciiu"].map(sin_region).fillna(0) / t["actividad_ciiu"].map(con_actividad.groupby("actividad_ciiu")["personas"].sum())
    e = ene.rename(columns={"ocupados": "ene_ocupados", "peso_relativo": "ene_peso_relativo", "lectura": "ene_lectura", "pct_nacional": "ene_pct_nacional"})
    t = t.merge(e, on=["codigo_region", "actividad_caenes"], how="left", validate="one_to_one")
    razon = t["pct_nacional"] / t["ene_pct_nacional"]
    t["alerta_difiere_fuente"] = (razon >= RAZON_FUENTES) | (razon <= 1 / RAZON_FUENTES)
    t["mostrar_en_mapa"] = ~t["actividad_ciiu"].isin(ACTIVIDADES_FUERA_DEL_MAPA)
    return (t[list(CONCENTRACION_REGION_ACTIVIDAD_CENSO)].astype(CONCENTRACION_REGION_ACTIVIDAD_CENSO)
            .sort_values(["codigo_region", "actividad_caenes"]).reset_index(drop=True))


def validar(t: pd.DataFrame, censo: pd.DataFrame) -> None:
    """Detiene el proceso si la tabla no cuadra con el censo o cambia el conjunto de alertas."""
    fila = t[(t["codigo_region"] == 2) & (t["actividad_ciiu"] == "B")].iloc[0]
    con_alerta = set(t.loc[t["alerta_difiere_fuente"], "actividad_ciiu"])
    controles = {
        "336 filas con clave única": len(t) == N_REGIONES * N_ACTIVIDADES and not t.duplicated(["codigo_region", "actividad_caenes"]).any(),
        "Nombres completos": t[["nombre_region", "actividad_ciiu", "actividad_glosa", "actividad_caenes"]].notna().all().all(),
        "Ocupados iguales al censo procesado": int(t["ocupados"].sum()) == OCUPADOS_VALIDOS_ESPERADOS,
        "pct_en_region suma 100 en cada región": np.isclose(t.groupby("codigo_region")["pct_en_region"].sum(), 100).all(),
        "pct_nacional suma 100 en cada región": np.isclose(t.groupby("codigo_region")["pct_nacional"].sum(), 100).all(),
        "Contraste con ENE completo": t["ene_ocupados"].notna().all() and t["ene_lectura"].notna().all(),
        "Alertas: B, D, N, O, P, Q y U": con_alerta == ACTIVIDADES_CON_ALERTA,
        "Solo U queda fuera de la lista del mapa": set(t.loc[~t["mostrar_en_mapa"], "actividad_ciiu"]) == set(ACTIVIDADES_FUERA_DEL_MAPA),
        "Antofagasta en Minería: 101.929 ocupados": fila["ocupados"] == 101_929 and fila["lectura"] == "concentra",
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    log.info("  [i] Lectura: %s", t["lectura"].value_counts().to_dict())
    log.info("  [i] Actividades concentra por región: %s", t[t["lectura"] == "concentra"].groupby("nombre_region").size().to_dict())
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    censo = obtener.cargar_censo()
    tabla = construir(censo, obtener.cargar_actividades(), obtener.cargar_ene())
    validar(tabla, censo)
    RUTA_SALIDA.parent.mkdir(exist_ok=True)
    tabla.to_csv(RUTA_SALIDA, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", RUTA_SALIDA.name, len(tabla))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(RUTA_SALIDA)
