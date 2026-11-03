# LIBRO DE CÓDIGOS BASE DE DATOS  
# ENCUESTA NACIONAL DE EMPLEO (ENE)  

**INSTITUTO NACIONAL DE ESTADÍSTICAS DE CHILE (INE)**  
Julio 2026  

---

**Libro de Códigos Base de Datos Encuesta Nacional de Empleo (ENE)**  
Instituto Nacional de Estadísticas de Chile  
Subdirección Técnica  
Subdepartamento de Estadísticas Continuas del Trabajo  
*Fecha de actualización: 31 de julio de 2026*  

---

## Tabla de contenidos

1. [Presentación](#1-presentación) .......................................................................................................... 3  
2. [Acceso a los datos](#2-acceso-a-los-datos) .................................................................................................. 6  
   2.1 [Descarga de bases de datos](#21-descarga-de-bases-de-datos) ................................................................................... 6  
   2.2 [Uso de Banco de Datos ENE](#22-uso-de-banco-de-datos-ene) .................................................................................. 9  
3. [Consideraciones sobre el uso de la información](#3-consideraciones-sobre-el-uso-de-la-información) .................................................... 13  
   3.1 [Aspectos generales](#31-aspectos-generales) ............................................................................................... 13  
   3.2 [Política de revisión y actualización de cifras](#32-política-de-revisión-y-actualización-de-cifras) ....................................................... 14  
4. [Indicaciones para el uso de los datos](#4-indicaciones-para-el-uso-de-los-datos) .................................................................... 15  
5. [Descripción de variables](#5-descripción-de-variables) ....................................................................................... 16  
   5.1 [Variables de contexto](#51-variables-de-contexto) ............................................................................................ 17  
   5.2 [Cuestionario sociodemográfico](#52-cuestionario-sociodemográfico) .......................................................................... 19  
   5.3 [Cuestionario central de empleo](#53-cuestionario-central-de-empleo) ............................................................................ 25  
   5.4 [Variables analíticas y factores de expansión](#54-variables-analíticas-y-factores-de-expansión) ...................................................... 59  
6. [Descripción de indicadores principales](#6-descripción-de-indicadores-principales) ................................................................. 70  
   6.1 [Indicadores sobre la fuerza de trabajo](#61-indicadores-sobre-la-fuerza-de-trabajo) ................................................................. 70  
   6.2 [Indicadores sobre informalidad laboral](#62-indicadores-sobre-informalidad-laboral) ............................................................... 74  
7. [Programación para la construcción de indicadores principales](#7-programación-para-la-construcción-de-indicadores-principales) .............................. 75  
   7.1 [Stata](#71-stata) ........................................................................................................................ 75  
   7.2 [R](#72-r) ............................................................................................................................... 77  
   7.3 [SPSS](#73-spss) ......................................................................................................................... 80  
8. [Preguntas frecuentes](#8-preguntas-frecuentes) ........................................................................................... 86  
   8.1 [¿Es posible realizar estimaciones comunales con la ENE?](#81-es-posible-realizar-estimaciones-comunales-con-la-ene) ................................ 86  
   8.2 [¿Cómo interpretar una variación de tasas en la ENE?](#82-cómo-interpretar-una-variación-de-tasas-en-la-ene) ....................................... 87  
9. [Glosario](#9-glosario) ................................................................................................................ 88  
10. [Referencias bibliográficas](#10-referencias-bibliográficas) .............................................................................. 100  
11. [Anexos](#11-anexos) ............................................................................................................. 104  
    - [Anexo 1. Clasificación de regiones, provincias y comunas](#anexo-1-clasificación-de-regiones-provincias-y-comunas) ......................................... 104  
    - [Anexo 2. Clasificación de países](#anexo-2-clasificación-de-países) ................................................................................... 114  
    - [Anexo 3. Clasificación de grupo ocupacional](#anexo-3-clasificación-de-grupo-ocupacional) ............................................................... 120  
    - [Anexo 4. Modificación de pregunta sobre prestaciones laborales](#anexo-4-modificación-de-pregunta-sobre-prestaciones-laborales) ............................. 121  
    - [Anexo 5. Clasificación de rama de actividad económica](#anexo-5-clasificación-de-rama-de-actividad-económica) ............................................ 124  
    - [Anexo 6. Variables descontinuadas](#anexo-6-variables-descontinuadas) .............................................................................. 125  
    - [Anexo 7. Exportación de archivos](#anexo-7-exportación-de-archivos) .................................................................................. 127  
    - [Anexo 8. Descarga automática de bases usando R](#anexo-8-descarga-automática-de-bases-usando-r) ..................................................... 128  
    - [Anexo 8. Nota sobre preguntas de cuestionario sobre impacto de COVID-19](#anexo-8-nota-sobre-preguntas-de-cuestionario-sobre-impacto-de-covid-19) .......... 129  

---

## 1 PRESENTACIÓN

El Instituto Nacional de Estadísticas de Chile (INE) pone a disposición del público las bases de datos correspondientes a la Encuesta Nacional de Empleo (ENE), en su versión vigente desde el trimestre enero–marzo de 2010.

El presente libro de códigos tiene como propósito facilitar el manejo de los datos por parte de las diferentes personas usuarias de la información contenida en las bases. El documento se estructura de la siguiente manera. La sección 2 detalla la forma de acceder a los datos disponibles en la página web institucional del INE. Posteriormente, en la sección 3 se plantean una serie de consideraciones respecto al uso de la información y la política de rectificación de cifras vigente, en tanto que en la 4, se señalan cómo usar los datos muestrales expandidos para realizar estimaciones de la población.

En la sección 5 se describen detalladamente cada una de las variables que componen las bases, tanto del propio cuestionario como aquellas que resultan de un procesamiento posterior.

La sección 6 incluye una guía de construcción de los principales indicadores incluidos en el boletín de empleo, la que se complementa con la sección 7, dedicada a la programación en Stata y R de dichos indicadores.

La sección 8 incorpora algunas preguntas frecuentes y la 9 presenta un glosario de términos utilizados en la encuesta. En la 10, en tanto, aparecen algunas referencias bibliográficas importantes para el análisis de la ENE.

Finalmente, la sección 11 corresponde a los anexos del manual cuyo contenido involucra los principales clasificadores utilizados y algunos elementos históricos de la serie vigente de la ENE y la exportación de archivos .csv.

Es importante considerar que, a la fecha de publicación de este libro de códigos, la información contenida en las bases de datos fue actualizada de acuerdo con el proceso anual de revisión y actualización de cifras de la Encuesta Nacional de Empleo realizado en julio de 2025.

En ese sentido, los indicadores provenientes de la encuesta se basan en un diseño muestral y metodológico que debe ser evaluado regularmente con el propósito de reducir y minimizar las distintas fuentes de error. Al ser la ENE una encuesta continua, este tipo de errores puede ser generado, en parte, por shocks demográficos, económicos, epidemiológicos y sociales a nivel nacional o local, ocurridos en un momento del tiempo, bajo el cual los insumos utilizados en el diseño, procesamiento y difusión de la información pudiesen ir quedando desactualizados o no acordes a la realidad.

Asimismo, existen errores no muestrales propios de los procesos estadísticos involucrados en la ENE detectados tras la difusión coyuntural de los datos y que tienen relación con los controles de calidad que la misma institución aplica a sus productos en las distintas fases del procesamiento de los datos. Es en este contexto, la implementación de una política de revisión y actualización de la ENE considera la evaluación constante de todas las áreas que intervienen en la generación de la encuesta, las que serán debidamente informadas a las personas usuarias de las bases de datos.[^1]

A continuación, se presenta una ficha resumen con los principales antecedentes técnicos de la ENE (Tabla 1):

### Tabla 1. Características de la Encuesta Nacional de Empleo

| Características | Detalle |
| :--- | :--- |
| **Organismo responsable** | Instituto Nacional de Estadísticas (Chile) |
| **Organismo ejecutor** | Instituto Nacional de Estadísticas (Chile) |
| **Objetivo** | Clasificar y caracterizar a la población objetivo según su condición de actividad. |
| **Población objetivo** | Población en edad de trabajar, es decir, todas las personas de quince años o más, que residen habitualmente en viviendas particulares ocupadas en el país. |
| **Unidad de información y análisis** | Personas en edad de trabajar con residencia habitual en hogares ubicados en viviendas particulares ocupadas dentro del territorio nacional. |
| **Marco Muestral** | Marco Muestral de Viviendas elaborado a partir de Censo de Población y Vivienda 2017 (MMV 2017). |
| **Diseño de muestra** | Muestra compleja: probabilística, estratificada y bietápica. |
| **Estratificación** | Los estratos de muestreo corresponden a la combinación “Estrato geográfico – Estrato Socioeconómico”. |
| **Parámetro de interés para cálculo de tamaño muestral** | El principal parámetro de interés para la determinación del tamaño muestral es la tasa de desocupación. |
| **Cobertura** | La cobertura geográfica de la ENE considera las 16 regiones del país, buscando presencia en todo el territorio nacional y abarcando 97% de las comunas del país. De esta manera, se excluyen algunas áreas geográficas que por presentar ciertas características especiales (Insularidad, clima, altitud, tiempo de traslados, estado de los caminos, etc.), son excluidas del marco de muestreo de la encuesta. |
| **Dominios de estudio**[^2] | - Nacional<br>- Nacional urbano<br>- Nacional rural<br>- Regional (16 regiones)<br>- Regional urbano (16 regiones)<br>- Regional rural (10 regiones: Coquimbo, Valparaíso, O’Higgins, Maule, Biobío, La Araucanía, Los Lagos, Metropolitana, Los Ríos y Ñuble).<br>- Provincial (30 provincias: Iquique, Antofagasta, El Loa, Copiapó, Huasco, Elqui, Limarí, Valparaíso, San Antonio, San Felipe, Marga Marga, Santiago, Cordillera, Maipo, Melipilla, Talagante, Cachapoal, Talca, Curicó, Linares, Diguillín,[^3] Concepción, Arauco, Biobío, Cautín, Valdivia, Llanquihue, Osorno, Coyhaique, Magallanes) |
| **Metodología de recolección** | Mixta, presencial y telefónica. |

Es importante señalar que este manual se actualiza periódicamente, por lo que se recomienda una revisión periódica del enlace: [https://www.ine.gob.cl/docs/default-source/ocupacion-y-desocupacion/bbdd/libro-de-codigos/codigos-ene-2020.pdf](https://www.ine.gob.cl/docs/default-source/ocupacion-y-desocupacion/bbdd/libro-de-codigos/codigos-ene-2020.pdf)

---

## 2 ACCESO A LOS DATOS

### 2.1 Descarga de bases de datos

#### 2.1.1 Acceso directo a página Web del INE
Las bases de datos de la ENE se encuentran publicadas en el portal Web del INE-Chile, en la dirección:  
`www.ine.cl/estadisticas/sociales/mercado-laboral/ocupacion-y-desocupacion`

Hay dos tipos de bases con distintas temporalidades de publicación:
- **Trimestrales**, correspondientes a la actual serie de la encuesta, que comenzó en enero-marzo de 2010 y que sigue vigente hasta la actualidad.
- **Anuales**, de acuerdo a metodología diseñada especialmente para contar con estimaciones de un año completo (INE, 2022e). Se encuentran disponibles las bases desde 2010 a 2023.

Cualquier requerimiento adicional de información debe ser canalizada a través del portal de Atención Ciudadana del INE ([https://atencionciudadana.ine.cl/](https://atencionciudadana.ine.cl/)), el que será evaluado de acuerdo con dos criterios:
- Disponibilidad de la información solicitada.
- Protección de la confidencialidad de los datos, de acuerdo con el secreto estadístico establecido en la Ley 17.374.

Las bases de datos de la ENE están disponibles en dos formatos:[^4]
- `.dta` (compatible con el software Stata, incluyendo bases con etiquetas de valores)
- `.csv` (*comma-separated values*, compatible con la mayoría de los softwares para análisis estadístico)

Para seleccionar la base de datos que se requiera consultar, se deben seguir tres pasos:
- **Paso 1.** Una vez abierta la página Web, se debe presionar la opción **BASES DE DATOS**. Al hacerlo se desplegarán todos los años con información disponible.
- **Paso 2.** Una vez seleccionado el año, se debe seleccionar una categoría para mostrar archivos, de acuerdo con las dos alternativas de formato disponibles vigentes.
- **Paso 3.** Finalmente, una vez seleccionado el formato, se desplegarán todos los trimestres, bastando sólo con presionar el ícono de descarga para que comience la bajada de la base requerida.

#### 2.1.2 Descarga de datos trimestrales usando URL
Las bases trimestrales de la ENE se almacenan siguiendo un patrón lógico en los URL de descarga de la página Web del INE:

`URL raíz / Año trimestre / Formato de descarga / Identificación de la base`

El detalle de cada uno de los componentes es el siguiente:
- **URL raíz:** Corresponde a `https://www.ine.cl/docs/default-source/ocupacion-y-desocupacion/bbdd`. Es invariable para todos los archivos.
- **Año trimestre:** abarca el período 2010 a 2026.[^5]
- **Formato de descarga:** considera las opciones `stata` o `csv`, según el formato del archivo.
- **Identificación de la base:** las bases de la ENE se estructuran con su propio patrón: `ene - año trimestre - número del trimestre - nombre del trimestre – tipo de archivo (.dta, o .csv)`. De este modo:
  - El **número del trimestre** va de 01 a 12, definido por el mes central. Por ejemplo, el trimestre julio-septiembre corresponderá al código 08, el noviembre-enero, a 12, y así sucesivamente.
  - El **nombre del trimestre** corresponde a las iniciales de cada mes que compone el trimestre, en minúsculas.

### Tabla 2. Equivalencia entre número y nombre del trimestre

| Trimestre | Número | Abreviación | Observaciones |
| :--- | :--- | :--- | :--- |
| Diciembre-febrero | 01 | def | Se considera el primer trimestre de cada año, por tener sólo un mes en el año anterior. |
| Enero-marzo | 02 | efm | |
| Febrero-abril | 03 | fma | |
| Marzo-mayo | 04 | mam | |
| Abril-junio | 05 | amj | |
| Mayo-julio | 06 | mjj | |
| Junio-agosto | 07 | jja | |
| Julio-septiembre | 08 | jas | |
| Agosto-octubre | 09 | aso | |
| Septiembre-noviembre | 10 | son | |
| Octubre-diciembre | 11 | ond | |
| Noviembre-enero | 12 | nde | Se considera el último trimestre de cada año, por tener sólo un mes en año siguiente. |

De este modo, es posible reconstruir el URL de un trimestre específico, facilitando su uso en cualquier software que permita programar descargas. Por ejemplo:
- El trimestre **EFM 2010 en formato Stata** corresponderá siempre a:  
  `https://www.ine.cl/docs/default-source/ocupacion-y-desocupacion/bbdd/2010/stata/ene-2010-02-efm.dta`
- El trimestre **JAS 2015 en formato CSV** corresponderá siempre a:  
  `https://www.ine.cl/docs/default-source/ocupacion-y-desocupacion/bbdd/2015/csv/ene-2015-07-jja.csv`

---

### 2.2 Uso de Banco de Datos ENE

#### 2.2.1 Antecedentes
El Banco de Datos de la Encuesta Nacional de Empleo (ENE) es un sistema de información orientado a la consulta directa y que permite a los usuarios realizar cruces de forma dinámica, sin necesidad de utilizar software de análisis estadístico como Stata o R.

Contiene toda la información registrada desde enero-marzo de 2010 al último trimestre móvil disponible y se ubica en el siguiente enlace: [http://bancodatosene.ine.cl/](http://bancodatosene.ine.cl/).

La actualización se realiza el mismo día de la publicación de las cifras de empleo, según el calendario oficial del INE. Los usuarios pueden consultar por un período específico (trimestre móvil) o una serie de períodos de varios trimestres.

#### 2.2.2 Instrucciones de uso
Una vez dentro del Banco de Datos, se debe detallar el cruce que se desea obtener en “Acceso de Información”. En ese caso, a modo de ejemplo, la tasa de desocupación para personas entre 20 y 24 años. Los pasos a seguir son los siguientes:

- **Paso 1. Seleccione tipo de información:**  
  En este caso, corresponde al segmento “Principales indicadores (tasas)”, ya que la tasa de desocupación se ubica en este grupo. Como información complementaria, hay otros tres segmentos dentro de la columna, por ejemplo “Ocupados”, “Desocupados e Inactivos” y “Todas las personas”, que señalan niveles (totales de población), de acuerdo a la clasificación de la población en función de su condición de actividad.
- **Paso 2. Seleccionar una medida:**  
  Debe seleccionar “Tasa de desocupación censo 2017”, dado que corresponde a las proyecciones que actualmente utiliza la ENE.
- **Paso 3. Variable para fila:**  
  Debe seleccionar el trimestre que desea analizar, en este caso, “Oct – Dic 2022”.  
  *(Como dato adicional, si se selecciona “Año trimestre móvil (Serie de tiempo desde EFM 2010)”, el sistema genera una serie con toda la información publicada desde el trimestre enero – marzo 2010 al último publicado).*
- **Paso 4. Variable para columna:**  
  En “Rango quinquenio edad”, debe seleccionar el tramo “De 20 a 24 años”.
- **Paso 5. Filtro:**  
  Seleccionar “Región”. Por defecto, entrega la tasa de desocupación a nivel nacional. Existen otros filtros posibles de realizar, por lo que se sugiere explorarlos en caso de requerirlo.
- **Paso 6. Generar resultados:**  
  Siguiendo los pasos señalados, arroja una tasa de desocupación de 16,7% para el tramo etario señalado.

Estos pasos deben realizarse tantas veces como resultados se requieran de la encuesta.

En sus estimaciones oficiales el INE utiliza un estándar institucional para la evaluación de la calidad de las estimaciones en encuestas de hogares. Por lo mismo, se recomienda a las personas usuarias aplicar dicho estándar, pues a mayor desagregación de la información no se puede asegurar su fiabilidad de la estimación (INE, 2020a).

Considerando lo anterior, el Banco de Datos ENE no utiliza este estándar, pues es una herramienta de consulta general. Por lo que el INE no será responsable por la interpretación y aplicación que la persona usuaria haga de los resultados; cualquier interpretación de los datos usando esta fuente excluye al INE de responsabilidad alguna.

---

## 3 CONSIDERACIONES SOBRE EL USO DE LA INFORMACIÓN

### 3.1 Aspectos generales
En relación a la información que se pone a disposición de las personas usuarias de los datos, es importante tener algunas consideraciones:

1. La información de la ENE se publica el último o penúltimo día hábil de cada mes. Si bien los datos se publican mensualmente, las bases contienen información de un trimestre completo, inmediatamente anterior al mes de publicación. Por ejemplo, en julio de 2020 se publica la información correspondiente al trimestre abril-junio. Debido a que cada mes se está agregando un nuevo trimestre, se debe eliminar el primero del trimestre anterior. Siguiendo con el mismo ejemplo, para el mes de agosto de 2021 se elimina el mes de abril y se agrega el de julio, conformando el trimestre mayo-julio. A esta lógica de publicación se le denomina **trimestres móviles**.
2. La actual serie de la ENE comienza en el trimestre móvil enero-marzo de 2010, siendo la que se pone a disposición del público en la página institucional de INE-Chile para su descarga directa. Para información anterior a este periodo, se deben solicitar los datos a través del portal de Atención Ciudadana del INE.
3. Los datos de la serie vigente no son comparables con series anteriores de la ENE, debido a la incorporación de importantes cambios conceptuales y metodológicos a partir de enero-marzo de 2010.
4. Si bien se entrega información sobre la comuna de residencia habitual de las personas en las bases de datos, la ENE **no tiene representatividad comunal**. Su diseño garantiza errores de muestreo aceptables sólo para los dominios nacional, nacional urbano, nacional rural, regional urbano (para todas las regiones) y regional rural (sólo para regiones Metropolitana, O’Higgins, Maule, Ñuble, La Araucanía, Los Ríos y Los Lagos) (INE, 2021a). El INE no se puede hacer cargo de estimaciones fuera de estos dominios oficiales de estudio, siendo responsabilidad de las personas investigadoras realizar las advertencias necesarias sobre esta situación.

### 3.2 Política de revisión y actualización de cifras
En línea con el Código de Buenas Prácticas de la Organización para la Cooperación y el Desarrollo Económicos (OCDE), el INE definió una política de revisión y actualización de cifras de la ENE, que se oficializó en febrero de 2020 (INE, 2020e).

Esta política responde a la necesidad de dar respuesta a la demanda de datos precisos que reflejen la realidad del mercado laboral y que permitan un mejor análisis de las variaciones trimestrales y anuales de forma coyuntural. En términos prácticos, se considera la revisión permanente del diseño metodológico y de las series de datos ya publicadas, incorporando actualizaciones en caso de ser pertinente.

El proceso de revisión se lleva a cabo en julio de cada año (INE, 2021b, 2022d, 2023b). Los resultados de este proceso tienen como consecuencia dos posibles escenarios:
- **No actualización de los datos**, manteniendo la serie de datos inalterable.
- **Actualización de los datos ya publicados**, teniendo que reconstruir una serie de manera retrospectiva, desde el trimestre móvil que se defina como punto de partida de la revisión de cifras. Esto implica metodológicamente poner a disposición las bases de datos con las actualizaciones correspondientes, de tal manera que los usuarios cuenten con toda la información para realizar análisis de impacto, además de toda la documentación sobre los ajustes y procedimientos realizados para actualizar la serie.

Es importante destacar que la revisión de cifras es propia de análisis tipo ex-post, que permite actualizar información sobre los procesos ya realizados para mejorar la precisión, en este caso, de la medición del fenómeno. Esto es especialmente necesario cuando el objetivo principal de la ENE es entregar información precisa sobre el mercado laboral, basada en marcos y diseños definidos con anterioridad.

---

## 4 INDICACIONES PARA EL USO DE LOS DATOS

La población objetivo de la ENE corresponde a la población en edad de trabajar, esto es, personas de quince años o más. Todas las estimaciones de empleo se acotan a esta definición, por lo que los filtros ya se encuentran incorporados. No obstante, la información sociodemográfica está disponible para la totalidad de los integrantes de un hogar.

Dado que la unidad de análisis corresponde a personas, en un contexto de diseño muestral polietápico, se utiliza un factor de expansión. Éste se interpreta como la cantidad de personas en la población que representa una persona en la muestra. De acuerdo con el diseño de la muestra, corresponde aplicar este factor a cada persona seleccionada.

En ese sentido, se deben tener tres consideraciones:
1. Entre el comienzo de la actual serie de la ENE y el trimestre octubre-diciembre de 2019, las bases de datos de la ENE incluyen dos factores de expansión, no comparables entre sí por consideraciones metodológicas:
   - **Factor tradicional (`fact`):** Se basa en las proyecciones de población del Censo 2002, utilizando una metodología de cálculo que divide a la población por sexo y según dos tramos etarios (personas menores de 15 años y personas de 15 años o más) (INE, 2018b). Este factor solo se encuentra disponible hasta el trimestre móvil octubre-diciembre de 2019, ya que a contar de la publicación del trimestre móvil noviembre-enero de 2020 se actualizó la serie completa de la ENE al factor calibrado a las proyecciones de población del Censo 2017.
   - **Factor calibrado (`fact_cal`):** Utiliza las proyecciones de población del Censo 2017 y una metodología llamada *raking*, de mayor precisión (INE, 2021a).
2. A partir del trimestre móvil noviembre-enero de 2019, las bases sólo contienen el factor calibrado (`fact_cal`).
3. Para el uso de bases anualizadas, utilizar el factor `fact_anual`.

---

## 5 DESCRIPCIÓN DE VARIABLES

En el marco del proyecto de fortalecimiento de la ENE (INE, 2020d), se incorporaron en el instrumento de recolección las últimas recomendaciones de la Organización Internacional del Trabajo (OIT) presentes en la resolución sobre las estadísticas de las relaciones de trabajo de 2018.

Si bien las preguntas que permiten identificar a las personas como ocupadas, desocupadas o fuera de la fuerza de trabajo se mantienen inalteradas, algunas preguntas de caracterización de estas categorías principales se vieron fortalecidas con el reemplazo y la inclusión de nuevas preguntas que han sido monitoreadas durante el año 2020-2021 para comenzar su difusión paulatina (INE, 2022a). Todos los casos en que se presenta esta situación se señalan en las observaciones.

---
[^1]: Para más información ver separata técnica *Política de revisión y actualización de cifras de la Encuesta Nacional de Empleo (ENE)*, publicada el 30 de julio de 2021 (INE, 2020e).
[^2]: Adicionalmente se incluyen cuatro conurbaciones, que no se definen como dominio de estudio: Gran Santiago, Gran Valparaíso, Gran Concepción y Coquimbo-La Serena.
[^3]: Disponible solo desde el trimestre agosto-octubre de 2018, debido a la fecha de creación de la región del Ñuble.
[^4]: Las bases en formato SPSS fueron eliminadas de la página web del INE en julio de 2025, debido a que dejaron de actualizarse a partir de junio de 2024.
[^5]: 2026 es el último periodo publicado a la fecha de confección del documento, no obstante, esto se extiende en el tiempo.



### 5.1 Variables de contexto

#### 5.1.1 Información de contexto

| Variable | Etiqueta | Valores | Observaciones |
| :--- | :--- | :--- | :--- |
| `ano_trimestre` | Año | 2010 - 2026 | Señala el año al cual corresponde el trimestre de la base de datos (véase sección 2.1.2). |
| `mes_central` | Trimestre | 1: Diciembre – febrero<br>2: Enero – marzo<br>3: Febrero – abril<br>4: Marzo – mayo<br>5: Abril – junio<br>6: Mayo – julio<br>7: Junio – agosto<br>8: Julio – septiembre<br>9: Agosto – octubre<br>10: Septiembre – noviembre<br>11: Octubre – diciembre<br>12: Noviembre – enero | Señala el trimestre móvil al cual corresponde la base de datos (véase sección 2.1.2). |
| `ano_encuesta` | Año de recolección de datos | 2010 - 2026 | Señala el año del periodo de recolección de datos. |
| `mes_encuesta` | Mes de recolección de datos | 1: Enero<br>2: Febrero<br>3: Marzo<br>4: Abril<br>5: Mayo<br>6: Junio<br>7: Julio<br>8: Agosto<br>9: Septiembre<br>10: Octubre<br>11: Noviembre<br>12: Diciembre | Señala el mes del periodo de recolección de datos. |

#### 5.1.2 Información muestral y de identificación

| Variable | Etiqueta | Valores | Observaciones |
| :--- | :--- | :--- | :--- |
| `region` | Región | Ver detalle de regiones en Anexo 1 | Los nombres oficiales de las regiones han sido simplificados con el fin de facilitar la visualización de datos. Para mayor detalle, véase Ley 21.074 de Fortalecimiento de la Regionalización del País, artículo 9, promulgada en 2018. |
| `provincia` | Provincia | Ver detalle de provincias en Anexo 1 | |
| `r_p_c` | Comuna | Ver detalle de comunas en Anexo 1 | |
| `tipo` | Tipo de estrato | 1: Ciudad (CD)<br>2: Resto de Área Urbana (RAU)<br>3: Rural | Categoría 2 Resto de Área Urbana (RAU) dejó de utilizarse a partir de EFM 2022. |
| `estrato` | Estrato muestral | | |
| `conglomerado` | Conglomerado | | Vigente desde NDE 2019 a la fecha. Permite identificar el conglomerado correspondiente a la unidad primaria de muestreo. |
| `id_directorio` | Manzana / sección | | Descontinuada. Producida entre EFM 2010 y OND 2019. Permite identificar el conglomerado correspondiente a la unidad primaria de muestreo, los cuales se denominaban manzanas en estrato urbano y secciones en RAU y rurales. |
| `id_identificacion` | Identificador único del hogar | | |
| `hogar` | Número del hogar dentro de la vivienda | | |
| `idrph` | Identificador único de personas | | |
| `nro_linea` | Número de línea de persona | | Corresponde al orden con el cual la persona fue identificada en el cuestionario. |

---

### 5.2 Cuestionario sociodemográfico

#### 5.2.1 Características básicas

| Variable | Descripción | Categorías observadas | Observaciones |
| :--- | :--- | :--- | :--- |
| `proveedor` | Proveedor/a principal del hogar | 0: No corresponde<br>1: Proveedor/a principal | |
| `parentesco` | Parentesco con proveedor/a principal del hogar | 1: Persona proveedora principal<br>2: Cónyuge<br>3: Conviviente<br>4: Hijo/a o hijastro/a<br>5: Yerno o nuera<br>6: Nieto/a<br>7: Hermano/a o cuñado/a<br>8: Padres o suegros<br>9: Otro pariente<br>10: No pariente<br>11: Servicio doméstico<br>88: No sabe<br>99: No responde | Entre EFM 2020 y NDE 2019, el código 1 identificaba al jefe o jefa de hogar, concepto que fue reemplazado por proveedor/a principal a partir de DEF 2020. |
| `sexo` | Sexo | 1: Hombre<br>2: Mujer | Corresponde al sexo declarado respecto a la persona entrevistada (INE, 2022b). |
| `edad` | Edad | 0 – 120 | Señala la edad de la persona durante la semana de referencia de la encuesta. |
| `est_conyugal` | Estado civil o conyugal | 0: No aplica<br>1: Casado/a<br>2: Conviviente<br>3: Soltero/a<br>4: Viudo/a<br>5: Separado/a de hecho o anulado/a<br>6: Divorciado/a<br>88: No sabe<br>99: No responde | |

#### 5.2.2 Migración y nacionalidad

| Variable | Descripción | Categorías observadas | Observaciones |
| :--- | :--- | :--- | :--- |
| `mig1` | ¿En qué país vivía hace cinco años? | 1: En esta comuna<br>2: En otra comuna<br>3: En otro país<br>4: No había nacido<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha como nueva dimensión de análisis (INE, 2021c). |
| `mig2_cod` | ¿En qué comuna? | Ver detalle de comunas en Anexo 1<br>88888: No sabe<br>99999: No responde | Vigente desde EFM 2020 a la fecha como nueva dimensión de análisis (INE, 2021c). |
| `mig3_cod` | ¿En qué país? | Ver detalle de países en Anexo 2<br>898: Zona no especificada<br>999: Sin información | Vigente desde EFM 2020 a la fecha como nueva dimensión de análisis (INE, 2021c). |
| `mig4` | Cuando nació, ¿en qué comuna o país vivía su madre? | 1: En esta comuna<br>2: En otra comuna<br>3: En otro país<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha como nueva dimensión de análisis (INE, 2021c). |
| `mig5_cod` | ¿En qué comuna? | Ver detalle de comunas en Anexo 1<br>88888: No sabe<br>99999: No responde | Vigente desde EFM 2020 a la fecha como nueva dimensión de análisis (INE, 2021c). |
| `mig6_cod` | ¿En qué país? | Ver detalle de países en Anexo 2<br>898: Zona no especificada<br>999: Sin información | Vigente desde EFM 2020 a la fecha como nueva dimensión de análisis (INE, 2021c). |
| `nacionalidad` | Nacionalidad | Ver detalle de países en Anexo 2<br>898: Zona no especificada<br>999: Sin información | |

#### 5.2.3 Pueblos originarios

| Variable | Descripción | Categorías observadas | Observaciones |
| :--- | :--- | :--- | :--- |
| `orig1` | ¿Se considera perteneciente a algún pueblo indígena u originario? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha como nueva dimensión de análisis (INE, 2021c). |
| `orig2` | ¿A cuál? | 1: Mapuche<br>2: Aymara<br>3: Rapa Nui<br>4: Lican Antai o Atacameños<br>5: Quechua<br>6: Colla<br>7: Diaguita<br>8: Kawésqar<br>9: Yagán o Yámana<br>10: Chango<br>11: Selk’nam<br>20: Otro<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha como nueva dimensión de análisis (INE, 2021c). |
| `orig3` | Especifica orig2=20 (Otro) | Pregunta abierta. | Vigente desde EFM 2020 a la fecha como nueva dimensión de análisis (INE, 2021c). |

#### 5.2.4 Educación

| Variable | Descripción | Categorías observadas | Observaciones |
| :--- | :--- | :--- | :--- |
| `curso` | Curso más alto aprobado | 1 – 8<br>88: No sabe<br>99: No responde | Vigente desde EFM 2010 a la fecha. Equivale a edu1 y se mantiene solo con fines de comparabilidad. |
| `nivel` | Nivel educacional más alto aprobado | 0: Nunca estudió<br>1: Sala cuna<br>2: Kínder<br>3: Básica o primaria<br>4: Media común<br>5: Media técnico profesional<br>6: Humanidades<br>7: Centro formación técnica<br>8: Instituto profesional<br>9: Universitario<br>10: Post títulos<br>11: Magíster<br>12: Doctorado<br>13: Educación diferencial<br>14: Normalista<br>88: No sabe<br>99: No responde | Vigente desde EFM 2010 a la fecha. |
| `termino_nivel` | Término de nivel educacional | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde EFM 2010 a la fecha. Equivale a edu3 y se mantiene solo con fines de comparabilidad. |
| `estudia_actual` | ¿Se encuentra estudiando actualmente en un establecimiento educacional? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha. Réplica de variable edu4 creada con fines analíticos. Corresponde a cuestionario vigente. |
| `edu1` | ¿Cuál es el curso o año más alto aprobado? | 0: Sin curso<br>1: Primer año<br>2: Segundo año<br>3: Tercer año<br>4: Cuarto año<br>5: Quinto año<br>6: Sexto año<br>7: Séptimo año<br>8: Octavo año<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha. |
| `edu2` | ¿A cuál de los siguientes niveles corresponde el curso declarado? | 1: Nunca asistió<br>2: Educación especial (diferencial)<br>3: Sala cuna o nivel medio de jardín infantil<br>4: Pre kínder<br>5: Kínder<br>6: Educación básica<br>7: Educación primaria (sistema antiguo)<br>8: Educación media científico-humanista o artística<br>9: Educación media técnica-profesional<br>10: Educación humanidades (sistema antiguo)<br>11: Educación técnica comercial, industrial o normalista (sistema antiguo)<br>12: Técnico nivel superior (incluye suboficial FFAA)<br>13: Profesional (incluye oficial FFAA)<br>14: Diplomados o postítulos (de un semestre o más)<br>15: Magíster<br>16: Doctorado<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha. No comparable con variable nivel. Son otras categorías, correspondientes a cuestionario vigente. |
| `edu3` | ¿Terminó el nivel antes declarado? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha. |
| `edu4` | ¿Se encuentra estudiando actualmente? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha. Réplica de variable estudia_actual creada con fines analíticos. Corresponde a cuestionario vigente. |

---

### 5.3 Cuestionario central de empleo

#### 5.3.1 Sección A: Situación laboral en la semana de referencia

| Variable | Descripción | Categorías observadas | Observaciones |
| :--- | :--- | :--- | :--- |
| `a1` | La semana pasada, es decir, entre lunes y domingo, ¿trabajó por lo menos una hora? | 1: Sí<br>2: No | |
| `a2` | Independientemente de lo que acaba de decir, ¿hizo algún negocio, "pololo" u otra actividad por cuenta propia por lo menos durante una hora? | 1: Sí<br>2: No | |
| `a3` | Por ese trabajo, ¿recibió o recibirá un pago en dinero o en especie? | 1: Sí<br>2: No | |
| `a4` | Ese trabajo, ¿fue realizado para la empresa o negocio perteneciente a un miembro de su hogar? | 1: Sí<br>2: No | |
| `a5` | Aunque no trabajó la semana pasada, ¿tenía durante dicho periodo un empleo, negocio u otra actividad por la que recibe o recibirá un pago en dinero o en especie? | 1: Sí<br>2: No | |
| `a6` | ¿Por qué razón no trabajó la semana pasada? | 1: Vacaciones o permisos<br>2: Licencia médica<br>3: Por horario o jornada variable o flexible<br>4: Huelga o conflicto laboral<br>5: Asistencia a cursos de capacitación<br>6: Problemas de salud<br>7: Suspensión temporal del trabajo<br>8: No tuvo pedidos o clientes<br>9: Razones climáticas o catástrofes naturales<br>10: Su trabajo es ocasional<br>11: Razones económicas o técnicas de la empresa o negocio<br>12: Su trabajo es estacional<br>13: Clausura de negocio o de empresa<br>14: Otras razones (especificar) | |
| `a6_otro` | Especifica a6 = Otras razones de ausencia del trabajo | Pregunta abierta. | |
| `a7` | Durante este período en que no trabajó, ¿siguió recibiendo sueldo o ganancias? | 1: Sí<br>2: No | |
| `a8` | ¿En cuánto tiempo más volverá a trabajar? | 1: En cuatro semanas o menos<br>2: En más de cuatro semanas<br>3: No sabe cuándo volverá a trabajar | |
| `a9` | Si las restricciones por la pandemia del COVID-19 se terminaran en las próximas cuatro semanas, ¿cree que podrá volver a su trabajo? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Descontinuada. Producida entre MAM 2020 y NDE 2022. Su inclusión fue recomendada por OIT en el contexto del impacto del COVID-19 en la población ocupada (INE, 2020b). |

#### 5.3.2 Sección B: Caracterización de la actividad principal

| Variable | Descripción | Categorías observadas | Observaciones |
| :--- | :--- | :--- | :--- |
| `b1` | Grupo de ocupación según CIUO-08 | Ver detalle de grupos de ocupación en Anexo 3<br>999: Sin información | Vigente desde EFM 2017 a la fecha. |
| `b1_ciuo88` | Grupo de ocupación según CIUO-88 | Ver detalle de grupos de ocupación en Anexo 3 | Descontinuada. Producida entre EFM 2010 y EFM 2019. |
| `b2` | Realizó ese trabajo… | 1: …¿para su propio negocio, empresa o actividad por cuenta propia?<br>2: …¿como empleado u obrero para un patrón, empresa, negocio o institución, o empleado(a) de casa particular?<br>3: …¿para el negocio, empresa o actividad por cuenta propia de un miembro de esta familia? | |
| `b3` | Por ese trabajo… | 1: …¿recibe sueldo o salario?<br>2: …¿retira dinero?<br>3: …¿retira sólo mercadería?<br>4: …¿no retira dinero ni mercadería? | |
| `b4` | En ese trabajo ¿emplea personas para su negocio o actividad? No incluya a miembros de su familia no remunerados. | 1: Sí<br>2: No | |
| `b5` | El negocio, empresa o institución donde trabajó la semana pasada era... | 1: …¿estatal?<br>2: …¿privado?<br>3: …¿hogar particular? | |
| `b6` | Su trabajo en ese hogar es… | 1: …¿servicio doméstico puertas afuera?<br>2: …¿servicio doméstico puertas adentro?<br>3: …¿otros servicios? | |
| `b7_1` | En ese empleo, le otorgan vacaciones anuales | 1: Sí<br>2: No<br>3: No sabe / No responde | Descontinuada. Producida entre EFM 2010 y JJA 2017 (véase Anexo 4). |
| `b7_2` | En ese empleo, le otorgan días pagados por enfermedad | 1: Sí<br>2: No<br>3: No sabe / No responde | Descontinuada. Producida entre EFM 2010 y JJA 2017 (véase Anexo 4). |
| `b7_3` | En ese empleo, le otorgan cotización en sistema previsional o de pensión | 1: Sí<br>2: No<br>3: No sabe / No responde | Descontinuada. Producida entre EFM 2010 y JJA 2017 (véase Anexo 4). |
| `b7_4` | En ese empleo, le otorgan cotización en sistema de salud | 1: Sí<br>2: No<br>3: No sabe / No responde | Descontinuada. Producida entre EFM 2010 y JJA 2017 (véase Anexo 4). |
| `b7_5` | En ese empleo, le otorgan cotización por seguro de desempleo | 1: Sí<br>2: No<br>3: No sabe / No responde | Descontinuada. Producida entre EFM 2010 y JJA 2017 (véase Anexo 4). |
| `b7_6` | En ese empleo, le otorgan permiso por maternidad o paternidad | 1: Sí<br>2: No<br>3: No sabe / No responde | Descontinuada. Producida entre EFM 2010 y JJA 2017 (véase Anexo 4). |
| `b7_7` | En ese empleo, le otorgan servicio de guarderías infantiles | 1: Sí<br>2: No<br>3: No sabe / No responde | Descontinuada. Producida entre EFM 2010 y JJA 2017 (véase Anexo 4). |
| `b7a_1` | Su empleador, ¿cotiza por usted en el sistema previsional o de pensión? | 1: Sí<br>2: No<br>77: No aplica<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha (véase Anexo 4). |
| `b7a_2` | Su empleador, ¿cotiza por usted en el sistema de salud (público o privado)? | 1: Sí<br>2: No<br>77: No aplica<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha (véase Anexo 4). |
| `b7a_3` | Su empleador, ¿cotiza por usted en el sistema de seguro de desempleo? | 1: Sí<br>2: No<br>77: No aplica<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha (véase Anexo 4). |
| `b7b_1` | En este trabajo, ¿tiene derecho, aunque no utilice, a vacaciones anuales? | 1: Sí<br>2: No<br>77: No aplica<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha (véase Anexo 4). |
| `b7b_2` | En este trabajo, ¿tiene derecho, aunque no utilice, a días pagados por enfermedad? | 1: Sí<br>2: No<br>77: No aplica<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha (véase Anexo 4). |
| `b7b_3` | En este trabajo, ¿tiene derecho, aunque no utilice, a permiso por maternidad o paternidad? | 1: Sí<br>2: No<br>77: No aplica<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha (véase Anexo 4). |
| `b7b_4` | En este trabajo, ¿tiene derecho, aunque no utilice, a servicio de guardería infantil? | 1: Sí<br>2: No<br>77: No aplica<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha (véase Anexo 4). |
| `b8` | En ese empleo, ¿tiene contrato escrito? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | |
| `b9` | La duración de ese contrato o acuerdo de trabajo es... | 1: …¿definido, es decir, con plazo de término o a plazo fijo?<br>2: …¿indefinido, es decir, sin plazo de término?<br>88: No sabe<br>99: No responde | |
| `b10` | Su contrato o acuerdo definido es… | 1: …¿limitado a la temporada?<br>2: …¿limitado al término de la obra, proyecto o actividad?<br>3: …¿limitado a menos de tres meses por contrato o acuerdo (a prueba, práctica)?<br>4: …¿renovable una vez al año?<br>5: …¿por reemplazo?<br>88: No sabe<br>99: No responde | |
| `b11` | Al momento de recibir sus ingresos... | 1: …¿entrega una boleta de honorarios?<br>2: …¿recibe una liquidación de sueldo?<br>3: …¿entrega un comprobante o recibo?<br>4: …¿no recibe ni entrega comprobante?<br>5: …¿entrega boleta o factura? | Descontinuada. Producida entre EFM 2010 y DEF 2020. |
| `b12` | Está contratado o tiene un acuerdo de trabajo… | 1: …¿directamente con la empresa en donde trabaja?<br>2: …¿con un contratista o subcontratista de bienes o servicios?<br>3: …¿con una empresa de servicios temporales o suministradora de trabajadores?<br>4: …¿con un enganchador (contratista agrícola)?<br>88: No sabe<br>99: No responde | |
| `b13_ciiu_rev3` | Rama de actividad económica de empresa que le paga según CIIU Rev. 3 | Ver detalle de rama de actividad en Anexo 5 | Descontinuada. Producida entre EFM 2010 y OND 2016. |
| `b13_rev4cl_caenes` | Rama de actividad económica de empresa que le paga según CAENES (adaptación de CIIU Rev. 4.cl) | Ver detalle de rama de actividad en Anexo 5<br>999: Sin información | Variable incorporada a partir de trimestre EFM 2016. |
| `b14_ciiu_rev3` | Rama de actividad económica de empresa donde trabaja según CIIU Rev. 3 | Ver detalle de rama de actividad en Anexo 5 | Descontinuada. Producida entre EFM 2010 y OND 2016. |
| `b14_rev4cl_caenes` | Rama de actividad económica de empresa donde trabaja según CAENES (adaptación de CIIU Rev. 4.cl) | Ver detalle de rama de actividad en Anexo 5<br>999: Sin información | Variable incorporada a partir de trimestre EFM 2013. |
| `b15_1` | En todo el país, ¿cuántas personas trabajan en esa empresa, negocio, institución que le paga o actividad por cuenta propia? | 1: Menos de 5<br>2: De 5 a 10 personas<br>3: Entre 11 y 49<br>4: Entre 50 y 199<br>5: 200 y más personas<br>88: No sabe<br>99: No responde | |
| `b15_2` | Número exacto, hasta 10 personas | Valores de 1 a 10.<br>88: No sabe<br>99: No responde | |
| `b16` | En la semana que terminó el domingo pasado, ¿dónde realizó principalmente sus tareas? | 1: En instalaciones u oficina del cliente o empleador<br>2: En la casa del empleador o cliente<br>3: En instalaciones u oficinas propias o arrendadas<br>4: En la oficina, local, taller o fábrica, anexo a su hogar (en el mismo predio)<br>5: En su propio hogar<br>6: En la calle o vía pública<br>7: En obras de construcción, mineras o similares<br>8: En un predio agrícola o espacio marítimo o aéreo<br>9: En otros lugares (especifique)<br>88: No sabe<br>99: No responde | |
| `b16_otro` | Especifica b16 = En otros lugares | Pregunta abierta. | |
| `b17_mes` | Y, ¿desde cuándo trabaja para ese empleador, en ese negocio o actividad por cuenta propia? Mes | 1: Enero ... 12: Diciembre<br>88: No sabe<br>99: No responde | |
| `b17_ano` | Y, ¿desde cuándo trabaja para ese empleador, en ese negocio o actividad por cuenta propia? Año | 8888: No sabe<br>9999: No responde | |
| `b18_codigo` | ¿En qué comuna se ubica la empresa, negocio, institución o actividad por cuenta propia donde realizó su trabajo? | Ver detalle de comunas en Anexo 1<br>Ver detalle de países en Anexo 2<br>88888: No sabe<br>99999: No responde | A contar de trimestre DEF 2020, se permite indicar el nombre de otro país. |
| `b18_region` | ¿En qué región se ubica la empresa, negocio, institución o actividad por cuenta propia donde realizó su trabajo? | Ver detalle de regiones en Anexo 1<br>88: No sabe<br>99: No responde | |
| `b18_varias` | ¿Realizó su trabajo en solamente una comuna? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | |
| `b19` | Durante la semana de referencia, además del trabajo descrito, ¿tuvo algún otro empleo o hizo algún negocio, "pololo" u actividad remunerada por cuenta propia por lo menos durante una hora? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | |
| `dependencia_segunda` | Ese otro trabajo, ¿lo hacía para su propia empresa, negocio o actividad por cuenta propia? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha como nueva dimensión de análisis (INE, 2021d). |

#### 5.3.3 Informalidad laboral

*Nota: Las preguntas sobre informalidad laboral fueron incorporadas a la ENE en el mes de julio de 2017 (JAS 2017). Para mayores antecedentes, véase INE, 2017.*

| Variable | Descripción | Categorías observadas | Observaciones |
| :--- | :--- | :--- | :--- |
| `i1` | La empresa, negocio o institución que le paga su sueldo, ¿está registrada en el Servicio de Impuestos Internos (SII) o tiene iniciación de actividades? | 1: Sí<br>2: No sabe, pero la empresa entrega boleta o factura por las ventas o prestación de servicios<br>3: No, ningún tipo de registro<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha (INE, 2017). |
| `i2` | La empresa, negocio o institución que le paga su sueldo, ¿cuenta con los servicios de un contador o tiene oficina de contabilidad? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha (INE, 2017). |
| `i3` | ¿Cuál es el nombre de la empresa, negocio o institución que le paga su sueldo? | 1: (Informante identifica nombre)<br>2: El negocio no tiene nombre<br>3: Trabaja para un hogar particular<br>4: Trabaja para otro asalariado<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha (INE, 2017). El nombre no se publica por estar regido por secreto estadístico. |
| `i3_v` | Verificación de respuesta entregada con Directorio de Empresas del INE | 0: Nombre no verificado<br>1: Nombre verificado | Vigente desde JAS 2017 a la fecha (INE, 2017). Variable creada tras la identificación de la empresa en registros administrativos. |
| `i4` | La empresa, negocio o actividad en la que trabaja, ¿está registrada en el Servicio de Impuestos Internos (SII) o tiene iniciación de actividades? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha (INE, 2017). |
| `i5` | La empresa, negocio o actividad en la que trabaja, ¿se encuentra registrada como… | 1: …trabajador independiente (con boleta de honorarios)<br>2: …persona natural (el RUT de la empresa es igual al RUT del dueño)<br>3: …¿otro tipo de registro?<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha (INE, 2017). |
| `i6` | La empresa, negocio o actividad por cuenta propia… | 1: …¿acude a los servicios de un contador para llevar la contabilidad completa?<br>2: …¿se encuentra acogido al régimen de contabilidad simplificada?<br>3: …¿sólo cuenta con registros personales de gastos e ingresos?<br>4: No cuenta con ningún tipo de contabilidad<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha (INE, 2017). |
| `i7` | A través de la contabilidad, ¿se pueden separar los gastos del negocio con los del hogar? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha (INE, 2017). |

#### 5.3.4 Asociatividad laboral en la ocupación principal

| Variable | Descripción | Categorías observadas | Observaciones |
| :--- | :--- | :--- | :--- |
| `f7a` | Participación en sindicato | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha como nueva dimensión de análisis (INE, 2024b). |
| `f7b` | Participación en asociación de funcionarios | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha como nueva dimensión de análisis (INE, 2024b). |
| `f7c` | Participación en asociación gremial | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha como nueva dimensión de análisis (INE, 2024b). |
| `f7d` | Participación en colegio profesional | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha como nueva dimensión de análisis (INE, 2024b). |
| `f7e` | Participación en otro tipo de organizaciones | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde JAS 2017 a la fecha como nueva dimensión de análisis (INE, 2024b). |

#### 5.3.5 Situación en la ocupación

| Variable | Descripción | Categorías observadas | Observaciones |
| :--- | :--- | :--- | :--- |
| `de_1a` | Para la realización del trabajo, ¿requiere de un local, establecimiento o predio? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha (INE, 2026). |
| `de_1b` | ¿Quién es el propietario o arrendatario del local, instalación o predio donde trabaja? | 1: [nombre de la persona]<br>2: Un socio de [nombre de persona]<br>3: Otra persona que no es socia<br>4: Otra empresa<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha (INE, 2026). |
| `de_2a` | En el trabajo, ¿utiliza algún tipo de maquinaria? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha (INE, 2026). |
| `de_2b` | ¿Quién es propietario o arrendatario de las máquinas con las que trabaja? | 1: [nombre de la persona]<br>2: Un socio de [nombre de persona]<br>3: Otra persona que no es socia<br>4: Otra empresa<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha (INE, 2026). |
| `de_3a` | En el trabajo, ¿utiliza algún vehículo de transporte? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha (INE, 2026). |
| `de_3b` | ¿Quién es el propietario o arrendatario del vehículo de transporte que utiliza en su trabajo? | 1: [nombre de la persona]<br>2: Un socio de [nombre de persona]<br>3: Otra persona que no es socia<br>4: Otra empresa<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha (INE, 2026). |
| `do_1` | En su trabajo, ¿quién decide sobre el horario de trabajo? | 1: [nombre de la persona]<br>2: Un socio de [nombre de persona]<br>3: Un cliente<br>4: Un proveedor<br>5: Otro<br>6: Institución pública<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha (INE, 2026). |
| `do_2` | En su trabajo, ¿quién decide sobre el lugar, rutas o zonas donde realiza su actividad? | 1: [nombre de la persona]<br>2: Un socio de [nombre de persona]<br>3: Un cliente<br>4: Un proveedor<br>5: Otro<br>6: Institución pública<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha (INE, 2026). |
| `do_3` | En su trabajo, ¿quién decide el tipo de producto o servicio que destina a la venta? | 1: [nombre de la persona]<br>2: Un socio de [nombre de persona]<br>3: Un cliente<br>4: Un proveedor<br>5: Otro<br>6: Institución pública<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha (INE, 2026). |
| `do_4` | En su trabajo, ¿quién decide sobre el precio de productos o servicios ofrecidos? | 1: [nombre de la persona]<br>2: Un socio de [nombre de persona]<br>3: Un cliente<br>4: Un proveedor<br>5: Otro<br>6: Institución pública<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha (INE, 2026). |
| `re1` | Por su actividad principal, ¿su pago fue a través de sueldo, salario o jornal? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha (INE, 2026). |
| `re2` | Por su actividad principal, ¿su pago fue por pieza o unidad vendida? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha (INE, 2026). |
| `re3` | Por su actividad principal, ¿su pago fue por comisión? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha (INE, 2026). |
| `re4` | Por su actividad principal, ¿su pago fue mediante un cobro por servicio prestado? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha (INE, 2026). |
| `re5` | Por su actividad principal, ¿su pago fue mediante propina? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha (INE, 2026). |
| `re6` | Por su actividad principal, ¿su pago fue obtenido mediante ganancias o utilidades de una actividad? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020 a la fecha (INE, 2026). |

#### 5.3.6 Impacto de pandemia COVID-19 en personas ocupadas

| Variable | Descripción | Categorías observadas | Observaciones |
| :--- | :--- | :--- | :--- |
| `i11` | Comparando los ingresos recibidos por su actividad principal en mes anterior, respecto a sus ingresos habituales, ¿disminuyeron, se mantuvieron o aumentaron? | 1: Disminuyeron<br>2: Se mantuvieron<br>3: Aumentaron<br>77: No tenía ese empleo<br>88: No sabe<br>99: No responde | Descontinuada. Vigente entre MAM 2020 y OND 2021. |
| `i12` | Comparando con sus ingresos habituales, ¿cuánto de los ingresos de su actividad principal recibió en el mes anterior? | 1: Más de la mitad<br>2: La mitad<br>3: Menos de la mitad<br>4: No recibió ingresos<br>88: No sabe<br>99: No responde | Descontinuada. Vigente entre MAM 2020 y OND 2021. |
| `i13_1` a `i13_11` | Medidas de financiamiento de gastos del hogar: Reducir gastos (`_1`), Trabajar más horas (`_2`), Buscar otro trabajo (`_3`), Usar ahorros (`_4`), Ayuda familiares (`_5`), Ayuda Estado (`_6`), Ayuda ONGs/Iglesias (`_7`), Tarjeta/Línea crédito (`_8`), Préstamo bancario (`_9`), Préstamo familiar (`_10`), No hará nada (`_11`), NS (`_88`), NR (`_99`) | 1: Sí | Descontinuadas. Vigentes entre MAM 2020 y OND 2021. |
| `i13_total` | Número de medidas de financiamiento de gastos del hogar | 1 – 10 | Descontinuada. Sumatoria de respuestas afirmativas de i13_1 a i13_10. |

#### 5.3.7 Sección C: Horas trabajadas

| Variable | Descripción | Categorías observadas | Observaciones |
| :--- | :--- | :--- | :--- |
| `c1` | ¿Qué tipo de jornada tiene en su trabajo? | 1: Completa<br>2: Parcial | Descontinuada. Producida entre EFM 2010 y OND 2019. |
| `turno` | ¿Trabaja por sistema de turno? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Incorporada a partir de EFM 2020 (INE, 2022). |
| `turno_d` | Actividad principal: Días trabajados habitualmente en el turno | 888: No sabe<br>999: No responde | Incorporada a partir de EFM 2020. |
| `turno_de` | Actividad principal: Días de descanso habituales en el turno | 888: No sabe<br>999: No responde | Incorporada a partir de EFM 2020. |
| `turno_h` | Actividad principal: Horas diarias trabajadas habitualmente en el turno | 888: No sabe<br>999: No responde | Incorporada a partir de EFM 2020. |
| `turno_t` | Actividad principal: Total horas trabajadas habitualmente en el turno | 8888: No sabe<br>9999: No responde | Incorporada a partir de EFM 2020. |
| `c2_1_1` | Actividad principal: Horas diarias trabajadas habitualmente | 888: No sabe<br>999: No responde | |
| `c2_1_2` | Actividad principal: Días a la semana trabajados habitualmente | 888: No sabe<br>999: No responde | |
| `c2_1_3` | Actividad principal: Total horas semanales trabajadas habitualmente | 888: No sabe<br>999: No responde | |
| `c2_2_1` | Actividad secundaria: Horas diarias trabajadas habitualmente | 888: No sabe<br>999: No responde | |
| `c2_2_2` | Actividad secundaria: Días a la semana trabajados habitualmente | 888: No sabe<br>999: No responde | |
| `c2_2_3` | Actividad secundaria: Total horas semanales trabajadas habitualmente | 888: No sabe<br>999: No responde | |
| `c3_1` | Actividad principal: Horas diarias contratadas o acordadas | 888: No sabe<br>999: No responde | |
| `c3_2` | Actividad principal: Días a la semana contratados o acordados | 888: No sabe<br>999: No responde | |
| `c3_3` | Actividad principal: Total horas semanales contratadas o acordadas | 888: No sabe<br>999: No responde | |
| `turno_cont_d` | Actividad principal: Días contratados o acordados en el turno | 888: No sabe<br>999: No responde | Incorporada a partir de EFM 2020. |
| `turno_cont_de`| Actividad principal: Días de descanso contratados o acordados en el turno | 888: No sabe<br>999: No responde | Incorporada a partir de EFM 2020. |
| `turno_cont_h` | Actividad principal: Horas diarias contratadas o acordadas en el turno | 888: No sabe<br>999: No responde | Incorporada a partir de EFM 2020. |
| `turno_cont_t` | Actividad principal: Total horas contratadas o acordadas en el turno | 8888: No sabe<br>9999: No responde | Incorporada a partir de EFM 2020. |
| `c4` | ¿Le pagan habitualmente las horas extras en su actividad principal? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | |
| `c5` | La semana pasada, ¿trabajó más horas que las habituales en su actividad principal? (sobre tiempo u horas extras, pagadas o no) | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | |
| `c6` | ¿Cuántas horas más de las habituales trabajó la semana pasada? | 888: No sabe<br>999: No responde | |
| `c7` | La semana pasada, ¿trabajó menos horas que las habituales en su actividad principal? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | |
| `c8` | ¿Cuántas horas menos de las habituales trabajó la semana pasada? | 888: No sabe<br>999: No responde | |
| `c9` | ¿Cuál fue la principal razón por la cual trabajó un número de horas diferente a lo habitual durante la semana pasada en su actividad principal? | 1: Por vacaciones, permiso o días festivos<br>2: Por razones climáticas o catástrofes naturales<br>3: Por enfermedad, incapacidad temporal o accidente<br>4: Porque es temporada baja<br>5: Hubo menos horas de trabajo por razones técnicas o económicas<br>6: Por razones personales o responsabilidades familiares<br>7: Porque tiene horario variable o flexible<br>8: Porque comenzó o cambió de empleo<br>9: Por conflicto laboral<br>10: Participó en cursos de capacitación<br>11: Representación sindical<br>12: Término de empleo sin haber comenzado otro<br>13: Terminar un proyecto, obra o faena<br>14: Horario flexible<br>15: Temporada alta<br>16: Aprovechar una oportunidad<br>17: Tenía trabajo acumulado<br>18: Recuperar horas no trabajadas<br>19: Si no lo hace podría perder el trabajo<br>20: Otra razón<br>88: No sabe<br>99: No responde | |
| `c9_otro` | Especifica c9 | Pregunta abierta. | |
| `c10` | Si de usted dependiera, ¿trabajaría habitualmente más horas de las que trabaja en la actualidad? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | |
| `c11` | Pero, si se diera la posibilidad, ¿estaría disponible para trabajar más horas a la semana? | 1: Sí, de inmediato<br>2: En los próximos 15 días<br>3: En un mes más<br>4: No tiene disponibilidad<br>88: No sabe<br>99: No responde | |
| `adicionales_h`| Horas diarias adicionales a la semana que podría trabajar habitualmente | 888: No sabe<br>999: No responde | Incorporada a partir de EFM 2020. |
| `adicionales_d`| Días adicionales a la semana que podría trabajar habitualmente | 888: No sabe<br>999: No responde | Incorporada a partir de EFM 2020. |
| `adicionales_t`| Total horas adicionales a la semana que podría trabajar habitualmente | 888: No sabe<br>999: No responde | Incorporada a partir de EFM 2020. |
| `c12` | ¿Cuál es la razón por la cual no trabaja más horas? | 1: La empresa no dispone de más horas / No hay más trabajo<br>2: No hay más clientes, temporada baja<br>3: No cancelan las horas extras<br>4: Razones personales<br>5: Cuidado de personas dependientes<br>6: Falta capital, local, mercadería<br>7: Por estudios<br>8: Factores climáticos<br>88: No sabe<br>99: No responde | |
| `c13` | Entonces, ¿trabajaría menos horas, aunque esto suponga una reducción proporcional de su sueldo? | 1: Sí<br>2: No | Descontinuada. Producida entre EFM 2010 y OND 2019. |

#### 5.3.8 Sección E: Búsqueda de empleo

| Variable | Descripción | Categorías observadas | Observaciones |
| :--- | :--- | :--- | :--- |
| `e1` | ¿Ha hecho algo para conseguir trabajo dentro de los últimos doce meses? | 1: Sí<br>2: No | Descontinuada (EFM 2010 a OND 2019). Responden ocupados y no ocupados. |
| `e2` | En las cuatro últimas semanas... ¿ha tratado de encontrar algún empleo o crear empresa? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Responden ocupados y no ocupados. |
| `e3_1` a `e3_12` | Gestiones de búsqueda: CV a empresas (`_1`), Directo con empleadores (`_2`), Contactos (`_3`), Avisos (`_4`), OMIL (`_5`), Por cuenta propia (`_6`), Búsqueda de clientes (`_7`), Avisos en medios (`_8`), Entrevistas (`_9`), Agencias de empleo (`_10`), Actualizó CV (`_11`), Nada (`_12`) | 0: No<br>1: Sí | Responden ocupados y no ocupados. |
| `e3_total` | Número de gestiones realizadas para buscar empleo | 1 – 11 | Sumatoria de valores afirmativos entre e3_1 y e3_11. |
| `e4` | Motivo principal por el cual está buscando otro trabajo | 1: Mayores ingresos<br>2: Calidad de vida<br>3: Condiciones laborales<br>4: Acorde a su formación<br>5: Inseguridad en empleo actual<br>6: Trabajo provisional<br>7: Dejó de buscar<br>88: No sabe<br>99: No responde | Solo responden ocupados/as. |
| `e5` | Cuándo fue la última vez que buscó trabajo | 1: Cuatro semanas o menos<br>2: Sólo la semana de entrevista<br>3: Más de 4 semanas y menos de 2 meses<br>4: Más de dos meses | Solo responden no ocupados/as. |
| `e5_dia`, `_sem`, `_mes`, `_ano` | Fecha de última búsqueda de empleo | Rangos de días (1-31), semanas (1-5), meses (1-12) y años | Solo responden no ocupados/as. |
| `e6_mes`, `e6_ano` | ¿Desde cuándo ha estado buscando trabajo? | Mes (1-12), Años | Solo responden no ocupados/as. |
| `e7` | ¿Qué tipo de jornada de trabajo está buscando? | 1: Jornada completa<br>2: Jornada parcial<br>3: Cualquiera<br>88: No sabe<br>99: No responde | Responden ocupados y no ocupados. |
| `e8` | Carácter temporal del trabajo que busca | 1: Permanente<br>2: De temporada<br>3: Ocasional<br>4: Cualquiera | Descontinuada (EFM 2010 a OND 2019). |
| `e9` | Razón por la que no buscó empleo en las últimas 4 semanas | 1: Iniciará pronto actividad por cuenta propia<br>2: Encontró empleo que empezará pronto<br>3: Responsabilidades familiares permanentes<br>4: Estudiando<br>5: Jubilado/a<br>6: Rentista<br>7: Pensionado/a o montepiado/a<br>8: Salud permanente<br>9: Espera temporada<br>10: Salud temporal<br>11: Responsabilidades familiares temporales<br>12: Embarazo<br>13: Espera selección<br>14: Oposición familiar<br>15: Edad<br>16: No encontrará<br>17: Desaliento<br>18: No calza con calificación<br>19: Trámites burocráticos<br>20: No sabe dónde acudir<br>21: No quiere o no necesita<br>22: Otra razón | Solo responden no ocupados/as. |
| `e10` | ¿Hizo gestiones para iniciar actividad o logró un acuerdo laboral? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Solo responden no ocupados/as. |
| `deseo_trabajar` | A pesar de que no buscó, ¿desea trabajar? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Vigente desde EFM 2020. Solo no ocupados/as. |
| `e11` | ¿Estaría disponible para comenzar de inmediato al otro lunes? | 1: Sí<br>2: No | Solo responden no ocupados/as. |
| `e12` | ¿Por qué motivo no estaría disponible? | Ver opciones en e9 (motivos similares: estudios, salud, familia, rentista, embarazo, no quiere/necesita, etc.) | Solo responden no ocupados/as. |
| `e13` | ¿Ha tenido anteriormente algún empleo por lo menos un mes? | 1: Sí<br>2: No<br>88: No sabe<br>99: No responde | Solo responden no ocupados/as. |

#### 5.3.9 Empleo anterior (Descontinuadas a partir de EFM 2020)

| Variable | Descripción | Categorías observadas | Observaciones |
| :--- | :--- | :--- | :--- |
| `e14_mes`, `_ano` | Mes y año hasta cuándo trabajó en anterior empleo | 88/8888: NS, 99/9999: NR | Descontinuada (EFM 2010 - OND 2019). |
| `e15_meses`, `_anos` | Tiempo trabajado en anterior ocupación | En meses / En años | Descontinuada (EFM 2010 - OND 2019). |
| `e16_ciuo88`, `_ciuo08` | Clasificación CIUO del empleo anterior | Ver Anexo 3 | Descontinuadas. |
| `e17` | Categoría ocupacional del empleo anterior | 1: Empleador<br>2: Cuenta propia<br>3: Asalariado privado<br>4: Asalariado público<br>5: Servicio doméstico adentro<br>6: Servicio doméstico afuera<br>7: Familiar no remunerado | Descontinuada (EFM 2010 - OND 2019). |
| `e18`, `e18_rev4cl_caenes` | Rama de actividad económica del empleo anterior | Ver Anexo 5 | Descontinuadas. |
| `e19` | Motivo por el cual dejó anterior empleo | 1: Término contrato/faena<br>2: Cierre cuenta propia<br>3: Quiebra<br>4: Jubilación<br>5-9: Despido (edad, embarazo, reducción, etc.)<br>10-17: Renuncia (estudio, ingresos, salud, embarazo, etc.) | Descontinuada (EFM 2010 - OND 2019). |

#### 5.3.10 Impacto COVID-19 en personas no ocupadas

| Variable | Descripción | Categorías observadas | Observaciones |
| :--- | :--- | :--- | :--- |
| `e21_mes`, `_ano` | Mes y año hasta cuándo trabajó en su última ocupación | Mes (1-12), Años | Incorporada en JJA 2020. |
| `e21_tramo` | Tramo temporal desde que dejó empleo | 1: Marzo 2020 a la fecha<br>2: Octubre 2019 a febrero 2020<br>3: 2017 a septiembre 2019<br>4: Antes de 2017<br>5: NS/NR | Calculada a partir de e21_mes y e21_ano. |
| `e22` | Razón por la cual ya no tiene ese empleo | 1: Despido<br>2: Renuncia<br>3: Fin de contrato/temporada<br>4: Jubilación<br>5: Término actividad cuenta propia<br>6: Quiebra económica<br>7: Fenómeno natural<br>8: Pandemia COVID-19 (quiebra)<br>9: Imposibilidad de trabajar por COVID-19 | Incorporada en JJA 2020. |
| `e23` | Motivo del despido | Opciones: edad, conflicto, falta calificación, fin trabajo, discriminación, enfermedad, COVID-19, reducción personal, etc. | Incorporada en JJA 2020. |
| `e24` | Motivo de la renuncia | Opciones: estudios, cuidado personas, salud, mejor ingreso, COVID-19, embarazo, cansancio, etc. | Incorporada en JJA 2020. |

---

### 5.4 Variables analíticas y factores de expansión

#### 5.4.1 Variables analíticas

| Variable | Descripción | Categorías observadas | Observaciones |
| :--- | :--- | :--- | :--- |
| `b11_proxy` | Pago por actividad principal mediante sueldo/salario | 1: Sí<br>2: No<br>88: NS, 99: NR | Reemplazo de variable b11 para informalidad laboral. |
| `ocup_honorarios`| Entrega de boleta de honorarios | 1: Sí<br>2: No<br>77: No aplica | Incorporada en EFM 2020. |
| `asocia` | Participante en organizaciones laborales | 0: No corresponde<br>1: Sí participa | Nueva dimensión analítica (INE, 2024c). |
| `plataformas_digitales` | Realiza trabajo vía app o web | 1: Sí<br>2: No<br>77: No aplica | Incorporada en EFM 2020 (INE, 2022b). |
| `pd_especifique` | Nombre de aplicación plataforma | Pregunta abierta | Incorporada en EFM 2020. |
| `pd_ley` | Plataforma sujeta a Ley 21.431 (principal) | 1: Sí<br>2: No | Incorporada en EFM 2020. |
| `sda_pd` | Realiza segundo trabajo por plataforma digital | 1: Sí<br>2: No | Incorporada en EFM 2020. |
| `sda_pd_ley` | Plataforma sujeta a Ley 21.431 (secundaria) | 1: Sí<br>2: No | Incorporada en EFM 2020. |
| `meses_ocup_actual` | Duración de ocupación (en meses) | Valor numérico | (INE, 2026). |
| `dep_economica` | Independiente con dependencia económica | 0: No<br>1: Ocupado/a con dependencia | (INE, 2026). |
| `dep_organizativa`| Independiente con dependencia organizativa | 0: No<br>1: Ocupado/a con dependencia | (INE, 2026). |
| `dep_ambas` | Independiente con ambas dependencias | 0: No<br>1: Sí | (INE, 2026). |
| `no_salario` | Dependiente sin salario fijo/jornal | 0: No<br>1: Sí | (INE, 2026). |
| `no_prevision` | Dependiente sin cotización previsional | 0: No<br>1: Sí | (INE, 2026). |
| `riesgo_economico`| Dependiente con riesgo económico | 0: No<br>1: Sí | (INE, 2026). |
| `n_dependencias` | Ámbitos de dependencia observados | Escala 0 – 7 | (INE, 2026). |
| `cdi` | Contratista dependiente como cuenta propia | 0: No<br>1: Sí | (INE, 2026). |
| `cdd` | Contratista dependiente como asalariado | 0: No<br>1: Sí | (INE, 2026). |
| `cd` | Contratista dependiente global | 0: No<br>1: Sí | (INE, 2026). |
| `ciso1` | CISO-18 Primer nivel jerárquico | 1: Independiente<br>2: Dependiente | (INE, 2026). |
| `ciso2` | CISO-18 Segundo nivel jerárquico | 1: Empleador/a<br>2: Cuenta propia<br>3: Contratista dependiente<br>4: Asalariado privado<br>5: Asalariado público<br>6: Servicio doméstico<br>7: Familiar no remunerado | (INE, 2026). |
| `ciso3_a` | CISO-18 Tercer nivel (Forma A) | Categorías 1 a 18 (desglose por tipo de sociedad, duración de contrato, etc.) | (INE, 2026). |
| `ciso3_b` | CISO-18 Tercer nivel (Forma B) | Categorías 1 a 19 (desglose con foco en riesgos y dependencias) | (INE, 2026). |
| `cine97` | Nivel educacional normalizado CINE 1997 | 0 a 5, 9: Sin clasificación | Clasificación UNESCO (1997). |
| `cine11_1d` | Nivel educacional normalizado CINE 2011 (1 dígito) | 0 a 6, 9: Sin clasificación | Clasificación UNESCO (2011). |
| `cine11_2d` | Clasificación CINE 2011 a 2 dígitos | Desglose vocacional/académico de dos dígitos | Clasificación UNESCO (2011). |
| `habituales` | Horas habituales de trabajo semanal | 1 – 168 | Calculada desde variables del bloque C2. |
| `efectivas` | Horas efectivas trabajadas en la semana | 0 – 168 | Calculada desde c2, c6 y c8. Si no hay respuesta se imputa 0 a ocupados. |
| `pet` | Población en edad de trabajar | 0: No corresponde<br>1: Población en edad de trabajar (>= 15 años) | |
| `ft` | Fuerza de trabajo | 0: No corresponde<br>1: Fuerza de trabajo | Suma de ocupados y desocupados. |
| `ftp` | Fuerza de trabajo potencial | 0: No corresponde<br>1: Fuerza de trabajo potencial | |
| `inhab` | Inactivos habituales | 0: No corresponde<br>1: Inactivo habitual | |
| `fta` | Fuerza de trabajo ampliada | 0: No corresponde<br>1: FTA | FT + FTP + Iniciadores disponibles. |
| `obe` | Ocupado/a que buscó un empleo | 0: No corresponde<br>1: Sí buscó empleo | |
| `idisp` | Iniciador/a disponible | 0: No corresponde<br>1: Iniciador disponible | |
| `tpi` | Ocupado a tiempo parcial involuntario | 0: No corresponde<br>1: Tiempo parcial involuntario | <= 30 horas habituales y disponible para más. |
| `ina_cal_edu` | Inadecuación por calificación educacional | 1: Subeducación<br>2: Sin inadecuación<br>3: Sobreeducación<br>999: Sin información | Estadística experimental (INE, 2025). |
| `ocup_form` | Formalidad de la ocupación | 1: Ocupado formal<br>2: Ocupado informal | Incorporada en JAS 2017. |
| `sector` | Sector institucional | 1: Sector formal<br>2: Sector informal<br>3: Hogares como empleadores<br>999: Sin clasificación | Incorporada en JAS 2017. |
| `r_p_rev4cl_caenes` | Rama de actividad de ocupación principal ajustada | Códigos CAENES Anexo 5 | |
| `tramo_edad` | Tramos quinquenales de edad | 1: 15-19 ... 12: 70 años o más | Construida en base a la variable `edad`. |
| `categoria_ocupacion`| Categoría en la ocupación (CISE 93) | 1: Empleador/a<br>2: Cuenta propia<br>3: Asalariado privado<br>4: Asalariado público<br>5: Servicio doméstico afuera<br>6: Servicio doméstico adentro<br>7: Familiar no remunerado | Adaptación nacional CISE-93. |
| `cae_general` | Código sumario de empleo general | 0: Menor de 15 años<br>1: Ocupado tradicional<br>2: Ocupado no tradicional<br>3: Ocupado ausente<br>4: Cesante<br>5: Búsqueda primera vez<br>6: Iniciador<br>7: Inactivo buscó<br>8: Inactivo disponible<br>9: Inactivo habitual | Clasificación marco de la encuesta. |
| `cae_especifico`| Código sumario de empleo específico | Categorías detalladas 0 a 28 | Base del cómputo de indicadores oficiales del mercado de trabajo. |
| `activ` | Condición de actividad básica | 1: Ocupado/a<br>2: Desocupado/a<br>3: Fuera de la fuerza de trabajo | |

#### 5.4.2 Factores de expansión

| Variable | Descripción | Categorías observadas | Observaciones |
| :--- | :--- | :--- | :--- |
| `fact` | Factor tradicional (proyecciones Censo 2002) | Factor de ponderación | Descontinuado. Disponible hasta OND 2019. |
| `fact_cal` | Factor calibrado (proyecciones Censo 2017) | Factor de ponderación | Vigente para toda la serie histórica (EFM 2010 a la fecha). |
| `fact_anual` | Factor de expansión anual | Factor de ponderación | Exclusivo de bases consolidadas anualizadas. |

## 6 DESCRIPCIÓN DE INDICADORES PRINCIPALES

### 6.1 Indicadores sobre la fuerza de trabajo

A partir de la identificación de categorías según el código sumario empleo específico (variable `cae_especifico`), se construyen los principales indicadores de empleo de la ENE.

#### 6.1.1 Tasa de desocupación (TD)
Corresponde al número de personas desocupadas, expresado como porcentaje de la fuerza de trabajo (entendida como la sumatoria de personas ocupadas y desocupadas):

$$TD = \left[ \frac{DO}{FT} \right] \times 100$$

Donde:
- $DO$ = Personas desocupadas
- $FT$ = Fuerza de trabajo

#### 6.1.2 Tasa de ocupación (TO)
Corresponde al número de personas ocupadas como porcentaje de la población en edad de trabajar (es decir, de quince años o más):

$$TO = \left[ \frac{O}{PET} \right] \times 100$$

Donde:
- $O$ = Personas ocupadas
- $PET$ = Población en edad de trabajar

#### 6.1.3 Tasa de participación (TP)
Corresponde al número de personas en la fuerza de trabajo expresado como porcentaje de la población en edad de trabajar:

$$TP = \left[ \frac{FT}{PET} \right] \times 100$$

Donde:
- $FT$ = Fuerza de trabajo
- $PET$ = Población en edad de trabajar

#### 6.1.4 Tasa de presión laboral (TPL)
Corresponde al número de personas ocupadas que buscaron un empleo, más los desocupados y más los iniciadores disponibles, expresado como porcentaje de la fuerza de trabajo incluyendo iniciadores disponibles:

$$TPL = \left[ \frac{DO + ID + OBE}{FT + ID} \right] \times 100$$

Donde:
- $DO$ = Personas desocupadas
- $ID$ = Iniciadores disponibles
- $OBE$ = Personas ocupadas que buscaron un empleo
- $FT$ = Fuerza de trabajo

#### 6.1.5 Tasa de desocupación con iniciadores disponibles (SU1)
Corresponde al número de personas desocupadas más los iniciadores disponibles, expresado como porcentaje de la fuerza de trabajo más iniciadores disponibles:

$$SU1 = \left[ \frac{DO + ID}{FT + ID} \right] \times 100$$

Donde:
- $DO$ = Personas desocupadas
- $ID$ = Iniciadores disponibles
- $FT$ = Fuerza de trabajo

#### 6.1.6 Tasa combinada de desocupación y tiempo parcial involuntario (SU2)
Corresponde al número de personas ocupadas a tiempo parcial involuntario, más los desocupados y más los iniciadores disponibles, expresado como porcentaje de la fuerza de trabajo más iniciadores disponibles:

$$SU2 = \left[ \frac{DO + ID + TPI}{FT + ID} \right] \times 100$$

Donde:
- $DO$ = Personas desocupadas
- $ID$ = Iniciadores disponibles
- $TPI$ = Personas ocupadas que trabajaron a tiempo parcial involuntario
- $FT$ = Fuerza de trabajo

#### 6.1.7 Tasa combinada de desocupación y fuerza de trabajo potencial (SU3)
Corresponde al número de personas desocupadas, más los iniciadores disponibles y más la fuerza de trabajo potencial, expresado como porcentaje de la fuerza de trabajo ampliada:

$$SU3 = \left[ \frac{DO + ID + FTP}{FTA} \right] \times 100$$

Donde:
- $DO$ = Personas desocupadas
- $ID$ = Iniciadores disponibles
- $FTP$ = Fuerza de trabajo potencial
- $FTA$ = Fuerza de trabajo ampliada

#### 6.1.8 Tasa global de subutilización (SU4)
Corresponde al número de personas desocupadas, más los iniciadores disponibles, más las personas ocupadas a tiempo parcial involuntario, más la fuerza de trabajo potencial, expresado como porcentaje de la fuerza de trabajo ampliada:

$$SU4 = \left[ \frac{DO + ID + TPI + FTP}{FTA} \right] \times 100$$

$$FTA = FT + FTP + ID$$

Donde:
- $DO$ = Personas desocupadas
- $ID$ = Iniciadores disponibles
- $TPI$ = Personas ocupadas que trabajaron a tiempo parcial involuntario
- $FTP$ = Fuerza de trabajo potencial
- $FTA$ = Fuerza de trabajo ampliada

---

### 6.2 Indicadores sobre informalidad laboral

#### 6.2.1 Tasa de ocupación informal (TOI)
Corresponde al número de personas con ocupaciones informales expresado como porcentaje del total de las personas ocupadas:

$$TOI = \left[ \frac{OI}{O} \right] \times 100$$

Donde:
- $OI$ = Personas ocupadas informales (independiente si es sector formal o informal)
- $O$ = Personas ocupadas

#### 6.2.2 Tasa de ocupación en el Sector Informal (TOSI)
Corresponde al número de ocupados en unidades económicas informales expresado como porcentaje del total de ocupados:

$$TOSI = \left[ \frac{OSI}{O} \right] \times 100$$

Donde:
- $OSI$ = Ocupados en el sector informal
- $O$ = Personas ocupadas

---

## 7 PROGRAMACIÓN PARA LA CONSTRUCCIÓN DE INDICADORES PRINCIPALES

### 7.1 Stata

#### 7.1.1 Componentes

* Población en edad de trabajar
generate mayores_15 = (edad>=15 & edad<.)
summarize mayores_15 if mayores_15==1 [iw=fact_cal]
global pet=r(sum_w)

* Fuerza de trabajo (FT)
generate fuerza_de_trabajo = inrange(cae_especifico,1,9)
summarize fuerza_de_trabajo if fuerza_de_trabajo==1 [iw=fact_cal]
global fdt=r(sum_w)

* Personas ocupadas (O)
generate ocupados = inrange(cae_especifico,1,7)
summarize ocupados if ocupados==1 [iw=fact_cal]
global o=r(sum_w)

* Personas desocupadas (DO)
generate desocupados = inlist(cae_especifico,8,9)
summarize desocupados if desocupados==1 [iw=fact_cal]
global d=r(sum_w)

* Iniciadores disponibles (ID)
generate iniciadores_disponibles=(cae_especifico==10)
summarize iniciadores_disponibles if iniciadores_disponibles==1 [iw=fact_cal]
global id=r(sum_w)

* Personas ocupadas a tiempo parcial involuntario (TPI)
generate ocupados_tpi=inrange(cae_especifico,1,7) & habituales<=30 & c10==1 & inlist(c11,1,2)
summarize ocupados_tpi if ocupados_tpi==1 [iw=fact_cal]
global tpi=r(sum_w)

* Personas ocupadas que buscaron empleo (OBE)
generate ocupados_obe=inrange(cae_especifico,1,7) & inrange(e4,1,6)
summarize ocupados_obe if ocupados_obe==1 [iw=fact_cal]
global obe=r(sum_w)

* Fuerza de trabajo potencial (FTP)
generate ftp = inlist(cae_especifico,12, 14, 16, 18, 20, 22, 25, 26, 27)
summarize ftp if ftp==1 [iw=fact_cal]
global ftp=r(sum_w)

* Fuerza de trabajo ampliada (FTA)
generate fta = inlist(cae_especifico, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 22, 25, 26, 27)
summarize fta if fta==1 [iw=fact_cal]
global fta=r(sum_w)

* Personas ocupadas informales (OI)
generate ocupados_inf = (ocup_form==2)
summarize ocupados_inf if ocupados_inf==1 [iw=fact_cal]
global oi=r(sum_w)

* Personas ocupadas en el sector informal (OSI)
generate ocupados_sec_inf = (sector==2)
summarize ocupados_sec_inf if ocupados_sec_inf==1 [iw=fact_cal]
global osi=r(sum_w)

* Indicador horas efectivas con ocupados ausentes
gen efe1 = efectivas
replace efe1 = 0 if !inrange(efe1, 1, 168) & activ==1
summarize efe1 [iw = fact_cal]
global efe1 = r(sum)
global oc_efe1 = r(sum_w)

* Indicador horas efectivas sin ocupados ausentes
gen efe2 = efectivas if efectivas > 0
summarize efe2 [iw = fact_cal]
global efe2 = r(sum)
global oc_efe2 = r(sum_w)



#### 7.1.2 Cálculo de indicadores 

* Tasa de desocupación
display %2.1f ($d/$fdt)*100

* Tasa de ocupación (TO)
display %2.1f ($o)/($pet)*100

* Tasa de participación (TP)
display %2.1f ($fdt)/($pet)*100

* Tasa de presión laboral (TPL)
display %2.1f ($d+$id+$obe)/($fdt+$id)*100

* Tasa de desocupación con iniciadores disponibles (SU1)
display %2.1f ($d+$id)/($fdt+$id)*100

* Tasa combinada de desocupación y tiempo parcial involuntario (SU2)
display %2.1f ($d+$id+$tpi)/($fdt+$id)*100

* Tasa combinada de desocupación y fuerza de trabajo potencial (SU3)
display %2.1f ($d+$id+$ftp)/($fta)*100

* Tasa global de subutilización (SU4)
display %2.1f ($d+$id+$tpi+$ftp)/($fta)*100

* Tasa de ocupación informal (TOI)
display %2.1f ($oi) /($o)*100

* Tasa de ocupación en el sector informal (TOSI)
display %2.1f ($osi)/($o)*100

* Promedio de horas habitualmente trabajadas a la semana
display ($hab)/($oc_hab)

* Promedio de horas efectivas trabajadas a la semana (incluyendo ocupados ausentes)
display ($efe1)/($oc_efe1)

* Promedio de horas efectivas trabajadas a la semana (excluyendo ocupados ausentes)
display ($efe1)/($oc_efe2)


# 7.2 R
## 7.2.1 Componentes

library(dplyr)
library(magrittr)

# Agregar componentes a data.frame
indicadores <- base %>% summarise(
  pet = sum(fact_cal[edad >= 15], na.rm = TRUE),
  fdt = sum(fact_cal[cae_especifico %in% 1:9], na.rm = TRUE),
  oc  = sum(fact_cal[cae_especifico %in% 1:7], na.rm = TRUE),
  des = sum(fact_cal[cae_especifico %in% 8:9], na.rm = TRUE),
  id  = sum(fact_cal[cae_especifico == 10], na.rm = TRUE),
  tpi = sum(fact_cal[habituales %in% 1:30 & c10 == 1 & c11 %in% 1:2], na.rm = TRUE),
  obe = sum(fact_cal[cae_especifico %in% 1:7 & e4 %in% 1:6], na.rm = TRUE),
  ftp = sum(fact_cal[cae_especifico %in% c(12,14,16,18,20,22,25,26,27)], na.rm = TRUE),
  fta = sum(fact_cal[cae_especifico %in% c(1,2,3,4,5,6,7,8,9,10,12,14,16,18,20,22,25,26,27)], na.rm = TRUE),
  fft = sum(fact_cal[cae_especifico %in% 10:28], na.rm = TRUE),
  oi  = sum(fact_cal[ocup_form == 2], na.rm = TRUE),
  osi = sum(fact_cal[sector == 2], na.rm = TRUE),
  efe1 = sum(fact_cal[efectivas %in% 1:168 & activ == 1], na.rm = TRUE),
  efe2 = sum(fact_cal[efectivas > 0], na.rm = TRUE)
)

###7.2.2 Cálculo de indicadores y evaluación de calidad

indicadores %<>% summarise(
  td  = des / fdt * 100,
  to  = oc / pet * 100,
  tp  = fdt / pet * 100,
  tpl = (id + obe + des) / (fdt + id) * 100,
  su1 = (des + id) / (fdt + id) * 100,
  su2 = (des + id + tpi) / (fdt + id) * 100,
  su3 = (des + id + ftp) / (fta) * 100,
  su4 = (des + id + tpi + ftp) / (fta) * 100,
  toi = oi / oc * 100,
  tosi = osi / oc * 100,
  habituales_prom = sum(fact_cal[habituales], na.rm = TRUE) / oc,
  prom_efe1 = efe1 / oc,
  prom_efe2 = efe2 / oc
)

## Estimación con calidad institucional INE
library(srvyr)

base_dc <- base |>
  mutate(
    pet = case_when(edad >= 15 ~ 1, TRUE ~ 0),
    fdt = case_when(cae_especifico %in% 1:9 ~ 1, TRUE ~ 0),
    oc  = case_when(cae_especifico %in% 1:7 ~ 1, TRUE ~ 0),
    des = case_when(cae_especifico %in% 8:9 ~ 1, TRUE ~ 0)
  )

base_dc <- base_dc |>
  as_survey_design(ids = conglomerado, strata = estrato, weights = fact_cal)

options(survey.lonely.psu = "certainty")

# Tasa de desocupacion con estándar de precisión
base_dc |>
  filter(fdt == 1) |>
  summarise(
    estimacion = survey_ratio(des, fdt, vartype = c("se", "cv"), na.rm = TRUE),
    n = unweighted(n()),
    gl = n_distinct(conglomerado) - n_distinct(estrato)
  ) |>
  mutate(
    se = estimacion_se,
    cv = estimacion_cv * 100,
    flag = ifelse((n < 60 | gl < 9), "b", # no fiable
           ifelse((n >= 60 & gl >= 9 & ((estimacion < 0.5 & ((estimacion^(2/3))/9 < se)) | (estimacion >= 0.5 & (((1-estimacion)^(2/3))/9 < se)))), "a", "")) # poco fiable
  )
  
## 7.3 SPSS
#### 7.3.1 Componentes
compute id_pet = (edad ge 15).
compute id_ft = range(cae_especifico,1,9).
compute id_o = range(cae_especifico,1,7).
compute id_do = any(cae_especifico,8,9).
compute id_id = (cae_especifico eq 10).
compute id_tpi = (range(cae_especifico,1,7) and (habituales le 30) and (c10 eq 1) and ((c11 eq 1) or (c11 eq 2))).
compute id_obe = (range(cae_especifico,1,7) and ((e4 ge 1) and (e4 le 6))).
compute id_ftp = any(cae_especifico,12, 14, 16, 18, 20, 22, 25, 26, 27).
compute id_fta = any(cae_especifico,1,2,3,4,5,6,7,8,9,10,12,14,16,18,20,22,25,26,27).
compute id_oi = (ocup_form eq 2).
compute id_osi = (sector eq 2).

compute var_hab = habituales.
recode var_hab (888=0) (999=0).

compute var_efe1 = efectivas.
recode var_efe1 (888=0) (999=0).

if (efectivas > 0) var_efe2=id_o.
execute.

#### 7.3.2 Cálculo de indicadores

weight by fact_cal.
execute.

aggregate
  /outfile=* mode=addvariables
  /break=
  /pet =sum(id_pet)
  /ft =sum(id_ft)
  /o =sum(id_o)
  /do =sum(id_do)
  /id =sum(id_id)
  /tpi =sum(id_tpi)
  /obe=sum(id_obe)
  /ftp=sum(id_ftp)
  /fta=sum(id_fta)
  /oi =sum(id_oi)
  /osi =sum(id_osi)
  /hab =sum(var_hab)
  /efe1 =sum(var_efe1)
  /efe2 =sum(var_efe2).
weight off.
execute.

* Tasa de desocupación (TD).
compute tasa=100 * (do / ft).
execute.
ctables
  /vlabels variables=tasa display=label
  /table tasa [s][mean pct2.1]
  /slabels visible=no
  /titles title='Tasa de desocupación'.

* Tasa de ocupación (TO).
compute tasa=100 * (o / pet).
execute.
ctables
  /vlabels variables=tasa display=label
  /table tasa [s][mean pct2.1]
  /slabels visible=no
  /titles title='Tasa de ocupación'.

* Tasa de participación (TP).
compute tasa=100 * (ft / pet).
execute.
ctables
  /vlabels variables=tasa display=label
  /table tasa [s][mean pct2.1]
  /slabels visible=no
  /titles title='Tasa de participación'.

* Tasa de presión laboral (TPL).
compute tasa=100 * ((do + id + obe) / (ft + id)).
execute.
ctables
  /vlabels variables=tasa display=label
  /table tasa [s][mean pct2.1]
  /slabels visible=no
  /titles title='Tasa de presión laboral'.

* Tasa de ocupación informal (TOI).
compute tasa=100 * (oi / o).
execute.
ctables
  /vlabels variables=tasa display=label
  /table tasa [s][mean pct2.1]
  /slabels visible=no
  /titles title='Tasa de ocupación informal'.

##8 PREGUNTAS FRECUENTES
###8.1 ¿Es posible realizar estimaciones comunales con la ENE?
La encuesta, según su diseño muestral, asegura representatividad en las estimaciones a nivel nacional y regional. De igual modo, se incluyen estimaciones específicas para dominios más desagregados, como algunas provincias y grandes conurbaciones. El diseño no contempla estimaciones comunales (INE, 2021a).
En efecto, para lograr representatividad comunal se requiere un diseño muestral distinto, con un aumento considerable de la muestra. Cualquier cálculo comunal que se realice contendrá un error de muestreo no controlado institucionalmente. El INE no se responsabiliza por estimaciones comunales hechas por usuarios externos.
En caso de realizar estimaciones comunales bajo cuenta y riesgo del usuario (ejemplo comuna de Antofagasta, r_p_c=2101 en Stata):

gen mujeres_ocupadas = 1 if activ==1 & sexo==2
tab mujeres_ocupadas if r_p_c==2101 [iw=fact_cal]

###8.2 ¿Cómo interpretar una variación de tasas en la ENE?
La variación de una tasa entre períodos se expresa en puntos porcentuales (pp.) y corresponde a la resta aritmética entre ambas tasas ya redondeadas al primer decimal. Por ejemplo: si la tasa pasa de 6,1% a 6,6%, la variación es de 0,5 pp., independiente de los decimales de base.

#9 GLOSARIO
Actividad económica: Conjunto de acciones que comprenden la utilización de insumos para producir bienes y servicios. Se refiere a la actividad principal de la unidad económica donde la persona trabaja (Clasificador CAENES / CIIU Rev. 4).
Busca trabajo por primera vez (BTPV): Subcategoría de desocupados sin experiencia laboral previa.
Categoría ocupacional: Clasificación según relación laboral con la empresa (dependiente, independiente, etc., según CISE-93).
Cesante: Subcategoría de desocupados que tuvieron empleo anterior de al menos un mes.
Condición de actividad: Situación en la semana de referencia: ocupado/a, desocupado/a o fuera de la fuerza de trabajo.
Dependiente: Ocupado que no ejerce control completo sobre la unidad económica; depende de un empleador (asalariados y servicio doméstico).
Desocupado/a (DO): Persona de 15 años o más sin empleo en la semana de referencia, que buscó trabajo activamente en las últimas cuatro semanas y está disponible de inmediato.
Encuesta Suplementaria de Ingresos (ESI): Módulo aplicado en octubre-diciembre para caracterizar los ingresos de las personas ocupadas.
Estadística experimental: Estimaciones en desarrollo metodológico no integradas en la producción oficial regular.
Familiar no remunerado: Persona ocupada que trabaja para un familiar sin percibir salario contractual.
Fuera de la fuerza de trabajo (FFT): Personas en edad de trabajar no ocupadas ni desocupadas.
Fuerza de trabajo (FT): Suma de personas ocupadas y desocupadas.
Fuerza de trabajo ampliada (FTA): Sumatoria de FT, fuerza de trabajo potencial e iniciadores disponibles.
Fuerza de trabajo potencial (FTP): Personas inactivas que manifiestan deseo/búsqueda de empleo sin disponibilidad simultánea inmediata.
Horas efectivas: Horas realmente trabajadas durante la semana de referencia.
Horas habituales: Horas típicas semanales trabajadas en los últimos 3 meses.
Inactivos habituales (IH): Personas FFT sin búsqueda ni disponibilidad.
Iniciadores/as: Personas que no buscaron porque empezarán a trabajar pronto. Se dividen en disponibles e indisponibles.
Ocupación principal: Actividad en la cual se dedicó la mayor cantidad de horas semanales.
Ocupado/a (O): Persona de 15 años o más que trabajó al menos una hora a cambio de sueldo/beneficio en la semana de referencia.
Ocupado/a ausente: Persona ocupada que no trabajó en la semana de referencia por licencia, vacaciones u otra causa temporal reteniendo vínculo laboral.
Ocupado/a informal: Dependientes sin cotizaciones de salud y pensión, o independientes en unidades del sector informal o familiares no remunerados.
Población en edad de trabajar (PET): Población de 15 años o más.
Sector informal: Empresas que carecen de registro tributario en el SII y de contabilidad formal.
Semana de referencia: Período de lunes a domingo inmediatamente previo al momento de aplicación de la encuesta.
10 REFERENCIAS BIBLIOGRÁFICAS
DANE. (2022). Estadística experimental.
Herrera, D., Huaracán, V., & Inostroza, D. (2019). Indicadores de subutilización de la fuerza de trabajo en Chile. INE Chile.
INE. (2016). Clasificador de Actividades Económicas Nacional para Encuestas Sociodemográficas (CAENES).
INE. (2017). Estadísticas de informalidad laboral: Marco conceptual y manual metodológico.
INE. (2018a). Clasificador Chileno de Ocupaciones (CIUO 08.CL).
INE. (2018b). Manual Conceptual y Metodológico. Diseño Muestral ENE.
INE. (2020a). Estándar para la evaluación de la calidad de las estimaciones en encuestas de hogares.
INE. (2020e). Política de revisión y actualización de cifras de la ENE.
INE. (2021a). Documento Metodológico Encuesta Nacional de Empleo (ENE).
OIT. (2013). 19.a CIET: Informe II: Estadísticas del trabajo, el empleo y la subutilización de la fuerza de trabajo.
OIT. (2018b). 20.a CIET: Resolución sobre las estadísticas de las relaciones de trabajo.
OIT. (2023). 21.a CIET: Modificación sobre las estadísticas del trabajo, ocupación y subutilización.
UNESCO. (2013). Clasificación Internacional Normalizada de la Educación (CINE 2011).

## 11 ANEXOS

### Anexo 1. Clasificación de regiones, provincias y comunas (Parte 1: Regiones 15 a 5)

La ENE utiliza la clasificación correspondiente a los códigos territoriales para identificar regiones, provincias y comunas de Chile, establecidos en el Decreto Exento N° 1.115, del Ministerio del Interior y Seguridad Pública, publicado en el Diario Oficial el 21 de septiembre de 2018.

Las variables de la base de datos que utilizan este clasificador son: `region`, `provincia`, `r_p_c`, `mig2_cod`, `mig5_cod`, `b18_codigo`.

#### Región de Arica y Parinacota (15)
* **Provincia de Arica (151):** 15101 Arica, 15102 Camarones.
* **Provincia de Parinacota (152):** 15201 Putre, 15202 General Lagos.

#### Región de Tarapacá (1)
* **Provincia de Iquique (011):** 1101 Iquique, 1107 Alto Hospicio.
* **Provincia del Tamarugal (014):** 1401 Pozo Almonte, 1402 Camiña, 1403 Colchane, 1404 Huara, 1405 Pica.

#### Región de Antofagasta (2)
* **Provincia de Antofagasta (021):** 2101 Antofagasta, 2102 Mejillones, 2103 Sierra Gorda, 2104 Taltal.
* **Provincia de El Loa (022):** 2201 Calama, 2202 Ollagüe, 2203 San Pedro de Atacama.
* **Provincia de Tocopilla (023):** 2301 Tocopilla, 2302 María Elena.

#### Región de Atacama (3)
* **Provincia de Copiapó (031):** 3101 Copiapó, 3102 Caldera, 3103 Tierra Amarilla.
* **Provincia de Chañaral (032):** 3201 Chañaral, 3202 Diego de Almagro.
* **Provincia de Huasco (033):** 3301 Vallenar, 3302 Alto del Carmen, 3303 Freirina, 3304 Huasco.

#### Región de Coquimbo (4)
* **Provincia de Elqui (041):** 4101 La Serena, 4102 Coquimbo, 4103 Andacollo, 4104 La Higuera, 4105 Paiguano, 4106 Vicuña.
* **Provincia de Choapa (042):** 4201 Illapel, 4202 Canela, 4203 Los Vilos, 4204 Salamanca.
* **Provincia de Limarí (043):** 4301 Ovalle, 4302 Combarbalá, 4303 Monte Patria, 4304 Punitaqui, 4305 Río Hurtado.

#### Región de Valparaíso (5)
* **Provincia de Valparaíso (051):** 5101 Valparaíso, 5102 Casablanca, 5103 Concón, 5104 Juan Fernández, 5105 Puchuncaví, 5107 Quintero, 5109 Viña del Mar.
* **Provincia de Isla de Pascua (052):** 5201 Isla de Pascua.
* **Provincia de Los Andes (053):** 5301 Los Andes, 5302 Calle Larga, 5303 Rinconada, 5304 San Esteban.
* **Provincia de Petorca (054):** 5401 La Ligua, 5402 Cabildo, 5403 Papudo, 5404 Petorca, 5405 Zapallar.
* **Provincia de Quillota (055):** 5501 Quillota, 5502 Calera, 5503 Hijuelas, 5504 La Cruz, 5506 Nogales.
* **Provincia de San Antonio (056):** 5601 San Antonio, 5602 Algarrobo, 5603 Cartagena, 5604 El Quisco, 5605 El Tabo, 5606 Santo Domingo.
* **Provincia de San Felipe (057):** 5701 San Felipe, 5702 Catemu, 5703 Llaillay, 5704 Panquehue, 5705 Putaendo, 5706 Santa María.
* **Provincia de Marga Marga (058):** 5801 Quilpué, 5802 Limache, 5803 Olmué, 5804 Villa Alemana.

#### Región Metropolitana de Santiago (13)
* **Provincia de Santiago (131):** 13101 Santiago, 13102 Cerrillos, 13103 Cerro Navia, 13104 Conchalí, 13105 El Bosque, 13106 Estación Central, 13107 Huechuraba, 13108 Independencia, 13109 La Cisterna, 13110 La Florida, 13111 La Granja, 13112 La Pintana, 13113 La Reina, 13114 Las Condes, 13115 Lo Barnechea, 13116 Lo Espejo, 13117 Lo Prado, 13118 Macul, 13119 Maipú, 13120 Ñuñoa, 13121 Pedro Aguirre Cerda, 13122 Peñalolén, 13123 Providencia, 13124 Pudahuel, 13125 Quilicura, 13126 Quinta Normal, 13127 Recoleta, 13128 Renca, 13129 San Joaquín, 13130 San Miguel, 13131 San Ramón, 13132 Vitacura.
* **Provincia de Cordillera (132):** 13201 Puente Alto, 13202 Pirque, 13203 San José de Maipo.
* **Provincia de Chacabuco (133):** 13301 Colina, 13302 Lampa, 13303 Tiltil.
* **Provincia de Maipo (134):** 13401 San Bernardo, 13402 Buin, 13403 Calera de Tango, 13404 Paine.
* **Provincia de Melipilla (135):** 13501 Melipilla, 13502 Alhué, 13503 Curacaví, 13504 María Pinto, 13505 San Pedro.
* **Provincia de Talagante (136):** 13601 Talagante, 13602 El Monte, 13603 Isla de Maipo, 13604 Padre Hurtado, 13605 Peñaflor.

#### Región del Libertador General Bernardo O’Higgins (6)
* **Provincia de Cachapoal (061):** 6101 Rancagua, 6102 Codegua, 6103 Coinco, 6104 Coltauco, 6105 Doñihue, 6106 Graneros, 6107 Las Cabras, 6108 Machalí, 6109 Malloa, 6110 Mostazal, 6111 Olivar, 6112 Peumo, 6113 Pichidegua, 6114 Quinta de Tilcoco, 6115 Rengo, 6116 Requínoa, 6117 San Vicente.
* **Provincia de Cardenal Caro (062):** 6201 Pichilemu, 6202 La Estrella, 6203 Litueche, 6204 Marchihue, 6205 Navidad, 6206 Paredones.
* **Provincia de Colchagua (063):** 6301 San Fernando, 6302 Chépica, 6303 Chimbarongo, 6304 Lolol, 6305 Nancagua, 6306 Palmilla, 6307 Peralillo, 6308 Placilla, 6309 Pumanque, 6310 Santa Cruz.

#### Región del Maule (7)
* **Provincia de Talca (071):** 7101 Talca, 7102 Constitución, 7103 Curepto, 7104 Empedrado, 7105 Maule, 7106 Pelarco, 7107 Pencahue, 7108 Río Claro, 7109 San Clemente, 7110 San Rafael.
* **Provincia de Cauquenes (072):** 7201 Cauquenes, 7202 Chanco, 7203 Pelluhue.
* **Provincia de Curicó (073):** 7301 Curicó, 7302 Hualañé, 7303 Licantén, 7304 Molina, 7305 Rauco, 7306 Romeral, 7307 Sagrada Familia, 7308 Teno, 7309 Vichuquén.
* **Provincia de Linares (074):** 7401 Linares, 7402 Colbún, 7403 Longaví, 7404 Parral, 7405 Retiro, 7406 San Javier, 7407 Villa Alegre, 7408 Yerbas Buenas.

#### Región del Biobío (8)
* **Provincia de Concepción (081):** 8101 Concepción, 8102 Coronel, 8103 Chiguayante, 8104 Florida, 8105 Hualqui, 8106 Lota, 8107 Penco, 8108 San Pedro de la Paz, 8109 Santa Juana, 8110 Talcahuano, 8111 Tomé, 8112 Hualpén.
* **Provincia de Arauco (082):** 8201 Lebu, 8202 Arauco, 8203 Cañete, 8204 Contulmo, 8205 Curanilahue, 8206 Los Álamos, 8207 Tirúa.
* **Provincia de Biobío (083):** 8301 Los Ángeles, 8302 Antuco, 8303 Cabrero, 8304 Laja, 8305 Mulchén, 8306 Nacimiento, 8307 Negrete, 8308 Quilaco, 8309 Quilleco, 8310 San Rosendo, 8311 Santa Bárbara, 8312 Tucapel, 8313 Yumbel, 8314 Alto Biobío.

#### Región de Ñuble (16)
* **Provincia de Diguillín (161):** 16101 Chillán (antiguo: 8401), 16102 Bulnes (8402), 16103 Chillán Viejo (8406), 16104 El Carmen (8407), 16105 Pemuco (8410), 16106 Pinto (8411), 16107 Quillón (8413), 16108 San Ignacio (8418), 16109 Yungay (8421).
* **Provincia de Itata (162):** 16201 Quirihue (8414), 16202 Cobquecura (8403), 16203 Coelemu (8404), 16204 Ninhue (8408), 16205 Portezuelo (8412), 16206 Ránquil (8415), 16207 Treguaco (8420).
* **Provincia de Punilla (163):** 16301 San Carlos (8416), 16302 Coihueco (8405), 16303 Ñiquén (8409), 16304 San Fabián (8417), 16305 San Nicolás (8419).

#### Región de La Araucanía (9)
* **Provincia de Cautín (091):** 9101 Temuco, 9102 Carahue, 9103 Cunco, 9104 Curarrehue, 9105 Freire, 9106 Galvarino, 9107 Gorbea, 9108 Lautaro, 9109 Loncoche, 9110 Melipeuco, 9111 Nueva Imperial, 9112 Padre Las Casas, 9113 Perquenco, 9114 Pitrufquén, 9115 Pucón, 9116 Saavedra, 9117 Teodoro Schmidt, 9118 Toltén, 9119 Vilcún, 9120 Villarrica, 9121 Cholchol.
* **Provincia de Malleco (092):** 9201 Angol, 9202 Collipulli, 9203 Curacautín, 9204 Ercilla, 9205 Lonquimay, 9206 Los Sauces, 9207 Lumaco, 9208 Purén, 9209 Renaico, 9210 Traiguén, 9211 Victoria.

#### Región de Los Ríos (14)
* **Provincia de Valdivia (141):** 14101 Valdivia, 14102 Corral, 14103 Lanco, 14104 Los Lagos, 14105 Máfil, 14106 Mariquina, 14107 Paillaco, 14108 Panguipulli.
* **Provincia de Ranco (142):** 14201 La Unión, 14202 Futrono, 14203 Lago Ranco, 14204 Río Bueno.

#### Región de Los Lagos (10)
* **Provincia de Llanquihue (101):** 10101 Puerto Montt, 10102 Calbuco, 10103 Cochamó, 10104 Fresia, 10105 Frutillar, 10106 Los Muermos, 10107 Llanquihue, 10108 Maullín, 10109 Puerto Varas.
* **Provincia de Chiloé (102):** 10201 Castro, 10202 Ancud, 10203 Chonchi, 10204 Curaco de Vélez, 10205 Dalcahue, 10206 Puqueldón, 10207 Queilén, 10208 Quellón, 10209 Quemchi, 10210 Quinchao.
* **Provincia de Osorno (103):** 10301 Osorno, 10302 Puerto Octay, 10303 Purranque, 10304 Puyehue, 10305 Río Negro, 10306 San Juan de la Costa, 10307 San Pablo.
* **Provincia de Palena (104):** 10401 Chaitén, 10402 Futaleufú, 10403 Hualaihué, 10404 Palena.

#### Región Aisén del General Carlos Ibáñez del Campo (11)
* **Provincia de Coyhaique (111):** 11101 Coyhaique, 11102 Lago Verde.
* **Provincia de Aysén (112):** 11201 Aysén, 11202 Cisnes, 11203 Guaitecas.
* **Provincia de General Carrera (113/114):** 11301 Cochrane, 11302 O'Higgins, 11303 Tortel, 11401 Chile Chico, 11402 Río Ibáñez.

#### Región de Magallanes y de la Antártica Chilena (12)
* **Provincia de Magallanes (121):** 12101 Punta Arenas, 12102 Laguna Blanca, 12103 Río Verde, 12104 San Gregorio.
* **Provincia de Antártica Chilena (122):** 12201 Cabo de Hornos, 12202 Antártica.
* **Provincia de Tierra del Fuego (123):** 12301 Porvenir, 12302 Primavera, 12303 Timaukel.
* **Provincia de Última Esperanza (124):** 12401 Natales, 12402 Torres del Paine.

### Anexo 2. Clasificación de países (Estándar ONU M49)

Utilizado en `nacionalidad`, `mig3_cod`, `mig6_cod`, `b18_codigo`.

| País | M49 | Antiguo ENE | País | M49 | Antiguo ENE |
| :--- | :---: | :---: | :--- | :---: | :---: |
| **Chile** | **152** | 0 | **Argentina** | **32** | 20004 |
| **Bolivia** | **68** | 20010 | **Brasil** | **76** | 20011 |
| **Colombia** | **170** | 20014 | **Ecuador** | **218** | 20018 |
| **España** | **724** | 40014 | **Estados Unidos** | **840** | 20020 |
| **Haití** | **332** | 20027 | **Perú** | **604** | 20042 |
| **Rep. Dominicana** | **214** | 20044 | **Uruguay** | **858** | 20051 |
| **Venezuela** | **862** | 20052 | **Alemania** | **276** | 40002 |
| **China** | **156** | 30011 | **Francia** | **250** | 40017 |
| **Italia** | **380** | 40025 | **Reino Unido** | **826** | 40036 |
| *Zona no especificada* | **898** | - | *Sin información* | **999** | - |

*(El resto de países sigue la codificación estándar numérica oficial de Naciones Unidas M49).*

### Anexo 3. Clasificación de grupo ocupacional (CIUO-08)

Variables: `b1`, `e16_ciuo08` (Gran Grupo).

| Código | Gran grupo CIUO-08 |
| :---: | :--- |
| **1** | Directores y gerentes |
| **2** | Profesionales científicos e intelectuales |
| **3** | Técnicos y profesionales de nivel medio |
| **4** | Personal de apoyo administrativo |
| **5** | Trabajadores de los servicios y vendedores de comercios y mercados |
| **6** | Agricultores y trabajadores calificados agropecuarios, forestales y pesqueros |
| **7** | Oficiales, operarios y artesanos de artes mecánicas y de otros oficios |
| **8** | Operadores de instalaciones y máquinas y ensambladores |
| **9** | Ocupaciones elementales |
| **10** | Otros no identificados |

---

### Anexo 4. Modificación de pregunta sobre prestaciones laborales

A partir del trimestre **JAS 2017**, la pregunta única `b7` fue reemplazada por dos bloques:
* **`b7a` (Cotizaciones obligatorias):** `b7a_1` (pensión), `b7a_2` (salud), `b7a_3` (seguro de cesantía).
* **`b7b` (Derechos laborales):** `b7b_1` (vacaciones), `b7b_2` (días por enfermedad), `b7b_3` (maternidad/paternidad), `b7b_4` (sala cuna/guardería).

---

### Anexo 5. Clasificación de rama de actividad económica (CAENES)

Variables: `b13_rev4cl_caenes`, `b14_rev4cl_caenes`, `r_p_rev4cl_caenes`.

| Código | Sección | Descripción |
| :---: | :---: | :--- |
| **1** | A | Agricultura, ganadería, silvicultura y pesca |
| **2** | B | Explotación de minas y canteras |
| **3** | C | Industrias manufactureras |
| **4** | D | Suministro de electricidad, gas, vapor y aire acondicionado |
| **5** | E | Suministro de agua; evacuación de aguas residuales y gestión de desechos |
| **6** | F | Construcción |
| **7** | G | Comercio al por mayor y al por menor; reparación de vehículos |
| **8** | H | Transporte y almacenamiento |
| **9** | I | Actividades de alojamiento y de servicio de comidas |
| **10** | J | Información y comunicaciones |
| **11** | K | Actividades financieras y de seguros |
| **12** | L | Actividades inmobiliarias |
| **13** | M | Actividades profesionales, científicas y técnicas |
| **14** | N | Actividades de servicios administrativos y de apoyo |
| **15** | O | Administración pública y defensa; planes de seguridad social |
| **16** | P | Enseñanza |
| **17** | Q | Actividades de atención de la salud humana y de asistencia social |
| **18** | R | Actividades artísticas, de entretenimiento y recreativas |
| **19** | S | Otras actividades de servicios |
| **20** | T | Actividades de los hogares como empleadores |
| **21** | U | Actividades de organizaciones y órganos extraterritoriales |

---

### Anexo 6. Variables descontinuadas

* **Ramas en CIIU Rev. 3:** `b13_ciiu_rev3`, `b14_ciiu_rev3`, `e18` (descontinuadas en OND 2016).
* **Ocupación en CIUO-88:** `b1_ciuo88`, `e16_ciuo88` (descontinuadas en EFM 2019).
* **Preguntas de empleo anterior:** `c1`, `c8`, `c13`, `e1`, `e14` a `e19` (descontinuadas en EFM 2020).

---

### Anexo 7. Exportación y conversión de formatos

* **CSV a Stata:** Archivos delimitados por punto y coma (`;`).
  ```stata
  import delimited "ruta.csv", delimiter(";") clear
  destring fact_cal, replace dpcomma
  
### DTA a SPSS (.sav) usando R:
 library(haven)
 base <- read_dta("https://www.ine.gob.cl/docs/default-source/ocupacion-y-desocupacion/bbdd/2024/stata/ene-2024-04-mam.dta")
 write_sav(base, "base.sav")

### Anexo 8. Cuestionario sobre impacto de COVID-19
Variables aplicadas de forma extraordinaria entre MAM 2020 y OND 2021 (i11, i12, i13_1 a i13_11, e21, e22, e23, e24) para registrar ingresos afectados, estrategias de financiamiento del hogar y causas de cese laboral asociadas a la pandemia.
