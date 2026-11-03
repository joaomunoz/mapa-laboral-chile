(Estructura.md Actualizada el 03-11-26)

# 📂 Estructura del Proyecto — Mapa de Actividades y Carreras por Región (Chile)

## 🌳 Esquema de Árbol

```text
.
├── Datos
│   └── datos_externos
│       ├── ENADEL
│       │   ├── ENADEL_2025.csv
│       │   └── FORMATO-CSV-ENADEL.zip
│       ├── glosarios
│       │   ├── CASEN
│       │   │   ├── Libro_de_codigos_Casen_2024.md
│       │   │   ├── Libro_de_codigos_Casen_2024.xlsx
│       │   │   └── urls
│       │   ├── CENSO_2024
│       │   │   ├── diccionario_variables_censo2024.xlsx
│       │   │   └── manual_uso_microdatos_censo2024.md
│       │   ├── EMPLEABILIDAD
│       │   │   └── Metodologia-Buscador-Empleabilidad-e-Ingresos_2025-2026.md
│       │   ├── ENADEL
│       │   │   ├── Libro_de_codigos_ENADEL_2025.md
│       │   │   ├── Libro_de_codigos_ENADEL_2025.xlsx
│       │   │   └── urls
│       │   ├── ENE
│       │   │   ├── codigos-ene-2020.md
│       │   │   ├── codigos-ene-2020.pdf
│       │   │   └── urls
│       │   ├── script
│       │   │   └── xlsx_to_md.py
│       │   └── TITULADOS
│       │       ├── GLOSARIO_DE_TITULADO_2007_2025_E.md
│       │       ├── GLOSARIO_DE_TITULADO_2007_2025_E.pdf
│       │       └── url
│       ├── censo_proyecciones_ed_superior.csv
│       └── cut_comuna.csv
├── src
│   ├── Analisis
│   │   ├── Archivo
│   │   │   ├── CW_Competencia_Desocupados
│   │   │   │   ├── Salida
│   │   │   │   │   ├── desocupados_carrera_region.csv
│   │   │   │   │   ├── desocupados_carrera_region_inspeccion.txt
│   │   │   │   │   ├── desocupados_region_titulo.csv
│   │   │   │   │   ├── desocupados_region_titulo_inspeccion.txt
│   │   │   │   │   ├── desocupados_validacion.csv
│   │   │   │   │   └── desocupados_validacion_inspeccion.txt
│   │   │   │   ├── crosswalk.py
│   │   │   │   ├── esquema.py
│   │   │   │   └── obtener.py
│   │   │   ├── CW_Demanda_Empresarial
│   │   │   │   ├── Salida
│   │   │   │   │   ├── vacantes_carrera_region_actividad.csv
│   │   │   │   │   ├── vacantes_carrera_region_actividad_inspeccion.txt
│   │   │   │   │   ├── vacantes_carrera_region.csv
│   │   │   │   │   ├── vacantes_carrera_region_inspeccion.txt
│   │   │   │   │   ├── vacantes_region_actividad.csv
│   │   │   │   │   ├── vacantes_region_actividad_inspeccion.txt
│   │   │   │   │   ├── vacantes_validacion.csv
│   │   │   │   │   └── vacantes_validacion_inspeccion.txt
│   │   │   │   ├── crosswalk.py
│   │   │   │   ├── esquema.py
│   │   │   │   └── obtener.py
│   │   │   ├── CW_Demanda_Jubilacion
│   │   │   │   ├── Salida
│   │   │   │   │   ├── jubilacion_carrera_region.csv
│   │   │   │   │   ├── jubilacion_carrera_region_inspeccion.txt
│   │   │   │   │   ├── jubilacion_region_titulo.csv
│   │   │   │   │   ├── jubilacion_region_titulo_inspeccion.txt
│   │   │   │   │   ├── jubilacion_validacion.csv
│   │   │   │   │   └── jubilacion_validacion_inspeccion.txt
│   │   │   │   ├── crosswalk.py
│   │   │   │   ├── esquema.py
│   │   │   │   └── obtener.py
│   │   │   ├── CW_Demanda_Publica
│   │   │   │   ├── Salida
│   │   │   │   │   ├── vacantes_publicas_carrera_region.csv
│   │   │   │   │   ├── vacantes_publicas_carrera_region_inspeccion.txt
│   │   │   │   │   ├── vacantes_publicas_validacion.csv
│   │   │   │   │   └── vacantes_publicas_validacion_inspeccion.txt
│   │   │   │   ├── crosswalk.py
│   │   │   │   ├── esquema.py
│   │   │   │   └── obtener.py
│   │   │   ├── CW_Empleabilidad_Oferta_Titulados
│   │   │   │   ├── Salida
│   │   │   │   │   ├── oferta_empleabilidad_procesado.csv
│   │   │   │   │   └── oferta_empleabilidad_procesado_inspeccion.txt
│   │   │   │   ├── crosswalk.py
│   │   │   │   ├── esquema.py
│   │   │   │   └── obtener.py
│   │   │   ├── CW_Ocupados_Carrera_Region_Actividad
│   │   │   │   ├── Salida
│   │   │   │   │   ├── ocupados_carrera_region_actividad.csv
│   │   │   │   │   ├── ocupados_carrera_region_actividad_inspeccion.txt
│   │   │   │   │   ├── ocupados_carrera_region_actividad_validacion.csv
│   │   │   │   │   └── ocupados_carrera_region_actividad_validacion_inspeccion.txt
│   │   │   │   ├── crosswalk.py
│   │   │   │   ├── esquema.py
│   │   │   │   ├── obtener.py
│   │   │   │   └── validar_reparto.py
│   │   │   ├── Indice_Cupos
│   │   │   │   ├── Salida
│   │   │   │   │   ├── indice_cupos_carrera_nacional.csv
│   │   │   │   │   ├── indice_cupos_carrera_nacional_inspeccion.txt
│   │   │   │   │   ├── indice_cupos_carrera_region.csv
│   │   │   │   │   ├── indice_cupos_carrera_region_inspeccion.txt
│   │   │   │   │   ├── indice_cupos_validacion.csv
│   │   │   │   │   └── indice_cupos_validacion_inspeccion.txt
│   │   │   │   ├── crosswalk.py
│   │   │   │   ├── esquema.py
│   │   │   │   └── obtener.py
│   │   │   └── README.md
│   │   ├── Calculos_control
│   │   │   ├── cobertura_enadel_ene_region_actividad
│   │   │   │   ├── Salida
│   │   │   │   │   ├── cobertura_enadel_ene_region_actividad.csv
│   │   │   │   │   └── cobertura_enadel_ene_region_actividad_inspeccion.txt
│   │   │   │   ├── crosswalk.py
│   │   │   │   ├── esquema.py
│   │   │   │   └── obtener.py
│   │   │   ├── conteo_instituciones_empleabilidad_titulados
│   │   │   │   ├── Salida
│   │   │   │   │   ├── conteo_instituciones_empleabilidad_titulados.csv
│   │   │   │   │   └── conteo_instituciones_empleabilidad_titulados_inspeccion.txt
│   │   │   │   ├── crosswalk.py
│   │   │   │   ├── esquema.py
│   │   │   │   └── obtener.py
│   │   │   ├── ocupados_region_actividad
│   │   │   │   ├── Salida
│   │   │   │   │   ├── ocupados_region_actividad.csv
│   │   │   │   │   └── ocupados_region_actividad_inspeccion.txt
│   │   │   │   ├── crosswalk.py
│   │   │   │   ├── esquema.py
│   │   │   │   └── obtener.py
│   │   │   ├── ocupados_region_actividad_categoria
│   │   │   │   ├── Salida
│   │   │   │   │   ├── ocupados_region_actividad_categoria.csv
│   │   │   │   │   └── ocupados_region_actividad_categoria_inspeccion.txt
│   │   │   │   ├── crosswalk.py
│   │   │   │   ├── esquema.py
│   │   │   │   └── obtener.py
│   │   │   └── titulados_ocupados_region_actividad
│   │   │       ├── Salida
│   │   │       │   ├── titulados_ocupados_region_actividad.csv
│   │   │       │   └── titulados_ocupados_region_actividad_inspeccion.txt
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
│   │   │   ├── Concentracion_Region_Area
│   │   │   │   ├── Salida
│   │   │   │   │   ├── concentracion_region_area.csv
│   │   │   │   │   └── concentracion_region_area_inspeccion.txt
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
│   │   │   │   ├── P2_puente_llaves_carrera.csv
│   │   │   │   ├── P2_puente_llaves_carrera_inspeccion.txt
│   │   │   │   ├── P4_puente_niveles_educativos.csv
│   │   │   │   ├── P4_puente_niveles_educativos_inspeccion.txt
│   │   │   │   ├── P5_puente_carrera_casen_cobertura.csv
│   │   │   │   ├── P5_puente_carrera_casen_cobertura_inspeccion.txt
│   │   │   │   ├── P5_puente_carrera_casen.csv
│   │   │   │   ├── P5_puente_carrera_casen_inspeccion.txt
│   │   │   │   ├── P6_matriz_carrera_actividad_ocupacion.csv
│   │   │   │   ├── P6_matriz_carrera_actividad_ocupacion_inspeccion.txt
│   │   │   │   ├── P6_matriz_carrera_actividad_ocupacion_no_asignados.csv
│   │   │   │   ├── P6_matriz_carrera_actividad_ocupacion_no_asignados_inspeccion.txt
│   │   │   │   ├── P7_perfil_carrera_actividad_ocupacion.csv
│   │   │   │   ├── P7_perfil_carrera_actividad_ocupacion_inspeccion.txt
│   │   │   │   ├── P8_razon_empleo_carrera.csv
│   │   │   │   ├── P8_razon_empleo_carrera_inspeccion.txt
│   │   │   │   ├── P9_perfil_laboral_carrera.csv
│   │   │   │   └── P9_perfil_laboral_carrera_inspeccion.txt
│   │   │   ├── esquema.py
│   │   │   ├── P1_puente_actividades.py
│   │   │   ├── P2_puente_llaves_carrera.py
│   │   │   ├── P4_puente_niveles_educativos.py
│   │   │   ├── P5_puente_carrera_casen.py
│   │   │   ├── P6_matriz_carrera_actividad_ocupacion.py
│   │   │   ├── P7_perfil_carrera_actividad_ocupacion.py
│   │   │   ├── P8_razon_empleo_carrera.py
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
│   │   │   │   ├── hogares_censo2024.parquet
│   │   │   │   ├── personas_censo2024.parquet
│   │   │   │   ├── viv_hog_per_censo2024.zip
│   │   │   │   └── viviendas_censo2024.parquet
│   │   │   ├── Salida
│   │   │   │   ├── censo_procesado.csv
│   │   │   │   └── censo_procesado_inspeccion.txt
│   │   │   ├── esquema.py
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
│   │   ├── ENADEL
│   │   │   ├── Entrada
│   │   │   │   ├── ENADEL_2025.csv
│   │   │   │   ├── ENADEL_2025_inspeccion.txt
│   │   │   │   └── FORMATO-CSV-ENADEL.zip
│   │   │   ├── Salida
│   │   │   │   ├── enadel_cargos_procesado.csv
│   │   │   │   ├── enadel_cargos_procesado_inspeccion.txt
│   │   │   │   ├── enadel_empresas_procesado.csv
│   │   │   │   └── enadel_empresas_procesado_inspeccion.txt
│   │   │   ├── esquema.py
│   │   │   ├── obtener.py
│   │   │   └── procesar.py
│   │   ├── ENE
│   │   │   ├── Entrada
│   │   │   │   ├── 2026
│   │   │   │   │   ├── ene-2026-01-def.csv
│   │   │   │   │   ├── ene-2026-01-def_inspeccion.txt
│   │   │   │   │   ├── ene-2026-02-efm.csv
│   │   │   │   │   ├── ene-2026-02-efm_inspeccion.txt
│   │   │   │   │   ├── ene-2026-03-fma.csv
│   │   │   │   │   ├── ene-2026-03-fma_inspeccion.txt
│   │   │   │   │   ├── ene-2026-04-mam.csv
│   │   │   │   │   ├── ene-2026-04-mam_inspeccion.txt
│   │   │   │   │   ├── ene-2026-05-amj.csv
│   │   │   │   │   ├── ene-2026-05-amj_inspeccion.txt
│   │   │   │   │   ├── ene-2026-06-mjj.csv
│   │   │   │   │   ├── ene-2026-06-mjj_inspeccion.txt
│   │   │   │   │   ├── ene-2026-07-jja.csv
│   │   │   │   │   ├── ene-2026-07-jja_inspeccion.txt
│   │   │   │   │   ├── ene-2026-08-jas.csv
│   │   │   │   │   └── ene-2026-08-jas_inspeccion.txt
│   │   │   │   └── ano-2024.csv
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
│       └── Mapa_Actividades
│           ├── Salida
│           │   ├── index.html
│           │   └── nota_de_lectura.md
│           ├── generar_mapa.py
│           └── plantilla.html
└── .gitignore

80 directories, 232 files
```

## 📝 Descripción de Componentes

### Raíz

- **`.gitignore`**: Deja fuera `.venv/`, datos crudos, microdatos y tablas intermedias grandes, que se regeneran.

### Datos

- **`Datos/datos_externos/cut_comuna.csv`**: Códigos CUT de comunas de Chile, usado para estandarizar geografía.
- **`Datos/datos_externos/censo_proyecciones_ed_superior.csv`**: Proyecciones del Censo para educación superior.
- **`Datos/datos_externos/ENADEL/FORMATO-CSV-ENADEL.zip`**: Formato de datos de la Encuesta de Demanda Laboral.
- **`Datos/datos_externos/ENADEL/ENADEL_2025.csv`**: CSV extraído del ZIP anterior (copia de referencia).
- **`Datos/datos_externos/glosarios/<FUENTE>/*`**: Libros de códigos, URLs y glosarios oficiales de cada fuente (ENE, ENADEL, TITULADOS, CASEN), en original (`.pdf`/`.xlsx`) y su conversión a `.md`.
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

### Fuente 4 — ENADEL (SENCE / Ministerio del Trabajo)

- **`src/Scrapers/ENADEL/obtener.py`**: Descarga microdatos de la Encuesta de Demanda Laboral.
- **`src/Scrapers/ENADEL/esquema.py`**: SSOT de las tablas EMPRESAS y CARGOS.
- **`src/Scrapers/ENADEL/procesar.py`**: Procesa vacantes históricas y proyectadas por región y sector CIIU; despivota CIUO.
- **`src/Scrapers/ENADEL/Entrada/`**: `FORMATO-CSV-ENADEL.zip` (respaldo crudo) y `ENADEL_2025.csv` extraído.
- **`src/Scrapers/ENADEL/Salida/enadel_empresas_procesado.csv`, `enadel_cargos_procesado.csv`**: 5,576×29 y 32,390×17 (formato largo CIUO 4/2/1).

### Fuente 5 — CASEN 2024 (Ministerio de Desarrollo Social y Familia)

- **`src/Scrapers/CASEN/obtener.py`**: Detecta el año vigente en la página oficial y descarga los microdatos Stata a `Entrada/`, con reanudación tras cortes.
- **`src/Scrapers/CASEN/esquema.py`**: SSOT de `casen_procesado.csv` (26 columnas), clave `(folio, id_persona)`, sentinelas y textos libres excluidos.
- **`src/Scrapers/CASEN/procesar.py`**: Filtra a educación superior, convierte `expr` a decimal, deriva `titulo_comun` y `carrera_normalizada`; 12 controles que detienen el proceso si fallan.
- **`src/Scrapers/CASEN/Entrada/casen_2024.dta`**: Crudo oficial (218,367 personas × 877 columnas, 1.6 GB).
- **`src/Scrapers/CASEN/Salida/casen_procesado.csv`**: 61,070×26, personas que asisten o asistieron a educación superior.

### Fuente 6 — Censo 2024 (INE)

- **`src/Scrapers/CENSO/obtener.py`**: Descarga a `Entrada/` el zip oficial en parquet y lo descomprime; no repite la descarga si ya existe.
- **`src/Scrapers/CENSO/esquema.py`**: SSOT de `censo_procesado.csv` (8 columnas).
- **`src/Scrapers/CENSO/procesar.py`**: Deriva región de trabajo, actividad y `nivel_titulo`, y agrega por combinación; 12 controles contra el manual del INE. Requiere `.venv` (pyarrow).
- **`src/Scrapers/CENSO/Entrada/*.parquet`, `viv_hog_per_censo2024.zip`**: Microdatos oficiales de personas, hogares y viviendas, y su zip.
- **`src/Scrapers/CENSO/Entrada/cartografia/Cartografia_censo2024_Pais_Regional.parquet`**: Límites oficiales de las 16 regiones.
- **`src/Scrapers/CENSO/Salida/censo_procesado.csv`**: 14,793×8, personas de 15 años o más agregadas; sumar `personas`, no contar filas.

### Compartido

- **`src/Scrapers/comun/normalizador.py`**: Normalización de texto y fuente única de regiones: `REGIONES` (código 1-16 → nombre), `codigo_region()`, que falla ante un nombre desconocido, y `regiones_incoherentes()`. Toda tabla con región expone `codigo_region` y `nombre_region`.
- **`src/Scrapers/comun/inspect_data.py`**: Auditoría rigurosa de datasets (CSV/Excel) con selección del diccionario de esquema por mayor solape de columnas; genera `<nombre>_inspeccion.txt` en la misma carpeta.
- **`**/*_inspeccion.txt`**: Reportes de auditoría generados por `inspect_data.py` junto a cada dataset (crudo o procesado).

### Análisis (referencia)

- **`src/Analisis/diccionario_atributos_relaciones.md`**: Atributos laborales y educacionales de las fuentes, con concepto, ejemplo y relaciones entre tablas. No incluye el censo.

### Análisis (puentes / crosswalk)

- **`src/Analisis/Puentes_de_mapeo/esquema.py`**: SSOT de los puentes del PER: `PUENTE_SECTORES` (CAENES↔CIIU), `PUENTE_LLAVES_CARRERA` (19 col), catálogos (`ORIGEN_LLAVES`, `NIVELES_MATCH`, `FUENTES_EMPLEABILIDAD`) y reglas `VALIDACIONES`; incluye P3 (`carrera_generica ↔ ciuo_nivel_2`) y P4 (niveles educativos).
- **`src/Analisis/Puentes_de_mapeo/P1_puente_actividades.py`** → **`Salida/P1_puente_actividades.csv`**: P1 — 21 filas, relación 1:1 CAENES (ENE) ↔ sección CIIU (ENADEL).
- **`src/Analisis/Puentes_de_mapeo/P2_puente_llaves_carrera.py`** → **`Salida/P2_puente_llaves_carrera.csv`**: P2 — 8,623 filas: oferta de titulados + `EMPLEABILIDAD_A1` resuelta con trazabilidad (`nivel_match`, `empleabilidad_fuente`, `n_empleabilidad_asociadas`); cobertura 79.5% del volumen de titulaciones.
- **`src/Analisis/Puentes_de_mapeo/P4_puente_niveles_educativos.py`** → **`Salida/P4_puente_niveles_educativos.csv`**: P4 v2 — 15 filas, llave común `titulo_comun` (tipo de título) entre ENE, SIES y ENADEL; 5 validaciones, 2 contra datos reales.

- **`src/Analisis/Puentes_de_mapeo/P5_puente_carrera_casen.py`** → **`Salida/P5_puente_carrera_casen.csv`**: P5 — 11,163 filas, texto `e7` de CASEN → `carrera_generica`, con método y estado; asigna 88,4% de las personas. Incluye `Salida/P5_puente_carrera_casen_cobertura.csv`.
- **`src/Analisis/Puentes_de_mapeo/P6_matriz_carrera_actividad_ocupacion.py`** → **`Salida/P6_matriz_carrera_actividad_ocupacion.csv`**: P6 — 9,773 filas, carrera → sector y ocupación medido a nivel nacional, con error por diseño y fiabilidad. Incluye `Salida/P6_matriz_carrera_actividad_ocupacion_no_asignados.csv`.
- **`src/Analisis/Puentes_de_mapeo/P7_perfil_carrera_actividad_ocupacion.py`** → **`Salida/P7_perfil_carrera_actividad_ocupacion.csv`**: P7 — 7,514 filas, perfil de las 274 carreras de pregrado, propio o heredado; reemplaza a P3.
- **`src/Analisis/Puentes_de_mapeo/P9_perfil_laboral_carrera.py`** → **`Salida/P9_perfil_laboral_carrera.csv`**: P9 — 7,288 filas, 259 carreras: categoría en la ocupación, actividad económica y ambas, con % en la carrera, % en el grupo, especialización, error y fiabilidad.
- **`src/Analisis/Puentes_de_mapeo/P8_razon_empleo_carrera.py`** → **`Salida/P8_razon_empleo_carrera.csv`**: P8 — 258 carreras, ocupados, desocupados e inactivos por cada 10 titulados de 22 a 54 años.

### Análisis (cálculos de control)

- **`src/Analisis/Calculos_control/<tabla>/`**: Cada cálculo tiene `obtener.py`, `esquema.py`, `crosswalk.py` y `Salida/`. Son controles: no alimentan el PER.
- **`src/Analisis/Calculos_control/titulados_ocupados_region_actividad/Salida/titulados_ocupados_region_actividad.csv`**: 747×12, ocupados con título por región × CAENES × tipo de título (ENE JAS 2026), con marca de fiabilidad.
- **`src/Analisis/Calculos_control/cobertura_enadel_ene_region_actividad/Salida/cobertura_enadel_ene_region_actividad.csv`**: 336×14, dotación ENADEL frente a asalariados privados ENE por región × sector, con concentración y lectura.

- **`src/Analisis/Calculos_control/ocupados_region_actividad/Salida/ocupados_region_actividad.csv`**: Todos los ocupados por región × CAENES y peso relativo del sector, en dos versiones (`base_region`: residencia o trabajo); el reparto usa trabajo.
- **`src/Analisis/Calculos_control/conteo_instituciones_empleabilidad_titulados/Salida/conteo_instituciones_empleabilidad_titulados.csv`**: 190×11, instituciones por carrera genérica en MiFuturo y Titulados.
- **`src/Analisis/Calculos_control/ocupados_region_actividad_categoria/Salida/ocupados_region_actividad_categoria.csv`**: 2,370×14, ocupados por región de residencia × sector × empleador × nivel; conserva toda celda y cuadra con el total nacional y el Boletín INE.

### Análisis (JOINS / tablas del mapa)

- **`src/Analisis/JOINS/Concentracion_Region_Actividad_Censo/`**: Capa principal del mapa. `Salida/concentracion_region_actividad_censo.csv`, 336×17: ocupados, peso relativo, lectura, contraste con ENE y alertas.
- **`src/Analisis/JOINS/Concentracion_Region_Actividad/`**: Misma medida con ENE, con rango y fiabilidad; sirve de contraste. `Salida/concentracion_region_actividad.csv`, 336×18.
- **`src/Analisis/JOINS/Areas_Por_Actividad/`**: Áreas CINE por actividad, nacional, con CASEN. `Salida/areas_por_actividad.csv`, 210×15.
- **`src/Analisis/JOINS/Carreras_Por_Actividad/`**: Carreras por actividad y afinidad, nacional, con datos de SIES y MiFuturo. `Salida/carreras_por_actividad.csv`, 2,162 filas, 189 carreras; incluye respaldo por instituciones y titulados que no trabajan.
- **`src/Analisis/JOINS/Fuerza_Trabajo_Region_Nivel/`**: Ocupados y desocupados por región y nivel educativo, con ENE como contraste. `Salida/fuerza_trabajo_region_nivel.csv`, 48×12.
- **`src/Analisis/JOINS/Concentracion_Region_Area/`**: Áreas CINE por región según dónde viven los titulados; capa opcional, no usada en el mapa. `Salida/concentracion_region_area.csv`, 160×16.

### Análisis (Archivo / enfoque retirado)

- **`src/Analisis/Archivo/README.md`**: Por qué se retiró el Índice de Cupos, qué contiene y en qué orden se vuelve a ejecutar.

- **`src/Analisis/Archivo/CW_Empleabilidad_Oferta_Titulados/obtener.py`**: Carga y valida `titulados_procesado.csv` y `P2_puente_llaves_carrera.csv`.
- **`src/Analisis/Archivo/CW_Empleabilidad_Oferta_Titulados/esquema.py`**: SSOT de `oferta_empleabilidad_procesado.csv`.
- **`src/Analisis/Archivo/CW_Empleabilidad_Oferta_Titulados/crosswalk.py`**: Cruce exacto + fallback genérico institucional; 4 validaciones.
- **`src/Analisis/Archivo/CW_Empleabilidad_Oferta_Titulados/Salida/oferta_empleabilidad_procesado.csv`**: Paso 1 del PER (234,074×28).
- **`src/Analisis/Archivo/CW_Ocupados_Carrera_Region_Actividad/`**: Ocupados estimados por región, carrera y sector (`Salida/ocupados_carrera_region_actividad.csv`, 41,600 filas); `validar_reparto.py` hace la prueba de región oculta (`..._validacion.csv`).
- **`src/Analisis/Archivo/CW_Competencia_Desocupados/`**: Paso 2. `Salida/desocupados_carrera_region.csv` (2,607 filas) entra al índice; `desocupados_region_titulo.csv` y `desocupados_validacion.csv` lo respaldan.
- **`src/Analisis/Archivo/CW_Demanda_Jubilacion/`**: Paso 3. `Salida/jubilacion_carrera_region.csv` (2,333 filas), más `jubilacion_region_titulo.csv` y `jubilacion_validacion.csv`.
- **`src/Analisis/Archivo/CW_Demanda_Publica/`**: Vacantes públicas estimadas con el panel ENE. `Salida/vacantes_publicas_carrera_region.csv` y `vacantes_publicas_validacion.csv`.
- **`src/Analisis/Archivo/CW_Demanda_Empresarial/`**: Paso 4. `Salida/vacantes_carrera_region.csv` (2,377 filas), más el detalle por sector, las celdas y `vacantes_validacion.csv`.
- **`src/Analisis/Archivo/Indice_Cupos/`**: Paso 5. `Salida/indice_cupos_carrera_nacional.csv` (274 filas, la lectura más sólida), `indice_cupos_carrera_region.csv` (3,540 filas) y `indice_cupos_validacion.csv`.

### Visualización

- **`src/Visualizacion/Mapa_Actividades/generar_mapa.py`**: Lee las tablas y la cartografía, simplifica los bordes y escribe la página; 6 controles. Requiere `.venv` (geopandas y pyarrow).
- **`src/Visualizacion/Mapa_Actividades/plantilla.html`**: Diseño e interacción del mapa; recibe los datos al generar.
- **`src/Visualizacion/Mapa_Actividades/Salida/index.html`**: El mapa final, autónomo.
- **`src/Visualizacion/Mapa_Actividades/Salida/nota_de_lectura.md`**: Qué mide cada dato, qué no dice y sus límites.
