"""
<src/Visualizacion/generar_mapa.py>

Genera el mapa interactivo: una sola página HTML, sin servidor ni dependencias externas.

Entradas: tablas de Analisis/JOINS y la capa regional de la cartografía del Censo 2024.
Salida:   docs/index.html, en la carpeta del resultado y no en src/: es lo que se publica
Ejecutar: .venv/bin/python src/Visualizacion/generar_mapa.py (requiere geopandas y pyarrow)

Este archivo arma los datos y la geometría y escribe la página. Lo demás está en módulos vecinos:
  config.py (rutas y constantes), formato.py (cómo se escriben cifras y nombres),
  indicadores.py (cálculos) y controles.py (controles que detienen la generación).

Decisiones:
  - Simplificación por cobertura: mantiene exactos los bordes compartidos; simplificar cada región por separado
    abriría huecos entre ellas. Exige bordes que calcen entre regiones, y la capa oficial no los trae: por eso se
    reconstruyen antes con una grilla de 0,01° (unos 1 km), un quinto de píxel a la escala del mapa.
  - Se omiten los territorios insulares lejanos (Rapa Nui, Juan Fernández): al incluirlos, el continente se vería
    diminuto. Sus datos siguen dentro de sus regiones.
  - Actividad U fuera de la lista: se conserva en la tabla, pero no aporta al mapa.
  - El color se decide con el CL redondeado a 2 decimales, la misma cifra que se muestra (06-11-26). Antes se
    usaba el valor completo y la cifra sumaba decimales para calzar (1,598), una precisión que el dato no tiene.
    El CL se calcula completo y se redondea una sola vez, al final.
  - Los cortes 0,8 y 1,2 son los de la lectura de la tabla. Vienen de otro módulo, así que controles.py detiene el
    proceso si el color y la lectura dejan de coincidir.
"""

from __future__ import annotations

import json
import logging
import math

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from config import (
    AFINIDADES_VISIBLES, ANCHO_SVG, AREA_MINIMA_PX, COLOR_RESUMEN, CORTES_ROJO, DECIMALES_CL, DESOCUPADO,
    FUERA_FUERZA_TRABAJO, GRILLA_GRADOS, HOMBRE, LATITUD_REFERENCIA, LONGITUD_MINIMA_CONTINENTE, MINIMO_VISIBLE,
    MUJER, NOMBRES_CORTOS, NOMBRES_REGION, OCUPADO, OCUPADOS_DIVERSIDAD_GENERO, OCUPADOS_GENERO_SUPRIMIDO,
    ORDEN_NIVELES, ORDEN_NORTE_SUR, POBLACION_POR_SEXO, POBLACION_TOTAL_CENSO, REGION_METROPOLITANA, RUTA_AREAS,
    RUTA_CARRERAS, RUTA_CENSO, RUTA_CENSO_PROCESADO, RUTA_CENSO_SEXO, RUTA_NIVELES, RUTA_PLANTILLA, RUTA_REGIONES,
    RUTA_SALIDA, TOLERANCIA_GRADOS, TRAMOS,
)
from formato import nombre_legible, redondear, texto_peso
from indicadores import clase_color
from controles import validar

log = logging.getLogger(__name__)


def a_svg(coordenadas: np.ndarray, x0: float, y1: float, escala: float, cos_lat: float) -> str:
    x = (coordenadas[:, 0] - x0) * cos_lat * escala
    y = (y1 - coordenadas[:, 1]) * escala
    return "M" + "L".join(f"{a:.1f},{b:.1f}" for a, b in zip(x, y)) + "Z"


def reconstruir_cobertura(regiones: np.ndarray) -> np.ndarray:
    """Hace que regiones vecinas compartan exactamente su borde; cada trozo queda en la región que lo contiene."""
    ajustadas = shapely.set_precision(shapely.make_valid(regiones), GRILLA_GRADOS)
    red = shapely.union_all(shapely.boundary(ajustadas))
    caras = shapely.get_parts(shapely.polygonize(list(shapely.get_parts(red))))
    indice_cara, indice_region = shapely.STRtree(ajustadas).query(shapely.point_on_surface(caras), predicate="within")
    # Los trozos que no caen en ninguna región son lagos o fiordos, y quedan fuera.
    region_de_cara: dict[int, int] = {}
    for cara, region in zip(indice_cara, indice_region):
        region_de_cara.setdefault(int(cara), int(region))
    por_region: list[list] = [[] for _ in regiones]
    for cara, region in region_de_cara.items():
        por_region[region].append(caras[cara])
    return np.array([shapely.union_all(p) for p in por_region])


def construir_geometria() -> dict:
    """Devuelve los trazados SVG de cada región, el tamaño del lienzo y los controles de la geometría."""
    g = gpd.read_parquet(RUTA_REGIONES).set_geometry("SHAPE")
    cobertura = reconstruir_cobertura(g.geometry.values)
    simplificadas = shapely.coverage_simplify(cobertura, TOLERANCIA_GRADOS)
    diferencia_area = float(np.abs(100 * (shapely.area(cobertura) / shapely.area(g.geometry.values) - 1)).max())
    geometria_valida = bool(shapely.coverage_is_valid(cobertura) and shapely.coverage_is_valid(simplificadas) and shapely.is_valid(simplificadas).all())
    cos_lat = math.cos(math.radians(LATITUD_REFERENCIA))
    partes = {}
    limites = []
    for region, geom in zip(g["COD_REGION"].astype(int), simplificadas):
        poligonos = [p for p in shapely.get_parts(geom) if p.geom_type == "Polygon" and p.centroid.x > LONGITUD_MINIMA_CONTINENTE]
        partes[region] = poligonos
        limites.extend(p.bounds for p in poligonos)
    b = np.array(limites)
    x0, y1 = b[:, 0].min(), b[:, 3].max()
    escala = ANCHO_SVG / ((b[:, 2].max() - x0) * cos_lat)
    alto = (y1 - b[:, 1].min()) * escala
    trazados = {}
    for region, poligonos in partes.items():
        area_minima = AREA_MINIMA_PX / (escala ** 2 * cos_lat)
        elegidos = [p for p in poligonos if p.area >= area_minima] or [max(poligonos, key=lambda p: p.area)]
        trazados[int(region)] = "".join(a_svg(np.asarray(p.exterior.coords), x0, y1, escala, cos_lat) for p in elegidos)
    return {"ancho": ANCHO_SVG, "alto": round(alto, 1), "trazados": trazados, "geometria_valida": geometria_valida, "diferencia_area_pct": diferencia_area}


def resumen_nacional(g: pd.DataFrame, total_censo: int, ene_total: float) -> dict:
    """Totales del país para una actividad; total_censo incluye a quienes no tienen región de trabajo."""
    con_personas, con_peso = g.loc[g["ocupados"].idxmax()], g.loc[g["peso_relativo"].idxmax()]
    return {"ocupados": int(g["ocupados"].sum()), "censo_total": total_censo, "ene_ocupados": int(round(g["ene_ocupados"].sum())),
            "ene_pct": redondear(100 * g["ene_ocupados"].sum() / ene_total, 1), "conc": int((g["lectura"] == "concentra").sum()),
            "mas_personas": {"r": int(con_personas["codigo_region"]), "n": int(con_personas["ocupados"]), "pct": redondear(100 * con_personas["ocupados"] / g["ocupados"].sum(), 1)},
            "mas_peso": {"r": int(con_peso["codigo_region"]), "txt": texto_peso(con_peso["peso_relativo"])}}


def sexo_por_actividad(por_sexo: pd.DataFrame) -> dict:
    """Ocupados por sexo en cada actividad, con la misma base que el mapa: lugar de trabajo y actividad informados."""
    base = por_sexo[(por_sexo["sit_fuerza_trabajo"] == OCUPADO) & por_sexo["codigo_region_trabajo"].notna() & por_sexo["actividad_ciiu"].notna()]
    tabla = base.pivot_table(index="actividad_ciiu", columns="sexo", values="personas", aggfunc="sum", fill_value=0)
    return {c: {"h": int(f[HOMBRE]), "m": int(f[MUJER]), "pct_h": redondear(100 * f[HOMBRE] / (f[HOMBRE] + f[MUJER]), 1), "pct_m": redondear(100 * f[MUJER] / (f[HOMBRE] + f[MUJER]), 1)} for c, f in tabla.iterrows()}


def agregar_sexo_por_region(actividades: list[dict], por_sexo: pd.DataFrame) -> dict:
    """Agrega ocupados por sexo a cada región y actividad, y devuelve las bases de la participación por sexo."""
    base = por_sexo[(por_sexo["sit_fuerza_trabajo"] == OCUPADO) & por_sexo["codigo_region_trabajo"].notna() & por_sexo["actividad_ciiu"].notna()]
    por_region = base.groupby(["codigo_region_trabajo", "sexo"])["personas"].sum()
    por_celda = base.groupby(["codigo_region_trabajo", "actividad_ciiu", "sexo"])["personas"].sum()
    por_chile = base.groupby("sexo")["personas"].sum()
    for a in actividades:
        a["sexo"]["part_h"], a["sexo"]["part_m"] = redondear(100 * a["sexo"]["h"] / por_chile[HOMBRE], 2), redondear(100 * a["sexo"]["m"] / por_chile[MUJER], 2)
        for r, d in a["regiones"].items():
            d["h"], d["m"] = int(por_celda.get((r, a["ciiu"], HOMBRE), 0)), int(por_celda.get((r, a["ciiu"], MUJER), 0))
            d["pct_h"], d["pct_m"] = redondear(100 * d["h"] / por_region[(r, HOMBRE)], 2), redondear(100 * d["m"] / por_region[(r, MUJER)], 2)
    return {"chile": {"h": int(por_chile[HOMBRE]), "m": int(por_chile[MUJER])},
            "regiones": {str(int(r)): {"h": int(por_region[(r, HOMBRE)]), "m": int(por_region[(r, MUJER)])} for r in por_region.index.levels[0]}}


def sexo_por_nivel(por_sexo: pd.DataFrame) -> tuple[dict, dict]:
    """Ocupados y desocupados por nivel y sexo. La tasa siempre usa residencia, igual que la tabla regional sin abrir."""
    c = por_sexo.dropna(subset=["nivel_titulo"])
    ocupados, desocupados = c[c["sit_fuerza_trabajo"] == OCUPADO], c[c["sit_fuerza_trabajo"] == DESOCUPADO]
    residencia = ocupados.groupby(["codigo_region", "nivel_titulo", "sexo"])["personas"].sum()
    trabajo = ocupados.dropna(subset=["codigo_region_trabajo"]).groupby(["codigo_region_trabajo", "nivel_titulo", "sexo"])["personas"].sum()
    desoc = desocupados.groupby(["codigo_region", "nivel_titulo", "sexo"])["personas"].sum()
    tasa = lambda d, o: redondear(100 * d / (d + o), 1)
    regiones: dict = {}
    for r in sorted(c["codigo_region"].unique()):
        regiones[str(int(r))] = {}
        for n in c["nivel_titulo"].unique():
            dh, dm = int(desoc.get((r, n, HOMBRE), 0)), int(desoc.get((r, n, MUJER), 0))
            regiones[str(int(r))][n] = {"oh": int(trabajo.get((r, n, HOMBRE), 0)), "om": int(trabajo.get((r, n, MUJER), 0)), "dh": dh, "dm": dm,
                                        "th": tasa(dh, residencia.get((r, n, HOMBRE), 0)), "tm": tasa(dm, residencia.get((r, n, MUJER), 0))}
    res_chile, des_chile = ocupados.groupby(["nivel_titulo", "sexo"])["personas"].sum(), desocupados.groupby(["nivel_titulo", "sexo"])["personas"].sum()
    chile = {n: {"oh": int(res_chile[(n, HOMBRE)]), "om": int(res_chile[(n, MUJER)]), "dh": int(des_chile[(n, HOMBRE)]), "dm": int(des_chile[(n, MUJER)]),
                 "th": tasa(des_chile[(n, HOMBRE)], res_chile[(n, HOMBRE)]), "tm": tasa(des_chile[(n, MUJER)], res_chile[(n, MUJER)])} for n in c["nivel_titulo"].unique()}
    return regiones, chile


def agregar_nivel_por_actividad(actividades: list[dict], por_sexo: pd.DataFrame) -> dict:
    """Perfil educativo de los ocupados de cada actividad, en Chile y por región. Los desocupados no tienen actividad registrada, así que aquí no hay tasas.

    Cada nivel va como [total, %, hombres, mujeres, % hombres, % mujeres], en el orden de ORDEN_NIVELES, porque son 960 celdas dentro de la página.
    Con menos de MINIMO_VISIBLE personas, el valor del sexo no se escribe en la página.
    """
    base = por_sexo[(por_sexo["sit_fuerza_trabajo"] == OCUPADO) & por_sexo["codigo_region_trabajo"].notna() & por_sexo["actividad_ciiu"].notna() & por_sexo["nivel_titulo"].notna()]
    base = base[base["actividad_ciiu"].isin([a["ciiu"] for a in actividades])]

    def perfil(g: pd.DataFrame) -> list:
        cuenta = g.groupby(["nivel_titulo", "sexo"])["personas"].sum()
        h = {n: int(cuenta.get((n, HOMBRE), 0)) for n in ORDEN_NIVELES}
        m = {n: int(cuenta.get((n, MUJER), 0)) for n in ORDEN_NIVELES}
        total_h, total_m = sum(h.values()), sum(m.values())
        filas = []
        for n in ORDEN_NIVELES:
            visible = lambda v, total: (v, redondear(100 * v / total, 1)) if v >= MINIMO_VISIBLE else (None, None)
            vh, ph = visible(h[n], total_h)
            vm, pm = visible(m[n], total_m)
            filas.append([h[n] + m[n], redondear(100 * (h[n] + m[n]) / (total_h + total_m), 1), vh, vm, ph, pm])
        return filas

    grupos = {c: g for c, g in base.groupby("actividad_ciiu")}
    for a in actividades:
        g = grupos[a["ciiu"]]
        a["niveles"] = perfil(g)
        for r, d in a["regiones"].items():
            d["niveles"] = perfil(g[g["codigo_region_trabajo"] == r])
    total = base.groupby("nivel_titulo")["personas"].sum()
    return {"orden": ORDEN_NIVELES, "todas": [redondear(100 * total[n] / total.sum(), 1) for n in ORDEN_NIVELES]}


def rango_ficha(f: pd.Series, columna: str, decimales: int) -> list | None:
    """[mínimo, máximo] entre instituciones; None si la carrera tiene 1 o 2 y no hay rango. Solo existe para empleabilidad."""
    lo, hi = f[f"{columna}_min"], f[f"{columna}_max"]
    return None if pd.isna(lo) else [redondear(lo, decimales), redondear(hi, decimales)]


def resumen_estudios(niveles: pd.DataFrame, sexo_chile: dict) -> dict:
    """Relación entre nivel de estudios y trabajo en Chile, según residencia y con nivel informado. Describe, no explica: la edad también influye."""
    suma = niveles.groupby("nivel_titulo")[["ocupados_residencia", "desocupados", "fuera_fuerza_trabajo"]].sum()
    total = suma["ocupados_residencia"].sum()
    con_titulo = ["Profesional", "Tecnico"]
    por_nivel = {n: {"ocupados": int(f["ocupados_residencia"]), "pct": redondear(100 * f["ocupados_residencia"] / total, 1),
                     "tasa_desocupacion": redondear(100 * f["desocupados"] / (f["ocupados_residencia"] + f["desocupados"]), 1),
                     "tasa_participacion": redondear(100 * (f["ocupados_residencia"] + f["desocupados"]) / f.sum(), 1)} for n, f in suma.iterrows()}
    # Situación educacional: población de 15 años o más con nivel y situación laboral informados, la misma base de "Estudios y trabajo".
    poblacion = niveles.assign(personas=niveles[["ocupados_residencia", "desocupados", "fuera_fuerza_trabajo"]].sum(axis=1))
    personas = poblacion.pivot_table(index="codigo_region", columns="nivel_titulo", values="personas", aggfunc="sum")[ORDEN_NIVELES]
    educacion = {str(r): [int(v) for v in f] for r, f in personas.iterrows()}
    educacion["chile"] = [int(v) for v in personas.sum()]
    # Desocupación con y sin título en cada región, para la relación entre ambas realidades.
    grupo = niveles.assign(con_titulo=niveles["nivel_titulo"].isin(con_titulo)).groupby(["codigo_region", "con_titulo"])[["ocupados_residencia", "desocupados"]].sum()
    tasa = (100 * grupo["desocupados"] / grupo.sum(axis=1)).unstack()
    desocupacion = {str(r): [redondear(f[True], 1), redondear(f[False], 1)] for r, f in tasa.iterrows()}
    sexo = {clave: redondear(100 * sum(sexo_chile[n][campo] for n in con_titulo) / sum(d[campo] for d in sexo_chile.values()), 1) for clave, campo in (("hombres", "oh"), ("mujeres", "om"))}
    return {"niveles": por_nivel, "total": int(total), "con_titulo": int(suma.loc[con_titulo, "ocupados_residencia"].sum()), "pct_con_titulo": redondear(100 * suma.loc[con_titulo, "ocupados_residencia"].sum() / total, 1),
            "sexo": sexo, "educacion": educacion, "desocupacion_titulo": desocupacion}


def situacion_poblacion(procesado: pd.DataFrame, por_sexo: pd.DataFrame) -> dict:
    """Situación laboral de las personas de 15 años o más; la región es donde viven, porque quien no trabaja no tiene región de trabajo."""
    def contar(g: pd.DataFrame) -> dict:
        total = int(g["personas"].sum())
        por_situacion = g.groupby("sit_fuerza_trabajo")["personas"].sum()
        trabajan, buscan, no_buscan = (int(por_situacion.get(c, 0)) for c in (OCUPADO, DESOCUPADO, FUERA_FUERZA_TRABAJO))
        return {"total": total, "trabajan": trabajan, "buscan": buscan, "no_buscan": no_buscan, "sin_dato": total - trabajan - buscan - no_buscan,
                "pct_trabajan": redondear(100 * trabajan / total, 1), "pct_buscan": redondear(100 * buscan / total, 1), "pct_no_buscan": redondear(100 * no_buscan / total, 1),
                "pct_sin_dato": redondear(100 * (total - trabajan - buscan - no_buscan) / total, 1),
                "tasa_desocupacion": redondear(100 * buscan / (trabajan + buscan), 1), "tasa_participacion": redondear(100 * (trabajan + buscan) / total, 1)}
    chile = contar(procesado)
    # Se suma aparte porque esta tabla agrupa por residencia, y quien trabaja en otra región cuenta donde trabaja.
    ocupados_con_lugar = procesado[(procesado["sit_fuerza_trabajo"] == OCUPADO) & procesado["codigo_region_trabajo"].notna()]
    por_lugar = ocupados_con_lugar.groupby("codigo_region_trabajo")["personas"].sum()
    chile["lugar_trabajo"] = int(por_lugar.sum())
    regiones = {str(int(r)): contar(g) | {"lugar_trabajo": int(por_lugar.get(r, 0)), "pct_lugar_trabajo": redondear(100 * por_lugar.get(r, 0) / por_lugar.sum(), 1)} for r, g in procesado.groupby("codigo_region")}
    for r, d in regiones.items():
        d["sexo"] = {nombre: contar(por_sexo[(por_sexo["codigo_region"] == int(r)) & (por_sexo["sexo"] == codigo)]) for nombre, codigo in (("hombres", HOMBRE), ("mujeres", MUJER))}
    sexo = {}
    for nombre, codigo in (("hombres", HOMBRE), ("mujeres", MUJER)):
        grupo = contar(por_sexo[por_sexo["sexo"] == codigo])
        sexo[nombre] = grupo | {"poblacion_total": POBLACION_POR_SEXO[codigo], "menores_15": POBLACION_POR_SEXO[codigo] - grupo["total"]}
    return {"poblacion_total": POBLACION_TOTAL_CENSO, "menores_15": POBLACION_TOTAL_CENSO - chile["total"], "chile": chile, "regiones": regiones, "sexo": sexo,
            "genero_ocupados": {"diversidades": OCUPADOS_DIVERSIDAD_GENERO, "suprimido": OCUPADOS_GENERO_SUPRIMIDO}}


def resumen_general(censo: pd.DataFrame, actividades: list[dict]) -> dict:
    """Panorama de todas las actividades. Una región se distingue por lo que más pesa ahí, sin contar bases pequeñas."""
    pct_por_actividad = censo.drop_duplicates("actividad_ciiu")["pct_nacional"]
    # El orden de mayor a menor se decide con el peso sin redondear, igual que el color.
    peso_maximo = censo[censo["lectura"] != "base_pequena"].groupby("actividad_ciiu")["peso_relativo"].max().sort_values(ascending=False)
    con_lectura = censo[censo["lectura"] != "base_pequena"]
    regiones = {}
    for r, g in con_lectura.groupby("codigo_region"):
        distintiva = g.loc[g["peso_relativo"].idxmax()]
        regiones[str(int(r))] = {"ciiu": distintiva["actividad_ciiu"], "peso": redondear(distintiva["peso_relativo"], 6), "txt": texto_peso(distintiva["peso_relativo"]),
                                 "suave": bool(round(distintiva["peso_relativo"], DECIMALES_CL) < CORTES_ROJO[1])}
    mas_empleo = censo.loc[censo.groupby("codigo_region")["ocupados"].idxmax()].set_index("codigo_region")["actividad_ciiu"]
    for r, ciiu in mas_empleo.items():
        regiones[str(int(r))]["mas_personas"] = ciiu
    mayor_empleador = mas_empleo.value_counts()
    por_actividad = {a["ciiu"]: a for a in actividades}
    no_metropolitanas = [a for a in actividades if a["nacional"]["mas_personas"]["r"] != REGION_METROPOLITANA]
    return {"total": sum(a["nacional"]["ocupados"] for a in actividades), "pct_5_mayores": redondear(pct_por_actividad.nlargest(5).sum(), 1),
            "n_metropolitana": len(actividades) - len(no_metropolitanas), "excepciones": [{"ciiu": a["ciiu"], "r": a["nacional"]["mas_personas"]["r"]} for a in no_metropolitanas],
            "mas_desiguales": [{"ciiu": c, "r": por_actividad[c]["nacional"]["mas_peso"]["r"], "txt": por_actividad[c]["nacional"]["mas_peso"]["txt"]} for c in peso_maximo.index[:2]],
            "repartidas": [a["ciiu"] for a in actividades if a["nacional"]["conc"] == 0], "corte_suave": texto_peso(CORTES_ROJO[1]).replace(",60", ",6"),
            "mayor_empleador": {"ciiu": mayor_empleador.index[0], "n": int(mayor_empleador.iloc[0])}, "colores": COLOR_RESUMEN, "regiones": regiones}


def construir_datos() -> dict:
    censo = pd.read_csv(RUTA_CENSO, sep=";")
    ene_total = float(censo["ene_ocupados"].sum())
    # Base de la participación: se toma antes del filtro porque incluye a la actividad que no se lista.
    base_ocupados = {"chile": int(censo["ocupados"].sum()), "regiones": {str(int(r)): int(v) for r, v in censo.groupby("codigo_region")["ocupados"].sum().items()}}
    censo = censo[censo["mostrar_en_mapa"]]
    procesado = pd.read_csv(RUTA_CENSO_PROCESADO, sep=";")
    totales_censo = procesado[procesado["sit_fuerza_trabajo"] == OCUPADO].groupby("actividad_ciiu")["personas"].sum()
    por_sexo = pd.read_csv(RUTA_CENSO_SEXO, sep=";")
    sexo_actividad = sexo_por_actividad(por_sexo)
    areas = pd.read_csv(RUTA_AREAS, sep=";")
    carreras = pd.read_csv(RUTA_CARRERAS, sep=";")
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
    niveles = pd.read_csv(RUTA_NIVELES, sep=";")
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    datos, geo = construir_datos(), construir_geometria()
    html = RUTA_PLANTILLA.read_text(encoding="utf-8").replace("__DATOS__", json.dumps(datos, ensure_ascii=False)).replace("__GEO__", json.dumps({k: geo[k] for k in ("ancho", "alto", "trazados")}))
    validar(datos, geo, html)
    RUTA_SALIDA.parent.mkdir(exist_ok=True)
    RUTA_SALIDA.write_text(html, encoding="utf-8")
    log.info("HTML generado: %s (%.0f KB, %d carreras)", RUTA_SALIDA, RUTA_SALIDA.stat().st_size / 1024, len(datos["fichas"]))
