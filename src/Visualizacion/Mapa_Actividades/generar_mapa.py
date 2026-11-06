"""
<src/Visualizacion/Mapa_Actividades/generar_mapa.py>

Genera el mapa interactivo: una sola página HTML, sin servidor ni dependencias externas.

Entradas: tablas de Analisis/JOINS y la capa regional de la cartografía del Censo 2024.
Salida:   Salida/index.html
Ejecutar: .venv/bin/python src/Visualizacion/Mapa_Actividades/generar_mapa.py (requiere geopandas y pyarrow)

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
  - Los cortes 0,8 y 1,2 son los de la lectura de la tabla. Vienen de otro módulo, así que validar() detiene el
    proceso si el color y la lectura dejan de coincidir.
"""

from __future__ import annotations

import json
import logging
import math
import re
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import shapely

log = logging.getLogger(__name__)

DIR = Path(__file__).parent
DIR_SRC = DIR.parents[1]
DIR_JOINS = DIR_SRC / "Analisis" / "JOINS"
RUTA_CENSO = DIR_JOINS / "Concentracion_Region_Actividad_Censo" / "Salida" / "concentracion_region_actividad_censo.csv"
RUTA_AREAS = DIR_JOINS / "Areas_Por_Actividad" / "Salida" / "areas_por_actividad.csv"
RUTA_CARRERAS = DIR_JOINS / "Carreras_Por_Actividad" / "Salida" / "carreras_por_actividad.csv"
RUTA_NIVELES = DIR_JOINS / "Fuerza_Trabajo_Region_Nivel" / "Salida" / "fuerza_trabajo_region_nivel.csv"
RUTA_CENSO_PROCESADO = DIR_SRC / "Scrapers" / "CENSO" / "Salida" / "censo_procesado.csv"
RUTA_CENSO_SEXO = DIR_SRC / "Scrapers" / "CENSO" / "Salida" / "censo_por_sexo.csv"
RUTA_PERSONAS = DIR_SRC / "Scrapers" / "CENSO" / "Entrada" / "personas_censo2024.parquet"
RUTA_REGIONES = DIR_SRC / "Scrapers" / "CENSO" / "Entrada" / "cartografia" / "Cartografia_censo2024_Pais_Regional.parquet"
RUTA_PLANTILLA = DIR / "plantilla.html"
RUTA_SALIDA = DIR / "Salida" / "index.html"

ANCHO_SVG = 250
LATITUD_REFERENCIA = -36.0  # Mantiene una proporción razonable en un país tan largo.
LONGITUD_MINIMA_CONTINENTE = -76.0
TOLERANCIA_GRADOS = 0.035
GRILLA_GRADOS = 0.01
DIFERENCIA_AREA_MAXIMA_PCT = 0.5
AREA_MINIMA_PX = 3.0
OCUPADO = 1
AFINIDADES_VISIBLES = ["afin", "indicio_sin_muestra"]
CORTES_AZUL = [0.4, 0.6, 0.8]    # Inclusivos: 0,8 ya es bajo lo nacional.
CORTES_ROJO = [1.2, 1.6, 2.5]    # Inclusivos: 1,2 ya concentra.
TRAMOS = ["hasta 0,4", "0,4–0,6", "0,6–0,8", "0,8–1,2", "1,2–1,6", "1,6–2,5", "2,5 o más"]
CLASE_NEUTRA = 3
DECIMALES_CL = 2
NOMBRES_REGION = {
    1: "Tarapacá", 2: "Antofagasta", 3: "Atacama", 4: "Coquimbo", 5: "Valparaíso", 6: "O'Higgins", 7: "Maule", 8: "Biobío",
    9: "La Araucanía", 10: "Los Lagos", 11: "Aysén", 12: "Magallanes", 13: "Metropolitana", 14: "Los Ríos", 15: "Arica y Parinacota", 16: "Ñuble",
}
NOMBRES_CORTOS = {
    "A": "Agricultura y pesca", "B": "Minería", "C": "Industria manufacturera", "D": "Electricidad y gas", "E": "Agua y residuos", "F": "Construcción", "G": "Comercio",
    "H": "Transporte", "I": "Alojamiento y comida", "J": "Información y comunicaciones", "K": "Finanzas y seguros", "L": "Inmobiliarias", "M": "Servicios profesionales",
    "N": "Servicios administrativos", "O": "Administración pública", "P": "Enseñanza", "Q": "Salud", "R": "Artes y deportes", "S": "Otros servicios", "T": "Hogares como empleadores",
}
# Índice de color de cada actividad que distingue a alguna región. Sigue a la actividad, no a su orden, y se eligió con
# validate_palette.js para que las actividades de regiones vecinas se distingan, también con daltonismo (ΔE 8,4 o más).
COLOR_RESUMEN = {"B": 0, "A": 1, "O": 2, "C": 3, "R": 4, "K": 5}
REGION_METROPOLITANA = 13
# Filas de personas_censo2024.parquet. Va como constante porque censo_procesado.csv solo trae 15 años o más, y regenerar
# el mapa no debe exigir los microdatos; validar() la compara con el archivo cuando está disponible.
POBLACION_TOTAL_CENSO = 18_480_432
HOMBRE, MUJER = 1, 2
ORDEN_NIVELES = ["Profesional", "Tecnico", "Sin_titulo"]
MINIMO_VISIBLE = 10
POBLACION_POR_SEXO = {HOMBRE: 8_967_033, MUJER: 9_513_399}
# Solo dos totales nacionales para la nota: el género es dato sensible y está suprimido en parte de las comunas, así que no
# se guarda en ninguna tabla ni se abre por actividad. validar() los compara con los microdatos cuando están disponibles.
OCUPADOS_DIVERSIDAD_GENERO, OCUPADOS_GENERO_SUPRIMIDO = 38_491, 633_803
DESOCUPADO, FUERA_FUERZA_TRABAJO = 2, 3
ORDEN_NORTE_SUR = [15, 1, 2, 3, 4, 5, 13, 6, 7, 16, 8, 9, 14, 10, 11, 12]
TILDES = {
    "Ingenieria": "Ingeniería", "Tecnico": "Técnico", "Tecnica": "Técnica", "Pedagogia": "Pedagogía", "Educacion": "Educación", "Administracion": "Administración",
    "Computacion": "Computación", "Informatica": "Informática", "Mecanica": "Mecánica", "Quimica": "Química", "Electronica": "Electrónica",
    "Electrica": "Eléctrica", "Electrico": "Eléctrico", "Agricola": "Agrícola", "Biotecnologia": "Biotecnología", "Geologia": "Geología", "Metalurgia": "Metalurgia",
    "Metalurgica": "Metalúrgica", "Logistica": "Logística", "Psicologia": "Psicología", "Odontologia": "Odontología", "Tecnologia": "Tecnología", "Medica": "Médica",
    "Dietetica": "Dietética", "Nutricion": "Nutrición", "Kinesiologia": "Kinesiología", "Fonoaudiologia": "Fonoaudiología", "Podologia": "Podología", "Clinico": "Clínico",
    "Radiologia": "Radiología", "Enfermeria": "Enfermería", "Automatizacion": "Automatización", "Instrumentacion": "Instrumentación", "Construccion": "Construcción",
    "Prevencion": "Prevención", "Gastronomia": "Gastronomía", "Gastronomica": "Gastronómica", "Turistica": "Turística", "Hoteleria": "Hotelería", "Produccion": "Producción",
    "Comunicacion": "Comunicación", "Diseno": "Diseño", "Grafico": "Gráfico", "Juridico": "Jurídico", "Publica": "Pública", "Fisica": "Física", "Matematicas": "Matemáticas",
    "Biologia": "Biología", "Sociologia": "Sociología", "Musica": "Música", "Geomineria": "Geominería", "Mineria": "Minería", "Topografia": "Topografía", "Telematica": "Telemática",
    "Biomedica": "Biomédica", "Tecnicas": "Técnicas", "Analisis": "Análisis", "Parvulos": "Párvulos", "Peluqueria": "Peluquería", "Estetica": "Estética", "Linguistica": "Lingüística",
    "Economia": "Economía", "Geografia": "Geografía", "Traduccion": "Traducción", "Interpretacion": "Interpretación", "Telecomunicaciones": "Telecomunicaciones",
    "Agronomia": "Agronomía", "Comun": "Común", "Electromecanica": "Electromecánica", "Recreacion": "Recreación", "Preparacion": "Preparación", "Y/O": "y/o",
    "Transito": "Tránsito", "Maritima": "Marítima", "Pesquera": "Pesquera", "Acuicola": "Acuícola", "Forestal": "Forestal", "Veterinaria": "Veterinaria", "Sanitaria": "Sanitaria",
}
MINUSCULAS = {"En", "De", "Del", "La", "Las", "Los", "Y", "E", "O", "A", "Con", "Para", "Al"}


def nombre_legible(texto: str) -> str:
    """Las carreras genéricas vienen en mayúsculas y sin tildes; esto solo afecta a lo que se muestra."""
    palabras = re.sub(r"\s+", " ", texto.title()).split(" ")
    salida = []
    for i, p in enumerate(palabras):
        limpia = p.strip(",()")
        nueva = TILDES.get(limpia, limpia)
        if i > 0 and nueva in MINUSCULAS:
            nueva = nueva.lower()
        salida.append(p.replace(limpia, nueva))
    return " ".join(salida)


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


def clase_color(peso: float) -> int | None:
    """Tramo de color del CL publicado, con 2 decimales; usa las mismas comparaciones que la lectura. Vacío si no hay dato."""
    if pd.isna(peso):
        return None
    peso = round(float(peso), DECIMALES_CL)
    if peso <= CORTES_AZUL[2]:
        return sum(peso > c for c in CORTES_AZUL[:2])
    if peso < CORTES_ROJO[0]:
        return CLASE_NEUTRA
    return CLASE_NEUTRA + 1 + sum(peso >= c for c in CORTES_ROJO[1:])


def texto_peso(peso: float) -> str:
    """CL con 2 decimales: la misma cifra con la que se decide el color."""
    if pd.isna(peso):
        return "s/d"
    return f"{round(float(peso), DECIMALES_CL):.{DECIMALES_CL}f}".replace(".", ",")


def redondear(valor: float, decimales: int = 2) -> float | None:
    return None if pd.isna(valor) else round(float(valor), decimales)


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
    # Situación educacional: toda la población de 15 años o más con nivel informado, la misma base de la situación laboral por región.
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
    return {"actividades": actividades, "fichas": fichas, "estudios": resumen_estudios(niveles, nivel_sexo_chile), "perfil_estudios": perfil_estudios,
            # Solo el total de las carreras del mapa: por carrera son 1 o 2 personas, y no se abre.
            "titulos_nb": sum(f["tit"] - f["tit_h"] - f["tit_m"] for f in fichas.values()), "niveles": por_region, "niveles_chile": niveles_chile, "regiones": {str(k): v for k, v in NOMBRES_REGION.items()}, "orden": ORDEN_NORTE_SUR, "tramos": TRAMOS, "resumen": resumen_general(censo, actividades), "poblacion": situacion_poblacion(procesado, por_sexo), "base_ocupados": base_ocupados}


def totales_sexo_genero_correctos() -> bool:
    """Compara las constantes con los microdatos; regenerar el mapa no los exige, así que sin ellos no hay nada que comparar."""
    if not RUTA_PERSONAS.exists():
        return True
    d = pd.read_parquet(RUTA_PERSONAS, columns=["sexo", "div_genero", "sit_fuerza_trabajo"])
    genero = d.loc[d["sit_fuerza_trabajo"] == OCUPADO, "div_genero"].value_counts()
    return d["sexo"].value_counts().to_dict() == POBLACION_POR_SEXO and genero[1] == OCUPADOS_DIVERSIDAD_GENERO and genero[-66] == OCUPADOS_GENERO_SUPRIMIDO


def validar(datos: dict, geo: dict, html: str) -> None:
    celdas = [d for a in datos["actividades"] for d in a["regiones"].values() if d["clase"] is not None]
    lectura_esperada = lambda c: "bajo_lo_nacional" if c < CLASE_NEUTRA else "similar" if c == CLASE_NEUTRA else "concentra"
    con_base = [d for d in celdas if d["lectura"] != "base_pequena"]
    texto_calza = lambda d: clase_color(float(d["peso_txt"].replace(",", "."))) == d["clase"]
    sin_dato = sum(d["clase"] is None for a in datos["actividades"] for d in a["regiones"].values())
    pob = datos["poblacion"]
    controles = {
        "El color coincide con la lectura en todas las celdas": all(lectura_esperada(d["clase"]) == d["lectura"] for d in con_base),
        "La cifra visible cae en el tramo de su color": all(texto_calza(d) for d in celdas),
        "20 actividades en la lista": len(datos["actividades"]) == 20 and "U" not in [a["ciiu"] for a in datos["actividades"]],
        "Bordes válidos antes y después de simplificar": geo["geometria_valida"],
        "El área de cada región cambia menos de 0,5%": geo["diferencia_area_pct"] < DIFERENCIA_AREA_MAXIMA_PCT,
        "Minería en Chile: 268.491 con región y 275.517 en total": next(a for a in datos["actividades"] if a["ciiu"] == "B")["nacional"]["ocupados"] == 268_491 and next(a for a in datos["actividades"] if a["ciiu"] == "B")["nacional"]["censo_total"] == 275_517,
        "Salud: más personas en la Metropolitana y más peso en Biobío": next(a for a in datos["actividades"] if a["ciiu"] == "Q")["nacional"]["mas_personas"]["r"] == 13 and next(a for a in datos["actividades"] if a["ciiu"] == "Q")["nacional"]["mas_peso"]["r"] == 8,
        "Profesionales desocupados en Chile: 153.695": datos["niveles_chile"]["Profesional"]["desocupados"] == 153_695,
        "Las 16 regiones tienen sus 3 niveles": len(datos["niveles"]) == 16 and all(len(n) == 3 for n in datos["niveles"].values()),
        "16 regiones con trazado": sorted(geo["trazados"]) == sorted(NOMBRES_REGION),
        "Cada actividad tiene las 16 regiones": all(len(a["regiones"]) == 16 for a in datos["actividades"]),
        "Antofagasta en Minería: 101.929": next(a for a in datos["actividades"] if a["ciiu"] == "B")["regiones"][2]["ocupados"] == 101_929,
        "Todas las carreras listadas tienen ficha": all(x["c"] in datos["fichas"] for a in datos["actividades"] for x in a["afines"] + a["indicios"]),
        # La página agrupa las carreras por nivel: una carrera con otro nivel quedaría fuera de todos los grupos.
        "Ficha: Psicología con 85.260 títulos 2007-2025 y empleabilidad de 43,7% a 89,7%": (datos["fichas"]["PSICOLOGIA"]["tit_hist"], datos["fichas"]["PSICOLOGIA"]["emp_r"]) == (85_260, [43.7, 89.7]),
        "Ficha: sin rango cuando hay aviso de pocas instituciones": all(f["emp_r"] is None for f in datos["fichas"].values() if f["alerta_inst"]),
        "Toda carrera listada es técnica o profesional": all(datos["fichas"][x["c"]]["nivel"] in ("Profesional", "Tecnico") for a in datos["actividades"] for x in a["afines"] + a["indicios"]),
        "Resumen: las 16 regiones tienen actividad distintiva y color": len(datos["resumen"]["regiones"]) == 16 and all(d["ciiu"] in COLOR_RESUMEN for d in datos["resumen"]["regiones"].values()),
        "Resumen: cada color se usa": {d["ciiu"] for d in datos["resumen"]["regiones"].values()} == set(COLOR_RESUMEN),
        "Resumen: Metropolitana en 18 de 20; excepciones en Maule y Antofagasta": datos["resumen"]["n_metropolitana"] == 18 and sorted(e["r"] for e in datos["resumen"]["excepciones"]) == [2, 7],
        "Resumen: Comercio emplea más en 12 de 16 regiones": datos["resumen"]["mayor_empleador"] == {"ciiu": "G", "n": 12},
        "Resumen: Minería y Agricultura son las más desiguales": [d["ciiu"] for d in datos["resumen"]["mas_desiguales"]] == ["B", "A"],
        "Resumen: Valparaíso y Biobío van en color suave; La Araucanía (1,60) ya no": sorted(r for r, d in datos["resumen"]["regiones"].items() if d["suave"]) == ["5", "8"],
        "CL: todas las cifras con 2 decimales": all(len(d["peso_txt"].split(",")[1]) == 2 for d in celdas),
        "Población: 15,2 millones de 15 años o más, y suman sus cuatro grupos": pob["chile"]["total"] == 15_205_784 and pob["chile"]["trabajan"] + pob["chile"]["buscan"] + pob["chile"]["no_buscan"] + pob["chile"]["sin_dato"] == pob["chile"]["total"],
        "Población: las regiones suman el total de Chile": sum(d["total"] for d in pob["regiones"].values()) == pob["chile"]["total"] and len(pob["regiones"]) == 16,
        "Población: el % que trabaja va de Ñuble a Aysén": min(pob["regiones"], key=lambda r: pob["regiones"][r]["pct_trabajan"]) == "16" and max(pob["regiones"], key=lambda r: pob["regiones"][r]["pct_trabajan"]) == "11",
        # Los indicadores, el título del mapa y sus anotaciones llevan estas afirmaciones escritas a mano: si los datos cambian, la generación se detiene.
        "Indicadores: la Metropolitana reúne 42,1% de los ocupados": pob["regiones"]["13"]["pct_lugar_trabajo"] == 42.1 and pob["regiones"]["13"]["lugar_trabajo"] == 3_286_880,
        "Mapa: 13 de 16 regiones tienen su mayor CL en Minería, Agricultura o Adm. pública": sum(d["ciiu"] in "BAO" for d in datos["resumen"]["regiones"].values()) == 13 and len(datos["resumen"]["regiones"]) == 16,
        "Indicadores: brecha de participación de 19,5 puntos": round(pob["sexo"]["hombres"]["tasa_participacion"] - pob["sexo"]["mujeres"]["tasa_participacion"], 1) == 19.5,
        "Anotaciones: Minería en el norte, Agricultura en el centro-sur y Adm. pública en los extremos": {c: sorted(int(r) for r, d in datos["resumen"]["regiones"].items() if d["ciiu"] == c) for c in "BAO"} == {"B": [1, 2, 3, 4], "A": [6, 7, 9, 10, 14, 16], "O": [11, 12, 15]},
        "Anotaciones: Antofagasta, Maule y Aysén son el mayor CL de sus grupos": all(max((d["peso"], int(r)) for r, d in datos["resumen"]["regiones"].items() if d["ciiu"] == c)[1] == m for c, m in (("B", 2), ("A", 7), ("O", 11))),
        "Sexo: hombres y mujeres suman cada grupo de la población de Chile": all(pob["sexo"]["hombres"][k] + pob["sexo"]["mujeres"][k] == v for k, v in (("poblacion_total", pob["poblacion_total"]), ("menores_15", pob["menores_15"]), ("total", pob["chile"]["total"]), ("trabajan", pob["chile"]["trabajan"]), ("buscan", pob["chile"]["buscan"]), ("no_buscan", pob["chile"]["no_buscan"]), ("sin_dato", pob["chile"]["sin_dato"]))),
        "Sexo: en cada actividad, hombres y mujeres suman sus ocupados": all(a["sexo"]["h"] + a["sexo"]["m"] == a["nacional"]["ocupados"] for a in datos["actividades"]),
        "Sexo: Comercio 665.041 y 646.953; Construcción 496.948 y 46.279": (lambda c, f: (c["h"], c["m"], f["h"], f["m"]) == (665_041, 646_953, 496_948, 46_279))(next(a for a in datos["actividades"] if a["ciiu"] == "G")["sexo"], next(a for a in datos["actividades"] if a["ciiu"] == "F")["sexo"]),
        "Estudios: 39,8% de los ocupados con título; desocupación 6,3%, 7,8% y 9,7%": (lambda e: e["pct_con_titulo"] == 39.8 and (e["niveles"]["Profesional"]["tasa_desocupacion"], e["niveles"]["Tecnico"]["tasa_desocupacion"], e["niveles"]["Sin_titulo"]["tasa_desocupacion"]) == (6.3, 7.8, 9.7))(datos["estudios"]),
        "Estudios: los niveles suman el total y su tasa coincide con la tabla regional": sum(d["ocupados"] for d in datos["estudios"]["niveles"].values()) == datos["estudios"]["total"] and all(datos["estudios"]["niveles"][n]["tasa_desocupacion"] == d["tasa"] for n, d in datos["niveles_chile"].items()),
        "Estudios: mujeres 46,5% y hombres 34,6% de los ocupados con título": datos["estudios"]["sexo"] == {"hombres": 34.6, "mujeres": 46.5},
        "Educación por región: suma 15.102.704 y va de Maule (21,1%) a la Metropolitana (32,9%)": (lambda e: sum(e["chile"]) == 15_102_704 and sum(sum(v) for r, v in e.items() if r != "chile") == sum(e["chile"])
            and sorted((round(100 * (v[0] + v[1]) / sum(v), 1), int(r)) for r, v in e.items() if r != "chile")[::15] == [(21.1, 7), (32.9, 13)])(datos["estudios"]["educacion"]),
        "Educación por región: Chile 28,2% con título": (lambda c: round(100 * (c[0] + c[1]) / sum(c), 1) == 28.2)(datos["estudios"]["educacion"]["chile"]),
        "Hallazgos: 4 de cada 10 ocupados con título; 1 de cada 10 en Hogares y 8 de cada 10 en Servicios profesionales": (lambda p: round(datos["estudios"]["pct_con_titulo"] / 10) == 4 and (round(min(p) / 10), round(max(p) / 10)) == (1, 8))(
            [100 * (a["niveles"][0][0] + a["niveles"][1][0]) / sum(f[0] for f in a["niveles"]) for a in datos["actividades"]]),
        "Desocupación menor con título en las 16 regiones: de Aysén (4,2% y 6,2%) a Biobío (9,1% y 11,1%)": (lambda d: len(d) == 16 and all(c < t for c, t in d.values()) and d["11"] == [4.2, 6.2] and d["8"] == [9.1, 11.1]
            and min(d, key=lambda r: d[r][0]) == "11" and max(d, key=lambda r: d[r][0]) == "8")(datos["estudios"]["desocupacion_titulo"]),
        "Nivel por actividad: Minería en Chile 82.082 profesionales; Antofagasta 28.576": (lambda a: a["niveles"][0] == [82_082, 30.6, 61_954, 20_128, 27.3, 48.7] and a["regiones"][2]["niveles"][0] == [28_576, 28.0, 21_907, 6_669, 25.3, 43.3])(next(a for a in datos["actividades"] if a["ciiu"] == "B")),
        "Nivel por actividad: solo faltan 2.757 ocupados sin nivel informado": sum(d["ocupados"] for a in datos["actividades"] for d in a["regiones"].values()) - sum(f[0] for a in datos["actividades"] for d in a["regiones"].values() for f in d["niveles"]) == 2_757,
        "Nivel por actividad: hombres y mujeres suman el total cuando ambos se muestran": all(f[2] + f[3] == f[0] for a in datos["actividades"] for d in [a, *a["regiones"].values()] for f in d["niveles"] if f[2] is not None and f[3] is not None),
        "Nivel por actividad: 16 filas regionales con menos de 10, y ninguna nacional": sum(f[2] is None or f[3] is None for a in datos["actividades"] for d in a["regiones"].values() for f in d["niveles"]) == 16 and not any(f[2] is None or f[3] is None for a in datos["actividades"] for f in a["niveles"]),
        "Nivel por actividad: todas las actividades 27,3%, 12,3% y 60,4%": datos["perfil_estudios"]["todas"] == [27.3, 12.3, 60.4],
        "Sexo por región: en cada celda, hombres y mujeres suman sus ocupados": all(d["h"] + d["m"] == d["ocupados"] for a in datos["actividades"] for d in a["regiones"].values()),
        "Sexo por región: las bases suman la base de cada región y de Chile": all(v["h"] + v["m"] == datos["base_ocupados"]["regiones"][r] for r, v in datos["base_ocupados"]["sexo"]["regiones"].items()) and sum(datos["base_ocupados"]["sexo"]["chile"].values()) == datos["base_ocupados"]["chile"],
        "Sexo por región: Biobío en Salud 15.108 y 45.643; 4,91% y 17,22%": (lambda d: (d["h"], d["m"], d["pct_h"], d["pct_m"]) == (15_108, 45_643, 4.91, 17.22))(next(a for a in datos["actividades"] if a["ciiu"] == "Q")["regiones"][8]),
        "Situación por sexo: cada región suma sus grupos": all(d["sexo"]["hombres"][k] + d["sexo"]["mujeres"][k] == d[k] for d in pob["regiones"].values() for k in ("total", "trabajan", "buscan", "no_buscan", "sin_dato")),
        "Nivel por sexo: suma los ocupados y desocupados de cada región y de Chile": all(d["sexo"]["oh"] + d["sexo"]["om"] == d["trabajo"] and d["sexo"]["dh"] + d["sexo"]["dm"] == d["desocupados"] for g in datos["niveles"].values() for d in g.values()) and all(d["sexo"]["oh"] + d["sexo"]["om"] == d["ocupados"] and d["sexo"]["dh"] + d["sexo"]["dm"] == d["desocupados"] for d in datos["niveles_chile"].values()),
        "Títulos por sexo: hombres y mujeres no superan el total; Enfermería 845 y 4.123": all(f["tit_h"] + f["tit_m"] <= f["tit"] for f in datos["fichas"].values()) and (datos["fichas"]["ENFERMERIA"]["tit_h"], datos["fichas"]["ENFERMERIA"]["tit_m"]) == (845, 4_123),
        "Sexo y género: las constantes coinciden con los microdatos, si están": totales_sexo_genero_correctos(),
        "Población: el total coincide con los microdatos, si están": not RUTA_PERSONAS.exists() or pq.ParquetFile(RUTA_PERSONAS).metadata.num_rows == POBLACION_TOTAL_CENSO,
        # La columna "Con título" se calcula en la página desde estas personas; aquí se fija contra la fuente.
        "Con título por actividad: Servicios profesionales 78,7%, Hogares 9,9% y todas 39,6%": (lambda pct: (round(pct(next(a for a in datos["actividades"] if a["ciiu"] == "M")["niveles"]), 1), round(pct(next(a for a in datos["actividades"] if a["ciiu"] == "T")["niveles"]), 1), round(pct([[sum(a["niveles"][i][0] for a in datos["actividades"])] for i in range(3)]), 1)) == (78.7, 9.9, 39.6))(lambda f: 100 * (f[0][0] + f[1][0]) / (f[0][0] + f[1][0] + f[2][0])),
        "Base de la participación: Valparaíso 706.053 y Chile 7.395.105": datos["base_ocupados"]["regiones"]["5"] == 706_053 and datos["base_ocupados"]["chile"] == 7_395_105,
        "Cada participación se puede recalcular con ocupados y su base": all(abs(100 * d["ocupados"] / datos["base_ocupados"]["regiones"][str(r)] - d["pct"]) < 0.0051 for a in datos["actividades"] for r, d in a["regiones"].items()),
        "Población: Chile con tasa de desocupación 8,6%, participación 59,6% y 7.801.449 con lugar de trabajo": pob["chile"]["tasa_desocupacion"] == 8.6 and pob["chile"]["tasa_participacion"] == 59.6 and pob["chile"]["lugar_trabajo"] == 7_801_449,
        "Población: ocupados por lugar de trabajo suman Chile; Antofagasta 372.015": sum(d["lugar_trabajo"] for d in pob["regiones"].values()) == pob["chile"]["lugar_trabajo"] and pob["regiones"]["2"]["lugar_trabajo"] == 372_015,
        "La plantilla quedó completa": "__DATOS__" not in html and "__GEO__" not in html,
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    log.info("  [i] Celdas sin dato: %d; mayor cambio de área: %.3f%%", sin_dato, geo["diferencia_area_pct"])
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    datos, geo = construir_datos(), construir_geometria()
    html = RUTA_PLANTILLA.read_text(encoding="utf-8").replace("__DATOS__", json.dumps(datos, ensure_ascii=False)).replace("__GEO__", json.dumps({k: geo[k] for k in ("ancho", "alto", "trazados")}))
    validar(datos, geo, html)
    RUTA_SALIDA.parent.mkdir(exist_ok=True)
    RUTA_SALIDA.write_text(html, encoding="utf-8")
    log.info("HTML generado: %s (%.0f KB, %d carreras)", RUTA_SALIDA, RUTA_SALIDA.stat().st_size / 1024, len(datos["fichas"]))
