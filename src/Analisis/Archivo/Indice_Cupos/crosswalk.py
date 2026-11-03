"""
<src/Analisis/Archivo/Indice_Cupos/crosswalk.py>

Paso 5: calcula el índice uniendo las partes de la fórmula.

    índice = Empleabilidad × (Jubilaciones + Vacantes privadas + Vacantes públicas) / (Titulados 2025 + Desocupados)

Salidas: Salida/indice_cupos_carrera_region.csv, Salida/indice_cupos_carrera_nacional.csv y Salida/indice_cupos_validacion.csv

Decisiones del usuario (02-11-26): pregrado terminal; Titulados como flujo anual (2025), para que
todas las partes sean de un año; la suma de la fórmula es la base y el doble conteo jubilación-vacantes
va como sensibilidad (indice_sin_doble_conteo solo suma las jubilaciones fuera del empleo privado). Las
vacantes públicas (CW_Demanda_Publica) son estimadas, pero entran al valor principal porque reducen el
sesgo contra carreras públicas (decisión 02-11-26); indice_solo_privado conserva la versión sin ellas.

Empleabilidad: una por carrera a nivel nacional, ponderada por titulaciones 2021-2025. MiFuturo no
tiene región, así que no distingue regiones. Sin dato, hereda de su área y nivel y lo declara.

Lectura: es un índice para comparar, no una probabilidad. La región de Titulados es la de la sede, de
modo que una región con pocas sedes y mucha demanda da valores altos, que pueden superar 100. La tabla
nacional no tiene ese problema y es la más sólida. Hay que leerlo con pct_asalariado_privado: ENADEL
no ve el sector público.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers"))
from comun.normalizador import REGIONES  # noqa: E402
from esquema import INDICE_CARRERA_NACIONAL, INDICE_CARRERA_REGION, VALIDACION_INDICE  # noqa: E402
import obtener  # noqa: E402

log = logging.getLogger(__name__)

DIR_SALIDA = Path(__file__).parent / "Salida"
ANIO_FLUJO, ANIOS_PROMEDIO, ANIO_INICIO_EMPLEABILIDAD = 2025, [2023, 2024, 2025], 2021
N_PRIVADO, T_ALTA, T_MEDIA, T_ALTA_NACIONAL = 60, 30, 10, 100
VARIANTES = ["indice_sin_doble_conteo", "indice_vacantes_menciones", "indice_edad_legal", "indice_titulados_3_anios", "indice_solo_privado", "indice_publico_sin_jubilacion"]
TOP = 20


def empleabilidad_por_carrera(paso1: pd.DataFrame, catalogo: pd.DataFrame) -> pd.DataFrame:
    """Promedio ponderado por titulaciones recientes; hereda del área y nivel si no hay dato."""
    x = paso1[(paso1["anio"] >= ANIO_INICIO_EMPLEABILIDAD) & paso1["empleabilidad_1er_anio"].notna()]
    x = x.assign(masa=x["empleabilidad_1er_anio"] * x["total_titulaciones"])
    g = x.groupby("carrera_generica")[["masa", "total_titulaciones"]].sum()
    g = g[g["total_titulaciones"] > 0]
    medida = (g["masa"] / g["total_titulaciones"]).rename("empleabilidad_pct")
    t = catalogo.merge(medida, left_on="carrera_generica", right_index=True, how="left")
    pesos = catalogo.merge(g, left_on="carrera_generica", right_index=True, how="inner")
    area = pesos.groupby(["area_cine_sies", "nivel_titulo"])[["masa", "total_titulaciones"]].sum()
    area = (area["masa"] / area["total_titulaciones"]).rename("heredada").reset_index()
    t = t.merge(area, on=["area_cine_sies", "nivel_titulo"], how="left")
    t["origen_empleabilidad"] = np.where(t["empleabilidad_pct"].notna(), "medida", "heredada_area_nivel")
    t["empleabilidad_pct"] = t["empleabilidad_pct"].fillna(t["heredada"])
    return t.drop(columns="heredada")


def proporcion_privada(privado: pd.DataFrame, catalogo: pd.DataFrame) -> pd.Series:
    """% asalariado privado por carrera; con menos de 60 casos usa su nivel."""
    f = lambda g: pd.Series({"n": len(g), "p": 100 * g.loc[g["o15"] == 5, "expr"].sum() / g["expr"].sum()})
    c = privado.groupby("carrera_generica").apply(f, include_groups=False)
    n = privado.groupby("nivel_titulo").apply(f, include_groups=False)["p"]
    base = catalogo.set_index("carrera_generica")["nivel_titulo"].map(n)
    propio = c["p"].where(c["n"] >= N_PRIVADO).reindex(base.index)
    return propio.fillna(base).rename("pct_asalariado_privado")


def calcular_indice(t: pd.DataFrame) -> pd.DataFrame:
    """Aplica la fórmula y sus sensibilidades. Sin competidores queda NA: no hay a quién comparar."""
    den = t["titulados_2025"] + t["desocupados"]
    den = den.where(den > 0)
    e = t["empleabilidad_pct"] / 100
    fuera_privado = t["jubilaciones_anuales"] * (1 - t["pct_asalariado_privado"] / 100)
    den3 = (t["titulados_3_anios"] + t["desocupados"]).where(lambda s: s > 0)
    privada = t["vacantes_proyectadas"]
    total = privada + t["vacantes_publicas"]
    t["cupos_por_100"] = 100 * (t["jubilaciones_anuales"] + total) / den
    t["indice_cupos"] = e * t["cupos_por_100"]
    t["indice_solo_privado"] = 100 * e * (t["jubilaciones_anuales"] + privada) / den
    t["indice_sin_doble_conteo"] = 100 * e * (fuera_privado + total) / den
    t["indice_vacantes_menciones"] = 100 * e * (t["jubilaciones_anuales"] + t["vacantes_con_menciones"] + t["vacantes_publicas"]) / den
    t["indice_edad_legal"] = 100 * e * (t["jubilaciones_edad_legal"] + total) / den
    t["indice_titulados_3_anios"] = 100 * e * (t["jubilaciones_anuales"] + total) / den3
    t["indice_publico_sin_jubilacion"] = 100 * e * total / den
    t["alerta_empleo_publico"] = t["pct_asalariado_privado"] < 50
    t["supera_100"] = t["indice_cupos"].gt(100)
    return t


def preparar() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    catalogo = obtener.cargar_catalogo()
    paso1 = obtener.cargar_paso1()
    d, j, v = obtener.cargar_desocupados(), obtener.cargar_jubilacion(), obtener.cargar_vacantes()
    llaves = ["codigo_region", "carrera_generica"]
    flujo = paso1[paso1["anio"] == ANIO_FLUJO].groupby(llaves, as_index=False)["total_titulaciones"].sum().rename(columns={"total_titulaciones": "titulados_2025"})
    tres = paso1[paso1["anio"].isin(ANIOS_PROMEDIO)].groupby(llaves, as_index=False)["total_titulaciones"].sum()
    tres["titulados_3_anios"] = tres["total_titulaciones"] / len(ANIOS_PROMEDIO)
    dd = d.groupby(llaves, as_index=False).agg(desocupados=("desocupados_estimados", "sum"), fiabilidad_desocupados=("fiabilidad_celda", "first"))
    t = dd.merge(flujo, on=llaves, how="outer").merge(tres[llaves + ["titulados_3_anios"]], on=llaves, how="outer").merge(
        j[llaves + ["jubilaciones_anuales", "jubilaciones_edad_legal"]], on=llaves, how="outer").merge(
        v[llaves + ["vacantes_estimadas", "vacantes_con_menciones", "vacantes_sin_winsorizar"]].rename(columns={"vacantes_estimadas": "vacantes_proyectadas"}), on=llaves, how="outer")
    t = t.merge(obtener.cargar_vacantes_publicas()[llaves + ["vacantes_publicas"]], on=llaves, how="outer")
    numericas = ["desocupados", "titulados_2025", "titulados_3_anios", "jubilaciones_anuales", "jubilaciones_edad_legal",
                 "vacantes_proyectadas", "vacantes_con_menciones", "vacantes_sin_winsorizar", "vacantes_publicas"]
    t[numericas] = t[numericas].fillna(0.0)
    t["fiabilidad_desocupados"] = t["fiabilidad_desocupados"].fillna("sin_celda")
    empleo = empleabilidad_por_carrera(paso1, catalogo)
    privado = proporcion_privada(obtener.cargar_privado(), catalogo)
    t = t.merge(empleo, on="carrera_generica", how="inner").merge(privado, left_on="carrera_generica", right_index=True, how="left")
    return t, empleo, privado


def confianza_region(t: pd.DataFrame) -> pd.Series:
    """Alta solo si cada parte tiene base propia; baja si el dato se apoya en herencia o pocos titulados."""
    medida = t["origen_empleabilidad"] == "medida"
    propia = t["nivel_confianza_perfil"] == "A_propia"
    alta = propia & medida & (t["titulados_2025"] >= T_ALTA) & t["fiabilidad_desocupados"].isin(["fiable", "poco_fiable"])
    media = medida & (t["nivel_confianza_perfil"] != "C_nivel") & (t["titulados_2025"] >= T_MEDIA)
    return pd.Series(np.select([alta, media], ["alta", "media"], "baja"), index=t.index)


def tabla_region(t: pd.DataFrame) -> pd.DataFrame:
    r = calcular_indice(t.copy())
    r["nombre_region"] = r["codigo_region"].map(REGIONES)
    r["confianza_indice"] = confianza_region(r)
    return r[list(INDICE_CARRERA_REGION)].astype(INDICE_CARRERA_REGION).sort_values(["codigo_region", "indice_cupos"], ascending=[True, False])


def tabla_nacional(t: pd.DataFrame, razon: pd.DataFrame) -> pd.DataFrame:
    fijas = ["carrera_generica", "nivel_titulo", "area_cine_sies", "empleabilidad_pct", "origen_empleabilidad", "pct_asalariado_privado", "nivel_confianza_perfil"]
    n = t.groupby(fijas, as_index=False)[["jubilaciones_anuales", "jubilaciones_edad_legal", "vacantes_proyectadas", "vacantes_con_menciones",
                                          "titulados_2025", "titulados_3_anios", "desocupados", "vacantes_publicas"]].sum()
    n = calcular_indice(n)
    n["confianza_indice"] = np.select(
        [(n["nivel_confianza_perfil"] == "A_propia") & (n["origen_empleabilidad"] == "medida") & (n["titulados_2025"] >= T_ALTA_NACIONAL),
         (n["origen_empleabilidad"] == "medida") & (n["titulados_2025"] >= T_MEDIA)], ["alta", "media"], "baja")
    z = razon[["carrera_generica", "ocupados_por_10", "desocupados_por_10", "inactivos_por_10", "fiabilidad"]].rename(columns={"fiabilidad": "fiabilidad_razon_empleo"})
    n = n.merge(z, on="carrera_generica", how="left")
    n["fiabilidad_razon_empleo"] = n["fiabilidad_razon_empleo"].fillna("sin_dato")
    return n[list(INDICE_CARRERA_NACIONAL)].astype(INDICE_CARRERA_NACIONAL).sort_values("indice_cupos", ascending=False)


def validacion(r: pd.DataFrame, n: pd.DataFrame, razon: pd.DataFrame) -> pd.DataFrame:
    filas = []
    agregar = lambda p, g, v, d: filas.append({"prueba": p, "grupo": g, "valor": float(v), "descripcion": d})
    base = n[n["confianza_indice"] != "baja"].dropna(subset=["indice_cupos"])
    top = set(base.nlargest(TOP, "indice_cupos")["carrera_generica"])
    for v in VARIANTES:
        agregar("orden_frente_a_base", v, base[["indice_cupos", v]].corr(method="spearman").iloc[0, 1], f"Correlación de rangos en {len(base)} carreras de confianza alta o media")
        agregar(f"coincidencia_top_{TOP}", v, len(top & set(base.nlargest(TOP, v)["carrera_generica"])), f"Carreras que siguen entre las {TOP} primeras")
    for nivel, g in base.groupby("nivel_titulo"):
        agregar("mediana_per", nivel, g["indice_cupos"].median(), "Mediana nacional de carreras de confianza alta o media")
    m = base.merge(razon[razon["n_activos"] >= 200][["carrera_generica", "tasa_desempleo_pct"]], on="carrera_generica")
    agregar("frente_a_desempleo_casen", "todas", m[["indice_cupos", "tasa_desempleo_pct"]].corr(method="spearman").iloc[0, 1], f"Correlación de rangos en {len(m)} carreras con 200 activos o más; se espera negativa")
    for col in ("indice_cupos", "indice_solo_privado", "indice_publico_sin_jubilacion"):
        agregar("sesgo_frente_a_pct_privado", col, base[[col, "pct_asalariado_privado"]].corr(method="spearman").iloc[0, 1], f"Correlación de rangos en {len(base)} carreras; cuanto más cerca de 0, menos sesgo")
        agregar("frente_a_desempleo_casen_variante", col, m[[col, "tasa_desempleo_pct"]].corr(method="spearman").iloc[0, 1], f"En {len(m)} carreras con 200 activos o más; se espera negativa")
    agregar("filas_regionales", "total", len(r), "Combinaciones carrera y región")
    agregar("filas_regionales", "supera_100", int(r["supera_100"].sum()), "Valores sobre 100, efecto probable de la región de la sede")
    for c, x in r.groupby("confianza_indice"):
        agregar("filas_regionales", c, len(x), "Combinaciones por confianza")
    return pd.DataFrame(filas)[list(VALIDACION_INDICE)].astype(VALIDACION_INDICE)


def validar(t: pd.DataFrame, r: pd.DataFrame, n: pd.DataFrame) -> None:
    d, j, v = obtener.cargar_desocupados(), obtener.cargar_jubilacion(), obtener.cargar_vacantes()
    paso1 = obtener.cargar_paso1()
    pares = [("desocupados", d["desocupados_estimados"].sum()), ("jubilaciones_anuales", j["jubilaciones_anuales"].sum()),
             ("vacantes_proyectadas", v["vacantes_estimadas"].sum()), ("titulados_2025", paso1.loc[paso1["anio"] == ANIO_FLUJO, "total_titulaciones"].sum())]
    controles = {f"Conserva {col}": np.isclose(r[col].sum(), total, rtol=1e-3) for col, total in pares}
    controles |= {
        "Clave regional única": not r.duplicated(["codigo_region", "carrera_generica"]).any(),
        "Nacional coincide con regional": np.isclose(n["titulados_2025"].sum(), r["titulados_2025"].sum()),
        "Regiones 1-16": r["codigo_region"].nunique() == 16,
        "índice no negativo": r["indice_cupos"].dropna().ge(0).all(),
        "Empleabilidad en todas las carreras": r["empleabilidad_pct"].notna().all(),
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    if not all(controles.values()):
        raise ValueError(f"Validaciones fallidas: {[k for k, ok in controles.items() if not ok]}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    t, _, _ = preparar()
    razon = obtener.cargar_razon()
    r, n = tabla_region(t), tabla_nacional(t, razon)
    validar(t, r, n)
    v = validacion(r, n, razon)
    DIR_SALIDA.mkdir(exist_ok=True)
    rutas = [(DIR_SALIDA / "indice_cupos_carrera_region.csv", r), (DIR_SALIDA / "indice_cupos_carrera_nacional.csv", n), (DIR_SALIDA / "indice_cupos_validacion.csv", v)]
    for ruta, tabla in rutas:
        tabla.to_csv(ruta, sep=";", index=False, encoding="utf-8")
        log.info("CSV generado: %s (%d filas)", ruta.name, len(tabla))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    for ruta, _ in rutas:
        inspeccion_rigurosa(ruta)
