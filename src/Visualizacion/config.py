"""
<src/Visualizacion/config.py>

Rutas y constantes del mapa: entradas, cortes del CL, nombres, colores y totales de referencia.

Están juntas para que un cambio de criterio (un corte, un nombre, una ruta) se haga en un solo lugar.
Los totales de referencia los comprueba controles.py contra los microdatos cuando están disponibles.
"""

import sys
from pathlib import Path

DIR = Path(__file__).parent
DIR_SRC = DIR.parent
sys.path.append(str(DIR_SRC / "Scrapers"))  # Al final: no debe tapar los módulos de Visualizacion.
from comun.periodos import TEXTO_ACTUAL, TEXTO_CONTRASTE, TEXTO_EVOLUCION  # noqa: E402
DIR_JOINS = DIR_SRC / "Analisis" / "JOINS"
RUTA_CENSO = DIR_JOINS / "Concentracion_Region_Actividad_Censo" / "Salida" / "concentracion_region_actividad_censo.csv"
RUTA_AREAS = DIR_JOINS / "Areas_Por_Actividad" / "Salida" / "areas_por_actividad.csv"
RUTA_CARRERAS = DIR_JOINS / "Carreras_Por_Actividad" / "Salida" / "carreras_por_actividad.csv"
RUTA_NIVELES = DIR_JOINS / "Fuerza_Trabajo_Region_Nivel" / "Salida" / "fuerza_trabajo_region_nivel.csv"
RUTA_EVOLUCION = DIR_JOINS / "Evolucion_Desocupacion" / "Salida" / "evolucion_desocupacion.csv"
RUTA_FORMALIDAD = DIR_JOINS / "Formalidad_Ocupados" / "Salida" / "formalidad_ocupados.csv"

# Periodo de cada fuente que la página nombra (08-11-26): cada cifra declara su periodo, y lo toma de aquí. Los de la
# ENE se arman desde los meses que usan las tablas (comun/periodos.py), así que no pueden quedar distintos.
# CASEN: fechas de su trabajo de campo, según el Ministerio de Desarrollo Social y Familia.
PERIODOS = {"ene_contraste": TEXTO_CONTRASTE, "ene_evolucion": TEXTO_EVOLUCION, "ene_actual": TEXTO_ACTUAL, "casen": "noviembre de 2024 a febrero de 2025"}
RUTA_CENSO_PROCESADO = DIR_SRC / "Scrapers" / "CENSO" / "Salida" / "censo_procesado.csv"
RUTA_CENSO_SEXO = DIR_SRC / "Scrapers" / "CENSO" / "Salida" / "censo_por_sexo.csv"
RUTA_PERSONAS = DIR_SRC / "Scrapers" / "CENSO" / "Entrada" / "personas_censo2024.parquet"
RUTA_REGIONES = DIR_SRC / "Scrapers" / "CENSO" / "Entrada" / "cartografia" / "Cartografia_censo2024_Pais_Regional.parquet"
DIR_WEB = DIR / "web"
RUTA_PLANTILLA = DIR_WEB / "index.html"
# El mapa se abre con doble clic (file://), donde el navegador no carga módulos JS: el generador une estos archivos en
# un solo <style> y un solo <script>. El orden importa: en CSS, layout.css va al final para que sus reglas de pantallas
# angostas ganen; en JS, datos.js va primero y main.js al final, cuando todo lo demás ya está definido.
ARCHIVOS_CSS = ["css/base.css", "css/componentes.css", "css/layout.css"]
ARCHIVOS_JS = ["js/datos.js", "js/formato.js", "js/mapa.js", "js/vistas/resumen.js", "js/vistas/actividad.js", "js/vistas/region.js",
               "js/vistas/carreras.js", "js/navegacion.js", "js/main.js"]
RUTA_SALIDA = DIR_SRC.parent / "docs" / "index.html"

ANCHO_SVG = 250
LATITUD_REFERENCIA = -36.0  # Mantiene una proporción razonable en un país tan largo.
LONGITUD_MINIMA_CONTINENTE = -76.0
TOLERANCIA_GRADOS = 0.035
GRILLA_GRADOS = 0.01
DIFERENCIA_AREA_MAXIMA_PCT = 0.5
# Simplificar cambia más el área que reconstruir los bordes: 0,71% en Valparaíso y 0,52% en Los Lagos (07-11-26).
DIFERENCIA_AREA_SIMPLIFICADA_MAXIMA_PCT = 1.0
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
    "N": "Servicios administrativos", "O": "Administración pública", "P": "Enseñanza", "Q": "Salud y asistencia social", "R": "Artes y recreación", "S": "Otros servicios", "T": "Hogares como empleadores",
}
# Áreas de estudio (CINE, como en SIES) en corto para las filas del gráfico: con el nombre completo, "Ingeniería,
# Industria y Construcción" partía en dos líneas la fila de Construcción. El nombre completo va en el globo.
AREAS_CORTAS = {
    "Administración de Empresas y Derecho": "Administración y Derecho", "Agricultura, Silvicultura, Pesca y Veterinaria": "Agricultura y Veterinaria",
    "Artes y Humanidades": "Artes y Humanidades", "Ciencias naturales, matemáticas y estadística": "Ciencias naturales", "Ciencias Sociales, Periodismo e Información": "Ciencias Sociales",
    "Educación": "Educación", "Ingeniería, Industria y Construcción": "Ingeniería", "Salud y Bienestar": "Salud y Bienestar", "Servicios": "Servicios",
    "Tecnología de la Información y la Comunicación (TIC)": "Tecnología (TIC)",
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
