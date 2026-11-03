"""
<src/Analisis/Calculos_control/conteo_instituciones_empleabilidad_titulados/crosswalk.py>
Actualizado 02-11-26 18:01

Compara, por carrera_generica, cuántas instituciones tiene cada fuente.

Salida: Salida/conteo_instituciones_empleabilidad_titulados.csv

Es una tabla de control: confirma que carrera_generica sirve de llave entre las dos fuentes y muestra
qué parte de Titulados publica MiFuturo. Los conteos no deben ser iguales: MiFuturo solo publica
combinaciones que alcanzan sus mínimos de casos (metodología 2025-2026).
"""

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import obtener
from esquema import CONTEO_INSTITUCIONES

log = logging.getLogger(__name__)
RUTA = Path(__file__).parent / "Salida" / "conteo_instituciones_empleabilidad_titulados.csv"
CLASES_QUE_COMPITEN = ["Técnico de Nivel Superior", "Profesional Con Licenciatura", "Profesional Sin Licenciatura"]
COHORTES = (2021, 2023)


def construir(tit: pd.DataFrame, emp: pd.DataFrame) -> pd.DataFrame:
    compite = tit[tit["carrera_clasificacion_nivel_1"].isin(CLASES_QUE_COMPITEN)]
    cohortes = compite[compite["anio"].between(*COHORTES)]
    todas = tit[tit["anio"].between(*COHORTES)]
    ids = lambda d: d.groupby("carrera_generica")["codigo_institucion"].agg(set)
    en_emp, en_coh = emp.groupby("carrera_generica")["id_institucion"].agg(set), ids(cohortes)
    filas = []
    for carrera, publicadas in en_emp.items():
        tit_coh = en_coh.get(carrera, set())
        x = cohortes[cohortes["carrera_generica"] == carrera]
        total = x["total_titulaciones"].sum()
        cubiertos = x.loc[x["codigo_institucion"].isin(publicadas), "total_titulaciones"].sum()
        filas.append({
            "carrera_generica": carrera, "instituciones_empleabilidad": int((emp["carrera_generica"] == carrera).sum()),
            "instituciones_titulados_2021_2023": len(tit_coh),
            "instituciones_titulados_todos": compite.loc[compite["carrera_generica"] == carrera, "codigo_institucion"].nunique(),
            "instituciones_todas_clases_2021_2023": todas.loc[todas["carrera_generica"] == carrera, "codigo_institucion"].nunique(),
            "filas_titulados": int((compite["carrera_generica"] == carrera).sum()),
            "diferencia_2021_2023": len(tit_coh) - len(publicadas), "solo_en_titulados": len(tit_coh - publicadas),
            "solo_en_empleabilidad": len(publicadas - tit_coh), "titulos_2021_2023": total,
            "pct_titulos_en_empleabilidad": 100 * cubiertos / total if total else np.nan,
        })
    return pd.DataFrame(filas)[list(CONTEO_INSTITUCIONES)].astype(CONTEO_INSTITUCIONES).sort_values("carrera_generica")


def validar(t: pd.DataFrame, tit: pd.DataFrame, emp: pd.DataFrame) -> None:
    """Detiene el proceso si la tabla no reproduce los conteos de las fuentes."""
    medicina = t.loc[t["carrera_generica"].str.upper() == "MEDICINA"].iloc[0]
    controles = {
        "Clave única": t["carrera_generica"].is_unique,
        "190 carreras genéricas": len(t) == 190,
        "Empleabilidad suma 1.690 filas": t["instituciones_empleabilidad"].sum() == len(emp) == 1690,
        "Toda carrera de Empleabilidad existe en Titulados": t["carrera_generica"].isin(tit["carrera_generica"]).all(),
        "Sin institución repetida en una carrera de Empleabilidad": not emp.duplicated().any(),
        "Medicina reproduce 22, 24 y 26": (medicina["instituciones_empleabilidad"], medicina["instituciones_titulados_2021_2023"], medicina["instituciones_titulados_todos"]) == (22, 24, 26),
        "Totales reproducen 3.065 y 4.543": t["instituciones_titulados_2021_2023"].sum() == 3065 and t["instituciones_titulados_todos"].sum() == 4543,
        "Diferencia = solo en Titulados - solo en Empleabilidad": (t["diferencia_2021_2023"] == t["solo_en_titulados"] - t["solo_en_empleabilidad"]).all(),
    }
    for nombre, ok in controles.items():
        log.info("  [%s] %s", "✓" if ok else "✗", nombre)
    if not all(controles.values()):
        raise ValueError("Validaciones fallidas")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    tit, emp = obtener.cargar()
    tabla = construir(tit, emp)
    validar(tabla, tit, emp)
    RUTA.parent.mkdir(exist_ok=True)
    tabla.to_csv(RUTA, sep=";", index=False, encoding="utf-8")
    log.info("CSV generado: %s (%d filas)", RUTA.name, len(tabla))
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Scrapers" / "comun"))
    from inspect_data import inspeccion_rigurosa  # noqa: E402
    inspeccion_rigurosa(RUTA)
