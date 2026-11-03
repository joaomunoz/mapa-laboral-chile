"""
<src/Analisis/Calculos_control/ocupados_region_actividad_categoria/esquema.py>
Actualizado 02-11-26 16:40

Single Source of Truth de la tabla de control ocupados_region_actividad_categoria.csv.

Grano: 1 fila por (codigo_region, actividad, categoria_ocupacion, nivel_titulo) con al menos un caso en la muestra.
No se elimina ninguna celda por tener pocos casos: queda con su fiabilidad, para que las regiones sumen
el total nacional. Una combinación ausente significa "sin casos en la muestra", no "cero personas".
Un caso en la muestra representa a muchas personas: ver n_personas frente a ocupados_10_meses.

actividad_caenes vacío = ocupado sin actividad informada (actividad_clave = sin_rama).
"""

OCUPADOS_REGION_ACTIVIDAD_CATEGORIA = {
    "codigo_region": "int64",
    "nombre_region": "object",
    "actividad_clave": "object",              # CAENES 1-21 como texto, o sin_rama
    "actividad_caenes": "Int64",
    "actividad_ciiu": "object",
    "actividad_glosa": "object",
    "categoria_ocupacion": "object",           # asalariado_privado, asalariado_publico, independiente u otros
    "nivel_titulo": "object",        # Sin_titulo, Tecnico o Profesional (incluye posgrado)
    "ocupados_10_meses": "float64",  # Promedio de un trimestre (10 meses × 3/10)
    "ocupados_jas": "float64",       # Trimestre julio-septiembre 2026 (Boletín INE n°336)
    "n_personas": "int64",           # idrph únicos en los 10 meses
    "gl": "int64",                   # Conglomerados - estratos de la celda
    "cv_pct": "float64",             # Coeficiente de variación de ocupados_10_meses
    "fiabilidad": "object",          # fiable, poco_fiable o no_fiable (n >= 60, gl >= 9, CV <= 30%)
}

CATEGORIA_POR_CODIGO = {1: "independiente", 2: "independiente", 3: "asalariado_privado", 4: "asalariado_publico",
                           5: "otros", 6: "otros", 7: "otros"}
