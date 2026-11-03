"""
<src/Analisis/JOINS/CW_Competencia_Desocupados/obtener.py>
Actualizado 02-11-26 16:40

Carga las entradas del Paso 2. El stock se lee de Titulados y no del Paso 1 porque este aún no
trae carrera_clasificacion_nivel_1, necesaria para aplicar la definición de título que compite.
"""

from pathlib import Path

import pandas as pd

DIR_ANALISIS = Path(__file__).resolve().parents[2]
DIR_SCRAPERS = DIR_ANALISIS.parent / "Scrapers"
DIR_PUENTES = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida"
SEP_LISTA = " | "


def clases_por_titulo() -> dict[str, list[str]]:
    """Categorías SIES de cada titulo_comun superior, según P4."""
    p4 = pd.read_csv(DIR_PUENTES / "P4_puente_niveles_educativos.csv", sep=";")
    p4 = p4[p4["titulo_comun"] != "No_superior"].dropna(subset=["sies_clasificacion_nivel_1"])
    return {t: sorted({c for v in g["sies_clasificacion_nivel_1"] for c in v.split(SEP_LISTA)})
            for t, g in p4.groupby("titulo_comun")}


def cargar_stock() -> pd.DataFrame:
    """Títulos por región de sede, carrera genérica y titulo_comun."""
    tit = pd.read_csv(DIR_SCRAPERS / "Titulados" / "Salida" / "titulados_procesado.csv", sep=";", low_memory=False,
                      usecols=["codigo_region", "carrera_generica", "carrera_clasificacion_nivel_1", "total_titulaciones"])
    partes = [tit[tit["carrera_clasificacion_nivel_1"].isin(clases)].assign(titulo_comun=titulo)
              for titulo, clases in clases_por_titulo().items()]
    return (pd.concat(partes).groupby(["codigo_region", "titulo_comun", "carrera_generica"], as_index=False)
            ["total_titulaciones"].sum().rename(columns={"total_titulaciones": "stock_sies"}))


def cargar_ene() -> pd.DataFrame:
    return pd.read_csv(DIR_SCRAPERS / "ENE" / "Salida" / "ene_procesado.csv", sep=";", low_memory=False,
                       usecols=["idrph", "mes", "codigo_region", "fact_cal", "cae_especifico", "cine11_1d",
                                "nivel", "edad", "estrato", "conglomerado"])


def cargar_razon() -> pd.DataFrame:
    return pd.read_csv(DIR_PUENTES / "P8_razon_empleo_carrera.csv", sep=";")


def cargar_ocupados() -> pd.DataFrame:
    return pd.read_csv(DIR_ANALISIS / "JOINS" / "CW_Ocupados_Carrera_Region_Actividad" / "Salida" / "ocupados_carrera_region_actividad.csv", sep=";")


def cargar_casen() -> pd.DataFrame:
    """Personas de CASEN con título y carrera asignada: ajustan el reparto y lo validan."""
    casen = pd.read_csv(DIR_SCRAPERS / "CASEN" / "Salida" / "casen_procesado.csv", sep=";", low_memory=False,
                        usecols=["e6a", "carrera_normalizada", "activ", "titulo_comun", "expr", "edad", "varunit"])
    p5 = pd.read_csv(DIR_PUENTES / "P5_puente_carrera_casen.csv", sep=";")[["e6a", "carrera_normalizada", "carrera_generica", "nivel_titulo", "estado"]]
    d = casen.merge(p5, on=["e6a", "carrera_normalizada"], validate="many_to_one")
    return d[d["titulo_comun"].notna() & (d["estado"] == "asignado") & d["edad"].between(22, 54)]
