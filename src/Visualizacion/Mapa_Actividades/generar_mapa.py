"""
<src/Visualizacion/Mapa_Actividades/generar_mapa.py>
Actualizado 03-11-26 13:10

Genera el mapa interactivo: una sola página HTML, sin servidor ni dependencias externas.

Entradas: tablas de Analisis/JOINS y la capa regional de la cartografía del Censo 2024.
Salida:   Salida/index.html
Ejecutar: .venv/bin/python src/Visualizacion/Mapa_Actividades/generar_mapa.py (requiere geopandas y pyarrow)

Decisiones:
  - Simplificación por cobertura: mantiene exactos los bordes compartidos; simplificar cada región por separado
    abriría huecos entre ellas.
  - Se omiten los territorios insulares lejanos (Rapa Nui, Juan Fernández): al incluirlos, el continente se vería
    diminuto. Sus datos siguen dentro de sus regiones.
  - Actividad U fuera de la lista: se conserva en la tabla, pero no aporta al mapa.
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
import shapely

log = logging.getLogger(__name__)

DIR = Path(__file__).parent
DIR_SRC = DIR.parents[1]
DIR_JOINS = DIR_SRC / "Analisis" / "JOINS"
RUTA_CENSO = DIR_JOINS / "Concentracion_Region_Actividad_Censo" / "Salida" / "concentracion_region_actividad_censo.csv"
RUTA_AREAS = DIR_JOINS / "Areas_Por_Actividad" / "Salida" / "areas_por_actividad.csv"
RUTA_CARRERAS = DIR_JOINS / "Carreras_Por_Actividad" / "Salida" / "carreras_por_actividad.csv"
RUTA_REGIONES = DIR_SRC / "Scrapers" / "CENSO" / "Entrada" / "cartografia" / "Cartografia_censo2024_Pais_Regional.parquet"
RUTA_PLANTILLA = DIR / "plantilla.html"
RUTA_SALIDA = DIR / "Salida" / "index.html"

ANCHO_SVG = 250
LATITUD_REFERENCIA = -36.0  # Mantiene una proporción razonable en un país tan largo.
LONGITUD_MINIMA_CONTINENTE = -76.0
TOLERANCIA_GRADOS = 0.035
AREA_MINIMA_PX = 3.0
AFINIDADES_VISIBLES = ["afin", "indicio_sin_muestra"]
NOMBRES_REGION = {
    1: "Tarapacá", 2: "Antofagasta", 3: "Atacama", 4: "Coquimbo", 5: "Valparaíso", 6: "O'Higgins", 7: "Maule", 8: "Biobío",
    9: "La Araucanía", 10: "Los Lagos", 11: "Aysén", 12: "Magallanes", 13: "Metropolitana", 14: "Los Ríos", 15: "Arica y Parinacota", 16: "Ñuble",
}
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


def construir_geometria() -> dict:
    """Devuelve los trazados SVG de cada región y el tamaño del lienzo."""
    g = gpd.read_parquet(RUTA_REGIONES).set_geometry("SHAPE")
    simplificadas = shapely.coverage_simplify(g.geometry.values, TOLERANCIA_GRADOS)
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
    return {"ancho": ANCHO_SVG, "alto": round(alto, 1), "trazados": trazados}


def redondear(valor: float, decimales: int = 2) -> float | None:
    return None if pd.isna(valor) else round(float(valor), decimales)


def construir_datos() -> dict:
    censo = pd.read_csv(RUTA_CENSO, sep=";")
    censo = censo[censo["mostrar_en_mapa"]]
    areas = pd.read_csv(RUTA_AREAS, sep=";")
    carreras = pd.read_csv(RUTA_CARRERAS, sep=";")
    actividades = []
    for (ciiu, glosa), g in censo.groupby(["actividad_ciiu", "actividad_glosa"]):
        primero = g.iloc[0]
        a = areas[(areas["actividad_ciiu"] == ciiu) & (areas["fiabilidad"] != "no_fiable")].nlargest(4, "pct_en_actividad")
        vinculadas = carreras[(carreras["actividad_ciiu"] == ciiu) & carreras["afinidad"].isin(AFINIDADES_VISIBLES)].sort_values("pct_en_carrera", ascending=False)
        actividades.append({
            "ciiu": ciiu, "glosa": glosa, "pct_nacional": redondear(primero["pct_nacional"]), "pct_sin_region": redondear(primero["pct_sin_region_trabajo"], 1),
            "alerta_fuente": bool(primero["alerta_difiere_fuente"]),
            "regiones": {int(f["codigo_region"]): {"ocupados": int(f["ocupados"]), "pct": redondear(f["pct_en_region"]), "peso": redondear(f["peso_relativo"]), "lectura": f["lectura"],
                                                 "pob": redondear(f["pct_poblacion_15_mas"], 1), "ene_peso": redondear(f["ene_peso_relativo"]), "ene_lectura": f["ene_lectura"]} for _, f in g.iterrows()},
            "areas": [{"area": f["area_cine"], "pct": redondear(f["pct_en_actividad"], 1), "min": redondear(f["pct_en_actividad_min"], 1), "max": redondear(f["pct_en_actividad_max"], 1)} for _, f in a.iterrows()],
            "afines": [{"c": f["carrera_generica"], "pct": redondear(f["pct_en_carrera"], 1), "min": redondear(f["pct_en_carrera_min"], 1), "max": redondear(f["pct_en_carrera_max"], 1),
                        "tit": int(round(f["ocupados_titulados"])), "fiab": f["fiabilidad"]} for _, f in vinculadas[vinculadas["afinidad"] == "afin"].iterrows()],
            "indicios": [{"c": f["carrera_generica"], "n": int(f["n_celda"])} for _, f in vinculadas[vinculadas["afinidad"] == "indicio_sin_muestra"].iterrows()],
        })
    usadas = carreras[carreras["afinidad"].isin(AFINIDADES_VISIBLES)]
    fichas = {}
    for c, f in usadas.drop_duplicates("carrera_generica").set_index("carrera_generica").iterrows():
        v = usadas[(usadas["carrera_generica"] == c) & (usadas["afinidad"] == "afin")].sort_values("pct_en_carrera", ascending=False)
        fichas[c] = {"nombre": nombre_legible(c), "nivel": f["nivel_titulo"], "area": f["area_cine"], "tit": int(f["titulados_2025"]), "emp": redondear(f["empleabilidad_1er_anio"], 1),
                     "ing1": redondear(f["ingreso_medio_1er_anio"], 0), "ing5": redondear(f["ingreso_medio_5to_anio"], 0), "inst": int(f["n_instituciones"]),
                     "alerta_inst": bool(f["alerta_pocas_instituciones"]), "pct_principal": redondear(f["pct_institucion_principal"], 0),
                     "actividades": v[["actividad_ciiu", "actividad_glosa", "pct_en_carrera"]].round(1).values.tolist()}
    return {"actividades": actividades, "fichas": fichas, "regiones": {str(k): v for k, v in NOMBRES_REGION.items()}, "orden": ORDEN_NORTE_SUR}


def validar(datos: dict, geo: dict, html: str) -> None:
    controles = {
        "20 actividades en la lista": len(datos["actividades"]) == 20 and "U" not in [a["ciiu"] for a in datos["actividades"]],
        "16 regiones con trazado": sorted(geo["trazados"]) == sorted(NOMBRES_REGION),
        "Cada actividad tiene las 16 regiones": all(len(a["regiones"]) == 16 for a in datos["actividades"]),
        "Antofagasta en Minería: 101.929": next(a for a in datos["actividades"] if a["ciiu"] == "B")["regiones"][2]["ocupados"] == 101_929,
        "Todas las carreras listadas tienen ficha": all(x["c"] in datos["fichas"] for a in datos["actividades"] for x in a["afines"] + a["indicios"]),
        "La plantilla quedó completa": "__DATOS__" not in html and "__GEO__" not in html,
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    fallidos = [n for n, ok in controles.items() if not ok]
    if fallidos:
        raise ValueError(f"Validaciones fallidas: {fallidos}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    datos, geo = construir_datos(), construir_geometria()
    html = RUTA_PLANTILLA.read_text(encoding="utf-8").replace("__DATOS__", json.dumps(datos, ensure_ascii=False)).replace("__GEO__", json.dumps(geo))
    validar(datos, geo, html)
    RUTA_SALIDA.parent.mkdir(exist_ok=True)
    RUTA_SALIDA.write_text(html, encoding="utf-8")
    log.info("HTML generado: %s (%.0f KB, %d carreras)", RUTA_SALIDA, RUTA_SALIDA.stat().st_size / 1024, len(datos["fichas"]))
