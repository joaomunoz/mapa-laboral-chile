"""
<src/Analisis/JOINS/Fuerza_Trabajo_Titulo_Edad/obtener.py>

Carga los microdatos de personas del Censo 2024 con la edad, que el censo procesado no trae, y la tabla de situación
laboral por región y nivel, contra la que se cuadra.

Por qué los microdatos: censo_procesado.csv agrega por región, actividad y nivel sin la edad. Agregar la edad ahí
multiplicaría sus filas para todas las tablas que lo leen; esta tabla es la única que la necesita.
"""

import importlib.util
import sys
from pathlib import Path

import pandas as pd

DIR_SCRAPERS = Path(__file__).resolve().parents[3] / "Scrapers"
DIR_CENSO = DIR_SCRAPERS / "CENSO"
# Lo descarga src/Scrapers/CENSO/obtener.py.
RUTA_PERSONAS = DIR_CENSO / "Entrada" / "personas_censo2024.parquet"
RUTA_NIVELES = Path(__file__).resolve().parents[1] / "Fuerza_Trabajo_Region_Nivel" / "Salida" / "fuerza_trabajo_region_nivel.csv"


def _modulo(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _procesar_censo():
    """CENSO/procesar.py cargado por su ruta, para usar la misma preparación de personas sin copiarla.

    Hace `from esquema import ...` e `import obtener`, que chocan de nombre con los módulos de esta tabla. Mientras se
    carga, esos dos nombres apuntan a los del Censo, y después se devuelven los que hubiera, igual que sys.path: así
    funciona en cualquier orden de imports y no deja módulos ni rutas cambiados.
    """
    # procesar.py agrega sus carpetas a sys.path al cargarse (y aquí se agrega Scrapers por comun.normalizador): se
    # guarda la lista completa y se devuelve igual, para que esas carpetas no tapen los módulos de esta tabla.
    ruta_previa = list(sys.path)
    sys.path.append(str(DIR_SCRAPERS))
    previos = {n: sys.modules.get(n) for n in ("esquema", "obtener")}
    try:
        for n in previos:
            sys.modules[n] = _modulo(n, DIR_CENSO / f"{n}.py")
        return _modulo("censo_procesar", DIR_CENSO / "procesar.py")
    finally:
        for n, m in previos.items():
            if m is None:
                sys.modules.pop(n, None)
            else:
                sys.modules[n] = m
        sys.path[:] = ruta_previa


def cargar_personas() -> pd.DataFrame:
    """Personas de 15 años o más con la misma preparación que el censo procesado, más la edad."""
    censo = _procesar_censo()
    crudo = pd.read_parquet(RUTA_PERSONAS, columns=censo.COLUMNAS_ENTRADA + ["edad"])
    return censo.preparar(crudo)


def cargar_niveles() -> pd.DataFrame:
    return pd.read_csv(RUTA_NIVELES, sep=";")
