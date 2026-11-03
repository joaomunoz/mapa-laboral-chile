"""
<src/Analisis/JOINS/CW_Empleabilidad_Oferta_Titulados/crosswalk.py>

Módulo de cruce (crosswalk) para el Paso 1:
Cruza `titulados_procesado.csv` con el puente P2 (`P2_puente_llaves_carrera.csv`)
utilizando estrategia de doble nivel (exacto y genérico institucional),
adsorbiendo la empleabilidad al 1er año y atributos CINE, y exportando
el resultado procesado a `Salida/oferta_empleabilidad_procesado.csv`.
"""

import logging
from pathlib import Path
import sys
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

DIR_ACTUAL = Path(__file__).resolve().parent
DIR_ANALISIS = DIR_ACTUAL.parents[1]
DIR_SCRAPERS = DIR_ANALISIS.parents[0] / "Scrapers"

# Importar normalizador
sys.path.insert(0, str(DIR_SCRAPERS / "comun"))
from normalizador import normalizar_texto  # noqa: E402

from obtener import cargar_datos_paso1
from esquema import OFERTA_EMPLEABILIDAD_ESQUEMA, VALIDACIONES_OFERTA_EMPLEABILIDAD


def ejecutar_crosswalk():
    log.info("=== INICIO CROSSWALK PASO 1: CW_Empleabilidad_Oferta_Titulados ===")

    # 1. Cargar datos
    tit, p2 = cargar_datos_paso1()

    # 2. Normalizar llaves en titulados
    log.info("Normalizando textos y claves en Titulados...")
    tit["carrera_norm"] = tit["carrera"].map(normalizar_texto)
    tit["gen_norm"] = tit["carrera_generica"].map(normalizar_texto)

    # 3. Preparar diccionarios de búsqueda desde P2
    p2["gen_norm"] = p2["carrera_generica"].map(normalizar_texto)

    # Diccionario 1: Búsqueda exacta (id_institucion, carrera_norm)
    cols_empleabilidad = [
        "empleabilidad_1er_anio",
        "nivel_match",
        "empleabilidad_fuente",
        "n_empleabilidad_asociadas",
        "anio_ultima_titulacion",
    ]

    exact_dict = p2.set_index(["id_institucion", "carrera_norm"])[cols_empleabilidad].to_dict(orient="index")

    # Diccionario 2: Búsqueda genérica institucional (id_institucion, gen_norm)
    p2_gen = p2.drop_duplicates(subset=["id_institucion", "gen_norm"])
    gen_dict = p2_gen.set_index(["id_institucion", "gen_norm"])[cols_empleabilidad].to_dict(orient="index")

    # 4. Asignar empleabilidad a cada fila de titulados
    log.info("Cruzando Titulados con Puente P2 (exacto + fallback genérico)...")
    res_empleabilidad = []
    res_nivel_match = []
    res_fuente = []
    res_asociadas = []
    res_anio_ult = []

    for _, row in tit.iterrows():
        inst = row["codigo_institucion"]
        car_norm = row["carrera_norm"]
        g_norm = row["gen_norm"]

        # Intento 1: Exacto
        match = exact_dict.get((inst, car_norm))
        if match and pd.notna(match["empleabilidad_1er_anio"]):
            res_empleabilidad.append(match["empleabilidad_1er_anio"])
            res_nivel_match.append(match["nivel_match"])
            res_fuente.append(match["empleabilidad_fuente"])
            res_asociadas.append(match["n_empleabilidad_asociadas"])
            res_anio_ult.append(match["anio_ultima_titulacion"])
            continue

        # Intento 2: Genérico institucional (residuo o genérica)
        match_gen = gen_dict.get((inst, g_norm))
        if match_gen and pd.notna(match_gen["empleabilidad_1er_anio"]):
            res_empleabilidad.append(match_gen["empleabilidad_1er_anio"])
            res_nivel_match.append(match_gen["nivel_match"])
            res_fuente.append(match_gen["empleabilidad_fuente"])
            res_asociadas.append(match_gen["n_empleabilidad_asociadas"])
            res_anio_ult.append(match_gen["anio_ultima_titulacion"])
            continue

        # Si no hay match en ninguno
        res_empleabilidad.append(np.nan)
        res_nivel_match.append("sin_dato")
        res_fuente.append("sin_dato")
        res_asociadas.append(pd.NA)
        res_anio_ult.append(pd.NA)

    tit["empleabilidad_1er_anio"] = res_empleabilidad
    tit["nivel_match"] = res_nivel_match
    tit["empleabilidad_fuente"] = res_fuente
    tit["n_empleabilidad_asociadas"] = res_asociadas
    tit["anio_ultima_titulacion"] = res_anio_ult

    # Eliminar columna auxiliar gen_norm
    tit = tit.drop(columns=["gen_norm"])

    # 5. Asegurar orden de columnas según esquema
    for col in OFERTA_EMPLEABILIDAD_ESQUEMA:
        if col not in tit.columns:
            tit[col] = pd.NA
    tit = tit[list(OFERTA_EMPLEABILIDAD_ESQUEMA)].astype(OFERTA_EMPLEABILIDAD_ESQUEMA)

    # 6. Validaciones
    log.info("Ejecutando validaciones sobre el resultado del Paso 1...")
    for desc, regla in VALIDACIONES_OFERTA_EMPLEABILIDAD:
        valido = regla(tit)
        log.info("  [✓] %s: %s", desc, valido)
        if not valido:
            raise ValueError(f"Validación fallida: {desc}")

    # 7. Exportación
    dir_salida = DIR_ACTUAL / "Salida"
    dir_salida.mkdir(parents=True, exist_ok=True)
    ruta_salida = dir_salida / "oferta_empleabilidad_procesado.csv"

    tit.to_csv(ruta_salida, index=False, sep=";", encoding="utf-8")
    log.info("CSV generado: %s (%d filas, %.2f MB)", ruta_salida.name, len(tit), ruta_salida.stat().st_size / 1024 / 1024)

    # 8. Reporte de inspección rigurosa
    try:
        sys.path.insert(0, str(DIR_SCRAPERS / "comun"))
        from inspect_data import inspeccion_rigurosa  # noqa: E402
        inspeccion_rigurosa(ruta_salida)
    except Exception as exc:
        log.warning("No se generó el reporte de inspección: %s", exc)

    log.info("=== FIN CROSSWALK PASO 1 EXITOSO ===")
    return ruta_salida


if __name__ == "__main__":
    ejecutar_crosswalk()
