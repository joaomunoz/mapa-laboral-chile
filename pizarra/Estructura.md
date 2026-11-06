(Estructura.md Actualizada el 06-11-26)

# 📂 Estructura del Proyecto — Mapa Laboral de Chile

## 🌳 Esquema de Árbol

```text
.
├── .claude
│   └── settings.json
├── Datos
│   └── datos_externos
│       └── glosarios
│           ├── CASEN
│           │   ├── Libro_de_codigos_Casen_2024.md
│           │   ├── Libro_de_codigos_Casen_2024.xlsx
│           │   └── urls
│           ├── CENSO_2024
│           │   ├── diccionario_variables_censo2024.xlsx
│           │   └── manual_uso_microdatos_censo2024.md
│           ├── EMPLEABILIDAD
│           │   └── Metodologia-Buscador-Empleabilidad-e-Ingresos_2025-2026.md
│           ├── ENE
│           │   ├── codigos-ene-2020.md
│           │   └── urls
│           ├── script
│           │   └── xlsx_to_md.py
│           └── TITULADOS
│               ├── GLOSARIO_DE_TITULADO_2007_2025_E.md
│               └── url
├── docs
│   ├── index.html
│   ├── mapa.png
│   └── nota_de_lectura.md
├── src
│   ├── Analisis
│   │   ├── Calculos_control
│   │   │   └── ocupados_region_actividad
│   │   │       ├── Salida
│   │   │       │   ├── ocupados_region_actividad.csv
│   │   │       │   └── ocupados_region_actividad_inspeccion.txt
│   │   │       ├── crosswalk.py
│   │   │       ├── esquema.py
│   │   │       └── obtener.py
│   │   ├── JOINS
│   │   │   ├── Areas_Por_Actividad
│   │   │   │   ├── Salida
│   │   │   │   │   ├── areas_por_actividad.csv
│   │   │   │   │   └── areas_por_actividad_inspeccion.txt
│   │   │   │   ├── crosswalk.py
│   │   │   │   ├── esquema.py
│   │   │   │   └── obtener.py
│   │   │   ├── Carreras_Por_Actividad
│   │   │   │   ├── Salida
│   │   │   │   │   ├── carreras_por_actividad.csv
│   │   │   │   │   └── carreras_por_actividad_inspeccion.txt
│   │   │   │   ├── crosswalk.py
│   │   │   │   ├── esquema.py
│   │   │   │   └── obtener.py
│   │   │   ├── Concentracion_Region_Actividad
│   │   │   │   ├── Salida
│   │   │   │   │   ├── concentracion_region_actividad.csv
│   │   │   │   │   └── concentracion_region_actividad_inspeccion.txt
│   │   │   │   ├── crosswalk.py
│   │   │   │   ├── esquema.py
│   │   │   │   └── obtener.py
│   │   │   ├── Concentracion_Region_Actividad_Censo
│   │   │   │   ├── Salida
│   │   │   │   │   ├── concentracion_region_actividad_censo.csv
│   │   │   │   │   └── concentracion_region_actividad_censo_inspeccion.txt
│   │   │   │   ├── crosswalk.py
│   │   │   │   ├── esquema.py
│   │   │   │   └── obtener.py
│   │   │   └── Fuerza_Trabajo_Region_Nivel
│   │   │       ├── Salida
│   │   │       │   ├── fuerza_trabajo_region_nivel.csv
│   │   │       │   └── fuerza_trabajo_region_nivel_inspeccion.txt
│   │   │       ├── crosswalk.py
│   │   │       ├── esquema.py
│   │   │       └── obtener.py
│   │   ├── Puentes_de_mapeo
│   │   │   ├── Salida
│   │   │   │   ├── P1_puente_actividades.csv
│   │   │   │   ├── P1_puente_actividades_inspeccion.txt
│   │   │   │   ├── P5_puente_carrera_casen_cobertura.csv
│   │   │   │   ├── P5_puente_carrera_casen_cobertura_inspeccion.txt
│   │   │   │   ├── P5_puente_carrera_casen.csv
│   │   │   │   ├── P5_puente_carrera_casen_inspeccion.txt
│   │   │   │   ├── P6_control_no_asignados.csv
│   │   │   │   ├── P6_control_no_asignados_inspeccion.txt
│   │   │   │   ├── P9_perfil_laboral_carrera.csv
│   │   │   │   └── P9_perfil_laboral_carrera_inspeccion.txt
│   │   │   ├── esquema.py
│   │   │   ├── P1_puente_actividades.py
│   │   │   ├── P5_puente_carrera_casen.py
│   │   │   ├── P6_control_no_asignados.py
│   │   │   └── P9_perfil_laboral_carrera.py
│   │   └── diccionario_atributos_relaciones.md
│   ├── Scrapers
│   │   ├── CASEN
│   │   │   ├── Entrada
│   │   │   │   └── casen_2024.dta
│   │   │   ├── Salida
│   │   │   │   ├── casen_procesado.csv
│   │   │   │   └── casen_procesado_inspeccion.txt
│   │   │   ├── esquema.py
│   │   │   ├── obtener.py
│   │   │   └── procesar.py
│   │   ├── CENSO
│   │   │   ├── Entrada
│   │   │   │   ├── cartografia
│   │   │   │   │   └── Cartografia_censo2024_Pais_Regional.parquet
│   │   │   │   └── personas_censo2024.parquet
│   │   │   ├── Salida
│   │   │   │   ├── censo_por_sexo.csv
│   │   │   │   ├── censo_por_sexo_inspeccion.txt
│   │   │   │   ├── censo_procesado.csv
│   │   │   │   └── censo_procesado_inspeccion.txt
│   │   │   ├── esquema.py
│   │   │   ├── obtener_cartografia.py
│   │   │   ├── obtener.py
│   │   │   └── procesar.py
│   │   ├── comun
│   │   │   ├── inspect_data.py
│   │   │   └── normalizador.py
│   │   ├── Empleabilidad
│   │   │   ├── Entrada
│   │   │   │   ├── empleabilidad_inspeccion.txt
│   │   │   │   └── empleabilidad_mifuturo.csv
│   │   │   ├── Salida
│   │   │   │   ├── empleabilidad_procesado.csv
│   │   │   │   └── empleabilidad_procesado_inspeccion.txt
│   │   │   ├── esquema.py
│   │   │   ├── obtener.py
│   │   │   └── procesar.py
│   │   ├── ENE
│   │   │   ├── Entrada
│   │   │   │   └── 2026
│   │   │   │       ├── ene-2026-01-def.csv
│   │   │   │       ├── ene-2026-01-def_inspeccion.txt
│   │   │   │       ├── ene-2026-02-efm.csv
│   │   │   │       ├── ene-2026-02-efm_inspeccion.txt
│   │   │   │       ├── ene-2026-03-fma.csv
│   │   │   │       ├── ene-2026-03-fma_inspeccion.txt
│   │   │   │       ├── ene-2026-04-mam.csv
│   │   │   │       ├── ene-2026-04-mam_inspeccion.txt
│   │   │   │       ├── ene-2026-05-amj.csv
│   │   │   │       ├── ene-2026-05-amj_inspeccion.txt
│   │   │   │       ├── ene-2026-06-mjj.csv
│   │   │   │       ├── ene-2026-06-mjj_inspeccion.txt
│   │   │   │       ├── ene-2026-07-jja.csv
│   │   │   │       ├── ene-2026-07-jja_inspeccion.txt
│   │   │   │       ├── ene-2026-08-jas.csv
│   │   │   │       └── ene-2026-08-jas_inspeccion.txt
│   │   │   ├── Salida
│   │   │   │   ├── ene_procesado.csv
│   │   │   │   └── ene_procesado_inspeccion.txt
│   │   │   ├── esquema.py
│   │   │   ├── obtener.py
│   │   │   └── procesar.py
│   │   └── Titulados
│   │       ├── Entrada
│   │       │   ├── titulados_2007_2025.xlsx
│   │       │   └── titulados_inspeccion.txt
│   │       ├── Salida
│   │       │   ├── titulados_procesado.csv
│   │       │   └── titulados_procesado_inspeccion.txt
│   │       ├── obtener.py
│   │       └── procesar.py
│   └── Visualizacion
│       ├── generar_mapa.py
│       └── plantilla.html
├── .gitignore
└── README.md

50 directories, 117 files
```

## 📝 Descripción de Componentes

### Raíz

- **`README.md`**: Presentación del proyecto para portafolio: qué muestra, fuentes, validación, límites y cómo reproducirlo.
- **`.claude/settings.json`**: Configuración local de Claude Code; sin versionar.
- **`docs/`**: Resultado publicable, separado del código de `src/`; GitHub Pages puede servirlo tal cual.
- **`docs/index.html`**: El mapa final, autónomo. Lo escribe `src/Visualizacion/generar_mapa.py`.
- **`docs/nota_de_lectura.md`**: Qué mide cada dato, qué no dice y sus límites.
- **`docs/mapa.png`**: Captura de la parte superior de la vista inicial del mapa (resumen, modo claro), que se muestra en el README.
- **`.gitignore`**: Deja fuera `.venv/`, datos crudos y microdatos, que se regeneran.

### Datos

- **`Datos/datos_externos/glosarios/<FUENTE>/*`**: Libros de códigos, URLs y glosarios oficiales de cada fuente (ENE, TITULADOS, CASEN), en `.md` y, si existe, el `.xlsx` original.
- **`Datos/datos_externos/glosarios/EMPLEABILIDAD/Metodologia-Buscador-Empleabilidad-e-Ingresos_2025-2026.md`**: Metodología oficial del Buscador de Empleabilidad de MiFuturo, versión 2025-2026, la de nuestros datos (1,690 combinaciones): definición del indicador proxy, cohortes 2021-2023 e ingresos 2022-2024.
- **`Datos/datos_externos/glosarios/script/xlsx_to_md.py`**: Convierte los libros de códigos a Markdown legible.

- **`Datos/datos_externos/glosarios/CENSO_2024/`**: Manual de uso de microdatos (`.md`) y diccionario de variables (`.xlsx`) del Censo 2024.

### Fuente 1 — Titulados (SIES / MINEDUC)

- **`src/Scrapers/Titulados/obtener.py`**: Descarga desde `mifuturo.cl` a `Entrada/` solo la base histórica; la anual es idéntica a su último año y ya no se baja. Falla si no encuentra la histórica.
- **`src/Scrapers/Titulados/procesar.py`**: Limpia, normaliza y tipifica el histórico (42 → 29 columnas). Agrega `codigo_region` y estandariza `nombre_region`. Conserva `carrera_clasificacion_nivel_1`, `tipo_plan`, `modalidad` y los 7 rangos de edad al titularse. Documenta que SIES cuenta titulaciones, no personas.
- **`src/Scrapers/Titulados/Entrada/titulados_2007_2025.xlsx`**: Base histórica descargada de SIES (42 columnas).
- **`src/Scrapers/Titulados/Salida/titulados_procesado.csv`**: 234,074×29, salida de `procesar.py`.

### Fuente 2 — Empleabilidad e Ingresos (MiFuturo.cl)

- **`src/Scrapers/Empleabilidad/obtener.py`**: Descarga estadísticas de empleabilidad e ingresos por carrera.
- **`src/Scrapers/Empleabilidad/esquema.py`**: SSOT de tipos y columnas de `empleabilidad_procesado.csv`.
- **`src/Scrapers/Empleabilidad/procesar.py`**: Procesa `PORCENTAJE_EMPLEABILIDAD_ANIO_1` e `INGRESO_MEDIO_ANIO_1..5`.
- **`src/Scrapers/Empleabilidad/Entrada/empleabilidad_mifuturo.csv`**: Crudo de MiFuturo (1,690×30).
- **`src/Scrapers/Empleabilidad/Salida/empleabilidad_procesado.csv`**: 1,690×23, salida de `procesar.py`.

### Fuente 3 — ENE (Instituto Nacional de Estadísticas)

- **`src/Scrapers/ENE/obtener.py`**: Descarga los microdatos mensuales de la Encuesta Nacional de Empleo (cascada AJAX del INE) a `Entrada/2026/`.
- **`src/Scrapers/ENE/esquema.py`**: SSOT con `ESQUEMA_ENE` (30 columnas, incluye `termino_nivel` y `codigo_region_trabajo`), clave `(idrph, ano_encuesta, mes_encuesta)`, proyección de lectura, sentinelas y las 10 validaciones; documenta el panel rotativo, la escala trimestral de `fact_cal` y el significado real de `nivel` 7-9 (tipo de título, no institución).
- **`src/Scrapers/ENE/procesar.py`**: Unifica los 8 trimestres móviles (782,303 → 324,054 entrevistas únicas), aplica la política de peso "central", repara `fact_cal` (coma decimal), deriva `mes` y `nombre_region`, limpia sentinelas y valida contra el Boletín INE.
- **`src/Scrapers/ENE/Entrada/2026/ene-2026-*.csv`**: 8 trimestres móviles crudos del INE (01-def … 08-jas).
- **`src/Scrapers/ENE/Salida/ene_procesado.csv`**: Microdatos unificados (324,054×30).

### Fuente 4 — CASEN 2024 (Ministerio de Desarrollo Social y Familia)

- **`src/Scrapers/CASEN/obtener.py`**: Detecta el año vigente en la página oficial y descarga los microdatos Stata a `Entrada/`, con reanudación tras cortes.
- **`src/Scrapers/CASEN/esquema.py`**: SSOT de `casen_procesado.csv` (26 columnas), clave `(folio, id_persona)`, sentinelas y textos libres excluidos.
- **`src/Scrapers/CASEN/procesar.py`**: Filtra a educación superior, convierte `expr` a decimal, deriva `titulo_comun` y `carrera_normalizada`; 12 controles que detienen el proceso si fallan.
- **`src/Scrapers/CASEN/Entrada/casen_2024.dta`**: Crudo oficial (218,367 personas × 877 columnas, 1.6 GB).
- **`src/Scrapers/CASEN/Salida/casen_procesado.csv`**: 61,070×26, personas que asisten o asistieron a educación superior.

### Fuente 5 — Censo 2024 (INE)

- **`src/Scrapers/CENSO/obtener.py`**: Descarga a `Entrada/` el zip oficial en parquet y lo descomprime; no repite la descarga si ya existe.
- **`src/Scrapers/CENSO/obtener_cartografia.py`**: Descarga el zip oficial de cartografía (795 MB), extrae solo la capa regional a `Entrada/cartografia/` y borra el zip; no repite la descarga si la capa ya existe.
- **`src/Scrapers/CENSO/esquema.py`**: SSOT de `censo_procesado.csv` (8 columnas) y `censo_por_sexo.csv` (7 columnas).
- **`src/Scrapers/CENSO/procesar.py`**: Deriva región de trabajo, actividad y `nivel_titulo`, y agrega por combinación; escribe también la tabla por sexo; 16 controles (12 de la tabla principal y 4 por sexo). Requiere `.venv` (pyarrow).
- **`src/Scrapers/CENSO/Entrada/personas_censo2024.parquet`**: Microdatos oficiales de personas; `obtener.py` lo vuelve a descargar si falta.
- **`src/Scrapers/CENSO/Entrada/cartografia/Cartografia_censo2024_Pais_Regional.parquet`**: Límites oficiales de las 16 regiones.
- **`src/Scrapers/CENSO/Salida/censo_procesado.csv`**: 14,793×8, personas de 15 años o más agregadas; sumar `personas`, no contar filas.
- **`src/Scrapers/CENSO/Salida/censo_por_sexo.csv`**: 17,531×7, las mismas personas de 15 años o más abiertas por sexo (1 Hombre, 2 Mujer), con región de residencia y de trabajo, situación laboral, actividad y nivel de estudios; sumar `personas`, no contar filas. No incluye género. Va con su `_inspeccion.txt`.

### Compartido

- **`src/Scrapers/comun/normalizador.py`**: Normalización de texto y fuente única de regiones: `REGIONES` (código 1-16 → nombre), `codigo_region()`, que falla ante un nombre desconocido, y `regiones_incoherentes()`. Toda tabla con región expone `codigo_region` y `nombre_region`.
- **`src/Scrapers/comun/inspect_data.py`**: Auditoría rigurosa de datasets (CSV/Excel) con selección del diccionario de esquema por mayor solape de columnas; genera `<nombre>_inspeccion.txt` en la misma carpeta.
- **`**/*_inspeccion.txt`**: Reportes de auditoría generados por `inspect_data.py` junto a cada dataset (crudo o procesado).

### Análisis (referencia)

- **`src/Analisis/diccionario_atributos_relaciones.md`**: Atributos laborales y educacionales de las fuentes, con concepto, ejemplo y relaciones entre tablas.

### Análisis (puentes / crosswalk)

- **`src/Analisis/Puentes_de_mapeo/esquema.py`**: SSOT de los puentes P1, P5, P6 y P9.
- **`src/Analisis/Puentes_de_mapeo/P1_puente_actividades.py`** → **`Salida/P1_puente_actividades.csv`**: P1 — 21 filas, relación 1:1 CAENES (ENE, CASEN) ↔ sección CIIU (censo).

- **`src/Analisis/Puentes_de_mapeo/P5_puente_carrera_casen.py`** → **`Salida/P5_puente_carrera_casen.csv`**: P5 — 11,163 filas, texto `e7` de CASEN → `carrera_generica`, con método y estado; asigna 88,4% de las personas. Incluye `Salida/P5_puente_carrera_casen_cobertura.csv`.
- **`src/Analisis/Puentes_de_mapeo/P6_control_no_asignados.py`** → **`Salida/P6_control_no_asignados.csv`**: P6 — 61 filas, control de sesgo: compara a los ocupados con título que tienen carrera asignada con quienes no la tienen. También aporta a P9 las funciones de error y fiabilidad. La matriz carrera × actividad × ocupación se retiró porque ninguna tabla la leía.
- **`src/Analisis/Puentes_de_mapeo/P9_perfil_laboral_carrera.py`** → **`Salida/P9_perfil_laboral_carrera.csv`**: P9 — 7,288 filas, 259 carreras: categoría en la ocupación, actividad económica y ambas, con % en la carrera, % en el grupo, especialización, error y fiabilidad.

### Análisis (cálculos de control)

- **`src/Analisis/Calculos_control/<tabla>/`**: Cada cálculo tiene `obtener.py`, `esquema.py`, `crosswalk.py` y `Salida/`. Solo queda `ocupados_region_actividad`, que controla a `Concentracion_Region_Actividad`.

- **`src/Analisis/Calculos_control/ocupados_region_actividad/Salida/ocupados_region_actividad.csv`**: Todos los ocupados por región × CAENES y peso relativo de la actividad económica, en dos versiones (`base_region`: residencia o trabajo); `Concentracion_Region_Actividad` usa trabajo.

### Análisis (JOINS / tablas del mapa)

- **`src/Analisis/JOINS/Concentracion_Region_Actividad_Censo/`**: Capa principal del mapa. `Salida/concentracion_region_actividad_censo.csv`, 336×17: ocupados, peso relativo, lectura, contraste con ENE y alertas.
- **`src/Analisis/JOINS/Concentracion_Region_Actividad/`**: Misma medida con ENE, con rango y fiabilidad; sirve de contraste. `Salida/concentracion_region_actividad.csv`, 336×18.
- **`src/Analisis/JOINS/Areas_Por_Actividad/`**: Áreas CINE por actividad, nacional, con CASEN. `Salida/areas_por_actividad.csv`, 210×15.
- **`src/Analisis/JOINS/Carreras_Por_Actividad/`**: Carreras por actividad y afinidad, nacional, con datos de SIES y MiFuturo. `Salida/carreras_por_actividad.csv`, 2,162 filas, 189 carreras, 33 columnas, con títulos 2007-2025, títulos de 2025 por sexo y rango de empleabilidad entre instituciones (con 3 o más); incluye respaldo por instituciones y titulados que no trabajan, que el mapa ya no muestra.
- **`src/Analisis/JOINS/Fuerza_Trabajo_Region_Nivel/`**: Ocupados y desocupados por región y nivel educativo, con ENE como contraste. `Salida/fuerza_trabajo_region_nivel.csv`, 48×12.

### Visualización

- **`src/Visualizacion/generar_mapa.py`**: Lee las tablas y la cartografía, simplifica los bordes, calcula el resumen de todas las actividades, la situación de la población y la apertura por sexo en Chile, regiones, actividades y niveles, y escribe la página; 55 controles. Requiere `.venv` (geopandas y pyarrow).
- **`src/Visualizacion/plantilla.html`**: Diseño e interacción del mapa; recibe los datos al generar. Guarda cada vista en la dirección (`#actividad/región/carrera`), así que el botón "atrás" funciona y cada vista tiene enlace.
