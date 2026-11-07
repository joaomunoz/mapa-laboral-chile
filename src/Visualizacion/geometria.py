"""
<src/Visualizacion/geometria.py>

Bordes de las regiones en SVG, simplificados sin abrir huecos entre ellas.

Decisiones:
  - Simplificación por cobertura: mantiene exactos los bordes compartidos; simplificar cada región por separado
    abriría huecos entre ellas. Exige bordes que calcen entre regiones, y la capa oficial no los trae: por eso se
    reconstruyen antes con una grilla de 0,01° (unos 1 km), un quinto de píxel a la escala del mapa.
  - Se omiten los territorios insulares lejanos (Rapa Nui, Juan Fernández): al incluirlos, el continente se vería
    diminuto. Sus datos siguen dentro de sus regiones.
"""

from __future__ import annotations

import math

import geopandas as gpd
import numpy as np
import shapely

from config import (
    ANCHO_SVG, AREA_MINIMA_PX, GRILLA_GRADOS, LATITUD_REFERENCIA, LONGITUD_MINIMA_CONTINENTE, TOLERANCIA_GRADOS,
)


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


def construir_geometria(g: gpd.GeoDataFrame) -> dict:
    """Devuelve los trazados SVG de cada región, el tamaño del lienzo y los controles de la geometría."""
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
