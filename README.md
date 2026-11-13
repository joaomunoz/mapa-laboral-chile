# Mapa Laboral de Chile

## Resumen

Mapa interactivo sobre la situación laboral y educacional de Chile. Muestra dónde se concentra cada actividad económica, cómo varía el trabajo por sexo y nivel de estudios, cuánto trabajo es informal o independiente, y qué carreras se vinculan con cada actividad.

La vista inicial resume la población, las 20 actividades (con un gráfico de hombres y mujeres y otro de la región donde más pesa cada una), el área de estudio de los titulados de cada actividad y la formalidad del trabajo, con un índice de secciones y el hallazgo de cada una como título. Al elegir una actividad, el mapa colorea cada región según su coeficiente de localización (CL). Al elegir una región, el detalle va por tema: el CL (la tabla de la actividad y el CL de las 20 actividades de la región, en escala logarítmica); hombres y mujeres (en la actividad, en Chile y en la región, y en cada grupo de toda la región, con la brecha de participación frente a Chile); el nivel de estudios (el título técnico o profesional de los ocupados de la actividad, por sexo y frente a Chile, y la desocupación de la región por nivel, con la tasa de Chile y la diferencia escritas); y las carreras afines a nivel nacional, cada una con su ficha de titulados, empleabilidad e ingresos, con el área de estudio de los titulados ocupados en un circular.

**Para verlo:** descarga [`docs/index.html`](docs/index.html) y ábrelo en el navegador. Es un solo archivo de 462 KB, sin servidor ni dependencias. Cada vista tiene su propio enlace: por ejemplo, `index.html#B/2` abre Minería en Antofagasta y baja a su detalle, y el botón "atrás" del navegador vuelve a la vista anterior.

![Vista inicial del mapa: cada región tiene el color de la actividad que la distingue, junto a los principales hallazgos, la lista de regiones y el gráfico de hombres y mujeres por actividad](docs/mapa.png)

*Vista inicial: principales hallazgos, mapa, regiones y el resumen con su índice por fuente, donde cada sección se titula con su hallazgo. Cada región tiene el color de la actividad con mayor CL, y un color más suave indica un CL de 1,2 a menos de 1,6, que también pesa más que en Chile.*

**Principales hallazgos (Censo 2024):**

- **Concentración:** 42,1% de los ocupados trabaja en la Metropolitana.
- **Especialización:** 13 de 16 regiones tienen su mayor CL en minería, agricultura o administración pública, aunque en 12 la actividad con más ocupados es Comercio.
- **Estudios:** 4 de cada 10 ocupados (39,8%) tiene título técnico o profesional. Por actividad, va de 1 de cada 10 en Hogares como empleadores (9,9%) a 8 de cada 10 en Servicios profesionales (78,7%).
- **Estudios y trabajo:** en las 16 regiones, la tasa de desocupación es menor con título técnico o profesional que sin título superior. En Chile es 6,3% en profesionales, 7,8% en técnicos y 9,7% sin título superior. No la explica la edad: se mantiene en cada tramo de 25 a 64 años, en las 16 regiones (de 25 a 34, 8,7% con título y 11,3% sin título); de 15 a 24 es al revés, con pocos titulados.
- **Sexo:** la tasa de participación es 69,7% en hombres y 50,2% en mujeres. Entre los ocupados, tiene título 46,5% de las mujeres y 34,6% de los hombres.

**Según la CASEN 2024:**

- **Área de estudio:** en 5 de 20 actividades, más de la mitad de los titulados ocupados viene de una sola área, con todo su rango de 95% sobre 50%: Salud y asistencia social (76,4% de Salud y Bienestar), Construcción (65,3%) y Minería (62,7%) de Ingeniería, Enseñanza (63,8% de Educación) y Finanzas (60,2% de Administración y Derecho). Solo en Enseñanza y Salud también trabaja ahí la mayoría de los titulados del área (75,8% y 62,8%); Construcción, en cambio, reúne solo 14,3% de los titulados de Ingeniería.

**Según la ENE (marzo a julio de 2026):**

- **Formalidad:** 73,4% de los ocupados tiene empleo formal y 26,6% informal. Sin título superior, 64,0% formal y 36,0% informal; con título técnico, 82,9% y 17,1%; con título profesional, 87,7% y 12,3%. La diferencia está sobre todo en los independientes: 69,2% de los que no tienen título superior es informal, frente a 22,6% de los profesionales. Se mantiene a igual edad: de 25 a 64 años, en cada tramo de 10 años, va de 68% a 72% sin título y de 16% a 31% en profesionales. La diferencia es mayor entre los de más edad: de 25 a 34 años, 72% frente a 31%; de 55 a 64, 68% frente a 16%. Por actividad, el empleo formal supera 93% en Minería, Electricidad y gas y Finanzas y seguros; en Hogares como empleadores, 59,1% es informal. Ser independiente no implica ser informal: Servicios profesionales y Comercio tienen 36% de independientes, pero 14,0% de ellos es informal en el primero y 56,6% en el segundo. Por región, la informalidad es más alta en La Araucanía, Ñuble, Los Ríos y Arica y Parinacota (33% a 36%) y queda bajo la de Chile en Antofagasta, Magallanes y la Metropolitana (22% a 23%); con el margen de error, la más y la menos informal no se distinguen de sus vecinas.
- **Independientes:** son 24,1% de los ocupados: 13,8% informales y 10,4% formales.
- **Desocupación:** subió de 8,6% en 2024 a 9,5% en 2026, con los mismos meses.

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
- **Censo y ENE difieren** en tamaño de seis actividades, también con los mismos meses. La causa no está comprobada. En desempleo difieren poco (profesionales: 6,3% y 6,9%).
- **Región de trabajo:** 5,8% de los ocupados del Censo no la tiene, sobre todo quienes trabajan en varias comunas. Por eso Transporte, Construcción y Electricidad aparecen bajo su tamaño.
- **Evolución solo de la desocupación:** el mapa usa un solo censo. El cambio de la desocupación entre 2024 y 2026 se mide con la ENE, en los mismos meses. Los ingresos de MiFuturo no muestran una evolución, porque el 1er y el 5° año vienen de generaciones distintas.
- **Formalidad solo de 2026 y solo con la ENE:** el Censo no mide formalidad, y las ocupadas informales de la ENE 2024 no reproducen el boletín del INE, así que no hay evolución de la informalidad. Por actividad se muestra solo donde la muestra la sostiene.
- **Rapa Nui y Juan Fernández no se dibujan,** pero sus datos siguen en Valparaíso.

## Metodología

1. **Limpieza:** cada fuente se descarga y procesa por separado, y su tabla se audita con un reporte de calidad.
2. **Cruces:** las actividades se unen por sección de la clasificación CIIU, y las carreras se normalizan para unir CASEN, SIES y MiFuturo.
3. **Indicadores:** se calculan por región, actividad, sexo y nivel de estudios, y cada cifra conserva su fuente.
4. **Mapa:** un script genera una sola página con los datos y los bordes oficiales simplificados.

### Flujo de datos

En la limpieza, cada fuente queda en una tabla. En el análisis se destacan solo las columnas clave de cada tabla.

```mermaid
flowchart TD
  subgraph F["1. Fuentes"]
    censo["Censo 2024 (INE)"]
    ene["ENE (INE)"]
    casen["CASEN 2024"]
    sies["Titulados 2007-2025 (SIES)"]
    mifuturo["MiFuturo"]
  end

  subgraph L["2. Limpieza · src/Scrapers/*/Salida"]
    cp["censo_procesado<br>Personas de 15 años o más por región de residencia y de trabajo, situación laboral, actividad y nivel de estudios"]
    cs["censo_por_sexo<br>Lo mismo, abierto por sexo"]
    geo["Cartografía regional<br>Bordes de las 16 regiones"]
    ep["ene_procesado y ene_procesado_2024<br>Microdatos de la ENE de 2026 y de 2024, con su diseño muestral"]
    kp["casen_procesado<br>Personas con su carrera declarada, su actividad y su diseño muestral"]
    tp["titulados_procesado<br>Titulaciones por carrera, año y sexo"]
    mp["empleabilidad_procesado<br>Empleabilidad e ingresos por carrera"]
  end

  subgraph P["3. Análisis: puentes entre fuentes · src/Analisis/Puentes_de_mapeo"]
    p1["P1_puente_actividades<br>Une los códigos de actividad con la sección CIIU<br>actividad_caenes → actividad_ciiu"]
    p5["P5_puente_carrera_casen<br>Lleva la carrera declarada en CASEN a la carrera del SIES<br>e6a → carrera_generica"]
    p9["P9_perfil_laboral_carrera<br>Dónde trabajan los titulados de cada carrera<br>carrera_generica × actividad_ciiu: pct_en_carrera, indice_especializacion"]
  end

  subgraph J["4. Análisis: tablas del mapa · src/Analisis/JOINS"]
    je["concentracion_region_actividad<br>CL según la ENE, como contraste<br>peso_relativo, fiabilidad"]
    jc["concentracion_region_actividad_censo<br>Ocupados y CL por región y actividad<br>ocupados, pct_en_region, pct_nacional, peso_relativo (CL), ene_peso_relativo"]
    jn["fuerza_trabajo_region_nivel<br>Situación laboral por región y nivel de estudios<br>ocupados_residencia, desocupados, fuera_fuerza_trabajo, tasa_desocupacion"]
    jt["fuerza_trabajo_titulo_edad<br>Desocupación con y sin título por región y tramo de edad<br>con_titulo, tramo_edad, ocupados, desocupados, tasa_desocupacion"]
    jf["formalidad_ocupados<br>Asalariado o independiente, y formal o informal, según ENE 2026<br>tasa_informalidad, pct_independientes, fiabilidad_informalidad"]
    jv["evolucion_desocupacion<br>Cambio de la desocupación entre 2024 y 2026, según ENE<br>tasa_2024, tasa_2026, diferencia_pp, lectura"]
    ja["areas_por_actividad<br>Áreas de estudio de los titulados en cada actividad<br>area_cine, pct_en_actividad"]
    jk["carreras_por_actividad<br>Carreras afines a cada actividad, con su ficha<br>carrera_generica, afinidad, titulados_2007_2025, empleabilidad_1er_anio, ingreso_medio_5to_anio"]
  end

  subgraph M["5. Mapa"]
    gen["src/Visualizacion/generar_mapa.py + web/ (HTML, CSS y JS)"]
    out["docs/index.html"]
  end

  censo --> cp & cs & geo
  ene --> ep
  casen --> kp
  sies --> tp
  mifuturo --> mp

  kp & tp --> p5
  kp & p1 & p5 --> p9

  ep & p1 --> je
  cp & p1 & je --> jc
  cp & ep --> jn
  censo & jn --> jt
  ep --> jv
  ep & p1 --> jf
  kp & p1 & p5 & tp --> ja
  p9 & p5 & tp & mp & kp --> jk

  jc & jn & jt & jv & jf & ja & jk & cp & cs & geo --> gen
  gen --> out
```

Las columnas completas de cada tabla están en su reporte `_inspeccion.txt`. No aparecen las tablas que solo validan un paso: `ocupados_region_actividad`, que reproduce el boletín del INE, y `P6_control_no_asignados`, que compara a quienes P5 asigna y a quienes no.

### Fórmulas

**Parámetros**

| Parámetro | Qué es | Chile |
|---|---|---:|
| Población de 15 años o más | Personas de 15 años o más, incluidas las sin dato de situación laboral | 15.205.784 |
| Ocupados | Trabajaron al menos una hora en la semana de referencia. Se cuentan donde viven | 8.277.501 |
| Desocupados | No trabajaron y buscaron trabajo | 777.920 |
| Ocupados por lugar de trabajo | Ocupados contados en la región donde trabajan, con actividad informada; incluye 2.769 en organismos internacionales, que no son una de las 20 actividades | 7.395.105 |

**Indicadores**

| Indicador | Fórmula | Ejemplo (Censo 2024) |
|---|---|---|
| Tasa de desocupación | desocupados ÷ (ocupados + desocupados) | Chile: 777.920 ÷ 9.055.421 = **8,6%** |
| Tasa de participación | (ocupados + desocupados) ÷ población de 15 años o más | Chile: 9.055.421 ÷ 15.205.784 = **59,6%** |
| Tasa de ocupación | ocupados ÷ población de 15 años o más | Chile: 8.277.501 ÷ 15.205.784 = **54,4%** |
| Participación | ocupados de la actividad ÷ ocupados de la región, por lugar de trabajo | Artes y recreación en Valparaíso: 10.007 ÷ 706.053 = **1,42%**; en Chile: 81.498 ÷ 7.395.105 = **1,10%** |
| Coeficiente de localización (CL) | participación en la región ÷ participación en Chile | Valparaíso en Artes y recreación: 1,42% ÷ 1,10% = **1,29** |

- **Un CL de 1,29** significa que la actividad pesa 29% más en Valparaíso que en Chile. No significa que sea la principal de la región: ahí Comercio tiene 124.015 ocupados.
- **"Participación" y "tasa de participación" son distintas:** la primera es el peso de una actividad entre los ocupados; la segunda, la parte de la población que trabaja o busca trabajo.

**Criterios principales** (son criterios de trabajo, no estándares oficiales):

- **Lectura del CL:** una región queda sobre Chile desde 1,2 y bajo Chile hasta 0,8. No se lee con menos de 60 personas.
- **Bases:** los ocupados se cuentan por lugar de trabajo para participación y CL, y por residencia para tasas de desocupación y participación. Por eso los totales de una región pueden diferir. Una tasa y sus componentes van siempre en la misma base: en el detalle de región, las secciones de toda la región usan residencia, para que desocupados / (ocupados + desocupados) dé la tasa mostrada, y una nota concilia los ocupados que viven en la región con los que trabajan en ella (con el traslado medido: los que salen, los que llegan y los que no informan dónde trabajan) y con la fila A del CL (con actividad informada).
- **Encuestas (ENE y CASEN):** un dato es fiable con n ≥ 60, gl ≥ 9 y CV ≤ 30, con errores calculados según el diseño muestral (linealización de Taylor).
- **Carrera afín:** al menos 10% de sus ocupados en la actividad, al menos el doble de lo normal entre titulados y un dato fiable. Si la muestra es insuficiente pero hay 10 casos o más, se muestra como posible vínculo.

**Validación:** cada paso se detiene si falla uno de sus controles.

- **Reproducibilidad:** en un clon limpio, el 03-11-26, la cadena completa generó un `index.html` idéntico byte a byte. Esa prueba es anterior a la última versión del mapa.
- **Contra el dato oficial:** el procesamiento de ENE reproduce el Boletín INE n°336 (julio-septiembre de 2026) con una desviación máxima de 0,08%, y el n°310 (mayo-julio de 2024) con 0,12%. En 2024, la cifra de ocupados informales del boletín no calza con el microdato publicado y no se valida.
- **Entre fuentes:** con los mismos meses, el CL del Censo y el de ENE tienen una correlación de 0,97 en las 187 combinaciones de región y actividad que ENE mide con fiabilidad.
- **Coherencia del mapa:** el color y la lectura se deciden con el mismo CL de 2 decimales que se muestra. La generación se detiene si los datos dejan de respaldar el color, la lectura o las frases de la página.

| Indicador | INE | Este proyecto | Desviación |
|---|---:|---:|---:|
| Fuerza de trabajo | 10.282.718 | 10.282.930 | +0,00% |
| Ocupadas | 9.274.742 | 9.275.130 | +0,00% |
| Desocupadas | 1.007.976 | 1.007.799 | −0,02% |
| Inactivas | 6.416.440 | 6.421.373 | +0,08% |
| Ocupadas informales | 2.451.443 | 2.452.190 | +0,03% |
| Tasa de desocupación | 9,8% | 9,80% | exacta |

La explicación completa de cada dato está en la [nota de lectura](docs/nota_de_lectura.md).

## Fuentes

| Fuente | Institución | Periodo | Aporta | Alcance |
|---|---|---|---|---|
| [Censo 2024](https://censo2024.ine.gob.cl/resultados/) | INE | Mar. a jul. de 2024 | Capa principal: ocupados por actividad, región, sexo y nivel de estudios (15,2 millones de personas de 15 años o más) | Regional |
| [Encuesta Nacional de Empleo (ENE)](https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/ocupacion-y-desocupacion) | INE | Mar. a jul. de 2024 y de 2026 | Contraste del Censo en sus mismos meses, y el cambio de la desocupación entre 2024 y 2026; sus cifras no se mezclan con las del Censo | Regional |
| [CASEN 2024](https://observatorio.ministeriodesarrollosocial.gob.cl/encuesta-casen-2024) | Ministerio de Desarrollo Social y Familia | Nov. de 2024 a feb. de 2025 | Único vínculo entre carrera y actividad económica | Nacional |
| [Titulados 2007-2025 (SIES)](https://www.mifuturo.cl/bases-de-datos-titulados/) | Mineduc | Años académicos 2007 a 2025, de marzo a febrero | Títulos por carrera y sexo | Nacional |
| [Buscador de Empleabilidad e Ingresos (MiFuturo)](https://www.mifuturo.cl/buscador-de-empleabilidad-e-ingresos/) | Mineduc | Empleo e ingresos de 2022 a 2024, en pesos de sept. de 2025 | Empleabilidad e ingresos por carrera | Nacional |

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
.venv/bin/python -W ignore src/Visualizacion/generar_mapa.py
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
# ENE 2024: los meses del Censo, para el contraste
$PY src/Scrapers/ENE/obtener.py 2024
$PY src/Scrapers/ENE/procesar.py 2024

# 2. Puentes entre fuentes
for p in P1_puente_actividades P5_puente_carrera_casen P6_control_no_asignados P9_perfil_laboral_carrera; do
  $PY src/Analisis/Puentes_de_mapeo/$p.py
done

# 3. Tablas del mapa, en este orden
$PY src/Analisis/Calculos_control/ocupados_region_actividad/crosswalk.py
for t in Concentracion_Region_Actividad Concentracion_Region_Actividad_Censo Areas_Por_Actividad Carreras_Por_Actividad Fuerza_Trabajo_Region_Nivel Fuerza_Trabajo_Titulo_Edad Evolucion_Desocupacion Formalidad_Ocupados; do
  $PY src/Analisis/JOINS/$t/crosswalk.py
done

# 4. Mapa
$PY src/Scrapers/CENSO/obtener_cartografia.py
$PY src/Visualizacion/generar_mapa.py
```

Los pasos de `procesar.py` en adelante y `obtener_cartografia.py` se probaron en un clon limpio. Las descargas con `obtener.py` no se repitieron en esa prueba, y dependen de que los sitios oficiales mantengan sus páginas y enlaces.

## Estructura

```text
Datos/datos_externos/glosarios/   Libros de códigos y metodologías oficiales
src/Scrapers/                     Descarga y limpieza de cada fuente (Entrada/ → Salida/)
src/Analisis/Puentes_de_mapeo/    Cruces entre fuentes: actividades y carreras
src/Analisis/Calculos_control/    Control de la tabla regional de ENE
src/Analisis/JOINS/               Tablas que alimentan el mapa
src/Visualizacion/                Generador del mapa (Python) y su página en web/ (HTML, CSS y JS)
docs/                             Mapa final, nota de lectura y captura
```

Cada tabla va acompañada de un reporte `_inspeccion.txt`, generado por `src/Scrapers/comun/inspect_data.py`. Los periodos de la ENE que usan las tablas se definen en `src/Scrapers/comun/periodos.py`.

**Tecnologías:** Python, pandas, GeoPandas, Shapely, requests y BeautifulSoup para los datos. HTML, CSS, JavaScript y SVG para el mapa, sin bibliotecas externas.

## Estado

El mapa está generado y validado en sus datos. El autor confirmó su uso con mouse y teclado, y por última vez los clics, el 05-11-26.
