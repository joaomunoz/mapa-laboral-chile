"""
<src/Analisis/JOINS/CW_Demanda_Empresarial/crosswalk.py>

Paso 4 del índice: estima Vacantes Proyectadas por carrera y región, numerador de la fórmula.

Salidas: Salida/vacantes_carrera_region.csv, Salida/vacantes_carrera_region_actividad.csv,
         Salida/vacantes_region_actividad.csv y Salida/vacantes_validacion.csv

Cadena: V(c,r,s) = V(r,s) × π(título | s) × w(c | r,s,título)
  V(r,s): vacantes ENADEL actuales + futuras 2025 (b11 + b12), por región y actividad.
  π:      parte de las vacantes de cada actividad que exige título, según contrataciones reales (c1).
  w:      peso de la carrera entre los ocupados de ese nivel, región y actividad (tabla de ocupados).

Decisiones:
  - b11 + b12 se suma aceptando un nulo: ENADEL/procesar.py deja la suma vacía si falta uno. Si
    faltan ambos no se imputa, por lo que el total tiende a quedar bajo.
  - Tope a empresas influyentes (winsorización al percentil 99 del aporte expandido): una empresa
    de 70 trabajadores aportaba 40.663 vacantes por su factor. Sin el tope, las estimaciones
    dependerían de unas pocas respuestas; el valor sin tope queda como sensibilidad.
  - Celdas débiles: una región × actividad solo usa su dato si tiene 30 empresas, ninguna aporta más
    de 25% y CV <= 30%. Lo demás reparte el total regional con la mezcla nacional × peso relativo
    dla actividad en la región (idea del usuario, 02-11-26).
  - π se mide con cantidades (c1) y no con menciones (c3), que no traen cantidad y dan igual peso
    a un cargo con 1 vacante y a otro con 500. Sale el mismo dato con c3 como sensibilidad, porque
    la diferencia es grande. Se usa π nacional por actividad porque c1 no alcanza por región.

Límite principal: ENADEL cubre empresas privadas formales. Las carreras del sector público
(Pedagogía, Medicina) quedan subestimadas: pct_asalariado_privado dice cuánto. El reparto asume que
las vacantes se distribuyen como los ocupados actuales.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers"))
from comun.normalizador import REGIONES  # noqa: E402
from esquema import (  # noqa: E402
    VACANTES_CARRERA_REGION,
    VACANTES_CARRERA_REGION_ACTIVIDAD,
    VACANTES_REGION_ACTIVIDAD,
    VALIDACION_VACANTES,
)
import obtener  # noqa: E402

log = logging.getLogger(__name__)

DIR_SALIDA = Path(__file__).parent / "Salida"
PERCENTIL_TOPE = 0.99
MIN_EMPRESAS, MAX_EMPRESA_PCT, CV_MAXIMO, MIN_CARGOS_ACTIVIDAD, N_PRIVADO = 30, 25.0, 30.0, 30, 60
TITULO_POR_NIVEL = {"Técnico superior": "Tecnico", "Profesional": "Profesional",
                    "Profesional con Magíster": "Profesional", "Profesional con Doctorado": "Profesional"}
NIVELES = ("Tecnico", "Profesional")


def winsorizar(aporte: pd.Series) -> tuple[pd.Series, float]:
    """Limita cada aporte positivo al percentil elegido."""
    tope = aporte[aporte > 0].quantile(PERCENTIL_TOPE)
    return aporte.clip(upper=tope), tope


def preparar_empresas(e: pd.DataFrame) -> pd.DataFrame:
    e = e.copy()
    e["vacantes"] = e[["vacantes_actuales", "vacantes_futuras_2025"]].sum(axis=1, min_count=1).fillna(0)
    e["aporte_sin_tope"] = e["vacantes"] * e["pond_final"]
    e["aporte"], tope = winsorizar(e["aporte_sin_tope"])
    log.info("Vacantes expandidas: %.0f; con tope de %.0f por empresa: %.0f (%d empresas afectadas)",
             e["aporte_sin_tope"].sum(), tope, e["aporte"].sum(), int((e["aporte_sin_tope"] > tope).sum()))
    return e


def cv_celda(g: pd.DataFrame, col: str, psu: pd.Series) -> float:
    z = g.groupby(["varstrat", "varunit"], sort=False)[col].sum()
    h = z.groupby(level="varstrat", sort=False).agg(s="sum", s2=lambda v: (v**2).sum())
    n_h = psu.reindex(h.index).to_numpy(dtype=float)
    var = np.where(n_h > 1, n_h / np.maximum(n_h - 1, 1) * (h["s2"] - h["s"]**2 / n_h), 0.0).sum()
    total = g[col].sum()
    return 100 * np.sqrt(var) / total if total > 0 else np.inf


def celdas_region_actividad(e: pd.DataFrame, pesos: pd.DataFrame, col: str = "aporte") -> pd.DataFrame:
    """Vacantes por región y actividad, aplicando la estrategia para celdas débiles."""
    psu = e[["varstrat", "varunit"]].drop_duplicates().groupby("varstrat").size()
    filas = []
    for (region, seccion), g in e.groupby(["codigo_region", "actividad_ciiu"]):
        total = g[col].sum()
        mayor = 100 * g[col].max() / total if total > 0 else 100.0
        cv = cv_celda(g, col, psu)
        filas.append({"codigo_region": region, "actividad_ciiu": seccion, "n_empresas": len(g), "vacantes_directo": total,
                      "vacantes_sin_winsorizar": g["aporte_sin_tope"].sum(), "pct_empresa_mayor": mayor,
                      "cv_pct": cv if np.isfinite(cv) else np.nan,
                      "celda_fiable": total > 0 and len(g) >= MIN_EMPRESAS and mayor <= MAX_EMPRESA_PCT and cv <= CV_MAXIMO})
    c = pd.DataFrame(filas)
    mezcla = c.groupby("actividad_ciiu")["vacantes_directo"].sum()
    relativo = pesos.set_index(["codigo_region", "actividad_ciiu"])["peso_relativo"]
    c["origen_celda"] = np.where(c["celda_fiable"], "celda_propia", "mezcla_nacional_ponderada")
    c["vacantes_usadas"] = c["vacantes_directo"]
    for region, g in c.groupby("codigo_region"):
        debiles = g[~g["celda_fiable"]]
        if debiles.empty:
            continue
        base = debiles["actividad_ciiu"].map(mezcla).to_numpy(dtype=float)
        peso = np.array([relativo.get((region, s), 0.0) for s in debiles["actividad_ciiu"]])
        cuota = base * peso
        c.loc[debiles.index, "vacantes_usadas"] = debiles["vacantes_directo"].sum() * cuota / cuota.sum()
    c["nombre_region"] = c["codigo_region"].map(REGIONES)
    return c[list(VACANTES_REGION_ACTIVIDAD)].astype(VACANTES_REGION_ACTIVIDAD)


def parte_con_titulo(e: pd.DataFrame, cargos: pd.DataFrame, fuente: str) -> pd.DataFrame:
    """π: fracción de vacantes de cada actividad por nivel; una actividad con pocos cargos usa el total."""
    c = cargos.merge(e[["idempresa_ficticio", "actividad_ciiu"]], on="idempresa_ficticio")
    c = c[c["nivel_educacional"].notna()].copy()
    c["nivel"] = c["nivel_educacional"].map(TITULO_POR_NIVEL).fillna("Sin_titulo")
    if fuente == "cantidades":
        c = c[(c["origen_bloque"] == "vacante_historica") & c["cantidad_contratada"].notna()]
        c["aporte"], _ = winsorizar(c["cantidad_contratada"] * c["pond_final"])
    else:
        c = c[c["origen_bloque"] == "vacante_2025"]
        c["aporte"] = c["pond_final"]
    t = c.pivot_table(index="actividad_ciiu", columns="nivel", values="aporte", aggfunc="sum", fill_value=0.0).reindex(columns=[*NIVELES, "Sin_titulo"], fill_value=0.0)
    pi = t.div(t.sum(axis=1), axis=0)
    general = t.sum() / t.sum().sum()
    pocos = c.groupby("actividad_ciiu").size().reindex(pi.index, fill_value=0) < MIN_CARGOS_ACTIVIDAD
    pi.loc[pocos] = general.to_numpy()
    if pocos.any():
        log.info("π general en actividades con pocos cargos (%s): %s", fuente, pi.index[pocos].tolist())
    log.info("π total (%s): %s", fuente, general.round(3).to_dict())
    return pi.reindex(sorted(set(e["actividad_ciiu"]))).fillna(general)


def repartir(celdas: pd.Series, pi: pd.DataFrame, ocupados: pd.DataFrame) -> pd.DataFrame:
    """Lleva V(r,s) a carreras con π y el peso de la carrera entre los ocupados."""
    nacional = ocupados.groupby(["nivel_titulo", "actividad_ciiu", "carrera_generica"], as_index=False)["ocupados_estimados"].sum()
    partes = []
    grupos = dict(tuple(ocupados.groupby(["codigo_region", "nivel_titulo", "actividad_ciiu"])))
    for (region, seccion), v in celdas.items():
        for nivel in NIVELES:
            monto = v * pi.loc[seccion, nivel]
            if monto <= 0:
                continue
            base = grupos.get((region, nivel, seccion))
            if base is None or base["ocupados_estimados"].sum() == 0:
                base = nacional[(nacional["nivel_titulo"] == nivel) & (nacional["actividad_ciiu"] == seccion)]
            if base.empty:
                continue
            w = base["ocupados_estimados"].to_numpy() / base["ocupados_estimados"].sum()
            partes.append(pd.DataFrame({"codigo_region": region, "nivel_titulo": nivel, "actividad_ciiu": seccion,
                                        "carrera_generica": base["carrera_generica"].to_numpy(), "vacantes": monto * w}))
    return pd.concat(partes, ignore_index=True)


def validar(detalle: pd.DataFrame, celdas: pd.DataFrame, pi: pd.DataFrame) -> None:
    objetivo = sum(f.vacantes_usadas * pi.loc[f.actividad_ciiu, list(NIVELES)].sum() for f in celdas.itertuples())
    por_region = celdas.groupby("codigo_region")[["vacantes_directo", "vacantes_usadas"]].sum()
    controles = {
        "Reparto conserva las vacantes con título": np.isclose(detalle["vacantes"].sum(), objetivo, rtol=1e-6),
        "Estrategia de celdas conserva cada región": np.isclose(por_region["vacantes_directo"], por_region["vacantes_usadas"]).all(),
        "Sin negativos": (detalle["vacantes"] >= 0).all(),
        "Regiones 1-16": detalle["codigo_region"].nunique() == 16,
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    if not all(controles.values()):
        raise ValueError("Validaciones fallidas en el Paso 4")


def validacion(e, cargos, pesos, celdas, pi, pi3, sin_tope, base, perfil) -> pd.DataFrame:
    filas = []
    def agregar(prueba, grupo, valor, desc):
        filas.append({"prueba": prueba, "grupo": grupo, "valor": float(valor), "descripcion": desc})

    # 1. Sin ver una celda fiable: ¿la mezcla ponderada la predice mejor que la nacional?
    fiables = celdas[celdas["celda_fiable"]]
    mezcla = celdas.groupby("actividad_ciiu")["vacantes_directo"].sum()
    rel = pesos.set_index(["codigo_region", "actividad_ciiu"])["peso_relativo"]
    d_nac, d_pes, w = [], [], []
    for region, g in fiables.groupby("codigo_region"):
        if len(g) < 2:
            continue
        real = g["vacantes_directo"].to_numpy(dtype=float)
        nac = g["actividad_ciiu"].map(mezcla).to_numpy(dtype=float)
        pes = nac * np.array([rel.get((region, s), 0.0) for s in g["actividad_ciiu"]])
        d_nac.append(50 * np.abs(real / real.sum() - nac / nac.sum()).sum())
        d_pes.append(50 * np.abs(real / real.sum() - pes / pes.sum()).sum())
        w.append(real.sum())
    agregar("celdas_ocultas", "mezcla_nacional", np.average(d_nac, weights=w), f"Disimilitud en {len(w)} regiones con 2 o más celdas fiables")
    agregar("celdas_ocultas", "mezcla_ponderada", np.average(d_pes, weights=w), f"Disimilitud en {len(w)} regiones con 2 o más celdas fiables")

    # 2. Ocupación: lo que predice el perfil frente a los cargos contratados con título.
    c = cargos[(cargos["origen_bloque"] == "vacante_historica") & cargos["cantidad_contratada"].notna()].copy()
    c["nivel"] = c["nivel_educacional"].map(TITULO_POR_NIVEL)
    c["aporte"], _ = winsorizar(c["cantidad_contratada"] * c["pond_final"])
    p = perfil[perfil["dimension"] == "grupo_ocupacion"][["carrera_generica", "grupo_ocupacion", "pct"]]
    for nivel in NIVELES:
        real = c[c["nivel"] == nivel].groupby("ciuo_nivel_1")["aporte"].sum().reindex(range(1, 11), fill_value=0.0).to_numpy(dtype=float)
        pred = base[base["nivel_titulo"] == nivel].groupby("carrera_generica")["vacantes"].sum().rename("v").reset_index().merge(p, on="carrera_generica")
        pred = (pred["v"] * pred["pct"]).groupby(pred["grupo_ocupacion"]).sum().reindex(range(1, 11), fill_value=0.0).to_numpy(dtype=float)
        agregar("ocupacion_cargos", nivel, 50 * np.abs(real / real.sum() - pred / pred.sum()).sum(), "Disimilitud entre ocupación predicha y cargos c1")
        log.info("  Ocupación %s: predicha %s | cargos %s", nivel, np.round(100 * pred / pred.sum(), 1).tolist(), np.round(100 * real / real.sum(), 1).tolist())

    # 3. Rango según las decisiones: la cifra más sensible del paso.
    con_pi = lambda serie, tabla: sum(v * tabla.loc[s, list(NIVELES)].sum() for (r, s), v in serie.items())
    serie = celdas.set_index(["codigo_region", "actividad_ciiu"])["vacantes_usadas"]
    agregar("rango_total", "base", con_pi(serie, pi), "Con tope y π de contrataciones")
    agregar("rango_total", "sin_tope", con_pi(sin_tope, pi), "Sin tope y π de contrataciones")
    agregar("rango_total", "con_menciones", con_pi(serie, pi3), "Con tope y π de cargos 2025")
    agregar("rango_total", "todas_las_vacantes", celdas["vacantes_directo"].sum(), "Con tope, con y sin título")
    return pd.DataFrame(filas)[list(VALIDACION_VACANTES)].astype(VALIDACION_VACANTES)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    e = preparar_empresas(obtener.cargar_empresas())
    cargos, ocupados, pesos, perfil = obtener.cargar_cargos(), obtener.cargar_ocupados(), obtener.cargar_pesos(), obtener.cargar_perfil()
    celdas = celdas_region_actividad(e, pesos)
    celdas_st = celdas_region_actividad(e.assign(aporte=e["aporte_sin_tope"]), pesos)
    pi, pi3 = parte_con_titulo(e, cargos, "cantidades"), parte_con_titulo(e, cargos, "menciones")
    serie = celdas.set_index(["codigo_region", "actividad_ciiu"])["vacantes_usadas"]
    serie_st = celdas_st.set_index(["codigo_region", "actividad_ciiu"])["vacantes_usadas"]
    base, sin_tope, menciones = repartir(serie, pi, ocupados), repartir(serie_st, pi, ocupados), repartir(serie, pi3, ocupados)
    validar(base, celdas, pi)

    claves = ["codigo_region", "nivel_titulo", "carrera_generica"]
    t = base.groupby(claves, as_index=False)["vacantes"].sum().rename(columns={"vacantes": "vacantes_estimadas"})
    for nombre, tabla in (("vacantes_sin_winsorizar", sin_tope), ("vacantes_con_menciones", menciones)):
        t = t.merge(tabla.groupby(claves, as_index=False)["vacantes"].sum().rename(columns={"vacantes": nombre}), on=claves, how="outer")
    t = t.fillna({"vacantes_estimadas": 0.0, "vacantes_sin_winsorizar": 0.0, "vacantes_con_menciones": 0.0})
    confianza = perfil[perfil["dimension"] == "actividad_economica"].drop_duplicates("carrera_generica")[["carrera_generica", "nivel_confianza"]]
    t = t.merge(confianza, on="carrera_generica", how="left")
    casen = obtener.cargar_casen().dropna(subset=["o15"])
    privado = casen.groupby("carrera_generica").apply(lambda g: pd.Series({
        "n": len(g), "p": 100 * g.loc[g["o15"] == 5, "expr"].sum() / g["expr"].sum()}), include_groups=False)
    t["pct_asalariado_privado"] = t["carrera_generica"].map(privado["p"].where(privado["n"] >= N_PRIVADO))
    t["nombre_region"] = t["codigo_region"].map(REGIONES)
    t = t[list(VACANTES_CARRERA_REGION)].astype(VACANTES_CARRERA_REGION).sort_values(["codigo_region", "vacantes_estimadas"], ascending=[True, False])
    detalle = base.rename(columns={"vacantes": "vacantes_estimadas"})
    detalle["nombre_region"] = detalle["codigo_region"].map(REGIONES)
    detalle = detalle[list(VACANTES_CARRERA_REGION_ACTIVIDAD)].astype(VACANTES_CARRERA_REGION_ACTIVIDAD)
    v = validacion(e, cargos, pesos, celdas, pi, pi3, serie_st, base, perfil)

    DIR_SALIDA.mkdir(exist_ok=True)
    rutas = [(DIR_SALIDA / "vacantes_carrera_region.csv", t), (DIR_SALIDA / "vacantes_carrera_region_actividad.csv", detalle),
             (DIR_SALIDA / "vacantes_region_actividad.csv", celdas), (DIR_SALIDA / "vacantes_validacion.csv", v)]
    for ruta, tabla in rutas:
        tabla.to_csv(ruta, sep=";", index=False, encoding="utf-8")
        log.info("CSV generado: %s (%d filas)", ruta.name, len(tabla))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    for ruta, _ in rutas:
        inspeccion_rigurosa(ruta)
