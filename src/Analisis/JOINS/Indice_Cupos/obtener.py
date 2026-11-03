"""
<src/Analisis/JOINS/Indice_Cupos/obtener.py>
Actualizado 02-11-26 16:40

Carga las salidas de los pasos 1 a 4, P7 y P8, y mide cuánto de cada carrera trabaja en la actividad
privado por si P4 no lo trae (carreras con menos de 60 casos).
"""

from pathlib import Path

import pandas as pd

DIR_JOINS = Path(__file__).resolve().parents[1]
DIR_ANALISIS = DIR_JOINS.parent
DIR_SCRAPERS = DIR_ANALISIS.parent / "Scrapers"
DIR_PUENTES = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida"
CLASES_QUE_COMPITEN = ["Técnico de Nivel Superior", "Profesional Con Licenciatura", "Profesional Sin Licenciatura"]


def cargar_paso1() -> pd.DataFrame:
    p = pd.read_csv(DIR_JOINS / "CW_Empleabilidad_Oferta_Titulados" / "Salida" / "oferta_empleabilidad_procesado.csv", sep=";", low_memory=False,
                    usecols=["anio", "codigo_region", "carrera_generica", "carrera_clasificacion_nivel_1", "total_titulaciones", "empleabilidad_1er_anio"])
    return p[p["carrera_clasificacion_nivel_1"].isin(CLASES_QUE_COMPITEN)]


def cargar_desocupados() -> pd.DataFrame:
    d = pd.read_csv(DIR_JOINS / "CW_Competencia_Desocupados" / "Salida" / "desocupados_carrera_region.csv", sep=";")
    return d[d["entra_al_indice"]]


def cargar_jubilacion() -> pd.DataFrame:
    return pd.read_csv(DIR_JOINS / "CW_Demanda_Jubilacion" / "Salida" / "jubilacion_carrera_region.csv", sep=";")


def cargar_vacantes() -> pd.DataFrame:
    return pd.read_csv(DIR_JOINS / "CW_Demanda_Empresarial" / "Salida" / "vacantes_carrera_region.csv", sep=";")


def cargar_vacantes_publicas() -> pd.DataFrame:
    return pd.read_csv(DIR_JOINS / "CW_Demanda_Publica" / "Salida" / "vacantes_publicas_carrera_region.csv", sep=";")


def cargar_catalogo() -> pd.DataFrame:
    p = pd.read_csv(DIR_PUENTES / "P7_perfil_carrera_actividad_ocupacion.csv", sep=";")
    p = p[p["dimension"] == "actividad_economica"].drop_duplicates("carrera_generica")
    return p[["carrera_generica", "nivel_titulo", "area_cine_sies", "nivel_confianza"]].rename(columns={"nivel_confianza": "nivel_confianza_perfil"})


def cargar_razon() -> pd.DataFrame:
    return pd.read_csv(DIR_PUENTES / "P8_razon_empleo_carrera.csv", sep=";")


def cargar_privado() -> pd.DataFrame:
    c = pd.read_csv(DIR_SCRAPERS / "CASEN" / "Salida" / "casen_procesado.csv", sep=";", low_memory=False,
                    usecols=["e6a", "carrera_normalizada", "activ", "titulo_comun", "expr", "o15"])
    p5 = pd.read_csv(DIR_PUENTES / "P5_puente_carrera_casen.csv", sep=";")[["e6a", "carrera_normalizada", "carrera_generica", "nivel_titulo", "estado"]]
    d = c.merge(p5, on=["e6a", "carrera_normalizada"], validate="many_to_one")
    return d[(d["activ"] == 1) & d["titulo_comun"].notna() & (d["estado"] == "asignado") & d["o15"].notna()]
