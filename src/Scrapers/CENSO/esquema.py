"""
<src/Scrapers/CENSO/esquema.py>
Actualizado 03-11-26 03:00

Definición del esquema del Censo 2024 — Single Source of Truth.

Salida: Salida/censo_procesado.csv
Grano: 1 fila por combinación de las columnas de abajo, con su cantidad en personas.
Universo: personas de 15 años o más (15.205.784).

Por qué agregado (decisión 02-11-26): el censo no usa factores de expansión, así que sumar a quienes
comparten características no cambia ningún total. Pasa de 15,2 millones de filas a unas 15 mil, y el CSV se
abre en cualquier programa. Para otra variable, se regenera desde el parquet de Entrada/.

Lectura: una fila no es una persona. Siempre sumar la columna personas, nunca contar filas.
Las columnas vacías son información: por ejemplo, sin región de trabajo o sin actividad codificada.

Región: codigo_region es donde VIVE; codigo_region_trabajo es donde TRABAJA.
Escala: cine11 no se conserva porque no usa la escala de cine11_1d de ENE (3 es primaria parcial, no técnico).
"""

from __future__ import annotations

ESQUEMA_CENSO: dict[str, str] = {
    "codigo_region": "int64",          # region del crudo, 1-16
    "nombre_region": "object",         # DERIVADA: comun.normalizador.REGIONES
    "codigo_region_trabajo": "Int64",  # DERIVADA de p44; vacía si no hay una región de trabajo en Chile
    "sit_fuerza_trabajo": "Int64",     # 1 Ocupado, 2 Desocupado, 3 Fuera de la fuerza de trabajo; vacía sin respuesta
    "actividad_ciiu": "object",        # Sección A-U (cod_caenes); vacía si no es codificable o no aplica
    "nivel_titulo": "object",          # DERIVADA de cine11: Tecnico, Profesional o Sin_titulo; vacía sin respuesta
    "p44_lug_trab": "Int64",           # 1-2 en su comuna, 3 otra comuna, 4 otro país, 5 varias; vacía sin respuesta o si no aplica
    "personas": "int64",
}
