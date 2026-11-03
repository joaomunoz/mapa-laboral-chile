"""
<src/Analisis/Archivo/CW_Demanda_Empresarial/obtener.py>

Carga las entradas del Paso 4: ENADEL, ocupados por carrera, región y actividad, pesos regionales,
P1 y P7. CASEN se usa solo para informar qué parte de cada carrera trabaja en el sector privado.
"""

from pathlib import Path

import pandas as pd

DIR_ANALISIS = Path(__file__).resolve().parents[2]
DIR_SCRAPERS = DIR_ANALISIS.parent / "Scrapers"
DIR_PUENTES = DIR_ANALISIS / "Puentes_de_mapeo" / "Salida"


def cargar_empresas() -> pd.DataFrame:
    # ENADEL conserva su nombre de origen; desde aquí se usa el nombre normalizado.
    return pd.read_csv(DIR_SCRAPERS / "ENADEL" / "Salida" / "enadel_empresas_procesado.csv", sep=";", low_memory=False,
                       usecols=["idempresa_ficticio", "varunit", "varstrat", "pond_final", "codigo_region", "nombre_region",
                                "ciiu_seccion", "vacantes_actuales", "vacantes_futuras_2025"]).rename(columns={"ciiu_seccion": "actividad_ciiu"})


def cargar_cargos() -> pd.DataFrame:
    return pd.read_csv(DIR_SCRAPERS / "ENADEL" / "Salida" / "enadel_cargos_procesado.csv", sep=";", low_memory=False,
                       usecols=["idempresa_ficticio", "pond_final", "origen_bloque", "nivel_educacional", "cantidad_contratada", "ciuo_nivel_1"])


def cargar_ocupados() -> pd.DataFrame:
    return pd.read_csv(DIR_ANALISIS / "Archivo" / "CW_Ocupados_Carrera_Region_Actividad" / "Salida" / "ocupados_carrera_region_actividad.csv", sep=";")


def cargar_pesos() -> pd.DataFrame:
    p = pd.read_csv(DIR_ANALISIS / "Calculos_control" / "ocupados_region_actividad" / "Salida" / "ocupados_region_actividad.csv", sep=";")
    return p[p["base_region"] == "trabajo"]


def cargar_perfil() -> pd.DataFrame:
    return pd.read_csv(DIR_PUENTES / "P7_perfil_carrera_actividad_ocupacion.csv", sep=";")


def cargar_casen() -> pd.DataFrame:
    casen = pd.read_csv(DIR_SCRAPERS / "CASEN" / "Salida" / "casen_procesado.csv", sep=";", low_memory=False,
                        usecols=["e6a", "carrera_normalizada", "activ", "titulo_comun", "expr", "o15"])
    p5 = pd.read_csv(DIR_PUENTES / "P5_puente_carrera_casen.csv", sep=";")[["e6a", "carrera_normalizada", "carrera_generica", "estado"]]
    d = casen.merge(p5, on=["e6a", "carrera_normalizada"], validate="many_to_one")
    return d[(d["activ"] == 1) & d["titulo_comun"].notna() & (d["estado"] == "asignado")]
