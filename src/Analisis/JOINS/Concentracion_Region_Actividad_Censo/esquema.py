"""
<src/Analisis/JOINS/Concentracion_Region_Actividad_Censo/esquema.py>
Actualizado 03-11-26 13:00

Single Source of Truth de concentracion_region_actividad_censo.csv: capa principal del mapa.

Grano: 1 fila por (codigo_region, actividad_caenes). Son 336 filas.
Región: donde está el TRABAJO. Población: ocupados con región de trabajo y actividad válidas.
peso_relativo: cuántas veces pesa la actividad en la región respecto del país.
No lleva rangos de error porque el censo no es una muestra; sí tiene no respuesta y datos sin codificar.
pct_poblacion_15_mas mezcla bases a propósito: ocupados donde trabajan, población donde vive. Puede subir en
regiones donde llega mucha gente de otras regiones a trabajar.
"""

CONCENTRACION_REGION_ACTIVIDAD_CENSO = {
    "codigo_region": "int64",
    "nombre_region": "object",
    "actividad_caenes": "int64",
    "actividad_ciiu": "object",
    "actividad_glosa": "object",
    "ocupados": "int64",
    "pct_en_region": "float64",
    "pct_nacional": "float64",
    "peso_relativo": "float64",
    "lectura": "object",                 # concentra, similar, bajo_lo_nacional o base_pequena
    "pct_poblacion_15_mas": "float64",
    "pct_sin_region_trabajo": "float64", # Dato nacional de la actividad
    "ene_ocupados": "float64",           # Contraste: tabla concentracion_region_actividad
    "ene_peso_relativo": "float64",
    "ene_lectura": "object",
    "alerta_difiere_fuente": "bool",
    "mostrar_en_mapa": "bool",           # False en U: se conserva en la tabla, pero no aparece en la lista del mapa
}
