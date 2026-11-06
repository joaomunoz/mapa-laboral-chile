# Mapa Laboral de Chile

## Resumen

Mapa interactivo sobre la situación laboral y educacional de Chile. Muestra dónde se concentra cada actividad económica, cómo varía el trabajo por sexo y nivel de estudios, y qué carreras se vinculan con cada actividad.

La vista inicial resume la población y las 20 actividades. Al elegir una actividad, el mapa colorea cada región según su coeficiente de localización (CL). Al elegir una región, se ven sus cifras por sexo y nivel de estudios, y las carreras afines a nivel nacional, cada una con su ficha de titulados, empleabilidad e ingresos.

**Para verlo:** descarga [`index.html`](src/Visualizacion/Mapa_Actividades/Salida/index.html) y ábrelo en el navegador. Es un solo archivo de 329 KB, sin servidor ni dependencias. Cada vista tiene su propio enlace: por ejemplo, `index.html#B/2` abre Minería en Antofagasta, y el botón "atrás" del navegador vuelve a la vista anterior.

![Vista inicial del mapa: cada región tiene el color de la actividad que la distingue, junto a los principales hallazgos, la lista de regiones y la tabla de actividades](docs/mapa.png)

*Vista inicial: principales hallazgos, mapa, regiones y tabla de actividades con su % de ocupados con título. Cada región tiene el color de la actividad con mayor CL, y un color más suave indica un CL menor a 1,6.*

**Principales hallazgos (Censo 2024):**

- **Concentración:** 42,1% de los ocupados trabaja en la Metropolitana.
- **Especialización:** 13 de 16 regiones tienen su mayor CL en minería, agricultura o administración pública, aunque en 12 la actividad con más ocupados es Comercio.
- **Estudios:** 39,8% de los ocupados tiene título técnico o profesional. Por actividad, va de 9,9% en Hogares como empleadores a 78,7% en Servicios profesionales. La tasa de desocupación es 6,3% en profesionales, 7,8% en técnicos y 9,7% sin título superior.
- **Sexo:** la tasa de participación es 69,7% en hombres y 50,2% en mujeres.

Estas diferencias son descriptivas: el mapa no les atribuye causas.

## Objetivo

Dar a quien quiere conocer la situación laboral y educacional de Chile una vista única, con cifras medidas y fuente visible, que conecte regiones, actividades, sexo, nivel de estudios y carreras.

El proyecto empezó como un cálculo de probabilidad de empleo por carrera y región, y luego pasó a un Índice de Cupos. Ambos se descartaron al comprobar que **carrera × región no es medible**: de 3.040 combinaciones, solo 62 pasaban el filtro de fiabilidad en ocupados y 0 en desocupados. Un reparto sintético habría dado una cifra para cada combinación, pero suponiendo la misma mezcla de carreras en todas las regiones.

Se eligió mostrar menos, pero medido. El trabajo retirado sigue disponible en la etiqueta de git `indice-cupos`.

## Límites

- **No mide demanda, vacantes ni probabilidad de encontrar trabajo.** Ninguna fuente mide demanda por carrera.
- **Las diferencias no indican causa.** Por ejemplo, las tasas por nivel de estudios también dependen de la edad de cada grupo.
- **Sin desocupación por actividad:** el Censo registra la actividad solo de quienes trabajan.
- **Las carreras son un dato nacional:** no indican cuántos titulados de una carrera hay en una región. La región de los títulos en el SIES es la sede, no el trabajo.
- **Afinidad no es ejercer la profesión:** indica dónde trabajan los titulados, no qué tareas realizan.
- **Sexo y género:** el Censo registra el sexo solo como hombre o mujer. La identidad de género se mide aparte, desde los 18 años, y está suprimida para 633.803 ocupados, por lo que no se abre por actividad.
- **Censo y ENE difieren** en tamaño de seis actividades y en desempleo (profesionales: 6,3% y 8,1%). La causa no está comprobada.
- **Región de trabajo:** 5,8% de los ocupados del Censo no la tiene, sobre todo quienes trabajan en varias comunas. Por eso Transporte, Construcción y Electricidad aparecen bajo su tamaño.
- **Sin evolución en el tiempo:** el mapa usa un solo censo. Los ingresos de MiFuturo tampoco muestran una evolución, porque el 1er y el 5° año vienen de generaciones distintas.
- **Rapa Nui y Juan Fernández no se dibujan,** pero sus datos siguen en Valparaíso.

## Metodología

1. **Limpieza:** cada fuente se descarga y procesa por separado, y su tabla se audita con un reporte de calidad.
2. **Cruces:** las actividades se unen por sección de la clasificación CIIU, y las carreras se normalizan para unir CASEN, SIES y MiFuturo.
3. **Indicadores:** se calculan por región, actividad, sexo y nivel de estudios, y cada cifra conserva su fuente.
4. **Mapa:** un script genera una sola página con los datos y los bordes oficiales simplificados.

**Criterios principales** (son criterios de trabajo, no estándares oficiales):

- **Coeficiente de localización (CL):** participación de la actividad en la región ÷ participación en Chile. Una región queda sobre Chile desde 1,2 y bajo Chile hasta 0,8. No se lee con menos de 60 personas.
- **Bases:** los ocupados se cuentan por lugar de trabajo para participación y CL, y por residencia para tasas de desocupación y participación. Por eso los totales de una región pueden diferir.
- **Encuestas (ENE y CASEN):** un dato es fiable con n ≥ 60, gl ≥ 9 y CV ≤ 30, con errores calculados según el diseño muestral (linealización de Taylor).
- **Carrera afín:** al menos 10% de sus ocupados en la actividad, al menos el doble de lo normal entre titulados y un dato fiable. Si la muestra es insuficiente pero hay 10 casos o más, se muestra como posible vínculo.

**Validación:** cada paso se detiene si falla uno de sus controles.

- **Reproducibilidad:** en un clon limpio, el 03-11-26, la cadena completa generó un `index.html` idéntico byte a byte. Esa prueba es anterior a la última versión del mapa.
- **Contra el dato oficial:** el procesamiento de ENE reproduce el Boletín INE n°336 (julio-septiembre de 2026), con una desviación máxima de 0,08%.
- **Entre fuentes:** el CL del Censo y el de ENE tienen una correlación de 0,95 en las 209 combinaciones de región y actividad que ENE mide con fiabilidad.
- **Coherencia del mapa:** el color y la lectura se deciden con el mismo CL de 2 decimales que se muestra. La generación se detiene si los datos dejan de respaldar el color, la lectura o las frases de la página.

| Indicador | INE | Este proyecto | Desviación |
|---|---:|---:|---:|
| Fuerza de trabajo | 10.282.718 | 10.282.930 | +0,00% |
| Ocupadas | 9.274.742 | 9.275.130 | +0,00% |
| Desocupadas | 1.007.976 | 1.007.799 | −0,02% |
| Inactivas | 6.416.440 | 6.421.373 | +0,08% |
| Ocupadas informales | 2.451.443 | 2.452.190 | +0,03% |
| Tasa de desocupación | 9,8% | 9,80% | exacta |

La explicación completa de cada dato está en la [nota de lectura](src/Visualizacion/Mapa_Actividades/Salida/nota_de_lectura.md).

## Fuentes

| Fuente | Institución | Aporta | Alcance |
|---|---|---|---|
| [Censo 2024](https://censo2024.ine.gob.cl/resultados/) | INE | Capa principal: ocupados por actividad, región, sexo y nivel de estudios (15,2 millones de personas de 15 años o más) | Regional |
| [Encuesta Nacional de Empleo (ENE)](https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/ocupacion-y-desocupacion), dic. 2025 a sep. 2026 | INE | Contraste del Censo; sus cifras no se mezclan con las de él | Regional |
| [CASEN 2024](https://observatorio.ministeriodesarrollosocial.gob.cl/encuesta-casen-2024) | Ministerio de Desarrollo Social y Familia | Único vínculo entre carrera y actividad económica | Nacional |
| [Titulados 2007-2025 (SIES)](https://www.mifuturo.cl/bases-de-datos-titulados/) | Mineduc | Títulos por carrera y sexo | Nacional |
| [Buscador de Empleabilidad e Ingresos (MiFuturo)](https://www.mifuturo.cl/buscador-de-empleabilidad-e-ingresos/) | Mineduc | Empleabilidad e ingresos por carrera | Nacional |

## Cómo reproducirlo

Probado con Python 3.13 en Linux.

```bash
python3 -m venv .venv
.venv/bin/pip install pandas==2.3.3 numpy==2.3.5 pyarrow==26.0.0 geopandas==1.2.0 shapely==2.2.0 \
  requests==2.32.5 beautifulsoup4==4.15.0 rapidfuzz==3.12.2 openpyxl==3.1.5
```

Los datos crudos no están en el repositorio porque pesan hasta 1,6 GB. Para regenerar el mapa hay dos caminos:

**Solo el mapa.** Las tablas intermedias ya están versionadas, así que basta con la capa de regiones. La descarga pesa 795 MB, puede tardar varios minutos (19 en la prueba) y el script borra el zip al terminar:

```bash
.venv/bin/python -W ignore src/Scrapers/CENSO/obtener_cartografia.py
.venv/bin/python -W ignore src/Visualizacion/Mapa_Actividades/generar_mapa.py
```

**La cadena completa.** El procesamiento tarda unos 10 minutos con los datos ya descargados:

```bash
PY=.venv/bin/python
export PYTHONWARNINGS=ignore

# 1. Descargar y procesar las fuentes
for f in Titulados Empleabilidad ENE CASEN CENSO; do
  $PY src/Scrapers/$f/obtener.py
  $PY src/Scrapers/$f/procesar.py
done

# 2. Puentes entre fuentes
for p in P1_puente_actividades P5_puente_carrera_casen P6_control_no_asignados P9_perfil_laboral_carrera; do
  $PY src/Analisis/Puentes_de_mapeo/$p.py
done

# 3. Tablas del mapa, en este orden
$PY src/Analisis/Calculos_control/ocupados_region_actividad/crosswalk.py
for t in Concentracion_Region_Actividad Concentracion_Region_Actividad_Censo Areas_Por_Actividad Carreras_Por_Actividad Fuerza_Trabajo_Region_Nivel; do
  $PY src/Analisis/JOINS/$t/crosswalk.py
done

# 4. Mapa
$PY src/Scrapers/CENSO/obtener_cartografia.py
$PY src/Visualizacion/Mapa_Actividades/generar_mapa.py
```

Los pasos de `procesar.py` en adelante y `obtener_cartografia.py` se probaron en un clon limpio. Las descargas con `obtener.py` no se repitieron en esa prueba, y dependen de que los sitios oficiales mantengan sus páginas y enlaces.

## Estructura

```text
Datos/datos_externos/glosarios/   Libros de códigos y metodologías oficiales
src/Scrapers/                     Descarga y limpieza de cada fuente (Entrada/ → Salida/)
src/Analisis/Puentes_de_mapeo/    Cruces entre fuentes: actividades y carreras
src/Analisis/Calculos_control/    Control de la tabla regional de ENE
src/Analisis/JOINS/               Tablas que alimentan el mapa
src/Visualizacion/Mapa_Actividades/  Generador, plantilla y mapa final
pizarra/                          Estado, decisiones y bitácora del proyecto
```

Cada tabla va acompañada de un reporte `_inspeccion.txt`, generado por `src/Scrapers/comun/inspect_data.py`. El detalle de cada archivo está en [`pizarra/Estructura.md`](pizarra/Estructura.md).

**Tecnologías:** Python, pandas, GeoPandas, Shapely, requests y BeautifulSoup para los datos. HTML, CSS, JavaScript y SVG para el mapa, sin bibliotecas externas.

## Estado

El mapa está generado y validado en sus datos. El autor confirmó su uso con mouse y teclado, y por última vez los clics, el 05-11-26.
