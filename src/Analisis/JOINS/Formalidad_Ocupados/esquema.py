"""
<src/Analisis/JOINS/Formalidad_Ocupados/esquema.py>

Single Source of Truth de formalidad_ocupados.csv: cómo trabajan los ocupados según la ENE de marzo a julio de 2026,
en dos ejes: tipo de trabajo (asalariado o independiente) y condición (formal o informal).

Grano: 1 fila por (ambito, codigo_region, nivel_titulo, actividad_ciiu). Son 41 filas: Chile, Chile por nivel de
título (3), las 16 regiones y las 21 actividades.
Región: donde VIVE la persona, igual que la desocupación. Actividad: la rama del empleo (CAENES ↔ CIIU, puente P1).
"""

FORMALIDAD_OCUPADOS = {
    "ambito": "object",                     # chile, nivel, region o actividad
    "codigo_region": "Int64",               # Solo en las filas de región
    "nivel_titulo": "object",               # Profesional, Tecnico o Sin_titulo; "Todos" en el resto
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
    "cv_familiar": "float64",               # Pocas personas: se mide para no mostrarla donde la muestra no alcanza
    # Una por cifra (decisión 08-11-26): con una sola, donde casi no hay independientes (Administración pública,
    # Hogares) la informalidad quedaba no fiable aunque su muestra la sostiene.
    "fiabilidad_informalidad": "object",    # fiable, poco_fiable o no_fiable
    "fiabilidad_independientes": "object",
    "fiabilidad_familiar": "object",        # Agregada el 08-11-26: en Profesional y Técnico hay menos de 60 personas
}
