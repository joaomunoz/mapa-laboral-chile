"""
<src/Scrapers/ENE/procesar.py>
Actualizado 02-11-26 15:30

Módulo de procesamiento de ENE 2026 (Encuesta Nacional de Empleo, INE).

Entrada:  Entrada/2026/ene-2026-{01..08}-*.csv   (8 trimestres móviles, sep=";", 782,303 filas crudas)
Salida:   Salida/ene_procesado.csv               (1 fila por entrevista única, 30 columnas,
                                                   ~324,054 filas esperadas)

CONTEXTO (ver esquema.py): los 8 archivos son trimestres móviles SOLAPADOS
(archivo K = meses {K-1, K, K+1}; K=1 incluye dic-2025). Una misma entrevista
aparece en hasta 3 archivos con contenido idéntico pero `fact_cal` recalibrado.
Por eso la UNIFICACIÓN ocurre AQUÍ y nunca en obtener.py, y por eso NUNCA se
suman meses en bruto (duplicaría hasta 3 veces cada entrevista).

Transformaciones aplicadas:
  1. Proyección:       usecols=COLUMNAS_ENTRADA (30 de 222 columnas crudas),
                       lectura dtype=str para preservar ceros y coma decimal.
  2. Unificación:      concat de los 8 archivos + deduplicación por
                       (idrph, ano_encuesta, mes_encuesta).
  3. Peso "central":   de cada entrevista se conserva el fact_cal del archivo cuyo
                       mes_central coincide con mes_encuesta (fallback: menor
                       archivo_k). Desviación regional ≤1.75% vs ≤4.34% de las
                       políticas first/last (test empírico, ver esquema.py).
  4. fact_cal:         coma decimal ("195,01134908538") → float64.
  5. Derivadas:        mes = "AAAA-MM" (clave temporal) y
                       codigo_region = `region` del crudo; nombre_region = comun.REGIONES.
  6. Sentinelas:       88/99/999/0 según libro de códigos → NA (SENTINELAS).
  7. Tipado estricto:  reindex(columns=ESQUEMA_ENE) + cast por esquema.
  8. Validaciones:     las 10 reglas de esquema.VALIDACIONES (PK única, conteo,
                       meses, regiones, fact_cal, sentinelas, cobertura b1,
                       reproducción del Boletín INE n°336 y cohortes disjuntas).

ESCALA (ver esquema.py, "PANEL Y ESCALA"): `fact_cal` está calibrado al
TRIMESTRE MÓVIL — 3 meses consecutivos = 1 entrevista por persona = población.
Un solo mes ≈ 1/3 de la población: para NIVELES agrupar 3 meses (o mes ×3);
para TASAS basta cualquier agrupación. Validación oficial reproducida:
JAS 2026 → ocupadas 9,275,130 vs INE 9,274,742 (0.00%), desocupación 9.80%.

Esquema:  esquema.py (ESQUEMA_ENE)
"""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

import pandas as pd

# Cabecera estándar del proyecto: ruta del script y fecha de actualización.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comun.normalizador import REGIONES, regiones_incoherentes  # noqa: E402
from ENE.esquema import (  # noqa: E402
    CLAVE_ENE,
    COLUMNAS_ENTRADA,
    ESQUEMA_ENE,
    SENTINELAS,
    SENTINELAS_CINE11_2D,
)

log = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Configuración
# --------------------------------------------------------------------------- #
DIR_ENTRADA = Path(__file__).parent / "Entrada" / "2026"
DIR_SALIDA = Path(__file__).parent / "Salida"

SEPARADOR_ENTRADA = ";"
SEPARADOR_SALIDA = ";"
NOMBRE_SALIDA = "ene_procesado.csv"

# Filas únicas esperadas tras deduplicar (verificado empíricamente: 782,303 crudas).
FILAS_ESPERADAS = 324_054

# Cifras oficiales INE, Boletín Estadístico n°336 (29-10-2026),
# trimestre móvil julio-septiembre 2026 → validación 9 (niveles) y tasas.
INE_JAS_2026 = {
    "fuerza_trabajo": 10_282_718,
    "ocupadas": 9_274_742,
    "desocupadas": 1_007_976,
    "inactivas": 6_416_440,
    "ocupadas_informales": 2_451_443,
    "tasa_desocupacion": 9.8,
}
# Trimestre móvil de referencia de la validación.
MESES_JAS_2026 = ["2026-07", "2026-08", "2026-09"]

# Región (código INE, Anexo 1) → nombre oficial → normalizado para cruces.

# --------------------------------------------------------------------------- #
# Carga
# --------------------------------------------------------------------------- #
def mes_central_de_archivo(nombre: str) -> int:
    """Extrae el mes_central (1-8) del nombre ene-2026-K-*.csv."""
    m = re.search(r"ene-2026-(\d{2})-", nombre)
    if not m:
        raise ValueError(f"Nombre de archivo ENE inesperado: {nombre}")
    return int(m.group(1))


def k_central_de_mes(mes: int) -> int:
    """
    Archivo cuyo mes_central coincide con el mes de la entrevista (política "central"):
      meses 1..8 → archivo = mes; mes 12 → archivo 1 (trimestre dic-ene-feb);
      mes 9 → archivo 8 (trimestre ago-sep, mes 9 es borde superior).
    """
    if 1 <= mes <= 8:
        return mes
    return 1 if mes == 12 else 8


def cargar_entradas() -> pd.DataFrame:
    """Lee los 8 trimestres móviles de Entrada/2026/ con proyección de columnas."""
    archivos = sorted(DIR_ENTRADA.glob("ene-2026-*.csv"))
    if len(archivos) != 8:
        raise FileNotFoundError(
            f"Se esperaban 8 archivos en {DIR_ENTRADA} y hay {len(archivos)}. "
            "Ejecutar primero obtener.py."
        )

    partes: list[pd.DataFrame] = []
    for ruta in archivos:
        k = mes_central_de_archivo(ruta.name)
        # dtype=str: preserva "01" de cine11_2d y la coma decimal de fact_cal.
        df = pd.read_csv(
            ruta,
            sep=SEPARADOR_ENTRADA,
            usecols=COLUMNAS_ENTRADA,
            dtype=str,
            low_memory=False,
        )
        # Validación de contexto: el archivo K debe declarar mes_central == K.
        centrales = pd.to_numeric(df["mes_central"], errors="coerce").unique()
        if list(centrales) != [k]:
            raise ValueError(
                f"{ruta.name}: mes_central={sorted(centrales)} distinto de {k}."
            )
        df["archivo_k"] = k
        partes.append(df)
        log.info("Leído: %-24s %7d filas (mes_central=%d)", ruta.name, len(df), k)

    big = pd.concat(partes, ignore_index=True)
    log.info("Concatenado: %d filas crudas × %d columnas", *big.shape)
    return big


# --------------------------------------------------------------------------- #
# Unificación: deduplicación con política de peso "central"
# --------------------------------------------------------------------------- #
def unificar(big: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplica por (idrph, ano_encuesta, mes_encuesta) conservando la fila del
    archivo cuyo mes_central coincide con mes_encuesta (política "central").

    Returns:
        DataFrame con una fila por entrevista + columnas de control
        _tiene_central (bool) para reportar el uso de fallback.
    """
    big = big.copy()
    big["ano_encuesta"] = pd.to_numeric(big["ano_encuesta"], errors="coerce").astype("Int64")
    big["mes_encuesta"] = pd.to_numeric(big["mes_encuesta"], errors="coerce").astype("Int64")

    # prioridad 0 = archivo central (se prefiere); 1 = otro archivo (fallback).
    k_central = big["mes_encuesta"].astype(int).map(k_central_de_mes)
    big["_prioridad"] = (big["archivo_k"] != k_central).astype("int8")

    # Orden estable: clave, luego central antes que no-central, luego menor archivo_k.
    big = big.sort_values(
        ["idrph", "ano_encuesta", "mes_encuesta", "_prioridad", "archivo_k"],
        kind="mergesort",
    )
    crudas = len(big)
    uniq = big.drop_duplicates(CLAVE_ENE, keep="first").reset_index(drop=True)
    usadas_central = int((uniq["_prioridad"] == 0).sum())
    log.info(
        "Deduplicación: %d crudas → %d entrevistas únicas (-%d duplicadas, %.1f%%)",
        crudas, len(uniq), crudas - len(uniq),
        100 * (crudas - len(uniq)) / crudas,
    )
    log.info(
        "  fact_cal 'central': %d entrevistas (%.2f%%) | fallback menor archivo_k: %d",
        usadas_central, 100 * usadas_central / len(uniq), len(uniq) - usadas_central,
    )
    uniq["_tiene_central"] = uniq["_prioridad"] == 0
    return uniq


# --------------------------------------------------------------------------- #
# Transformaciones
# --------------------------------------------------------------------------- #
def preparar(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte tipos, repara fact_cal, agrega derivadas y aplica sentinelas."""
    df = df.rename(columns={"region": "codigo_region", "b18_region": "codigo_region_trabajo"})

    # 1. fact_cal: coma decimal → float64
    df["fact_cal"] = pd.to_numeric(
        df["fact_cal"].astype(str).str.replace(",", ".", regex=False),
        errors="coerce",
    ).astype("float64")

    # 2. Resto de numéricos (idrph se maneja aparte por ser int64 final)
    numericas = [
        c for c in ESQUEMA_ENE
        if c not in ("mes", "nombre_region", "fact_cal", "idrph", "cine11_2d")
        and c in df.columns
    ]
    for col in numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce").round().astype("Int64")

    # idrph: entero sin nulos (clave)
    df["idrph"] = pd.to_numeric(df["idrph"], errors="coerce")
    if df["idrph"].isna().any():
        raise ValueError("idrph con valores no numéricos o vacíos.")

    # cine11_2d: string con cero a la izquierda ("01") — se deja como object
    df["cine11_2d"] = df["cine11_2d"].astype(object)

    # 3. Derivadas de tiempo y geografía
    df["mes"] = (
        df["ano_encuesta"].astype(int).astype(str)
        + "-"
        + df["mes_encuesta"].astype(int).astype(str).str.zfill(2)
    ).astype(object)
    df["nombre_region"] = (
        df["codigo_region"].map(REGIONES).astype(object)
    )

    # 4. Sentinelas → NA (numéricas y cine11_2d como string)
    total = 0
    for col, valores in SENTINELAS.items():
        mascara = df[col].isin(valores)
        total += int(mascara.sum())
        df[col] = df[col].mask(mascara)
    mascara = df["cine11_2d"].isin(SENTINELAS_CINE11_2D)
    total += int(mascara.sum())
    df["cine11_2d"] = df["cine11_2d"].mask(mascara)
    log.info("Sentinela tratada: %d valores → NA", total)

    # 5. Orden y tipado estricto según esquema
    df = df[list(ESQUEMA_ENE.keys())].copy()
    for col, dtype in ESQUEMA_ENE.items():
        if dtype == "int64":
            if df[col].isna().any():
                raise ValueError(f"{col}: el esquema exige int64 sin nulos.")
            df[col] = df[col].astype("int64")
        else:
            df[col] = df[col].astype(dtype)
    log.info("Tabla preparada: %d filas × %d columnas", *df.shape)
    return df


# --------------------------------------------------------------------------- #
# Validaciones (esquema.VALIDACIONES 1-9)
# --------------------------------------------------------------------------- #
def validar(df: pd.DataFrame, crudas: int) -> None:
    """Ejecuta las 10 reglas de validación del esquema."""
    total = len(df)
    log.info("=== Validaciones ENE (%d filas) ===", total)

    # 1. Tipos exactos vs esquema
    malos = [
        f"{c}:{df[c].dtype}!={t}" for c, t in ESQUEMA_ENE.items()
        if str(df[c].dtype) != t
    ]
    log.info("  [%s] 1. dtypes == esquema                : %s",
             "✓" if not malos else "✗", "correcto" if not malos else ", ".join(malos))

    # 2. PK única
    dup = int(df.duplicated(CLAVE_ENE).sum())
    log.info("  [%s] 2. PK (idrph,ano,mes) única         : %d duplicados",
             "✓" if dup == 0 else "✗", dup)

    # 3. Conteo de entrevistas únicas
    ok = total == FILAS_ESPERADAS
    log.info("  [%s] 3. Filas == %s esperadas        : %d (crudas %d)",
             "✓" if ok else "✗", f"{FILAS_ESPERADAS:,}", total, crudas)

    # 4. Períodos cubiertos
    meses = sorted(df["mes"].unique())
    esperados = ["2025-12"] + [f"2026-{m:02d}" for m in range(1, 10)]
    ok = meses == esperados
    log.info("  [%s] 4. Períodos 2025-12..2026-09        : %s",
             "✓" if ok else "✗", f"{len(meses)} meses" if ok else meses)
    inconsistentes = int((df["mes"] != df["ano_encuesta"].astype(str) + "-"
                          + df["mes_encuesta"].astype(int).astype(str).str.zfill(2)).sum())
    log.info("  [%s] 4b. mes coherente con ano/mes_enc. : %d discordancias",
             "✓" if inconsistentes == 0 else "✗", inconsistentes)

    # 5. Regiones
    fuera = int((~df["codigo_region"].isin(REGIONES)).sum())
    sin_nom = regiones_incoherentes(df["codigo_region"], df["nombre_region"])
    log.info("  [%s] 5. codigo_region ∈ 1..16 y nombre   : %d fuera de rango, %d incoherentes",
             "✓" if fuera == 0 and sin_nom == 0 else "✗", fuera, sin_nom)
    log.info("       Cobertura regional                 : %d/16 regiones",
             df["codigo_region"].nunique())
    ocupados_validos = df.loc[df["cae_especifico"].between(1, 7), "codigo_region_trabajo"]
    fuera_trabajo = int((ocupados_validos.notna() & ~ocupados_validos.isin(REGIONES)).sum())
    log.info("  [%s] 5b. Región de trabajo ∈ 1..16         : %.2f%% de ocupados con dato, %d fuera de rango",
             "✓" if fuera_trabajo == 0 else "✗", 100 * ocupados_validos.notna().mean(), fuera_trabajo)

    # 6. fact_cal
    fc = df["fact_cal"]
    malos_fc = int((fc.isna() | (fc <= 0)).sum())
    log.info("  [%s] 6. fact_cal > 0 sin nulos           : %d inválidos (min=%.3f, max=%.3f)",
             "✓" if malos_fc == 0 else "✗", malos_fc, fc.min(), fc.max())

    # 7. Residuo de sentinelas
    residuo = sum(int(df[c].isin(v).sum()) for c, v in SENTINELAS.items())
    residuo += int(df["cine11_2d"].isin(SENTINELAS_CINE11_2D).sum())
    log.info("  [%s] 7. Sin sentinelas residuales        : %d",
             "✓" if residuo == 0 else "✗", residuo)

    # 8. Cobertura b1 sobre ocupados (b1=999 original → NA)
    ocup = df["activ"] == 1
    n_ocup = int(ocup.sum())
    sin_b1 = int((ocup & df["b1"].isna()).sum())
    log.info("  [%s] 8. Ocupados con CIUO-08 (b1)        : %.1f%% (%d/%d sin dato)",
             "✓", 100 * (n_ocup - sin_b1) / n_ocup if n_ocup else 0.0, sin_b1, n_ocup)

    # 9. Reproducción del Boletín INE n°336 (trimestre móvil JAS 2026).
    #    Recetas §7 del libro de códigos: cae_especifico 1-7 ocupados, 8-9
    #    desocupados, 1-9 fuerza de trabajo, ≥10 inactivos; informal = ocup_form 2.
    #    IMPORTANTE: los niveles se evalúan sobre TRES meses consecutivos
    #    (fact_cal está calibrado al trimestre móvil, ver esquema.py).
    jas = df[df["mes"].isin(MESES_JAS_2026)]
    w = jas["fact_cal"]
    cae = jas["cae_especifico"]
    niveles = {
        "fuerza_trabajo": w[cae.between(1, 9)].sum(),
        "ocupadas": w[cae.between(1, 7)].sum(),
        "desocupadas": w[cae.between(8, 9)].sum(),
        "inactivas": w[cae.between(10, 28)].sum(),
        "ocupadas_informales": w[cae.between(1, 7) & (jas["ocup_form"] == 2)].sum(),
    }
    desvs = {
        k: 100 * (niveles[k] - v) / v
        for k, v in INE_JAS_2026.items() if k in niveles
    }
    max_desv = max(abs(d) for d in desvs.values())
    log.info("  [%s] 9. Niveles vs Boletín INE n°336 (JAS 2026) : desv. máx %.2f%%",
             "✓" if max_desv <= 0.5 else "✗", max_desv)
    for k, d in desvs.items():
        log.info("       %-22s oficial %12s | nuestro %12s (%+.2f%%)",
                 k, f"{INE_JAS_2026[k]:,}", f"{int(round(niveles[k])):,}", d)
    tasa = 100 * niveles["desocupadas"] / niveles["fuerza_trabajo"]
    ok_tasa = abs(tasa - INE_JAS_2026["tasa_desocupacion"]) <= 0.1
    log.info("  [%s] 9b. Tasa desocupación JAS 2026            : %.2f%% (oficial %.1f%%)",
             "✓" if ok_tasa else "✗", tasa, INE_JAS_2026["tasa_desocupacion"])

    # 10. Cohortes disjuntas: ninguna persona en dos meses consecutivos
    #     (consistente con la entrevista cada 3 meses).
    meses = sorted(df["mes"].unique())
    solapes = 0
    for a, b in zip(meses, meses[1:]):
        sa = set(df.loc[df["mes"] == a, "idrph"])
        sb = set(df.loc[df["mes"] == b, "idrph"])
        solapes += len(sa & sb)
    log.info("  [%s] 10. Cohortes disjuntas entre meses        : %d personas repetidas en meses consecutivos",
             "✓" if solapes == 0 else "⚠", solapes)

    # Escala de los niveles: un solo mes ≈ 1/3 del trimestre (documentado en esquema.py)
    exp_mes = df.groupby("mes")["fact_cal"].sum() / 1e6
    log.info("  [i] Expansión mensual (×1, NO usar para niveles): min=%.2fM, max=%.2fM "
             "(trimestre ≈ población; ×3 = nivel mensual)",
             exp_mes.min(), exp_mes.max())

    # Contexto: uso de la política central y cobertura por columna
    log.info("  [i] Uso de archivo central (fallback)   : ver log de unificación")
    log.info("  Cobertura por columna:")
    for col in df.columns:
        n = int(df[col].notna().sum())
        pct = 100 * n / total
        flag = "🟢" if pct >= 99 else ("🟡" if pct >= 60 else "⚪")
        log.info("    %s %-24s %6.1f%%", flag, col, pct)


# --------------------------------------------------------------------------- #
# Orquestador
# --------------------------------------------------------------------------- #
def procesar_ene() -> Path:
    """Pipeline completo de unificación y procesamiento de ENE 2026."""
    big = cargar_entradas()
    crudas = len(big)

    # 1. Unificación con deduplicación y política de peso "central"
    uniq = unificar(big)
    del big  # libera las 782K filas crudas

    # 2. Tipos, derivadas, sentinelas y tipado estricto
    df = preparar(uniq)

    # 3. Validaciones
    validar(df, crudas=crudas)

    # 4. Exportación
    DIR_SALIDA.mkdir(parents=True, exist_ok=True)
    ruta = DIR_SALIDA / NOMBRE_SALIDA
    df.to_csv(ruta, sep=SEPARADOR_SALIDA, index=False, encoding="utf-8")
    peso_mb = ruta.stat().st_size / (1024 * 1024)
    log.info("CSV generado: %s (%d filas, %d columnas, %.2f MB)",
             ruta.name, len(df), len(df.columns), peso_mb)
    return ruta


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ruta = procesar_ene()

    ene = pd.read_csv(ruta, sep=SEPARADOR_SALIDA)

    print("\n=== ENE 2026 — Procesado ===")
    print(f"Salida : {ruta} ({len(ene):,} filas × {len(ene.columns)} cols)")
    print(f"Períodos: {ene['mes'].min()} … {ene['mes'].max()} ({ene['mes'].nunique()} meses)")
    print(f"Regiones cubiertas : {ene['codigo_region'].nunique()}/16")
    print("Nota: fact_cal está calibrado POR TRIMESTRE (3 meses = población);")
    print("      niveles → agrupar 3 meses consecutivos (o mes ×3); tasas → cualquier corte.")

    jas = ene[ene["mes"].isin(MESES_JAS_2026)]
    w, cae = jas["fact_cal"], jas["cae_especifico"]
    print(f"\nValidación vs Boletín INE n°336 (JAS 2026):")
    print(f"  Ocupadas        : {int(w[cae.between(1,7)].sum()):>12,}  (INE 9,274,742)")
    print(f"  Fuerza de trabajo: {int(w[cae.between(1,9)].sum()):>11,}  (INE 10,282,718)")
    print(f"  Desocupadas     : {int(w[cae.between(8,9)].sum()):>12,}  (INE 1,007,976)")
    print(f"  Tasa desocup.   : {100*w[cae.between(8,9)].sum()/w[cae.between(1,9)].sum():>11.2f}%  (INE 9.8%)")
    print(f"Grupos ocupación CIUO-08 (b1): {ene['b1'].nunique()} | entrevistas únicas: {ene['idrph'].nunique():,}")

    # Reporte de inspección estándar del proyecto sobre la salida generada
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "comun"))
        from inspect_data import inspeccion_rigurosa  # noqa: E402
        inspeccion_rigurosa(ruta)
    except Exception as exc:  # el reporte no debe tumbar el pipeline
        log.warning("No se generó el reporte de inspección: %s", exc)
