"""
<src/Visualizacion/datos.py>

Arma el JSON que lee la página (DATOS en plantilla.html) a partir de las tablas y los cálculos de indicadores.py.

Decisiones:
  - Actividad U fuera de la lista: se conserva en la tabla, pero no aporta al mapa.
"""

from __future__ import annotations

import pandas as pd

from config import AFINIDADES_VISIBLES, NOMBRES_CORTOS, NOMBRES_REGION, OCUPADO, ORDEN_NORTE_SUR, TRAMOS
from formato import nombre_legible, redondear, texto_peso
from indicadores import (
    agregar_nivel_por_actividad, agregar_sexo_por_region, clase_color, rango_ficha, resumen_estudios,
    resumen_general, resumen_nacional, sexo_por_actividad, sexo_por_nivel, situacion_poblacion,
)


def construir_datos(tablas: dict[str, pd.DataFrame]) -> dict:
    """Arma el JSON que lee la página. Las tablas vienen de carga.cargar_tablas()."""
    censo = tablas["censo"]
    ene_total = float(censo["ene_ocupados"].sum())
    # Base de la participación: se toma antes del filtro porque incluye a la actividad que no se lista.
    base_ocupados = {"chile": int(censo["ocupados"].sum()), "regiones": {str(int(r)): int(v) for r, v in censo.groupby("codigo_region")["ocupados"].sum().items()}}
    censo = censo[censo["mostrar_en_mapa"]]
    procesado = tablas["procesado"]
    totales_censo = procesado[procesado["sit_fuerza_trabajo"] == OCUPADO].groupby("actividad_ciiu")["personas"].sum()
    por_sexo = tablas["por_sexo"]
    sexo_actividad = sexo_por_actividad(por_sexo)
    areas = tablas["areas"]
    carreras = tablas["carreras"]
    actividades = []
    for (ciiu, glosa), g in censo.groupby(["actividad_ciiu", "actividad_glosa"]):
        primero = g.iloc[0]
        a = areas[(areas["actividad_ciiu"] == ciiu) & (areas["fiabilidad"] != "no_fiable")].nlargest(4, "pct_en_actividad")
        vinculadas = carreras[(carreras["actividad_ciiu"] == ciiu) & carreras["afinidad"].isin(AFINIDADES_VISIBLES)].sort_values("pct_en_carrera", ascending=False)
        actividades.append({
            "ciiu": ciiu, "glosa": glosa, "corto": NOMBRES_CORTOS[ciiu], "pct_nacional": redondear(primero["pct_nacional"], 2), "pct_sin_region": redondear(primero["pct_sin_region_trabajo"], 1),
            "alerta_fuente": bool(primero["alerta_difiere_fuente"]), "nacional": resumen_nacional(g, int(totales_censo[ciiu]), ene_total), "sexo": sexo_actividad[ciiu],
            "regiones": {int(f["codigo_region"]): {"ocupados": int(f["ocupados"]), "pct": redondear(f["pct_en_region"], 2), "peso": redondear(f["peso_relativo"], 6), "clase": clase_color(f["peso_relativo"]), "peso_txt": texto_peso(f["peso_relativo"]), "lectura": f["lectura"],
                                                 "ene_peso_txt": texto_peso(f["ene_peso_relativo"]), "ene_lectura": f["ene_lectura"]} for _, f in g.iterrows()},
            "areas": [{"area": f["area_cine"], "pct": redondear(f["pct_en_actividad"], 1), "min": redondear(f["pct_en_actividad_min"], 1), "max": redondear(f["pct_en_actividad_max"], 1)} for _, f in a.iterrows()],
            "afines": [{"c": f["carrera_generica"], "pct": redondear(f["pct_en_carrera"], 1), "min": redondear(f["pct_en_carrera_min"], 1), "max": redondear(f["pct_en_carrera_max"], 1),
                        "tit": int(round(f["ocupados_titulados"])), "fiab": f["fiabilidad"]} for _, f in vinculadas[vinculadas["afinidad"] == "afin"].iterrows()],
            "indicios": [{"c": f["carrera_generica"], "n": int(f["n_celda"])} for _, f in vinculadas[vinculadas["afinidad"] == "indicio_sin_muestra"].iterrows()],
        })
    base_ocupados["sexo"] = agregar_sexo_por_region(actividades, por_sexo)
    perfil_estudios = agregar_nivel_por_actividad(actividades, por_sexo)
    usadas = carreras[carreras["afinidad"].isin(AFINIDADES_VISIBLES)]
    fichas = {}
    for c, f in usadas.drop_duplicates("carrera_generica").set_index("carrera_generica").iterrows():
        v = usadas[(usadas["carrera_generica"] == c) & (usadas["afinidad"] == "afin")].sort_values("pct_en_carrera", ascending=False)
        fichas[c] = {"nombre": nombre_legible(c), "nivel": f["nivel_titulo"], "area": f["area_cine"], "tit": int(f["titulados_2025"]), "tit_h": int(f["titulados_2025_hombres"]), "tit_m": int(f["titulados_2025_mujeres"]),
                     "pct_tit_h": redondear(100 * f["titulados_2025_hombres"] / f["titulados_2025"], 1) if f["titulados_2025"] else None, "pct_tit_m": redondear(100 * f["titulados_2025_mujeres"] / f["titulados_2025"], 1) if f["titulados_2025"] else None, "emp": redondear(f["empleabilidad_1er_anio"], 1),
                     "ing1": redondear(f["ingreso_medio_1er_anio"], 0), "ing5": redondear(f["ingreso_medio_5to_anio"], 0), "inst": int(f["n_instituciones"]),
                     "tit_hist": int(f["titulados_2007_2025"]), "emp_r": rango_ficha(f, "empleabilidad_1er_anio", 1),
                     "alerta_inst": bool(f["alerta_pocas_instituciones"]), "pct_principal": redondear(f["pct_institucion_principal"], 0),
                     "actividades": v[["actividad_ciiu", "actividad_glosa", "pct_en_carrera"]].round(1).values.tolist()}
    niveles = tablas["niveles"]
    por_region = {str(r): {f["nivel_titulo"]: {"trabajo": int(f["ocupados_trabajo"]), "desocupados": int(f["desocupados"]), "tasa": redondear(f["tasa_desocupacion"], 1),
                                               "nacional": redondear(f["tasa_nacional_nivel"], 1), "ene": redondear(f["ene_tasa_desocupacion"], 1) if f["ene_fiabilidad"] != "no_fiable" else None,
                                               "ene_poco": f["ene_fiabilidad"] == "poco_fiable"} for _, f in g.iterrows()} for r, g in niveles.groupby("codigo_region")}
    suma = niveles.groupby("nivel_titulo")[["ocupados_residencia", "desocupados"]].sum()
    primera = niveles.drop_duplicates("nivel_titulo").set_index("nivel_titulo")
    niveles_chile = {n: {"ocupados": int(suma.loc[n, "ocupados_residencia"]), "desocupados": int(suma.loc[n, "desocupados"]), "tasa": redondear(primera.loc[n, "tasa_nacional_nivel"], 1),
                         "ene": redondear(primera.loc[n, "ene_tasa_nacional_nivel"], 1)} for n in suma.index}
    nivel_sexo_region, nivel_sexo_chile = sexo_por_nivel(por_sexo)
    for r, g in por_region.items():
        for n, d in g.items():
            d["sexo"] = nivel_sexo_region[r][n]
    for n, d in niveles_chile.items():
        d["sexo"] = nivel_sexo_chile[n]
    estudios = resumen_estudios(niveles, nivel_sexo_chile)
    # La tabla educacional exige nivel y situación laboral: la página informa por separado a quienes les falta cada uno.
    sin_nivel = procesado["nivel_titulo"].isna()
    estudios["excluidos"] = {"sin_nivel": int(procesado.loc[sin_nivel, "personas"].sum()),
                             "sin_situacion": int(procesado.loc[~sin_nivel & procesado["sit_fuerza_trabajo"].isna(), "personas"].sum())}
    return {"actividades": actividades, "fichas": fichas, "estudios": estudios, "perfil_estudios": perfil_estudios,
            # Solo el total de las carreras del mapa: por carrera son 1 o 2 personas, y no se abre.
            "titulos_nb": sum(f["tit"] - f["tit_h"] - f["tit_m"] for f in fichas.values()), "niveles": por_region, "niveles_chile": niveles_chile, "regiones": {str(k): v for k, v in NOMBRES_REGION.items()}, "orden": ORDEN_NORTE_SUR, "tramos": TRAMOS, "resumen": resumen_general(censo, actividades), "poblacion": situacion_poblacion(procesado, por_sexo), "base_ocupados": base_ocupados}
