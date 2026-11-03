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
  - El color y el texto de las veces se calculan aquí, una sola vez y con el valor sin redondear. Si se
    redondea antes, un 1,2024 cae en el tramo equivocado, aunque su lectura diga concentra.
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
MARGEN_CORTE = 0.05              # Cerca de un corte, 1 decimal ya no permite explicar el color.
MAX_DECIMALES = 4
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
    """Tramo de color; usa las mismas comparaciones que la lectura. Vacío si no hay dato."""
    if pd.isna(peso):
        return None
    if peso <= CORTES_AZUL[2]:
        return sum(peso > c for c in CORTES_AZUL[:2])
    if peso < CORTES_ROJO[0]:
        return CLASE_NEUTRA
    return CLASE_NEUTRA + 1 + sum(peso >= c for c in CORTES_ROJO[1:])


def texto_peso(peso: float) -> str:
    """Muestra 1 decimal, o más si hace falta para que la cifra visible calce con el tramo de su color."""
    if pd.isna(peso):
        return "s/d"
    cerca_de_corte = any(abs(peso - c) <= MARGEN_CORTE for c in CORTES_AZUL + CORTES_ROJO)
    for decimales in range(2 if cerca_de_corte else 1, MAX_DECIMALES + 1):
        if clase_color(round(peso, decimales)) == clase_color(peso):
            break
    return f"{peso:.{decimales}f}".replace(".", ",")


def redondear(valor: float, decimales: int = 2) -> float | None:
    return None if pd.isna(valor) else round(float(valor), decimales)


def resumen_nacional(g: pd.DataFrame, total_censo: int, ene_total: float) -> dict:
    """Totales del país para una actividad; total_censo incluye a quienes no tienen región de trabajo."""
    con_personas, con_peso = g.loc[g["ocupados"].idxmax()], g.loc[g["peso_relativo"].idxmax()]
    return {"ocupados": int(g["ocupados"].sum()), "censo_total": total_censo, "ene_ocupados": int(round(g["ene_ocupados"].sum())),
            "ene_pct": redondear(100 * g["ene_ocupados"].sum() / ene_total, 1), "conc": int((g["lectura"] == "concentra").sum()),
            "mas_personas": {"r": int(con_personas["codigo_region"]), "n": int(con_personas["ocupados"]), "pct": redondear(100 * con_personas["ocupados"] / g["ocupados"].sum(), 1)},
            "mas_peso": {"r": int(con_peso["codigo_region"]), "txt": texto_peso(con_peso["peso_relativo"])}}


def construir_datos() -> dict:
    censo = pd.read_csv(RUTA_CENSO, sep=";")
    ene_total = float(censo["ene_ocupados"].sum())
    censo = censo[censo["mostrar_en_mapa"]]
    procesado = pd.read_csv(RUTA_CENSO_PROCESADO, sep=";")
    totales_censo = procesado[procesado["sit_fuerza_trabajo"] == OCUPADO].groupby("actividad_ciiu")["personas"].sum()
    areas = pd.read_csv(RUTA_AREAS, sep=";")
    carreras = pd.read_csv(RUTA_CARRERAS, sep=";")
    actividades = []
    for (ciiu, glosa), g in censo.groupby(["actividad_ciiu", "actividad_glosa"]):
        primero = g.iloc[0]
        a = areas[(areas["actividad_ciiu"] == ciiu) & (areas["fiabilidad"] != "no_fiable")].nlargest(4, "pct_en_actividad")
        vinculadas = carreras[(carreras["actividad_ciiu"] == ciiu) & carreras["afinidad"].isin(AFINIDADES_VISIBLES)].sort_values("pct_en_carrera", ascending=False)
        actividades.append({
            "ciiu": ciiu, "glosa": glosa, "pct_nacional": redondear(primero["pct_nacional"], 1), "pct_sin_region": redondear(primero["pct_sin_region_trabajo"], 1),
            "alerta_fuente": bool(primero["alerta_difiere_fuente"]), "nacional": resumen_nacional(g, int(totales_censo[ciiu]), ene_total),
            "regiones": {int(f["codigo_region"]): {"ocupados": int(f["ocupados"]), "pct": redondear(f["pct_en_region"], 1), "peso": redondear(f["peso_relativo"], 6), "clase": clase_color(f["peso_relativo"]), "peso_txt": texto_peso(f["peso_relativo"]), "lectura": f["lectura"],
                                                 "pob": redondear(f["pct_poblacion_15_mas"], 1), "ene_peso_txt": texto_peso(f["ene_peso_relativo"]), "ene_lectura": f["ene_lectura"]} for _, f in g.iterrows()},
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
                     "alerta_inst": bool(f["alerta_pocas_instituciones"]), "no_trab": redondear(f["pct_no_trabajan"], 1) if f["fiabilidad_no_trabajan"] != "no_fiable" else None,
                     "no_trab_n": int(round(f["titulados_no_trabajan"])) if f["fiabilidad_no_trabajan"] != "no_fiable" else None, "no_trab_poco": f["fiabilidad_no_trabajan"] == "poco_fiable", "pct_principal": redondear(f["pct_institucion_principal"], 0),
                     "actividades": v[["actividad_ciiu", "actividad_glosa", "pct_en_carrera"]].round(1).values.tolist()}
    niveles = pd.read_csv(RUTA_NIVELES, sep=";")
    por_region = {str(r): {f["nivel_titulo"]: {"trabajo": int(f["ocupados_trabajo"]), "desocupados": int(f["desocupados"]), "tasa": redondear(f["tasa_desocupacion"], 1),
                                               "nacional": redondear(f["tasa_nacional_nivel"], 1), "ene": redondear(f["ene_tasa_desocupacion"], 1) if f["ene_fiabilidad"] != "no_fiable" else None,
                                               "ene_poco": f["ene_fiabilidad"] == "poco_fiable"} for _, f in g.iterrows()} for r, g in niveles.groupby("codigo_region")}
    suma = niveles.groupby("nivel_titulo")[["ocupados_residencia", "desocupados"]].sum()
    primera = niveles.drop_duplicates("nivel_titulo").set_index("nivel_titulo")
    niveles_chile = {n: {"ocupados": int(suma.loc[n, "ocupados_residencia"]), "desocupados": int(suma.loc[n, "desocupados"]), "tasa": redondear(primera.loc[n, "tasa_nacional_nivel"], 1),
                         "ene": redondear(primera.loc[n, "ene_tasa_nacional_nivel"], 1)} for n in suma.index}
    return {"actividades": actividades, "fichas": fichas, "niveles": por_region, "niveles_chile": niveles_chile, "regiones": {str(k): v for k, v in NOMBRES_REGION.items()}, "orden": ORDEN_NORTE_SUR, "tramos": TRAMOS}


def validar(datos: dict, geo: dict, html: str) -> None:
    celdas = [d for a in datos["actividades"] for d in a["regiones"].values() if d["clase"] is not None]
    lectura_esperada = lambda c: "bajo_lo_nacional" if c < CLASE_NEUTRA else "similar" if c == CLASE_NEUTRA else "concentra"
    con_base = [d for d in celdas if d["lectura"] != "base_pequena"]
    texto_calza = lambda d: clase_color(float(d["peso_txt"].replace(",", "."))) == d["clase"]
    sin_dato = sum(d["clase"] is None for a in datos["actividades"] for d in a["regiones"].values())
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
