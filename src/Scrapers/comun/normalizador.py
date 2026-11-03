"""
<src/Scrapers/comun/normalizador.py>

Módulo común de configuración y normalización de datos para los scrapers.
Contiene funciones estándar para normalizar nombres de regiones, carreras, tildes,
espacios y formatos de fecha/año.

REGIONES es la fuente única de regiones del proyecto. Toda tabla con región expone las
mismas dos columnas: `codigo_region` (1-16) y `nombre_region`. El cruce entre tablas se
hace por código: en las fuentes el mismo nombre de columna significaba cosas distintas
(`region` era código en ENE y nombre en ENADEL) y SIES nombraba distinto a O'Higgins.
"""

import re
import unicodedata

# Código oficial (Anexo 1 del libro de códigos ENE) → nombre canónico.
REGIONES: dict[int, str] = {
    1: "TARAPACA", 2: "ANTOFAGASTA", 3: "ATACAMA", 4: "COQUIMBO", 5: "VALPARAISO",
    6: "O'HIGGINS", 7: "MAULE", 8: "BIOBIO", 9: "LA ARAUCANIA", 10: "LOS LAGOS",
    11: "AYSEN", 12: "MAGALLANES", 13: "METROPOLITANA", 14: "LOS RIOS",
    15: "ARICA Y PARINACOTA", 16: "NUBLE",
}
_CODIGO_POR_NOMBRE = {nombre: codigo for codigo, nombre in REGIONES.items()}

# Variantes observadas en las fuentes → nombre canónico.
_ALIAS_REGION = {"LIB. GRAL. B. O'HIGGINS": "O'HIGGINS"}  # SIES Titulados

def normalizar_texto(texto: str) -> str:
    """
    Limpia y normaliza cadenas de texto eliminando tildes, espacios excessivos
    y convirtiendo a mayúsculas para facilitar cruces (matching).
    """
    if not isinstance(texto, str):
        return ""
    # Eliminar acentos y diacríticos
    nfkd = unicodedata.normalize('NFKD', texto)
    sin_tildes = "".join([c for c in nfkd if not unicodedata.combining(c)])
    # Mayúsculas y limpieza de espacios
    return re.sub(r'\s+', ' ', sin_tildes).strip().upper()

def normalizar_region(nombre_region: str) -> str:
    """
    Normaliza los nombres de regiones de Chile para asegurar consistencia
    entre SIES, MiFuturo, ENE y ENADEL.
    """
    texto = normalizar_texto(nombre_region)
    return _ALIAS_REGION.get(texto, texto)


def codigo_region(nombre_region: str) -> int:
    """
    Devuelve el código 1-16 de una región. Falla ante un nombre desconocido: asignarle
    un valor por defecto o NA haría desaparecer esa región de los cruces sin aviso.
    """
    nombre = normalizar_region(nombre_region)
    if nombre not in _CODIGO_POR_NOMBRE:
        raise ValueError(f"Región no reconocida: {nombre_region!r}")
    return _CODIGO_POR_NOMBRE[nombre]


def regiones_incoherentes(codigos, nombres) -> int:
    """Cuenta las filas cuyo par (codigo_region, nombre_region) no coincide con REGIONES."""
    return sum(REGIONES.get(c) != n for c, n in zip(codigos, nombres))
