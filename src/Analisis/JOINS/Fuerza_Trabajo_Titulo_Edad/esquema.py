"""
<src/Analisis/JOINS/Fuerza_Trabajo_Titulo_Edad/esquema.py>

Single Source of Truth de fuerza_trabajo_titulo_edad.csv: desocupación con y sin título técnico o profesional, por
región y tramo de edad (Censo 2024, región de residencia).

Grano: 1 fila por (codigo_region, con_titulo, tramo_edad). Son 272 filas: 16 regiones y Chile, × 2 grupos × 8 tramos (los 7 de comun/tramos_edad.py y Sin_edad).
Para qué: comprobar si la menor desocupación con título se mantiene entre personas de la misma edad. Sin la edad,
podría deberse a que los sin título son más jóvenes, y los jóvenes tienen más desocupación.
Tramo "Sin_edad": activos con la edad sin dato en el Censo (código -66, 68.783 en Chile; 20% en Aysén). Va como fila
para que los tramos sumen exacto la tabla por región y nivel; las comparaciones por edad no la usan.
Chile: codigo_region vacío; es la suma de las regiones, no una medición aparte.
"""

FUERZA_TRABAJO_TITULO_EDAD = {
    "codigo_region": "Int64",       # Vacío en Chile
    "nombre_region": "object",
    "con_titulo": "bool",           # Técnico o profesional, frente a sin título superior
    "tramo_edad": "object",         # 15-17, 18-24, 25-34, 35-44, 45-54, 55-64, 65+ o Sin_edad (15-24 hasta el 13-11-26)
    "ocupados": "int64",            # Por residencia
    "desocupados": "int64",
    "tasa_desocupacion": "float64",  # 100 × desocupados / (ocupados + desocupados)
}
