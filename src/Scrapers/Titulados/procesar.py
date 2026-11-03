"""
<src/Scrapers/Titulados/procesar.py>

Módulo de procesamiento de la base de Titulados SIES.

Entrada:  Entrada/titulados_2007_2025.xlsx   (42 columnas, 234,074 filas)
Salida:   Salida/titulados_procesado.csv      (29 columnas, ~234K filas)

UNIDAD DE CONTEO (auditoría 01-11-26): SIES cuenta TITULACIONES, no personas.
Una persona puede sumar varias (licenciatura no conducente + título, técnico +
continuidad profesional, pregrado + diplomado/postítulo/posgrado). Cota inferior
del doble conteo ≈21%. Por eso se conservan `carrera_clasificacion_nivel_1`,
`tipo_plan` y `modalidad`: sin ellas no se distingue un título terminal de un
diplomado o de una continuidad. El filtro de "título que compite" se decide aguas
abajo (JOINS/), no aquí: este script preserva la información (principio ETL).

Transformaciones aplicadas:

  1. Parseo de AÑO:        'TIT_2025' → 2025 (int16)
  2. Tipado numérico:      pd.to_numeric(errors='coerce') en todas las métricas
  3. Normalización texto:  tildes, espacios, mayúsculas en claves de cruce; la región se
                           estandariza con comun.REGIONES y se agrega `codigo_region`
                           (SIES no trae código y llama distinto a O'Higgins)
  4. Código institución:   Incorporado como `codigo_institucion` (int32)
  5. Edad promedio:        Redondeada matemáticamente y convertida a entero nullable (Int16)
  6. Rangos de edad:       6 rangos quinquenales + sin información (edad AL TITULARSE);
                           titulados_mayores_40 = rango "40 y más" y titulados_menores_40
                           = total − mayores_40 se conservan por compatibilidad (P2, Paso 1)
  7. Descarte de columnas: 42 → 29 (se eliminan redundantes y legacy)
  8. Validaciones:         suma de sexos, suma de rangos de edad, rangos de valores

Esquema de salida (29 columnas):
  anio, codigo_region, nombre_region, comuna, codigo_institucion, institucion, tipo_institucion,
  carrera, carrera_generica, cine13_area, cine13_subarea, nivel_carrera,
  carrera_clasificacion_nivel_1, tipo_plan, modalidad,
  total_titulaciones, titulaciones_mujeres, titulaciones_hombres, titulaciones_nb,
  titulados_15_19, titulados_20_24, titulados_25_29, titulados_30_34,
  titulados_35_39, titulados_mayores_40, titulados_edad_sin_info, titulados_menores_40,
  edad_promedio, duracion_semestres
"""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

import pandas as pd

# Cabecera estándar del proyecto: ruta del script y fecha de actualización.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comun.normalizador import (  # noqa: E402
    codigo_region,
    normalizar_region,
    normalizar_texto,
    regiones_incoherentes,
)

log = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Configuración
# --------------------------------------------------------------------------- #
DIR_ENTRADA = Path(__file__).parent / "Entrada"
DIR_SALIDA = Path(__file__).parent / "Salida"

ARCHIVO_ENTRADA = "titulados_2007_2025.xlsx"
HOJA_ENTRADA = "in"
ARCHIVO_SALIDA = "titulados_procesado.csv"
SEPARADOR_CSV = ";"

# Columnas de entrada → salida (mapeo directo).
COLUMNAS_MANTENER = [
    "REGIÓN",
    "COMUNA",
    "CÓDIGO INSTITUCIÓN",
    "NOMBRE INSTITUCIÓN",
    "CLASIFICACIÓN INSTITUCIÓN NIVEL 1",
    "NOMBRE CARRERA",
    "ÁREA CARRERA GENÉRICA",
    "CINE-F_13 ÁREA",
    "CINE-F_13 SUBAREA",
    "CARRERA CLASIFICACIÓN NIVEL 2",
    "CARRERA CLASIFICACIÓN NIVEL 1",
    "TIPO DE PLAN DE LA CARRERA",
    "MODALIDAD",
    "TOTAL TITULACIONES",
    "TITULACIONES MUJERES POR PROGRAMA",
    "TITULACIONES HOMBRES POR PROGRAMA",
    "TITULACIONES NB E INDEFINIDO POR PROGRAMA",
    "RANGO DE EDAD 15 A 19 AÑOS",
    "RANGO DE EDAD 20 A 24 AÑOS",
    "RANGO DE EDAD 25 A 29 AÑOS",
    "RANGO DE EDAD 30 A 34 AÑOS",
    "RANGO DE EDAD 35 A 39 AÑOS",
    "RANGO DE EDAD 40 Y MÁS AÑOS",
    "RANGO DE EDAD SIN INFORMACIÓN",
    "PROMEDIO EDAD PROGRAMA",
    "DURACIÓN ESTUDIO CARRERA",
]

# Rangos de edad al titularse. En el crudo un rango vacío significa 0 titulados
# (verificado: suma de rangos con NaN=0 == TOTAL TITULACIONES en el 100% de las filas).
# "40 Y MÁS" se trata aparte en derivar_edad() porque genera mayores/menores_40.
RANGOS_EDAD_QUINQUENALES = [
    "RANGO DE EDAD 15 A 19 AÑOS",
    "RANGO DE EDAD 20 A 24 AÑOS",
    "RANGO DE EDAD 25 A 29 AÑOS",
    "RANGO DE EDAD 30 A 34 AÑOS",
    "RANGO DE EDAD 35 A 39 AÑOS",
    "RANGO DE EDAD SIN INFORMACIÓN",
]

# Columnas numéricas que deben tiparse.
COLUMNAS_NUMERICAS = [
    "CÓDIGO INSTITUCIÓN",
    "TOTAL TITULACIONES",
    "TITULACIONES MUJERES POR PROGRAMA",
    "TITULACIONES HOMBRES POR PROGRAMA",
    "TITULACIONES NB E INDEFINIDO POR PROGRAMA",
    *RANGOS_EDAD_QUINQUENALES,
    "RANGO DE EDAD 40 Y MÁS AÑOS",
    "PROMEDIO EDAD PROGRAMA",
    "DURACIÓN ESTUDIO CARRERA",
]

# Columnas categóricas (category reduce memoria ~60%).
COLUMNAS_CATEGORICAS = [
    "REGIÓN",
    "COMUNA",
    "CLASIFICACIÓN INSTITUCIÓN NIVEL 1",
    "ÁREA CARRERA GENÉRICA",
    "CINE-F_13 ÁREA",
    "CINE-F_13 SUBAREA",
    "CARRERA CLASIFICACIÓN NIVEL 2",
    "CARRERA CLASIFICACIÓN NIVEL 1",
    "TIPO DE PLAN DE LA CARRERA",
    "MODALIDAD",
]

# Renombrado final de columnas.
RENOMBRAR = {
    "AÑO": "anio",
    "REGIÓN": "nombre_region",
    "COMUNA": "comuna",
    "CÓDIGO INSTITUCIÓN": "codigo_institucion",
    "NOMBRE INSTITUCIÓN": "institucion",
    "CLASIFICACIÓN INSTITUCIÓN NIVEL 1": "tipo_institucion",
    "NOMBRE CARRERA": "carrera",
    "ÁREA CARRERA GENÉRICA": "carrera_generica",
    "CINE-F_13 ÁREA": "cine13_area",
    "CINE-F_13 SUBAREA": "cine13_subarea",
    "CARRERA CLASIFICACIÓN NIVEL 2": "nivel_carrera",
    "CARRERA CLASIFICACIÓN NIVEL 1": "carrera_clasificacion_nivel_1",
    "TIPO DE PLAN DE LA CARRERA": "tipo_plan",
    "MODALIDAD": "modalidad",
    "TOTAL TITULACIONES": "total_titulaciones",
    "TITULACIONES MUJERES POR PROGRAMA": "titulaciones_mujeres",
    "TITULACIONES HOMBRES POR PROGRAMA": "titulaciones_hombres",
    "TITULACIONES NB E INDEFINIDO POR PROGRAMA": "titulaciones_nb",
    "RANGO DE EDAD 15 A 19 AÑOS": "titulados_15_19",
    "RANGO DE EDAD 20 A 24 AÑOS": "titulados_20_24",
    "RANGO DE EDAD 25 A 29 AÑOS": "titulados_25_29",
    "RANGO DE EDAD 30 A 34 AÑOS": "titulados_30_34",
    "RANGO DE EDAD 35 A 39 AÑOS": "titulados_35_39",
    "RANGO DE EDAD 40 Y MÁS AÑOS": "titulados_mayores_40",
    "RANGO DE EDAD SIN INFORMACIÓN": "titulados_edad_sin_info",
    "PROMEDIO EDAD PROGRAMA": "edad_promedio",
    "DURACIÓN ESTUDIO CARRERA": "duracion_semestres",
}

# Columnas de rangos de edad ya renombradas (para validar que suman el total).
RANGOS_EDAD_SALIDA = [
    "titulados_15_19", "titulados_20_24", "titulados_25_29", "titulados_30_34",
    "titulados_35_39", "titulados_mayores_40", "titulados_edad_sin_info",
]

# Orden final de columnas en el CSV de salida (29 columnas).
ORDEN_SALIDA = [
    "anio", "codigo_region", "nombre_region", "comuna", "codigo_institucion", "institucion",
    "tipo_institucion", "carrera", "carrera_generica", "cine13_area", "cine13_subarea",
    "nivel_carrera", "carrera_clasificacion_nivel_1", "tipo_plan", "modalidad",
    "total_titulaciones", "titulaciones_mujeres", "titulaciones_hombres",
    "titulaciones_nb", *RANGOS_EDAD_SALIDA, "titulados_menores_40",
    "edad_promedio", "duracion_semestres",
]

# Límites de validación.
EDAD_MIN, EDAD_MAX = 15, 80
DURACION_MAX_SEMESTRES = 30


# --------------------------------------------------------------------------- #
# Carga
# --------------------------------------------------------------------------- #
def cargar_entrada() -> pd.DataFrame:
    """Lee el Excel histórico de titulados."""
    ruta = DIR_ENTRADA / ARCHIVO_ENTRADA
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta}. Ejecutar primero obtener.py."
        )
    log.info("Leyendo: %s", ruta.name)
    df = pd.read_excel(ruta, sheet_name=HOJA_ENTRADA)
    log.info("Cargado: %d filas × %d columnas", len(df), len(df.columns))
    return df


# --------------------------------------------------------------------------- #
# Transformaciones
# --------------------------------------------------------------------------- #
def parseear_anio(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte 'TIT_2025' → 2025 (int16)."""
    originales = df["AÑO"].copy()
    df["AÑO"] = (
        df["AÑO"]
        .astype(str)
        .str.extract(r"(\d{4})", expand=False)
        .astype("int16")
    )
    perdidos = (originales.notna() & df["AÑO"].isna()).sum()
    if perdidos:
        log.warning("AÑO no parseado en %d filas", perdidos)
    log.info("AÑO parseado: rango [%d, %d]", df["AÑO"].min(), df["AÑO"].max())
    return df


def limpiar_numericas(df: pd.DataFrame) -> pd.DataFrame:
    """Fuerza tipado numérico; 's/i', '', '-' → NaN."""
    for col in COLUMNAS_NUMERICAS:
        antes = df[col].dtype
        df[col] = pd.to_numeric(df[col], errors="coerce")
        nulos = df[col].isna().sum()
        log.info("  %-42s %s → %s  (%d nulos)",
                 col, antes, df[col].dtype, nulos)
    return df


def limpiar_texto(df: pd.DataFrame) -> pd.DataFrame:
    """Trim + colapso de espacios en columnas de texto."""
    text_cols = ["NOMBRE INSTITUCIÓN", "NOMBRE CARRERA"] + COLUMNAS_CATEGORICAS
    for col in text_cols:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace(r"\s+", " ", regex=True)
                .str.strip()
            )
            df[col] = df[col].replace({"nan": pd.NA, "None": pd.NA, "": pd.NA})
    log.info("Texto limpiado en %d columnas", len(text_cols))
    return df


def normalizar_claves_cruce(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica normalizar_texto() a las columnas que serán claves de cruce
    con otras fuentes (MiFuturo, ENADEL): region y carrera_generica.
    """
    df["ÁREA CARRERA GENÉRICA"] = df["ÁREA CARRERA GENÉRICA"].apply(lambda x: normalizar_texto(x) if pd.notna(x) else x)
    df["REGIÓN"] = df["REGIÓN"].apply(normalizar_region)
    df["codigo_region"] = df["REGIÓN"].map(codigo_region).astype("int8")
    log.info("Claves de cruce normalizadas: REGIÓN, ÁREA CARRERA GENÉRICA")
    return df


def derivar_edad(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera titulados_mayores_40 y titulados_menores_40 asegurando suma exacta.
    """
    df["RANGO DE EDAD 40 Y MÁS AÑOS"] = (
        df["RANGO DE EDAD 40 Y MÁS AÑOS"]
        .fillna(0)
        .clip(lower=0)
        .astype("int32")
    )

    df["titulados_menores_40"] = (
        df["TOTAL TITULACIONES"].astype("int64")
        - df["RANGO DE EDAD 40 Y MÁS AÑOS"].astype("int64")
    ).clip(lower=0).astype("int32")

    df["RANGO DE EDAD 40 Y MÁS AÑOS"] = (
        df["TOTAL TITULACIONES"].astype("int64")
        - df["titulados_menores_40"].astype("int64")
    ).astype("int32")

    n_mayores = (df["RANGO DE EDAD 40 Y MÁS AÑOS"] > 0).sum()
    log.info(
        "Edad derivada: %d filas con mayores_40 > 0 (%.1f%%)",
        n_mayores, 100 * n_mayores / len(df),
    )
    return df


def cast_final(df: pd.DataFrame) -> pd.DataFrame:
    """Asigna tipos finales óptimos antes del renombrado."""
    # Código institución
    df["CÓDIGO INSTITUCIÓN"] = df["CÓDIGO INSTITUCIÓN"].fillna(0).astype("int32")

    # Enteros compactos (NaN = 0 titulados en el crudo, ver RANGOS_EDAD_QUINQUENALES)
    for col in ["TOTAL TITULACIONES", "TITULACIONES MUJERES POR PROGRAMA",
                "TITULACIONES HOMBRES POR PROGRAMA",
                "TITULACIONES NB E INDEFINIDO POR PROGRAMA",
                *RANGOS_EDAD_QUINQUENALES,
                "RANGO DE EDAD 40 Y MÁS AÑOS"]:
        df[col] = df[col].fillna(0).astype("int32")

    # Edad promedio: redondear y convertir a entero nullable (Int16) para preservar NaN
    df["PROMEDIO EDAD PROGRAMA"] = (
        df["PROMEDIO EDAD PROGRAMA"]
        .round()
        .astype("Int16")
    )

    # Duración semestres
    df["DURACIÓN ESTUDIO CARRERA"] = df["DURACIÓN ESTUDIO CARRERA"].astype("float32")

    # Categorías
    for col in COLUMNAS_CATEGORICAS:
        if col in df.columns:
            df[col] = df[col].astype("category")

    return df


# --------------------------------------------------------------------------- #
# Validaciones
# --------------------------------------------------------------------------- #
def validar(df: pd.DataFrame) -> None:
    """Ejecuta las validaciones de integridad y reporta resultados (post-renombrado)."""
    total = len(df)
    log.info("=== Validaciones (%d filas) ===", total)

    # 1. Suma de sexos == total
    suma_sexos = (
        df["titulaciones_mujeres"].fillna(0)
        + df["titulaciones_hombres"].fillna(0)
        + df["titulaciones_nb"].fillna(0)
    )
    ok_sexos = (df["total_titulaciones"] == suma_sexos).mean()
    log.info("  [✓] total == sumatoria sexos        : %.1f%%", 100 * ok_sexos)

    # 2. mayores_40 + menores_40 == total
    ok_edad = (
        df["titulados_mayores_40"] + df["titulados_menores_40"]
        == df["total_titulaciones"]
    ).mean()
    log.info("  [✓] mayores40 + menores40 == total  : %.1f%%", 100 * ok_edad)

    # 2b. Los 7 rangos de edad suman el total (falla: si no, la edad no es usable aguas abajo)
    ok_rangos = (df[RANGOS_EDAD_SALIDA].sum(axis=1) == df["total_titulaciones"]).mean()
    log.info("  [%s] suma de 7 rangos de edad == total: %.1f%%",
             "✓" if ok_rangos == 1 else "✗", 100 * ok_rangos)
    if ok_rangos < 1:
        raise ValueError(f"Rangos de edad no suman el total en {100 * (1 - ok_rangos):.2f}% de las filas")

    # 2c. Las 3 columnas de clasificación conservan las categorías oficiales del glosario
    for col, esperadas in [("carrera_clasificacion_nivel_1", 10), ("tipo_plan", 3), ("modalidad", 3)]:
        n = df[col].nunique(dropna=True)
        log.info("  [%s] %-30s: %d categorías (glosario ≤%d), %.1f%% nulos",
                 "✓" if n <= esperadas else "⚠", col, n, esperadas, 100 * df[col].isna().mean())

    # 2d. Región coherente con la fuente única
    incoherentes = regiones_incoherentes(df["codigo_region"], df["nombre_region"].astype(str))
    n_regiones = df["codigo_region"].nunique()
    log.info("  [%s] codigo_region y nombre (%d/16)    : %d incoherentes",
             "✓" if incoherentes == 0 and n_regiones == 16 else "✗", n_regiones, incoherentes)
    if incoherentes or n_regiones != 16:
        raise ValueError(f"Regiones inválidas: {incoherentes} incoherentes, {n_regiones}/16")

    # 3. totales no negativos
    negativos = (df["total_titulaciones"] < 0).sum()
    log.info("  [%s] total_titulaciones >= 0         : %d negativos",
             "✓" if negativos == 0 else "✗", negativos)

    # 4. edad_promedio en rango razonable (enteros)
    edad_ok = df["edad_promedio"].dropna()
    fuera_rango = ((edad_ok < EDAD_MIN) | (edad_ok > EDAD_MAX)).sum()
    log.info("  [%s] edad_promedio en [%d, %d]       : %d fuera de rango",
             "✓" if fuera_rango == 0 else "⚠",
             EDAD_MIN, EDAD_MAX, fuera_rango)

    # 5. duración en rango
    dur = df["duracion_semestres"].dropna()
    dur_mala = (dur <= 0).sum() + (dur > DURACION_MAX_SEMESTRES).sum()
    log.info("  [%s] duracion_semestres (0, %d]       : %d fuera de rango",
             "✓" if dur_mala == 0 else "⚠",
             DURACION_MAX_SEMESTRES, dur_mala)

    # 6. Duplicados en clave lógica
    clave = ["anio", "codigo_region", "comuna", "codigo_institucion", "carrera"]
    duplicados = df.duplicated(subset=clave).sum()
    log.info("  [%s] Sin duplicados en clave          : %d duplicados",
             "✓" if duplicados == 0 else "⚠", duplicados)

    # 7. Cobertura general
    log.info("  Cobertura por columna:")
    for col in df.columns:
        n = df[col].notna().sum()
        pct = 100 * n / total
        flag = "🟢" if pct >= 99 else ("🟡" if pct >= 90 else "🔴")
        log.info("    %s %-32s %6.1f%%", flag, col, pct)


# --------------------------------------------------------------------------- #
# Orquestador
# --------------------------------------------------------------------------- #
def procesar_titulados() -> Path:
    """
    Pipeline completo de procesamiento de Titulados.

    Returns:
        Ruta del CSV generado en Salida/.
    """
    df = cargar_entrada()

    # Seleccionar solo las columnas necesarias
    columnas_entrada = ["AÑO"] + COLUMNAS_MANTENER
    faltantes = [c for c in columnas_entrada if c not in df.columns]
    if faltantes:
        raise KeyError(f"Columnas faltantes en el Excel: {faltantes}")
    df = df[columnas_entrada].copy()
    log.info("Selección de columnas: 42 → %d", len(df.columns))

    # Transformaciones
    df = parseear_anio(df)
    df = limpiar_numericas(df)
    df = limpiar_texto(df)
    df = normalizar_claves_cruce(df)
    df = derivar_edad(df)
    df = cast_final(df)

    # Renombrar al esquema final
    df = df.rename(columns=RENOMBRAR)

    # Orden de columnas
    df = df[ORDEN_SALIDA]

    # Validaciones
    validar(df)

    # Exportar
    DIR_SALIDA.mkdir(parents=True, exist_ok=True)
    destino = DIR_SALIDA / ARCHIVO_SALIDA
    df.to_csv(destino, sep=SEPARADOR_CSV, index=False, encoding="utf-8")
    peso_mb = destino.stat().st_size / (1024 * 1024)
    log.info("CSV generado: %s (%d filas, %d columnas, %.1f MB)",
             destino, len(df), len(df.columns), peso_mb)
    return destino


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ruta = procesar_titulados()

    # Resumen final
    df = pd.read_csv(ruta, sep=SEPARADOR_CSV)
    print("\n=== Titulados SIES — Procesado ===")
    print(f"Archivo : {ruta}")
    print(f"Filas   : {len(df):,}")
    print(f"Columnas: {len(df.columns)}")
    print(f"Años    : {df['anio'].min()} – {df['anio'].max()}")
    print(f"Regiones: {df['codigo_region'].nunique()}")
    print(f"Carreras: {df['carrera_generica'].nunique()} genéricas / "
          f"{df['carrera'].nunique()} específicas")
    print(f"Instituciones: {df['institucion'].nunique()} ({df['codigo_institucion'].nunique()} códigos únicos)")
    print(f"\nTotal titulaciones: {df['total_titulaciones'].sum():,}")
    print(f"Mayores 40        : {df['titulados_mayores_40'].sum():,}")
    print(f"Edad promedio gral: {df['edad_promedio'].mean():.1f} años")
