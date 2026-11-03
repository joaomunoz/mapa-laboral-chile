"""
<src/Analisis/Calculos_control/titulados_ocupados_region_actividad/esquema.py>

Single Source of Truth de la tabla de control titulados_ocupados_region_actividad.csv:
cuántos titulados trabajan en cada actividad (CAENES) y región, por tipo de título.

Grano: 1 fila por (codigo_region, actividad_caenes, nivel_titulo) con al menos un caso en la muestra.
Una combinación ausente significa "sin casos en la muestra", no "cero personas".

Población: ocupados ENE (cae_especifico 1-7) con educación superior COMPLETA
(cine11_1d >= 3), de todas las edades, trimestre móvil julio-septiembre 2026.
- Se usa ese trimestre porque 3 meses consecutivos son el nivel poblacional de fact_cal y
  es el que se valida contra el Boletín INE n°336.
- Se usa cine11_1d y no nivel porque registra el nivel más alto completado.
- La región es la de RESIDENCIA del ocupado, no la del lugar de trabajo.

Fiabilidad: solo la primera barrera del estándar INE (n >= 60 personas y gl >= 9).
Falta el criterio de error estándar, que requiere estimar con el diseño muestral.
"""

TITULADOS_OCUPADOS_ESQUEMA = {
    "codigo_region": "int64",          # Código 1-16 (comun.normalizador.REGIONES)
    "nombre_region": "object",
    "actividad_caenes": "int64",                 # Rama CAENES 1-21 (Anexo 5 ENE)
    "actividad_ciiu": "object",          # Letra equivalente vía P1, para cruzar con ENADEL
    "actividad_glosa": "object",
    "nivel_titulo": "object",           # Tecnico (cine 3) | Profesional (cine 4) | Postgrado (cine 5-6)
    "titulados_ocupados": "int64",     # Personas expandidas (suma de fact_cal)
    "pct_en_region": "float64",        # % sobre los titulados ocupados de la región
    "pct_en_actividad": "float64",        # % sobre los titulados ocupados dla actividad a nivel nacional
    "n_personas": "int64",             # Personas distintas en la muestra
    "gl": "int64",                     # Conglomerados - estratos de la celda
    "fiable_n_gl": "bool",             # n_personas >= 60 y gl >= 9
}

# Mínimos de la primera barrera del estándar INE (libro de códigos ENE, sección 7.2).
N_MINIMO = 60
GL_MINIMO = 9

VALIDACIONES_TITULADOS_OCUPADOS = [
    ("1. Clave (codigo_region, actividad_caenes, nivel_titulo) única",
     lambda df: not df.duplicated(["codigo_region", "actividad_caenes", "nivel_titulo"]).any()),
    ("2. 16 regiones con un nombre por código",
     lambda df: df["codigo_region"].nunique() == 16 and df.groupby("codigo_region")["nombre_region"].nunique().eq(1).all()),
    ("3. actividad_caenes en 1..21 y con sección P1",
     lambda df: df["actividad_caenes"].between(1, 21).all() and df["actividad_ciiu"].notna().all()),
    ("4. Solo 3 tipos de título",
     lambda df: set(df["nivel_titulo"]) <= {"Tecnico", "Profesional", "Postgrado"}),
    ("5. Porcentajes de región suman 100 en cada región",
     lambda df: (df.groupby("codigo_region")["pct_en_region"].sum() - 100).abs().max() < 0.5),
    ("6. Porcentajes de actividad suman 100 en cada actividad",
     lambda df: (df.groupby("actividad_caenes")["pct_en_actividad"].sum() - 100).abs().max() < 0.5),
    ("7. Sin personas negativas ni celdas vacías",
     lambda df: (df["titulados_ocupados"] >= 0).all() and (df["n_personas"] >= 1).all()),
]
