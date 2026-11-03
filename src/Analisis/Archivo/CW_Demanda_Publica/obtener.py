"""
<src/Analisis/Archivo/CW_Demanda_Publica/obtener.py>

Carga ENE con su panel, las vacantes privadas del Paso 4, CASEN con P5 y la tabla de ocupados.
"""

from pathlib import Path

import numpy as np
import pandas as pd

DIR_JOINS = Path(__file__).resolve().parents[1]
DIR_ANALISIS = DIR_JOINS.parent
DIR_SCRAPERS = DIR_ANALISIS.parent / "Scrapers"
DIR_PUENTES = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida"


def cargar_ene() -> pd.DataFrame:
    e = pd.read_csv(DIR_SCRAPERS / "ENE" / "Salida" / "ene_procesado.csv", sep=";", low_memory=False,
                    usecols=["idrph", "mes", "codigo_region", "codigo_region_trabajo", "fact_cal", "cae_especifico", "cine11_1d",
                             "categoria_ocupacion", "r_p_rev4cl_caenes", "estrato", "conglomerado"])
    ocupado = e["cae_especifico"].between(1, 7)
    e["estado"] = np.select([ocupado & (e["categoria_ocupacion"] == 4), ocupado & (e["categoria_ocupacion"] == 3)], ["publico", "privado"], "otro")
    e["nivel_titulo"] = np.select([e["cine11_1d"] == 3, e["cine11_1d"] >= 4], ["Tecnico", "Profesional"], default=None)
    e["periodo"] = pd.PeriodIndex(e["mes"], freq="M").astype("int64")
    return e


def cargar_vacantes_privadas() -> pd.Series:
    v = pd.read_csv(DIR_JOINS / "CW_Demanda_Empresarial" / "Salida" / "vacantes_carrera_region.csv", sep=";")
    return v.groupby("nivel_titulo")["vacantes_estimadas"].sum()


def cargar_casen_publico() -> pd.DataFrame:
    """Asalariados públicos con título y carrera asignada (o15: gobierno y empresas públicas)."""
    c = pd.read_csv(DIR_SCRAPERS / "CASEN" / "Salida" / "casen_procesado.csv", sep=";", low_memory=False,
                    usecols=["e6a", "carrera_normalizada", "activ", "titulo_comun", "expr", "o15", "rama1", "varunit"])
    p5 = pd.read_csv(DIR_PUENTES / "P5_puente_carrera_casen.csv", sep=";")[["e6a", "carrera_normalizada", "carrera_generica", "nivel_titulo", "estado"]]
    d = c.merge(p5, on=["e6a", "carrera_normalizada"], validate="many_to_one")
    return d[(d["activ"] == 1) & d["titulo_comun"].notna() & (d["estado"] == "asignado") & d["o15"].isin([3, 4]) & d["rama1"].notna()]


def cargar_ocupados() -> pd.DataFrame:
    return pd.read_csv(DIR_JOINS / "CW_Ocupados_Carrera_Region_Actividad" / "Salida" / "ocupados_carrera_region_actividad.csv", sep=";")
