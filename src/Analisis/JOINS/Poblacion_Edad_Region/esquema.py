"""
<src/Analisis/JOINS/Poblacion_Edad_Region/esquema.py>

Single Source of Truth de poblacion_edad_region.csv: personas de 15 años o más por región de residencia y tramo de
edad, con su situación laboral (Censo 2024).

Grano: 1 fila por (codigo_region, tramo_edad). Son 136 filas: 16 regiones y Chile, × 8 tramos.
Para qué: comparar el % de ocupados y la participación entre regiones a igual edad, sin dejar a nadie fuera. Las
regiones con más jóvenes o más personas mayores tienen menos ocupados aunque en cada edad trabajen igual; con los
tramos se ajusta por edad (mezcla de edades de Chile) usando a todas las personas, incluidas las de 15 a 17 y las de
65 o más, que también trabajan (448.019 en Chile).
Tramo "65+": uno solo, aprobado por el usuario (13-11-26); partirlo en 65-74 y 75+ cambiaba el ajuste 0,21 puntos como
máximo. Tramo "Sin_edad": edad -66 en el Censo (125.651 en Chile); va como fila para que los tramos sumen exacto la
población de cada región, y el ajuste por edad no lo usa.
Chile: codigo_region vacío; es la suma de las regiones, no una medición aparte.
"""

POBLACION_EDAD_REGION = {
    "codigo_region": "Int64",            # Vacío en Chile
    "nombre_region": "object",
    "tramo_edad": "object",              # 15-17, 18-24, 25-34, 35-44, 45-54, 55-64, 65+ o Sin_edad
    "poblacion": "int64",                # Personas de 15 años o más, por residencia
    "ocupados": "int64",
    "desocupados": "int64",
    "fuera_fuerza": "int64",             # No trabajan ni buscan trabajo
    "sin_dato": "int64",                 # Sin situación laboral en el Censo
    "pct_ocupados": "float64",           # 100 × ocupados / poblacion
    "tasa_participacion": "float64",     # 100 × (ocupados + desocupados) / poblacion, como el mapa
}
