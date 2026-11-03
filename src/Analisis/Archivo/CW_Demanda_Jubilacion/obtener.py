"""
<src/Analisis/Archivo/CW_Demanda_Jubilacion/obtener.py>

Carga las entradas del Paso 3: ENE, CASEN con P5 y la tabla de ocupados por carrera y región.
"""

from pathlib import Path

import numpy as np
import pandas as pd

DIR_ANALISIS = Path(__file__).resolve().parents[2]
DIR_SCRAPERS = DIR_ANALISIS.parent / "Scrapers"
DIR_PUENTES = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida"


def cargar_ene() -> pd.DataFrame:
    """Personas con título, con nivel común a CASEN: magíster y doctorado cuentan como profesional."""
    e = pd.read_csv(DIR_SCRAPERS / "ENE" / "Salida" / "ene_procesado.csv", sep=";", low_memory=False,
                    usecols=["idrph", "codigo_region", "codigo_region_trabajo", "fact_cal", "cae_especifico", "cine11_1d", "edad", "sexo", "estrato", "conglomerado"])
    t = e[e["cine11_1d"].ge(3) & e["edad"].ge(20)].copy()
    t["nivel_titulo"] = np.where(t["cine11_1d"] == 3, "Tecnico", "Profesional")
    t["ocupado"] = t["cae_especifico"].between(1, 7)
    return t, e[["estrato", "conglomerado"]].drop_duplicates().groupby("estrato").size()


def cargar_casen() -> pd.DataFrame:
    """Ocupados con título y carrera asignada."""
    c = pd.read_csv(DIR_SCRAPERS / "CASEN" / "Salida" / "casen_procesado.csv", sep=";", low_memory=False,
                    usecols=["e6a", "carrera_normalizada", "activ", "titulo_comun", "expr", "edad", "sexo", "varunit"])
    p5 = pd.read_csv(DIR_PUENTES / "P5_puente_carrera_casen.csv", sep=";")[["e6a", "carrera_normalizada", "carrera_generica", "nivel_titulo", "area_cine_sies", "estado"]]
    d = c.merge(p5, on=["e6a", "carrera_normalizada"], validate="many_to_one")
    return d[(d["activ"] == 1) & d["titulo_comun"].notna() & (d["estado"] == "asignado")].copy()


def cargar_ocupados() -> pd.DataFrame:
    return pd.read_csv(DIR_ANALISIS / "Archivo" / "CW_Ocupados_Carrera_Region_Actividad" / "Salida" / "ocupados_carrera_region_actividad.csv", sep=";")
