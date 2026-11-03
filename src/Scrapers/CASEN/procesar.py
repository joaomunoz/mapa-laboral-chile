"""
<src/Scrapers/CASEN/procesar.py>
Actualizado 02-11-26 11:32

Módulo de procesamiento de CASEN 2024 (Ministerio de Desarrollo Social y Familia).

Entrada:  Entrada/casen_2024.dta       (218,367 personas × 877 columnas)
Salida:   Salida/casen_procesado.csv   (61,070 personas con educación superior, 26 columnas)

Transformaciones: proyección de columnas, filtro a e6a 12-15, expr a float64, sentinelas a NA,
códigos con cero a la izquierda, codigo_region/nombre_region, titulo_comun y carrera_normalizada.

Las validaciones detienen el proceso si fallan: un error aquí (como el desborde de expr) se
propagaría sin aviso a todas las estimaciones que usen esta tabla.

Esquema: esquema.py (ESQUEMA_CASEN)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from CASEN.esquema import (  # noqa: E402
    CLAVE_CASEN,
    COLUMNAS_CON_SENTINELAS,
    COLUMNAS_ENTRADA,
    ESQUEMA_CASEN,
    SENTINELAS,
    TEXTOS_EXCLUIDOS,
    TITULO_POR_E6A,
)
from comun.normalizador import REGIONES, normalizar_texto, regiones_incoherentes  # noqa: E402

log = logging.getLogger(__name__)

RUTA_ENTRADA = Path(__file__).parent / "Entrada" / "casen_2024.dta"
RUTA_SALIDA = Path(__file__).parent / "Salida" / "casen_procesado.csv"

# Conteos medidos en la base 2024: si cambian, la base o la lectura no son las esperadas.
PERSONAS_ESPERADAS = 218_367
FILAS_ESPERADAS = 61_070
POBLACION_ESPERADA = 20_131_682


def codigo_con_ceros(serie: pd.Series) -> pd.Series:
    """Pasa un código numérico a texto de 4 dígitos (110 → "0110"), conservando NA."""
    return serie.round().astype("Int64").astype("string").str.zfill(4).astype(object)


def cargar() -> tuple[pd.DataFrame, dict[str, float]]:
    """Lee la base y devuelve también los totales previos al filtro, para validar."""
    if not RUTA_ENTRADA.exists():
        raise FileNotFoundError(f"No se encontró {RUTA_ENTRADA}. Ejecutar primero obtener.py.")
    crudo = pd.read_stata(RUTA_ENTRADA, columns=COLUMNAS_ENTRADA, convert_categoricals=False)
    # Antes de cualquier suma: expr int16 se desborda en groupby.
    crudo["expr"] = crudo["expr"].astype("float64")
    totales = {
        "personas": len(crudo),
        "poblacion": crudo["expr"].sum(),
        "ocupados": crudo.loc[crudo["activ"] == 1, "expr"].sum(),
    }
    log.info("Leído: %d personas, población %.0f, ocupados %.0f",
             totales["personas"], totales["poblacion"], totales["ocupados"])
    return crudo, totales


def preparar(crudo: pd.DataFrame) -> pd.DataFrame:
    """Filtra a educación superior y construye la tabla del esquema."""
    df = crudo[crudo["e6a"].isin(TITULO_POR_E6A)].copy()

    tratadas = 0
    for col in COLUMNAS_CON_SENTINELAS:
        mascara = df[col].isin(SENTINELAS)
        tratadas += int(mascara.sum())
        df[col] = df[col].mask(mascara)
    log.info("Sentinelas tratadas: %d valores → NA", tratadas)

    df["codigo_region"] = df["region"].astype("int64")
    df["nombre_region"] = df["codigo_region"].map(REGIONES)
    df["titulo_comun"] = df["e6a"].map(TITULO_POR_E6A).where(df["e6c_completo"] == 1)
    df["e7"] = df["e7"].str.strip()
    df["carrera_normalizada"] = df["e7"].map(normalizar_texto)
    df["oficio4_08"] = codigo_con_ceros(df["oficio4_08"])
    df["rama4"] = codigo_con_ceros(df["rama4"])

    df = df[list(ESQUEMA_CASEN)].copy()
    for col, dtype in ESQUEMA_CASEN.items():
        if dtype in ("Int64", "int64"):
            df[col] = df[col].round().astype(dtype)
        else:
            df[col] = df[col].astype(dtype)
    return df.reset_index(drop=True)


def validar(df: pd.DataFrame, totales: dict[str, float]) -> None:
    """Ejecuta los controles y detiene el proceso ante cualquier falla."""
    ocupados = df["activ"] == 1
    primer_digito = df["oficio4_08"].dropna().str[0].astype(int)
    con_oficio = df.loc[primer_digito.index, "oficio1_08"]
    numericas = df.select_dtypes("number")
    controles = {
        "Personas en la base": totales["personas"] == PERSONAS_ESPERADAS,
        "Población expandida (expr sin desborde)": round(totales["poblacion"]) == POBLACION_ESPERADA,
        "Filas de educación superior": len(df) == FILAS_ESPERADAS,
        "Clave (folio, id_persona) única": not df.duplicated(CLAVE_CASEN).any(),
        "Regiones 1-16 coherentes": df["codigo_region"].nunique() == 16
            and regiones_incoherentes(df["codigo_region"], df["nombre_region"]) == 0,
        "expr decimal y positivo": df["expr"].dtype == "float64" and (df["expr"] > 0).all(),
        "Sin sentinelas residuales": not numericas.isin(SENTINELAS).any().any(),
        "e7 presente en todas las filas": df["e7"].ne("").all(),
        "Título solo con nivel completo": df["titulo_comun"].notna().eq(df["e6c_completo"].eq(1).fillna(False)).all(),
        "oficio4_08 coherente con oficio1_08": con_oficio.eq(primer_digito).all(),
        "Sin ocupación fuera de ocupados": df.loc[~ocupados.fillna(False), "oficio1_08"].isna().all(),
        "Sin textos libres sensibles": not set(TEXTOS_EXCLUIDOS) & set(df.columns),
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    fallidos = [nombre for nombre, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")

    # e7 es texto libre: se avisa si parece traer datos personales en vez de una carrera.
    sospechosos = df["e7"].str.contains(r"@|\d{6,}", regex=True).sum()
    log.info("  [i] e7 con correo o número largo: %d", sospechosos)


def procesar_casen() -> Path:
    """Pipeline completo de CASEN 2024."""
    crudo, totales = cargar()
    df = preparar(crudo)
    validar(df, totales)
    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RUTA_SALIDA, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas × %d columnas)", RUTA_SALIDA.name, *df.shape)
    return RUTA_SALIDA


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ruta = procesar_casen()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(ruta)
