"""
<src/Analisis/JOINS/Formalidad_Ocupados/esquema.py>

Single Source of Truth de formalidad_ocupados.csv: cómo trabajan los ocupados según la ENE de marzo a julio de 2026,
en dos ejes: tipo de trabajo (asalariado o independiente) y condición (formal o informal).

Grano: 1 fila por (ambito, codigo_region, nivel_titulo, tramo_edad, actividad_ciiu). Son 68 filas: Chile, Chile por
nivel de título (3), las 16 regiones, las 21 actividades, cada nivel por tramo de edad (19: 3 niveles × 7 tramos, sin
Profesional ni Técnico de 15 a 17, donde nadie tiene título), el total de cada tramo (7: asalariados e independientes
de los tres niveles, la suma de las filas por nivel) y los sin nivel informado (1), para cuadrar la tabla con Chile.
Los tramos (agregados el 11-11-26) responden si la diferencia por título es de edad: se comparan personas de la misma
edad, de 25 a 64. Desde el 13-11-26 son los 7 de comun/tramos_edad.py, de 15-17 a 65 o más, los mismos de las otras
tablas por edad: de 18 a 64 quedaban fuera 612.502 ocupados de 65 o más, 56,3% informales. 15-17, 18-24 y 65 o más se
muestran, pero no entran en la comparación a igual edad: tienen cifras no fiables.
Región: donde VIVE la persona, igual que la desocupación. Actividad: la rama del empleo (CAENES ↔ CIIU, puente P1).
"""

FORMALIDAD_OCUPADOS = {
    "ambito": "object",                     # chile, nivel, region, actividad, nivel_edad, edad o sin_nivel
    "codigo_region": "Int64",               # Solo en las filas de región
    "nivel_titulo": "object",               # Profesional, Tecnico o Sin_titulo; Sin_informar en sin_nivel; "Todos" en el resto
    "tramo_edad": "object",                 # 15-17 a 65+ en nivel_edad y edad (comun/tramos_edad.py); "Todos" en el resto
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
