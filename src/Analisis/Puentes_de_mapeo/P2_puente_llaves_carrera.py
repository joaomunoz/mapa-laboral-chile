"""
<src/Analisis/Puentes_de_mapeo/P2_puente_llaves_carrera.py>
Actualizado 02-11-26 16:40

Generador del P2 · PUENTE_LLAVES_CARRERA del proyecto.

Entradas: src/Scrapers/Titulados/Salida/titulados_procesado.csv        (234,074 filas)
          src/Scrapers/Empleabilidad/Salida/empleabilidad_procesado.csv (1,690 filas)
Salida:   Salida/P2_puente_llaves_carrera.csv (Titulados ⋈ Empleabilidad resuelto,
                                               8,623 filas, trazable por nivel de match)

  Resuelve la relación directa Titulados ⋈ Empleabilidad en 3 niveles de fallback:
    nivel_match exacto   → existe fila MiFuturo con esa institución+carrera
                    generica → media de las carreras MiFuturo de esa institución con
                               la misma carrera_generica
                    nacional → media nacional de esa carrera_generica
                    ninguno  → sin dato de empleabilidad
  Llave maestra = CÓDIGO de institución (`codigo_institucion` SIES ↔ `id_institucion`
  MiFuturo): los 105 códigos MiFuturo existen en SIES (98.1% mismo nombre; las 2
  diferencias son solo apóstrofes de O'Higgins).
  Grano de salida: (id_institucion, carrera_norm) para filas con match exacto/generica;
  las carreras de Titulados sin valor por debajo de generica se COLAPSAN a un residuo
  por (id_institucion, carrera_generica) para no repetir la media nacional por carrera.
  Las filas Empleabilidad sin titulados coincidentes quedan con oferta = 0
  (origen = solo_empleabilidad).

Cobertura reportada en AMBAS direcciones (validación 6):
  - % de filas Empleabilidad resueltas por nivel de match (lo que el índice necesita).
  - % del volumen de titulados con empleabilidad resuelta.

Esquema:  esquema.py (PUENTE_LLAVES_CARRERA, catálogos, VALIDACIONES)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

# Cabecera estándar del proyecto: ruta del script y acceso al módulo común.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Scrapers"))
from comun.normalizador import normalizar_texto  # noqa: E402

from esquema import (  # noqa: E402  (esquema.py hermano)
    FUENTES_EMPLEABILIDAD,
    NIVELES_MATCH,
    ORIGEN_LLAVES,
    PUENTE_LLAVES_CARRERA,
)

log = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Configuración
# --------------------------------------------------------------------------- #
DIR_SCRAPERS = Path(__file__).resolve().parents[2] / "Scrapers"
RUTA_TITULADOS = DIR_SCRAPERS / "Titulados" / "Salida" / "titulados_procesado.csv"
RUTA_EMPLEABILIDAD = DIR_SCRAPERS / "Empleabilidad" / "Salida" / "empleabilidad_procesado.csv"
DIR_SALIDA = Path(__file__).parent / "Salida"

SEPARADOR_SALIDA = ";"

# Año más reciente del dataset de Titulados (para titulaciones_ult_anio).
ANIO_MAX_TITULADOS = 2025


# --------------------------------------------------------------------------- #
# P2 — Llaves de carrera: Titulados ⋈ Empleabilidad con fallback de 3 niveles
# --------------------------------------------------------------------------- #
def cargar_fuentes() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lee los dos CSV procesados y normaliza las llaves de cruce."""
    tit = pd.read_csv(RUTA_TITULADOS, sep=";", low_memory=False)
    emp = pd.read_csv(RUTA_EMPLEABILIDAD, sep=";", low_memory=False)

    tit["carrera_norm"] = tit["carrera"].map(normalizar_texto)
    tit["gen_norm"] = tit["carrera_generica"].map(normalizar_texto)
    emp["carrera_norm"] = emp["carrera"].map(normalizar_texto)
    emp["gen_norm"] = emp["carrera_generica"].map(normalizar_texto)

    log.info("Titulados: %d filas | Empleabilidad: %d filas", len(tit), len(emp))
    log.info("  Titulados  · llaves (inst, carrera): %d únicas",
             tit.groupby(["codigo_institucion", "carrera_norm"]).ngroups)
    log.info("  Empleabilidad · llaves (inst, carrera): %d únicas",
             emp.groupby(["id_institucion", "carrera_norm"]).ngroups)
    return tit, emp


def agregar_titulados(tit: pd.DataFrame) -> pd.DataFrame:
    """Agrega Titulados al grano (id_institucion, carrera_norm) con métricas de oferta."""
    ult_anio = tit.loc[tit["anio"] == ANIO_MAX_TITULADOS]

    agg = (
        tit.groupby(["codigo_institucion", "carrera_norm"], as_index=False)
        .agg(
            institucion=("institucion", "first"),
            tipo_institucion=("tipo_institucion", "first"),
            carrera=("carrera", "first"),
            carrera_generica=("carrera_generica", "first"),
            cine13_area=("cine13_area", lambda s: " | ".join(
                sorted({v for v in s if isinstance(v, str) and v}))),
            cine13_subarea=("cine13_subarea", lambda s: " | ".join(
                sorted({v for v in s if isinstance(v, str) and v}))),
            nivel_carrera=("nivel_carrera", "first"),
            gen_norm=("gen_norm", "first"),
            titulaciones_total=("total_titulaciones", "sum"),
            titulados_mayores_40=("titulados_mayores_40", "sum"),
            n_regiones_titulados=("codigo_region", "nunique"),
            anio_ultima_titulacion=("anio", "max"),
        )
        .rename(columns={"codigo_institucion": "id_institucion"})
    )
    # Titulaciones del último año del dataset (2025), por llave.
    ult = (
        ult_anio.groupby(["codigo_institucion", "carrera_norm"])["total_titulaciones"]
        .sum()
        .rename("titulaciones_ult_anio")
        .reset_index()
        .rename(columns={"codigo_institucion": "id_institucion"})
    )
    agg = agg.merge(ult, on=["id_institucion", "carrera_norm"], how="left")
    agg["titulaciones_ult_anio"] = agg["titulaciones_ult_anio"].fillna(0).astype("Int64")
    return agg


def tablas_emp(emp: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Tablas de respaldo de empleabilidad a los 3 niveles: exacto, generica, nacional."""
    exacto = (
        emp.groupby(["id_institucion", "carrera_norm"], as_index=False)
        .agg(val=("empleabilidad_1er_anio", "mean"), n=("empleabilidad_1er_anio", "size"))
    )
    generica = (
        emp.groupby(["id_institucion", "gen_norm"], as_index=False)
        .agg(val=("empleabilidad_1er_anio", "mean"), n=("empleabilidad_1er_anio", "size"))
    )
    nacional = (
        emp.groupby("gen_norm", as_index=False)
        .agg(val=("empleabilidad_1er_anio", "mean"), n=("empleabilidad_1er_anio", "size"))
    )
    return exacto, generica, nacional


def resolver_empleabilidad(
    claves: pd.DataFrame,
    exacto: pd.DataFrame,
    generica: pd.DataFrame,
    nacional: pd.DataFrame,
) -> pd.DataFrame:
    """
    Resuelve empleabilidad_1er_anio para cada llave (id_institucion, carrera_norm)
    siguiendo la jerarquía exacto → generica → nacional → sin_dato.
    `claves` debe traer id_institucion, carrera_norm y gen_norm.
    """
    out = claves[["id_institucion", "carrera_norm", "gen_norm"]].copy()
    out = out.merge(
        exacto.rename(columns={"val": "e_exacto", "n": "n_exacto"}),
        on=["id_institucion", "carrera_norm"], how="left",
    ).merge(
        generica.rename(columns={"val": "e_gen", "n": "n_gen"}),
        on=["id_institucion", "gen_norm"], how="left",
    ).merge(
        nacional.rename(columns={"val": "e_nac", "n": "n_nac"}),
        on="gen_norm", how="left",
    )

    def _resolver(fila) -> tuple[float, str, int]:
        if pd.notna(fila["e_exacto"]):
            return fila["e_exacto"], "exacto", int(fila["n_exacto"])
        if pd.notna(fila["e_gen"]):
            return fila["e_gen"], "media_institucion_generica", int(fila["n_gen"])
        if pd.notna(fila["e_nac"]):
            return fila["e_nac"], "media_nacional", int(fila["n_nac"])
        return pd.NA, "sin_dato", 0

    res = out.apply(_resolver, axis=1, result_type="expand")
    res.columns = ["empleabilidad_1er_anio", "empleabilidad_fuente", "n_empleabilidad_asociadas"]
    return pd.concat([out[["id_institucion", "carrera_norm"]], res], axis=1)


def generar_puente_llaves(tit: pd.DataFrame, emp: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Construye P2: unión Titulados ∪ Empleabilidad resuelta en 3 niveles."""
    exacto, generica, nacional = tablas_emp(emp)
    tit_agg = agregar_titulados(tit)

    # --- 1) Empleabilidad: una fila por carrera medida (queda siempre a su grano) ---
    emp_claves = emp[["id_institucion", "carrera_norm", "gen_norm"]].drop_duplicates()
    emp_res = resolver_empleabilidad(emp_claves, exacto, generica, nacional)
    emp_info = (
        emp.groupby(["id_institucion", "carrera_norm"], as_index=False)
        .agg(
            institucion=("institucion", "first"),
            tipo_institucion=("tipo_institucion", "first"),
            carrera=("carrera", "first"),
            carrera_generica=("carrera_generica", "first"),
        )
    )
    emp_lado = emp_res.merge(emp_info, on=["id_institucion", "carrera_norm"], how="left")
    emp_lado = emp_lado.merge(
        tit_agg.drop(columns=["institucion", "tipo_institucion", "carrera",
                              "carrera_generica", "gen_norm"]),
        on=["id_institucion", "carrera_norm"], how="left",
    )
    # Sin titulados coincidentes → oferta 0 y sin atributos CINE.
    for col in ("titulaciones_total", "titulaciones_ult_anio", "titulados_mayores_40",
                "n_regiones_titulados"):
        emp_lado[col] = emp_lado[col].fillna(0).astype("Int64")
    emp_lado["origen"] = [
        "ambos" if pd.notna(t) else "solo_empleabilidad"
        for t in emp_lado["anio_ultima_titulacion"]
    ]
    emp_lado["cine13_area"] = emp_lado.get("cine13_area", pd.NA)
    emp_lado["cine13_subarea"] = emp_lado.get("cine13_subarea", pd.NA)
    emp_lado["nivel_carrera"] = emp_lado.get("nivel_carrera", pd.NA)
    emp_lado["anio_ultima_titulacion"] = emp_lado["anio_ultima_titulacion"].astype("Int64")

    # --- 2) Titulados: nivel de match por llave (SOLO las no presentes en Empleabilidad,
    #         porque las coincidentes ya quedaron en emp_lado con ambos lados) ---
    emp_keys = emp[["id_institucion", "carrera_norm"]].drop_duplicates()
    tit_agg = tit_agg.merge(
        emp_keys.assign(_en_emp=True), on=["id_institucion", "carrera_norm"], how="left"
    )
    sin_emp = tit_agg["_en_emp"].isna()
    log.info("Titulados sin fila Empleabilidad exacta: %d de %d llaves (%.1f%%)",
             int(sin_emp.sum()), len(tit_agg), 100 * sin_emp.mean())
    tit_agg = tit_agg.drop(columns="_en_emp")
    tit_llaves = tit_agg.loc[sin_emp, ["id_institucion", "carrera_norm", "gen_norm"]].copy()
    tit_res = resolver_empleabilidad(tit_llaves, exacto, generica, nacional)
    tit_agg = tit_agg.loc[sin_emp].merge(
        tit_res, on=["id_institucion", "carrera_norm"], how="left"
    )
    tit_agg["origen"] = [
        "ambos" if f != "sin_dato" else "solo_titulados"
        for f in tit_agg["empleabilidad_fuente"]
    ]

    # Residuo: carreras cuyo valor SOLO existe a nivel nacional (o nada) → colapsar
    # por (institución, genérica) para no repetir la media nacional por carrera.
    residuo_mask = tit_agg["empleabilidad_fuente"].isin(["media_nacional", "sin_dato"])
    tit_residuo = tit_agg[residuo_mask].copy()
    tit_exacto = tit_agg[~residuo_mask].copy()

    if len(tit_residuo):
        colapsado = (
            tit_residuo.groupby(["id_institucion", "gen_norm"], as_index=False)
            .agg(
                institucion=("institucion", "first"),
                tipo_institucion=("tipo_institucion", "first"),
                carrera_generica=("carrera_generica", "first"),
                cine13_area=("cine13_area", lambda s: " | ".join(
                    sorted({v for v in s if isinstance(v, str) and v}))),
                cine13_subarea=("cine13_subarea", lambda s: " | ".join(
                    sorted({v for v in s if isinstance(v, str) and v}))),
                nivel_carrera=("nivel_carrera", "first"),
                titulaciones_total=("titulaciones_total", "sum"),
                titulaciones_ult_anio=("titulaciones_ult_anio", "sum"),
                titulados_mayores_40=("titulados_mayores_40", "sum"),
                n_regiones_titulados=("n_regiones_titulados", "max"),
                anio_ultima_titulacion=("anio_ultima_titulacion", "max"),
                empleabilidad_1er_anio=("empleabilidad_1er_anio", "first"),
                empleabilidad_fuente=("empleabilidad_fuente", "first"),
                n_empleabilidad_asociadas=("n_empleabilidad_asociadas", "first"),
                n_carreras_colapsadas=("carrera_norm", "size"),
            )
        )
        colapsado["carrera"] = colapsado["carrera_generica"].map(
            lambda g: f"[GENÉRICA] {g}")
        # Identidad del residuo = la genérica institucional (evita choque de PK).
        colapsado["carrera_norm"] = colapsado["gen_norm"]
        colapsado["origen"] = [
            "solo_titulados" if f == "sin_dato" else "ambos"
            for f in colapsado["empleabilidad_fuente"]
        ]
        log.info(
            "Residuo generica: %d carreras de Titulados colapsadas en %d llaves "
            "(match solo nacional o sin dato)",
            int(colapsado["n_carreras_colapsadas"].sum()), len(colapsado),
        )
    else:
        colapsado = pd.DataFrame(columns=list(PUENTE_LLAVES_CARRERA) + ["n_carreras_colapsadas"])

    # --- 3) Unión y tipado estricto ---
    puente = pd.concat([tit_exacto, emp_lado, colapsado], ignore_index=True, sort=False)

    # Defensa: un residuo (id, gen_norm) no debería chocar con una llave exacta
    # (una carrera específica con el mismo nombre normalizado que su genérica en la
    # misma institución). Si chocara, el residuo se marca con prefijo "GEN::".
    if puente.duplicated(["id_institucion", "carrera_norm"]).any():
        es_residuo = puente["carrera"].str.startswith("[GENÉRICA]", na=False)
        chocan = puente.duplicated(["id_institucion", "carrera_norm"], keep=False) & es_residuo
        puente.loc[chocan, "carrera_norm"] = (
            "GEN::" + puente.loc[chocan, "gen_norm"]
        )
        log.warning("Residuos renombrados por colisión de PK: %d", int(chocan.sum()))

    puente["nivel_match"] = puente["empleabilidad_fuente"].map(_MAPEA_NIVEL)
    for col in PUENTE_LLAVES_CARRERA:
        if col not in puente.columns:
            puente[col] = pd.NA
    puente = puente[list(PUENTE_LLAVES_CARRERA)].astype(PUENTE_LLAVES_CARRERA)

    métricas = _metricas_cobertura(puente)
    return puente, métricas


_MAPEA_NIVEL = {
    "exacto": "exacto",
    "media_institucion_generica": "generica",
    "media_nacional": "nacional",
    "sin_dato": "ninguno",
}


def _metricas_cobertura(puente: pd.DataFrame) -> dict:
    """
    Cobertura bidireccional:
      - Lado Empleabilidad: por construcción cada fila MiFuturo queda en nivel exacto;
        lo que se reporta aquí es el % de carreras Ti con empleabilidad resuelta.
      - Lado Titulados: % de llaves (residuos colapsados incluidos) por nivel de match.
      - Volumen: % de titulaciones (2007-2025) cubiertas con algún valor de empleabilidad.
    """
    con_valor = puente["empleabilidad_fuente"] != "sin_dato"
    total_tit = puente["titulaciones_total"].sum()
    cubierto_tit = puente.loc[con_valor, "titulaciones_total"].sum()
    # Lado Titulados = todas las filas menos las que solo vienen de MiFuturo.
    lado_tit = puente[puente["origen"] != "solo_empleabilidad"]
    return {
        "filas_puente": len(puente),
        "pct_titulados_con_empleabilidad": (
            100 * cubierto_tit / total_tit if total_tit else 0.0
        ),
        "pct_lado_titulados_por_nivel": (
            lado_tit["nivel_match"].value_counts(normalize=True).mul(100).round(1).to_dict()
        ),
        "nivel_match_total": puente["nivel_match"].value_counts().to_dict(),
    }


# --------------------------------------------------------------------------- #
# Validaciones (esquema.VALIDACIONES)
# --------------------------------------------------------------------------- #
def validar_llaves(df: pd.DataFrame, métricas: dict) -> None:
    log.info("=== Validaciones P2_puente_llaves_carrera (%d filas) ===", len(df))

    dup = int(df.duplicated(["id_institucion", "carrera_norm"]).sum())
    log.info("  [%s] 1. PK (id_institucion, carrera_norm) única    : %d duplicados",
             "✓" if dup == 0 else "✗", dup)

    mal_orig = sorted(set(df["origen"]) - set(ORIGEN_LLAVES))
    mal_nivel = sorted(set(df["nivel_match"]) - set(NIVELES_MATCH))
    mal_fuente = sorted(set(df["empleabilidad_fuente"]) - set(FUENTES_EMPLEABILIDAD))
    log.info("  [%s] 2. Catálogos respetados (origen/nivel/fuente) : %s",
             "✓" if not (mal_orig or mal_nivel or mal_fuente) else "✗",
             "correcto" if not (mal_orig or mal_nivel or mal_fuente)
             else f"{mal_orig} {mal_nivel} {mal_fuente}")

    e = df["empleabilidad_1er_anio"]
    rango_ok = bool(((e.dropna() >= 0) & (e.dropna() <= 100)).all())
    na_sindato = bool((e.isna() == (df["empleabilidad_fuente"] == "sin_dato")).all())
    log.info("  [%s] 3. empleabilidad ∈ [0,100]; NA ⇔ sin_dato    : rango_ok=%s, na_coherente=%s",
             "✓" if rango_ok and na_sindato else "✗", rango_ok, na_sindato)

    exactas = df[df["nivel_match"] == "exacto"]
    ok4 = bool(
        (exactas["empleabilidad_fuente"] == "exacto").all()
        and (exactas["n_empleabilidad_asociadas"] == 1).all()
    )
    log.info("  [%s] 4. nivel exacto ⇒ fuente exacto y n=1        : %d filas exactas",
             "✓" if ok4 else "✗", len(exactas))

    ok5_total = bool((df["titulaciones_total"].fillna(0) >= df["titulados_mayores_40"].fillna(0)).all())
    solo_emp = df["origen"] == "solo_empleabilidad"
    ok5_emp = bool((df.loc[solo_emp, "titulaciones_total"].fillna(0) == 0).all())
    log.info("  [%s] 5. total ≥ mayores_40; solo_empleabilidad ⇒ 0 : %s / %s (%d filas solo_empleabilidad)",
             "✓" if ok5_total and ok5_emp else "✗", ok5_total, ok5_emp, int(solo_emp.sum()))

    log.info("  [i] 6. COBERTURA BIDIRECCIONAL:")
    log.info("       Filas del puente                       : %d", métricas["filas_puente"])
    log.info("       Lado Titulados por nivel de match:")
    for nivel, pct in sorted(métricas["pct_lado_titulados_por_nivel"].items()):
        log.info("         %-10s %5.1f%%", nivel, pct)
    log.info("       Volumen de titulados con empleabilidad : %.1f%%",
             métricas["pct_titulados_con_empleabilidad"])
    log.info("       Distribución nivel_match (todas las filas): %s",
             métricas["nivel_match_total"])


def generar_p2() -> Path:
    """Construye, valida y exporta P2."""
    tit, emp = cargar_fuentes()
    llaves, métricas = generar_puente_llaves(tit, emp)
    validar_llaves(llaves, métricas)
    DIR_SALIDA.mkdir(parents=True, exist_ok=True)
    ruta = DIR_SALIDA / "P2_puente_llaves_carrera.csv"
    llaves.to_csv(ruta, sep=SEPARADOR_SALIDA, index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas, %.1f MB)", ruta.name, len(llaves),
             ruta.stat().st_size / (1024 * 1024))
    return ruta


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ruta = generar_p2()
    llaves = pd.read_csv(ruta, sep=SEPARADOR_SALIDA, dtype=PUENTE_LLAVES_CARRERA)
    print(f"\nP2 llaves carrera: {ruta.name} ({len(llaves):,} filas × {len(llaves.columns)} cols)")
    print("\nDistribución por nivel_match:")
    print(llaves["nivel_match"].value_counts().to_string())
    print("\nDistribución por origen:")
    print(llaves["origen"].value_counts().to_string())
    print("\nEmpleabilidad resuelta (no nula):",
          f"{llaves['empleabilidad_1er_anio'].notna().sum():,} filas "
          f"({100*llaves['empleabilidad_1er_anio'].notna().mean():.1f}%)")
    print("\nEjemplos de nivel 'exacto':")
    ej = llaves[llaves["nivel_match"] == "exacto"][
        ["id_institucion", "carrera", "empleabilidad_1er_anio", "titulaciones_total"]
    ].head(5)
    print(ej.to_string(index=False))

    # Reporte de inspección estándar del proyecto sobre la salida
    sys.path.insert(0, str(DIR_SCRAPERS / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(ruta)
