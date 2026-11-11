"""
<src/Analisis/JOINS/Formalidad_Ocupados/esquema.py>

Single Source of Truth de formalidad_ocupados.csv: cómo trabajan los ocupados según la ENE de marzo a julio de 2026,
en dos ejes: tipo de trabajo (asalariado o independiente) y condición (formal o informal).

Grano: 1 fila por (ambito, codigo_region, nivel_titulo, tramo_edad, actividad_ciiu). Son 64 filas: Chile, Chile por
nivel de título (3), las 16 regiones, las 21 actividades, cada nivel por tramo de edad de 18 a 64 años (15), el
total de cada tramo (5: asalariados e independientes de los tres niveles, la suma de las filas por nivel) y lo que
queda fuera de esa tabla (3: 15-17 años, 65 o más y 18-64 sin nivel informado), para cuadrarla con Chile.
Los tramos (agregados el 11-11-26) responden si la diferencia por título es de edad: se comparan personas de la misma
edad, de 25 a 64. El tramo 18-24 (agregado el 11-11-26) se muestra para que la tabla cubra la edad de trabajar, pero
no entra en esa comparación: sus independientes con título no son fiables. Fuera quedan 15-17 (muy pocos) y 65 o más
(edad de jubilación; sí son ocupados y activos, pero trabajar ya es opcional).
Región: donde VIVE la persona, igual que la desocupación. Actividad: la rama del empleo (CAENES ↔ CIIU, puente P1).
"""

FORMALIDAD_OCUPADOS = {
    "ambito": "object",                     # chile, nivel, region, actividad, nivel_edad, edad o edad_fuera
    "codigo_region": "Int64",               # Solo en las filas de región
    "nivel_titulo": "object",               # Profesional, Tecnico o Sin_titulo; Sin_informar en edad_fuera 18-64; "Todos" en el resto
    "tramo_edad": "object",                 # 18-24 a 55-64 en nivel_edad y edad; 15-17, 65+ o 18-64 en edad_fuera; "Todos" en el resto
    "actividad_ciiu": "object",             # Letra A-U; solo en las filas de actividad
    "nombre": "object",                     # Chile, la región, el nivel o la actividad
    "ocupados": "int64",                    # Estimados, promedio trimestral (suma de 5 meses x 3/5)
    "n_ocupados": "int64",                  # Personas en la muestra (idrph únicos)
    "pct_asalariado_formal": "float64",     # Los cinco repartos suman 100
    "pct_asalariado_informal": "float64",
    "pct_independiente_formal": "float64",
    "pct_independiente_informal": "float64",
    "pct_familiar": "float64",              # Familiar no remunerado: siempre informal
    "tasa_informalidad": "float64",         # % de ocupados informales (ocup_form del INE)
    "cv_informalidad": "float64",
    "pct_independientes": "float64",        # Empleador o cuenta propia
    "cv_independientes": "float64",
    "cv_familiar": "float64",
    # Informalidad dentro de cada grupo (agregada el 11-11-26): la tarjeta compara independientes y asalariados por
    # título, y esa cifra necesita su propio error; dividir dos repartos no lo da.
    "pct_informal_independientes": "float64",   # % informal entre los independientes
    "cv_informal_independientes": "float64",
    "pct_informal_asalariados": "float64",      # % informal entre los asalariados
    "cv_informal_asalariados": "float64",               # Pocas personas: se mide para no mostrarla donde la muestra no alcanza
    # Una por cifra (decisión 08-11-26): con una sola, donde casi no hay independientes (Administración pública,
    # Hogares) la informalidad quedaba no fiable aunque su muestra la sostiene.
    "fiabilidad_informalidad": "object",    # fiable, poco_fiable o no_fiable
    "fiabilidad_independientes": "object",
    "fiabilidad_familiar": "object",        # Agregada el 08-11-26: en Profesional y Técnico hay menos de 60 personas
    "fiabilidad_informal_independientes": "object",
    "fiabilidad_informal_asalariados": "object",
}
