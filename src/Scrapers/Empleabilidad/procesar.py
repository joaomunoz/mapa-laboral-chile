"""
<src/Scrapers/Empleabilidad/procesar.py>
Actualizado 30-10-26 17:15

Módulo de procesamiento de la base de Empleabilidad (MiFuturo).

Entrada:  Entrada/empleabilidad_mifuturo.csv   (30 columnas, 1,690 filas)
Salida:   Salida/empleabilidad_procesado.csv      (23 columnas, 1,690 filas)

Transformaciones aplicadas:
  1. Selección de columnas:  Se conservan 23 columnas clave (según esquema.py).
  2. Empleabilidad (%):      Multiplicada por 100 (ej. 0.884 → 88.4 float64).
  3. Ingresos y percentiles: Redondeados a enteros puros (Int64 nullable).
  4. Normalización texto:    Trim, espacios y normalización de tildes/mayúsculas.
  5. Validaciones:           Rangos de empleabilidad [0.0, 100.0], no negativos.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

# Cabecera estándar del proyecto: ruta del script y fecha de actualización.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comun.normalizador import normalizar_texto  # noqa: E402
from Empleabilidad.esquema import ESQUEMA_EMPLEABILIDAD  # noqa: E402

log = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Configuración
# --------------------------------------------------------------------------- #
DIR_ENTRADA = Path(__file__).parent / "Entrada"
DIR_SALIDA = Path(__file__).parent / "Salida"

ARCHIVO_ENTRADA = "empleabilidad_mifuturo.csv"
ARCHIVO_SALIDA = "empleabilidad_procesado.csv"
SEPARADOR_CSV = ";"

COLUMNAS_SALIDA = list(ESQUEMA_EMPLEABILIDAD.keys())

COLUMNAS_EMPLEABILIDAD = [
    "empleabilidad_1er_anio",
    "empleabilidad_2do_anio",
]

COLUMNAS_INGRESOS_PERCENTILES = [
    "ingreso_medio_1er_anio",
    "ingreso_medio_2do_anio",
    "ingreso_medio_3er_anio",
    "ingreso_medio_4to_anio",
    "ingreso_medio_5to_anio",
    "percentil_10_anio_1",
    "percentil_25_anio_1",
    "percentil_50_anio_1",
    "percentil_75_anio_1",
    "percentil_90_anio_1",
    "percentil_10_anio_5",
    "percentil_25_anio_5",
    "percentil_50_anio_5",
    "percentil_75_anio_5",
    "percentil_90_anio_5",
]


# --------------------------------------------------------------------------- #
# Carga
# --------------------------------------------------------------------------- #
def cargar_entrada() -> pd.DataFrame:
    """Lee el CSV crudo de empleabilidad MiFuturo."""
    ruta = DIR_ENTRADA / ARCHIVO_ENTRADA
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta}. Ejecutar primero obtener.py."
        )
    log.info("Leyendo: %s", ruta.name)
    df = pd.read_csv(ruta, sep=SEPARADOR_CSV)
    log.info("Cargado: %d filas × %d columnas", len(df), len(df.columns))
    return df


# --------------------------------------------------------------------------- #
# Transformaciones
# --------------------------------------------------------------------------- #
def limpiar_texto(df: pd.DataFrame) -> pd.DataFrame:
    """Trim y normalización de textos en columnas categóricas."""
    text_cols = ["institucion", "tipo_institucion", "carrera", "carrera_generica", "regiones_sede"]
    for col in text_cols:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace(r"\\s+", " ", regex=True)
                .str.strip()
            )
            df[col] = df[col].replace({"nan": pd.NA, "None": pd.NA, "": pd.NA})
    log.info("Texto limpiado en columnas categóricas.")
    return df


def normalizar_claves_cruce(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica normalización a institucion, carrera_generica y regiones_sede."""
    for col in ["institucion", "carrera_generica", "regiones_sede"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: normalizar_texto(x) if pd.notna(x) else x)
    log.info("Claves de cruce normalizadas: institucion, carrera_generica, regiones_sede")
    return df


def transformar_tipos(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica las transformaciones de tipo según esquema.py."""
    # id_institucion
    df["id_institucion"] = pd.to_numeric(df["id_institucion"], errors="coerce").fillna(0).astype("int64")

    # Empleabilidad: multiplicar por 100 y redondear a 1 decimal (ej. 0.884 → 88.4)
    for col in COLUMNAS_EMPLEABILIDAD:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce") * 100.0
            df[col] = df[col].round(1).astype("float64")

    # Ingresos y percentiles: redondear a enteros (Int64 nullable)
    for col in COLUMNAS_INGRESOS_PERCENTILES:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").round().astype("Int64")

    log.info("Tipos transformados según esquema oficial.")
    return df


# --------------------------------------------------------------------------- #
# Validaciones
# --------------------------------------------------------------------------- #
def validar(df: pd.DataFrame) -> None:
    """Ejecuta validaciones de integridad sobre el dataset procesado."""
    total = len(df)
    log.info("=== Validaciones Empleabilidad (%d filas) ===", total)

    # 1. Empleabilidad en rango [0.0, 100.0]
    for col in COLUMNAS_EMPLEABILIDAD:
        if col in df.columns:
            s = df[col].dropna()
            invalidos = ((s < 0.0) | (s > 100.0)).sum()
            log.info("  [%s] %s en [0, 100]           : %d inválidos",
                     "✓" if invalidos == 0 else "✗", col, invalidos)

    # 2. Ingresos no negativos
    for col in COLUMNAS_INGRESOS_PERCENTILES:
        if col in df.columns:
            s = df[col].dropna()
            negativos = (s < 0).sum()
            if negativos > 0:
                log.warning("  [⚠] %s tiene %d valores negativos", col, negativos)

    # 3. Duplicados
    clave = ["id_institucion", "carrera"]
    duplicados = df.duplicated(subset=clave).sum() if all(c in df.columns for c in clave) else 0
    log.info("  [%s] Duplicados en clave (id, carrera) : %d",
             "✓" if duplicados == 0 else "⚠", duplicados)

    # 4. Cobertura general
    log.info("  Cobertura por columna:")
    for col in df.columns:
        n = df[col].notna().sum()
        pct = 100 * n / total
        flag = "🟢" if pct >= 99 else ("🟡" if pct >= 90 else "🔴")
        log.info("    %s %-30s %6.1f%%", flag, col, pct)


# --------------------------------------------------------------------------- #
# Orquestador
# --------------------------------------------------------------------------- #
def procesar_empleabilidad() -> Path:
    """
    Pipeline completo de procesamiento de Empleabilidad (MiFuturo).

    Returns:
        Ruta del CSV generado en Salida/.
    """
    df = cargar_entrada()

    # Seleccionar columnas necesarias según esquema
    faltantes = [c for c in COLUMNAS_SALIDA if c not in df.columns]
    if faltantes:
        raise KeyError(f"Columnas faltantes en el CSV de entrada: {faltantes}")
    
    df = df[COLUMNAS_SALIDA].copy()
    log.info("Selección de columnas: 30 → %d", len(df.columns))

    # Transformaciones
    df = limpiar_texto(df)
    df = normalizar_claves_cruce(df)
    df = transformar_tipos(df)

    # Validaciones
    validar(df)

    # Exportar
    DIR_SALIDA.mkdir(parents=True, exist_ok=True)
    destino = DIR_SALIDA / ARCHIVO_SALIDA
    df.to_csv(destino, sep=SEPARADOR_CSV, index=False, encoding="utf-8")
    peso_mb = destino.stat().st_size / (1024 * 1024)
    log.info("CSV generado: %s (%d filas, %d columnas, %.2f MB)",
             destino, len(df), len(df.columns), peso_mb)
    return destino


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ruta = procesar_empleabilidad()

    # Resumen final
    df = pd.read_csv(ruta, sep=SEPARADOR_CSV)
    print("\\n=== Empleabilidad MiFuturo — Procesado ===")
    print(f"Archivo : {ruta}")
    print(f"Filas   : {len(df):,}")
    print(f"Columnas: {len(df.columns)}")
    print(f"Instituciones: {df['institucion'].nunique()}")
    print(f"Carreras genéricas: {df['carrera_generica'].nunique()}")
    print(f"Empleabilidad 1° año promedio: {df['empleabilidad_1er_anio'].mean():.1f}%")
    print(f"Ingreso medio 1° año promedio: ${df['ingreso_medio_1er_anio'].mean():,.0f}")
