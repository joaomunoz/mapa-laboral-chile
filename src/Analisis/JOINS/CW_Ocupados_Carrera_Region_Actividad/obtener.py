"""
<src/Analisis/JOINS/CW_Ocupados_Carrera_Region_Actividad/obtener.py>
Actualizado 02-11-26 16:40

Carga las entradas del reparto: stock de SIES por sede, ocupados de ENE con educación superior
completa (julio-septiembre 2026), el perfil de P7 y las secciones de P1.
"""

from pathlib import Path

import pandas as pd

DIR_ANALISIS = Path(__file__).resolve().parents[2]
DIR_SCRAPERS = DIR_ANALISIS.parent / "Scrapers"
DIR_PUENTES = DIR_ANALISIS / "Puentes_de_mapeo"

MESES_JAS = ["2026-07", "2026-08", "2026-09"]
CLASES_QUE_COMPITEN = ["Técnico de Nivel Superior", "Profesional Con Licenciatura", "Profesional Sin Licenciatura"]
# CASEN clasifica a magíster y doctorado por su pregrado, así que ENE debe agruparlos igual.
NIVEL_POR_CINE = {3: "Tecnico", 4: "Profesional", 5: "Profesional", 6: "Profesional"}


def cargar_stock() -> pd.DataFrame:
    """Títulos que compiten por región de sede y carrera genérica."""
    tit = pd.read_csv(DIR_SCRAPERS / "Titulados" / "Salida" / "titulados_procesado.csv", sep=";", low_memory=False,
                      usecols=["codigo_region", "carrera_generica", "carrera_clasificacion_nivel_1", "total_titulaciones"])
    tit = tit[tit["carrera_clasificacion_nivel_1"].isin(CLASES_QUE_COMPITEN)]
    return (tit.groupby(["codigo_region", "carrera_generica"], as_index=False)["total_titulaciones"].sum()
            .rename(columns={"total_titulaciones": "stock_sies"}))


def cargar_ene() -> pd.DataFrame:
    """Ocupados con educación superior completa, con actividad y gran grupo disponibles."""
    ene = pd.read_csv(DIR_SCRAPERS / "ENE" / "Salida" / "ene_procesado.csv", sep=";", low_memory=False,
                      usecols=["idrph", "mes", "codigo_region", "codigo_region_trabajo", "fact_cal", "cae_especifico", "cine11_1d",
                               "r_p_rev4cl_caenes", "b1", "estrato", "conglomerado"])
    o = ene[ene["mes"].isin(MESES_JAS) & ene["cae_especifico"].between(1, 7) & ene["cine11_1d"].ge(3)].copy()
    o["nivel_titulo"] = o["cine11_1d"].astype(int).map(NIVEL_POR_CINE)
    # La tabla ubica a cada persona donde está su empleo; sin ese dato (0,07%), donde vive.
    o["codigo_region"] = o["codigo_region_trabajo"].fillna(o["codigo_region"]).astype(int)
    return o.rename(columns={"r_p_rev4cl_caenes": "actividad_caenes"})


def cargar_perfil() -> pd.DataFrame:
    return pd.read_csv(DIR_PUENTES / "Salida" / "P7_perfil_carrera_actividad_ocupacion.csv", sep=";")


def cargar_actividades() -> pd.DataFrame:
    return pd.read_csv(DIR_PUENTES / "Salida" / "P1_puente_actividades.csv", sep=";")[["actividad_caenes", "actividad_ciiu", "actividad_glosa"]]
