"""
<src/Analisis/Calculos_control/cobertura_enadel_ene_region_actividad/esquema.py>
Actualizado 02-11-26 16:40

Single Source of Truth de la tabla de control cobertura_enadel_ene_region_actividad.csv:
compara la dotación de ENADEL con los asalariados privados de la ENE, para saber en qué
regiones y actividades ENADEL representa bien al mercado privado.

Grano: 1 fila por (codigo_region, actividad_caenes). La grilla es completa (16 × 21 = 336 filas) para
que las actividades que ENADEL no encuesta queden visibles en vez de desaparecer.

razon_cobertura = dotacion_enadel / asalariados_privados_ene. Una razón cercana a 1 indica
tamaños parecidos; no es un error de cobertura puro, porque las fuentes difieren:
- Fecha: ENADEL al 31-may-2025; ENE julio-septiembre 2026.
- Región: ENADEL ubica la empresa y la ENE la residencia del trabajador.
- Unidad: la dotación de ENADEL incluye honorarios y aprendices, y exige un tamaño mínimo de
  dotación que su libro de códigos no especifica.

Concentración: el factor de expansión hace que pocas empresas pesen mucho (una empresa de
13,625 trabajadores con pond_final 16 representa 58% de La Araucanía). Por eso una celda con
muestra suficiente también puede no ser comparable. pct_top1_empresa mide ese riesgo.
"""

COBERTURA_ESQUEMA = {
    "codigo_region": "int64",
    "nombre_region": "object",
    "actividad_caenes": "int64",                     # Rama CAENES 1-21
    "actividad_ciiu": "object",              # Letra equivalente vía P1
    "actividad_glosa": "object",
    "actividad_en_enadel": "bool",            # False en secciones que ENADEL no encuesta
    "dotacion_enadel": "Int64",            # Trabajadores expandidos; NA si ENADEL no encuesta la actividad
    "n_empresas_enadel": "Int64",          # Empresas en la muestra
    "pct_top1_empresa": "float64",         # % de la dotación expandida que aporta su mayor empresa
    "asalariados_privados_ene": "int64",   # categoria_ocupacion = 3, personas expandidas
    "n_personas_ene": "int64",             # Personas distintas en la muestra
    "gl_ene": "int64",                     # Conglomerados - estratos de la celda
    "razon_cobertura": "float64",          # NA si no se puede calcular
    "lectura": "object",                   # Ver LECTURAS
}

# Primera barrera del estándar INE para la ENE (n >= 60 y gl >= 9).
N_MINIMO_ENE = 60
GL_MINIMO_ENE = 9
# ENADEL no publica un mínimo equivalente: 30 empresas es un criterio de trabajo de este
# control, para no leer razones que dependen de muy pocas empresas.
N_MINIMO_EMPRESAS = 30
# Criterio de trabajo de este control, no un estándar oficial: sobre este valor, la razón
# de la celda depende en buena parte de una sola empresa.
PCT_TOP1_MAXIMO = 25.0

LECTURAS = ["comparable", "concentrada", "muestra_insuficiente", "actividad_fuera_de_enadel"]

VALIDACIONES_COBERTURA = [
    ("1. Grilla completa de 336 filas sin claves repetidas",
     lambda df: len(df) == 336 and not df.duplicated(["codigo_region", "actividad_caenes"]).any()),
    ("2. 16 regiones con un nombre por código",
     lambda df: df["codigo_region"].nunique() == 16 and df.groupby("codigo_region")["nombre_region"].nunique().eq(1).all()),
    ("3. 21 actividades con sección P1",
     lambda df: df["actividad_caenes"].nunique() == 21 and df["actividad_ciiu"].notna().all()),
    ("4. Dotación vacía solo en actividades fuera de ENADEL",
     lambda df: (df["dotacion_enadel"].isna() == ~df["actividad_en_enadel"]).all()),
    ("5. Razón no negativa cuando existe",
     lambda df: (df["razon_cobertura"].dropna() >= 0).all()),
    ("6. Lectura dentro del catálogo",
     lambda df: df["lectura"].isin(LECTURAS).all()),
    ("7. pct_top1_empresa entre 0 y 100 cuando existe",
     lambda df: df["pct_top1_empresa"].dropna().between(0, 100).all()),
    ("8. Ninguna celda comparable supera el umbral de concentración",
     lambda df: (df.loc[df["lectura"] == "comparable", "pct_top1_empresa"] <= PCT_TOP1_MAXIMO).all()),
]
