"""
<src/Scrapers/comun/tramos_edad.py>

Tramos de edad de todas las tablas por edad del mapa (Censo y ENE). Viven en un solo lugar para que las secciones se
puedan comparar entre sí: antes había tres esquemas (15-24 en Estudios y trabajo, 18-64 en Formalidad y 15-17 a 65 o
más en Trabajo por región), y un mismo tramo no significaba lo mismo en cada sección.

Decisión (13-11-26): todas las edades de 15 años o más, sin dejar a nadie fuera.
  - 15-17 aparte de 18-24: 18 es la edad para trabajar sin restricciones, y a los 15-17 nadie tiene título.
  - 65 o más en un solo tramo: la edad de jubilación. Dejarlos fuera sesgaba Formalidad (612.502 ocupados en la ENE,
    56,3% informales, frente a 26,6% en Chile), y no hace falta separarlos más.
Las comparaciones "a igual edad" eligen su propio subconjunto (TRAMOS_IGUAL_EDAD), donde todas sus cifras son fiables.
"""

TRAMOS_EDAD = {"15-17": (15, 17), "18-24": (18, 24), "25-34": (25, 34), "35-44": (35, 44), "45-54": (45, 54),
               "55-64": (55, 64), "65+": (65, 200)}
# De 25 a 64: donde las dos fuentes comparan por título con todas sus cifras fiables (en la ENE, 18-24 y 65 o más
# tienen independientes profesionales no fiables).
TRAMOS_IGUAL_EDAD = ["25-34", "35-44", "45-54", "55-64"]
