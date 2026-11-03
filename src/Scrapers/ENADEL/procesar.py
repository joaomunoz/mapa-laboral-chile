"""
<src/Scrapers/ENADEL/procesar.py>
Actualizado 02-11-26 01:37

Módulo de procesamiento de ENADEL 2025 (Encuesta a empresas, Dirección del Trabajo).

Entrada:  Entrada/ENADEL_2025.csv                  (5,576 filas × 529 columnas, sep=coma)
Salidas:  Salida/enadel_empresas_procesado.csv     (1 fila por empresa, 29 columnas)
          Salida/enadel_cargos_procesado.csv       (formato largo, 17 columnas, ~32K filas)

Transformaciones aplicadas:
  1. Sentinela:            -88 (No sabe) y -99 (No responde) → pd.NA en módulo B
                           y años de experiencia.
  2. Tabla empresas:       Selección de 26 columnas según esquema (identificación,
                           diseño muestral, región normalizada, CIIU como string
                           con cero a la izquierda, dotación, flujos 12m, vacantes).
  3. Derivadas:            vacantes_proyectadas = b11_1 + b12_1,
                           tasa_rotacion = (renuncias + despidos) / dotacion,
                           tasa_vacantes = vacantes_proyectadas / dotacion.
  4. Tabla cargos:         Despivotar 5 bloques CIUO (c1[1..7], c3[1..3],
                           d1[1..3], d15[1..3], e13[1..3]) a formato largo,
                           con ciuo_08 (4 dígitos), ciuo_nivel_2 y ciuo_nivel_1
                           (jerarquía de fallback para el crosswalk) y nivel
                           educacional etiquetado (libro de códigos 0–7).
  5. Validaciones:         PK única, integridad referencial FK, residuo de
                           sentinela = 0, formato CIUO, cobertura por columna.

Esquema:  esquema.py (ESQUEMA_ENADEL_EMPRESAS / ESQUEMA_ENADEL_CARGOS)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

# Cabecera estándar del proyecto: ruta del script y fecha de actualización.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comun.normalizador import REGIONES, regiones_incoherentes  # noqa: E402
from ENADEL.esquema import (  # noqa: E402
    ESQUEMA_ENADEL_CARGOS,
    ESQUEMA_ENADEL_EMPRESAS,
)

log = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Configuración
# --------------------------------------------------------------------------- #
DIR_ENTRADA = Path(__file__).parent / "Entrada"
DIR_SALIDA = Path(__file__).parent / "Salida"

ARCHIVO_ENTRADA = "ENADEL_2025.csv"
SEPARADOR_ENTRADA = ","
SEPARADOR_SALIDA = ";"

# Sentinela oficial del libro de códigos ENADEL.
SENTINELAS = [-88, -99]

# Nivel educacional requerido (c1_c / c3_c) → etiqueta oficial.
NIVELES_EDUCACIONALES = {
    0: "Sin exigencia de educación formal",
    1: "Educación básica",
    2: "Educación media Científico humanista",
    3: "Educación media Técnico profesional",
    4: "Técnico superior",
    5: "Profesional",
    6: "Profesional con Magíster",
    7: "Profesional con Doctorado",
}

# Definición de los 5 bloques CIUO a despivotar:
# (origen_bloque, prefijo, posiciones, ¿incluye nivel/experiencia?, ¿incluye contratación?)
BLOQUES_CIUO = [
    ("vacante_historica", "c1", range(1, 8), True, True),
    ("vacante_2025", "c3", range(1, 4), True, False),
    ("cargo_clave", "d1", range(1, 4), False, False),
    ("cargo_capacitacion", "d15", range(1, 4), False, False),
    ("cargo_tecnologico", "e13", range(1, 4), False, False),
]


# --------------------------------------------------------------------------- #
# Carga
# --------------------------------------------------------------------------- #
def cargar_entrada() -> pd.DataFrame:
    """Lee el CSV crudo de ENADEL 2025 (separador coma, UTF-8)."""
    ruta = DIR_ENTRADA / ARCHIVO_ENTRADA
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta}. Ejecutar primero obtener.py."
        )
    log.info("Leyendo: %s", ruta.name)
    df = pd.read_csv(ruta, sep=SEPARADOR_ENTRADA, low_memory=False)
    log.info("Cargado: %d filas × %d columnas", len(df), len(df.columns))
    return df


# --------------------------------------------------------------------------- #
# Transformaciones comunes
# --------------------------------------------------------------------------- #
def tratar_sentinelas(df: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    """Convierte los códigos sentinela (-88 No sabe / -99 No responde) en NA."""
    total = 0
    for col in columnas:
        if col in df.columns:
            mascara = df[col].isin(SENTINELAS)
            total += int(mascara.sum())
            df[col] = df[col].mask(mascara)
    log.info("Sentinela tratada: %d valores (-88/-99) → NA", total)
    return df


# --------------------------------------------------------------------------- #
# Tabla 1 — Empresas
# --------------------------------------------------------------------------- #
def construir_empresas(df: pd.DataFrame) -> pd.DataFrame:
    """Construye la tabla de empresas (1 fila por establecimiento)."""
    emp = pd.DataFrame(index=df.index)

    # Identificación y diseño muestral
    for col in ["idempresa_ficticio", "varunit", "varstrat", "pond_final", "fpc"]:
        emp[col] = df[col]

    # Regionalización: código → nombre oficial → normalizado (cruce con SIES/MiFuturo)
    emp["codigo_region"] = df["reg_encuesta"]
    emp["nombre_region"] = df["reg_encuesta"].map(REGIONES)

    # CIIU4.CL 2012 como string con cero a la izquierda
    emp["ciiu_seccion"] = df["a1_Sección"].astype(str).str.strip()
    emp["ciiu_seccion_glosa"] = df["Glosa_Sección"].astype(str).str.strip()
    emp["ciiu_division"] = (
        pd.to_numeric(df["a1_División"], errors="coerce").round().astype("Int64").astype("string").str.zfill(2)
    )
    emp["ciiu_division_glosa"] = df["Glosa_División"].astype(str).str.strip()
    emp["ciiu_clase"] = (
        pd.to_numeric(df["a1_Clase"], errors="coerce").round().astype("Int64").astype("string").str.zfill(4)
    )
    emp["ciiu_clase_glosa"] = df["Glosa_Clase"].astype(str).str.strip()

    # Dotación al 31-may-2025 (totales por tipo de contrato)
    emp["dotacion_total"] = df["b6_1"]
    emp["dotacion_indefinido"] = df["b1_1"]
    emp["dotacion_plazo_fijo"] = df["b2_1"]
    emp["dotacion_aprendizaje"] = df["b3_1"]
    emp["dotacion_honorarios"] = df["b4_1"]
    emp["dotacion_de_palabra"] = df["b5_1"]

    # Flujos jun-2024 → may-2025
    emp["renuncias_12m"] = df["b7_1"]
    emp["despidos_ceses_12m"] = df["b8_1"]
    emp["contrataciones_12m"] = df["b9_1"]
    emp["vacantes_no_llenadas_12m"] = df["b10_1"]

    # Vacantes (numerador del PER)
    emp["vacantes_actuales"] = df["b11_1"]
    emp["vacantes_futuras_2025"] = df["b12_1"]
    emp["vacantes_futuras_2026"] = df["b13_1"]
    emp["vacantes_proyectadas"] = df["b11_1"] + df["b12_1"]

    # Derivadas (dotación 0 o NA → NA, evita división por cero)
    dot = emp["dotacion_total"].astype("Float64").mask(lambda s: s == 0)
    emp["tasa_rotacion"] = (
        (emp["renuncias_12m"].astype("Float64") + emp["despidos_ceses_12m"].astype("Float64")) / dot
    ).astype("float64")
    emp["tasa_vacantes"] = (
        emp["vacantes_proyectadas"].astype("Float64") / dot
    ).astype("float64")

    # Orden y tipado estricto según esquema
    emp = emp[list(ESQUEMA_ENADEL_EMPRESAS.keys())]
    for col, dtype in ESQUEMA_ENADEL_EMPRESAS.items():
        if dtype in ("Int64", "int64"):
            emp[col] = pd.to_numeric(emp[col], errors="coerce")
            if emp[col].isna().sum() == 0 and dtype == "int64":
                emp[col] = emp[col].astype("int64")
            else:
                emp[col] = emp[col].round().astype("Int64")
        else:
            emp[col] = emp[col].astype(dtype)
    log.info("Tabla empresas construida: %d filas × %d columnas", *emp.shape)
    return emp


# --------------------------------------------------------------------------- #
# Tabla 2 — Cargos (despivoto de bloques CIUO)
# --------------------------------------------------------------------------- #
def ciuo_a_string(serie: pd.Series) -> pd.Series:
    """Convierte el código CIUO (float con NA) a string de 4 dígitos."""
    num = pd.to_numeric(serie, errors="coerce").round().astype("Int64").astype("string")
    return num.str.zfill(4)


def construir_cargos(df: pd.DataFrame) -> pd.DataFrame:
    """Despivota los 5 bloques CIUO a formato largo (1 fila por cargo)."""
    partes: list[pd.DataFrame] = []

    for origen, prefijo, posiciones, tiene_req, tiene_contratacion in BLOQUES_CIUO:
        for n in posiciones:
            col_cod = f"{prefijo}_Codigo_CIUO_{n}"
            if col_cod not in df.columns:
                continue

            parte = pd.DataFrame(index=df.index)
            parte["origen_bloque"] = origen
            parte["posicion"] = n
            parte["ciuo_08"] = ciuo_a_string(df[col_cod])
            parte["ciuo_glosa"] = df[f"{prefijo}_glosa_CIUO_{n}"].astype(str).str.strip()
            parte["puesto_estandarizado"] = df[f"{prefijo}_Puesto_Trabajo_{n}"].astype(str).str.strip()

            if tiene_req:
                nivel = df[f"{prefijo}_c_{n}"].round()
                parte["nivel_educacional"] = nivel.map(NIVELES_EDUCACIONALES).astype(object)
                exp = df[f"{prefijo}_d_{n}"].mask(df[f"{prefijo}_d_{n}"].isin(SENTINELAS))
                parte["experiencia_anios"] = exp.round().astype("Int64")
            else:
                # Dtype explícito idéntico en todas las partes → concat estable
                parte["nivel_educacional"] = pd.Series(pd.NA, index=df.index, dtype=object)
                parte["experiencia_anios"] = pd.Series(pd.NA, index=df.index, dtype="Int64")

            if tiene_contratacion:
                parte["logro_contratar"] = df[f"c1_f_{n}"].round().astype("Int64")
                parte["cantidad_contratada"] = df[f"c1_h_{n}"].round().astype("Int64")
            else:
                parte["logro_contratar"] = pd.Series(pd.NA, index=df.index, dtype="Int64")
                parte["cantidad_contratada"] = pd.Series(pd.NA, index=df.index, dtype="Int64")

            # Solo conservar filas con CIUO efectivamente reportado
            # (se conserva el índice original de df para anexar el contexto)
            parte = parte[parte["ciuo_08"].notna()]
            partes.append(parte)

    cargos = pd.concat(partes, ignore_index=False)

    # Contexto de la empresa (región, sector, peso muestral) alineado por índice
    contexto = df[
        ["idempresa_ficticio", "reg_encuesta", "a1_División", "Glosa_División", "pond_final"]
    ].copy()
    contexto = contexto.rename(columns={"reg_encuesta": "codigo_region"})
    contexto["nombre_region"] = contexto["codigo_region"].map(REGIONES)
    contexto["ciiu_division"] = (
        pd.to_numeric(contexto["a1_División"], errors="coerce").round().astype("Int64").astype("string").str.zfill(2)
    )
    contexto["ciiu_division_glosa"] = contexto["Glosa_División"].astype(str).str.strip()
    contexto = contexto[["idempresa_ficticio", "codigo_region", "nombre_region",
                         "ciiu_division", "ciiu_division_glosa", "pond_final"]]

    # Anexar contexto por índice original y reordenar limpio
    cargos = cargos.join(contexto, how="left").reset_index(drop=True)

    # Jerarquía CIUO para fallback del crosswalk
    cargos["ciuo_nivel_2"] = cargos["ciuo_08"].str[:2]
    cargos["ciuo_nivel_1"] = cargos["ciuo_08"].str[:1]

    # Orden y tipado estricto según esquema
    cargos = cargos[list(ESQUEMA_ENADEL_CARGOS.keys())]
    for col, dtype in ESQUEMA_ENADEL_CARGOS.items():
        if dtype in ("Int64", "int64"):
            cargos[col] = pd.to_numeric(cargos[col], errors="coerce").round().astype(
                "int64" if cargos[col].isna().sum() == 0 and dtype == "int64" else "Int64"
            )
        else:
            cargos[col] = cargos[col].astype(dtype)

    log.info("Tabla cargos construida: %d filas × %d columnas", *cargos.shape)
    return cargos


# --------------------------------------------------------------------------- #
# Validaciones
# --------------------------------------------------------------------------- #
def validar_empresas(emp: pd.DataFrame) -> None:
    """Validaciones de integridad de la tabla empresas."""
    total = len(emp)
    log.info("=== Validaciones ENADEL Empresas (%d filas) ===", total)

    # PK única
    dup = emp["idempresa_ficticio"].duplicated().sum()
    log.info("  [%s] PK idempresa_ficticio única        : %d duplicados",
             "✓" if dup == 0 else "✗", dup)

    # Residuo de sentinela
    num = emp.select_dtypes(include="number")
    residuo = int(num.isin(SENTINELAS).sum().sum())
    log.info("  [%s] Residuo sentinela (-88/-99)        : %d",
             "✓" if residuo == 0 else "✗", residuo)

    # Regiones
    regiones = emp["codigo_region"].nunique()
    log.info("  [%s] Cobertura regional                 : %d/16 regiones",
             "✓" if regiones == 16 else "⚠", regiones)
    incoherentes = regiones_incoherentes(emp["codigo_region"], emp["nombre_region"])
    log.info("  [%s] codigo_region y nombre coherentes  : %d incoherentes",
             "✓" if incoherentes == 0 else "✗", incoherentes)

    # Dotación
    ceros = int((emp["dotacion_total"] == 0).sum())
    log.info("  [i] Empresas con dotación = 0           : %d", ceros)

    # Tasas
    for col in ["tasa_rotacion", "tasa_vacantes"]:
        s = emp[col].dropna()
        neg = int((s < 0).sum())
        log.info("  [%s] %s ≥ 0                     : máx=%.2f, neg=%d",
                 "✓" if neg == 0 else "✗", col, s.max() if len(s) else float("nan"), neg)

    # Cobertura
    log.info("  Cobertura por columna:")
    for col in emp.columns:
        n = emp[col].notna().sum()
        pct = 100 * n / total
        flag = "🟢" if pct >= 99 else ("🟡" if pct >= 90 else "🔴")
        log.info("    %s %-30s %6.1f%%", flag, col, pct)


def validar_cargos(cargos: pd.DataFrame, emp: pd.DataFrame) -> None:
    """Validaciones de integridad de la tabla cargos."""
    total = len(cargos)
    log.info("=== Validaciones ENADEL Cargos (%d filas) ===", total)

    # Integridad referencial FK → PK
    fk_ok = cargos["idempresa_ficticio"].isin(emp["idempresa_ficticio"]).all()
    log.info("  [%s] FK → empresas (referencial)         : %s",
             "✓" if fk_ok else "✗", "todas resueltas" if fk_ok else "hay huérfanas")

    # Formato CIUO
    fmt_ok = cargos["ciuo_08"].str.fullmatch(r"\d{4}").all()
    n_fmt2 = cargos["ciuo_nivel_2"].str.fullmatch(r"\d{2}").all()
    n_fmt1 = cargos["ciuo_nivel_1"].str.fullmatch(r"\d").all()
    log.info("  [%s] Formato CIUO 4 dígitos              : %s",
             "✓" if fmt_ok else "✗", "válido" if fmt_ok else "inválido")
    log.info("  [%s] Jerarquía ciuo_nivel_2 / nivel_1    : %s / %s",
             "✓" if (n_fmt2 and n_fmt1) else "✗",
             "válido" if n_fmt2 else "inválido", "válido" if n_fmt1 else "inválido")

    # Distribución por bloque
    log.info("  Distribución por origen_bloque:")
    for origen, conteo in cargos["origen_bloque"].value_counts().items():
        log.info("    %-22s %6d filas (%5.1f%%)", origen, conteo, 100 * conteo / total)

    # Únicos y cobertura
    log.info("  CIUO-08 únicos: %d | Nivel educacional con dato: %.1f%%",
             cargos["ciuo_08"].nunique(),
             100 * cargos["nivel_educacional"].notna().mean())
    log.info("  Cobertura por columna:")
    for col in cargos.columns:
        n = cargos[col].notna().sum()
        pct = 100 * n / total
        flag = "🟢" if pct >= 99 else ("🟡" if pct >= 60 else "⚪")
        log.info("    %s %-30s %6.1f%%", flag, col, pct)


# --------------------------------------------------------------------------- #
# Orquestador
# --------------------------------------------------------------------------- #
def procesar_enadel() -> tuple[Path, Path]:
    """
    Pipeline completo de procesamiento de ENADEL 2025 (dos tablas de salida).

    Returns:
        Tupla (ruta_empresas, ruta_cargos) en Salida/.
    """
    df = cargar_entrada()

    # 1. Sentinela en módulo B (flujos y vacantes) y años de experiencia
    columnas_b = [c for c in df.columns if c.startswith("b")]
    columnas_exp = [c for c in df.columns
                    if (c.startswith("c1_d_") or c.startswith("c3_d_"))]
    df = tratar_sentinelas(df, columnas_b + columnas_exp)

    # 2. Tabla 1 — Empresas
    emp = construir_empresas(df)

    # 3. Tabla 2 — Cargos (despivoto CIUO)
    cargos = construir_cargos(df)

    # 4. Validaciones cruzadas
    validar_empresas(emp)
    validar_cargos(cargos, emp)

    # 5. Exportación
    DIR_SALIDA.mkdir(parents=True, exist_ok=True)
    ruta_emp = DIR_SALIDA / "enadel_empresas_procesado.csv"
    ruta_cargos = DIR_SALIDA / "enadel_cargos_procesado.csv"
    emp.to_csv(ruta_emp, sep=SEPARADOR_SALIDA, index=False, encoding="utf-8")
    cargos.to_csv(ruta_cargos, sep=SEPARADOR_SALIDA, index=False, encoding="utf-8")

    for ruta, tabla in [(ruta_emp, emp), (ruta_cargos, cargos)]:
        peso_mb = ruta.stat().st_size / (1024 * 1024)
        log.info("CSV generado: %s (%d filas, %d columnas, %.2f MB)",
                 ruta.name, len(tabla), len(tabla.columns), peso_mb)
    return ruta_emp, ruta_cargos


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ruta_emp, ruta_cargos = procesar_enadel()

    emp = pd.read_csv(ruta_emp, sep=SEPARADOR_SALIDA)
    cargos = pd.read_csv(ruta_cargos, sep=SEPARADOR_SALIDA)

    print("\n=== ENADEL 2025 — Procesado ===")
    print(f"Empresas : {ruta_emp} ({len(emp):,} filas × {len(emp.columns)} cols)")
    print(f"Cargos   : {ruta_cargos} ({len(cargos):,} filas × {len(cargos.columns)} cols)")
    print(f"Regiones cubiertas : {emp['codigo_region'].nunique()}/16")
    print(f"Dotación total (ponderada): {int((emp['dotacion_total'] * emp['pond_final']).sum()):,}")
    print(f"Vacantes proyectadas (ponderadas): {int((emp['vacantes_proyectadas'].fillna(0) * emp['pond_final']).sum()):,}")
    print(f"CIUO-08 únicos en demanda : {cargos['ciuo_08'].nunique()}")
    print(f"Carreras-macro (ciuo_nivel_1) : {cargos['ciuo_nivel_1'].nunique()} grupos")
