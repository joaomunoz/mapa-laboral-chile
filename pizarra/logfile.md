(logfile.md Actualizada el 03-11-26)

# 📜 Logfile — Bitácora de Sesiones, Cambios y Completados

## ✅ Completado (Hitos y Logros Consolidados)
<!-- Índice de hitos, lo más nuevo arriba. Una línea por hito; el detalle vive solo en la entrada del log. -->
- 03-11-26 — Mapa interactivo generado (`Mapa_Actividades/Salida/index.html`, 6/6 controles; 20 actividades y 115 fichas recorridas por código sin valores vacíos; clic real pendiente) → log 03-11-26 13:11
- 03-11-26 — Revisión de MiFuturo: años de ingreso confirmados en la fuente y alerta de pocas instituciones (`carreras_por_actividad.csv`, 13/13 controles) → log 03-11-26 13:04
- 03-11-26 — Capa principal con censo (`concentracion_region_actividad_censo.csv` 336×17, 9/9 controles) → log 03-11-26 12:29
- 03-11-26 — Censo 2024 como sexta fuente (`censo_procesado.csv` 14,793×8, 12/12 controles contra el manual del INE) → log 03-11-26 03:00
- 02-11-26 — Tablas 1 a 4 del mapa (`concentracion_region_actividad`, `areas_por_actividad`, `carreras_por_actividad`, `concentracion_region_area`; controles en verde) → log 02-11-26 21:45
- 02-11-26 — Tabla de control de instituciones por carrera (`conteo_instituciones_empleabilidad_titulados.csv` 190×11, 8/8 controles) → log 02-11-26 20:21
- 02-11-26 — Normalización según glosarios y depuración (32 tablas con valores idénticos; P3 y `Titulados/cargar.py` retirados, respaldo en `~/Escritorio/respaldo_P3_cargar_02-11-26/`) → log 02-11-26 17:28
- 02-11-26 — `P9_perfil_laboral_carrera.csv` (7,288 filas, 259 carreras, 9/9 controles) → log 02-11-26 17:28
- 02-11-26 — Objetivo cambia de probabilidad a indicadores comparativos (confirmación del usuario; pizarra actualizada) → log 02-11-26 15:48
- 02-11-26 — Región de trabajo en ENE y demanda (`ene_procesado.csv` 324,054×30, columnas previas idénticas; índice recalculado, orden 0,999) → log 02-11-26 15:45
- 02-11-26 — Control por empleador (`ocupados_region_sector_empleador.csv` 2,370×14; regiones suman el total y calza con Boletín INE) → log 02-11-26 15:20
- 02-11-26 — Demanda pública y reparto revisado del Paso 2 en el índice principal (`CW_Demanda_Publica/`, `per_pct`; controles en verde) → log 02-11-26 14:40
- 02-11-26 — Primer índice completo (`per_carrera_nacional.csv` 274 filas, `per_carrera_region.csv` 2,377 filas; controles en verde) → log 02-11-26 14:02
- 02-11-26 — Pasos 2, 3 y 4 construidos (`desocupados_carrera_region.csv`, `jubilacion_carrera_region.csv`, `vacantes_carrera_region.csv`; totales conservados) → log 02-11-26 14:00
- 02-11-26 — P6 y P7 miden carrera → sector y reemplazan a P3 (prueba contra `b1` de 28,8 a 6,0 en técnicos; errores contrastados con jackknife) → log 02-11-26 13:30
- 02-11-26 — P5 lleva `e7` a `carrera_generica` (88,4% de personas, 99,3% de acuerdo con CINE) → log 02-11-26 12:45
- 02-11-26 — Puentes renombrados a `P<n>_<nombre_tabla>`, P1 y P2 separados (4 tablas y 3 tablas dependientes idénticas byte a byte) → log 02-11-26 12:00
- 02-11-26 — CASEN 2024 procesada (`casen_procesado.csv` 61,070×26, 12/12 controles) → log 02-11-26 11:32
- 02-11-26 — CASEN 2024 descargada como quinta fuente (`casen_2024.dta` 218,367×877, `obtener.py`) → log 02-11-26 03:32
- 02-11-26 — 2 cálculos de control (`titulados_ocupados_region_sector.csv` 747×12; `cobertura_enadel_ene_region_sector.csv` 336×14) → log 02-11-26 02:34
- 02-11-26 — Región estandarizada por código en 5 tablas (`comun/normalizador.py`; 16 pares código-nombre idénticos, validaciones en verde) → log 02-11-26 01:52
- 02-11-26 — Auditoría de las 4 fuentes cerrada (fichas de unidad de conteo; cohortes de Empleabilidad confirmadas en `Metodologia-Buscador-Empleabilidad-e-Ingresos_2025-2026.md`) → log 02-11-26 00:05
- 01-11-26 — P4 v2 con llave común `titulo_comun` (`puente_niveles_educativos.csv` 15×9, 5/5 validaciones) → log 01-11-26 23:10
- 01-11-26 — `procesar.py` de Titulados ampliado (`titulados_procesado.csv` 234,074×28; 19 columnas originales idénticas) y `obtener.py` solo histórica (detección probada contra mifuturo.cl) → log 01-11-26 22:21
- 01-11-26 — ENE ampliada con `termino_nivel` (`ene_procesado.csv` 324,054×29, validaciones en verde, Boletín INE ≤0.08%) → log 01-11-26 21:49
- 01-11-26 — Paso 1 `CW_Empleabilidad_Oferta_Titulados` (`oferta_empleabilidad_procesado.csv` 234,074×25, 4/4 validaciones) → log 01-11-26 10:45
- 01-11-26 — `src/Analisis/` reorganizado en `Puentes_de_mapeo/` y `JOINS/` (generadores re-ejecutados sin error) → log 01-11-26 09:30
- 01-11-26 — Puentes P3 (621 filas) y P4 (15 filas) generados y validados (`puente_carrera_ocupacion.csv`, `puente_niveles_educativos.csv` + inspecciones) → log 01-11-26 09:30
- 31-10-26 — Puentes P1 (21 filas) y P2 (8,623 filas, 6/6 validaciones) (`puente_sectores.csv`, `puente_llaves_carrera.csv`) → log 31-10-26 02:45
- 31-10-26 — `procesar.py` de ENE validado contra Boletín INE n°336, desv. ≤0.08% (`ene_procesado.csv` 324,054×28, 10/10 validaciones) → log 31-10-26 02:09
- s/f — `esquema.py` + `procesar.py` de ENADEL (`enadel_empresas_procesado.csv` 5,576×29, `enadel_cargos_procesado.csv` 32,390×17) → sin entrada de log
- s/f — `esquema.py` + `procesar.py` de Empleabilidad (`empleabilidad_procesado.csv` 1,690×23) → sin entrada de log
- s/f — `procesar.py` de Titulados mejorado: `codigo_institucion` y `edad_promedio` Int16 (`titulados_procesado.csv` 234,074×19) → sin entrada de log
- 29-10-26 — `procesar.py` de Titulados (`titulados_procesado.csv`, sumas de sexo y edad 100% exactas) → log 29-10-26 23:57
- 29-10-26 — `obtener.py` de ENADEL (`ENADEL_2025.csv` 5,604 filas) → log 29-10-26 20:35
- 29-10-26 — `obtener.py` de ENE (8 CSV, 291.9 MB en `Entrada/2026/`) → log 29-10-26 20:05
- 29-10-26 — `obtener.py` de Empleabilidad (`empleabilidad_mifuturo.csv` 1,690×30) y endpoint mal etiquetado descartado → log 29-10-26 17:36
- 29-10-26 — `obtener.py` de Titulados (2 bases descargadas en `Entrada/`) → log 29-10-26 15:45
- 29-10-26 — Esqueleto ETL por scraper + `comun/normalizador.py` (scripts stub creados) → log 29-10-26 15:00
- 29-10-26 — Contexto analítico y fórmula PER definidos (confirmación del usuario) → log 29-10-26 14:30

---

<!-- Entradas del log: lo más nuevo arriba, inmediatamente debajo de esta línea. -->

## 03-11-26 14:59 — Pizarra actualizada al nuevo alcance
- **Contexto / Discusión:** el usuario pidió actualizar la pizarra, que seguía describiendo el índice.
- **Acción / Cambio realizado:** `PIZARRA.md` reescrita al mapa, con decisiones vigentes (el detalle anterior sigue en este log); árbol de `Estructura.md` regenerado desde el disco y descripciones nuevas. El proyecto no es git, así que no aplica `.gitignore` para `pizarra/`.
- **Estado:** verificado.

## 03-11-26 13:11 — Mapa interactivo y nota de lectura
- **Contexto / Discusión:** flujo pedido por el usuario: actividad → mapa de calor → región → estadísticas → carreras afines.
- **Acción / Cambio realizado:** `src/Visualizacion/Mapa_Actividades/` (`generar_mapa.py`, `plantilla.html`, `Salida/index.html`, `Salida/nota_de_lectura.md`). Se extrajo solo la capa regional de la cartografía del censo. Geopandas instalado en `.venv`. Escala de color fija en vez de una por actividad; capa de área CINE fuera del mapa. Corregidos tras capturas: frase, tildes, barras grises, azul dominante y altura.
- **Estado:** pendiente. Generación y recorrido por código verificados, con capturas de escritorio, móvil y modo oscuro. Falta probar clic real y recuadro al pasar el cursor, y la revisión del usuario.

## 03-11-26 13:04 — Revisión de MiFuturo y columnas de la tabla 3
- **Contexto / Discusión:** ingresos que bajaban en 5 carreras y empleabilidades muy altas con poca evidencia.
- **Acción / Cambio realizado:** en la fuente, `primer_ano` a `quinto_ano` coinciden con los datos y cada año viene de cohortes distintas (año 1: 2021-2023; año 5: 2017-2019). No se muestran como evolución. Se corrigió la lectura de Psicología ("cuesta entrar, no quedarse"), que no se sostiene. 37 carreras dependen de 1 institución y 19 de 2. Agregados `ocupados_titulados`, rango de `pct_en_carrera`, `n_instituciones`, `pct_institucion_principal` y `alerta_pocas_instituciones`. U fuera de la lista del mapa con `mostrar_en_mapa`.
- **Estado:** verificado (9/9 y 13/13 controles). Rótulo de percentiles sin confirmar; el mapa no los usa.

## 03-11-26 12:29 — Capa principal con censo
- **Contexto / Discusión:** el usuario aprobó censo como capa principal, ENE como contraste y umbrales de 1,2 y 0,8. La actualización a 2026 queda como opcional: requiere ENE 2024.
- **Acción / Cambio realizado:** `Concentracion_Region_Actividad_Censo/`. Resultado: 55 `concentra`, 149 `similar`, 117 `bajo_lo_nacional` y 15 `base_pequena`. Alertas en B, D, N, O, P y Q. Contraste externo de Minería: censo 268 mil, ENE 156 mil, estudios sectoriales de 200 a 286 mil; sin dato oficial de Sernageomin para 2024.
- **Estado:** verificado (controles); causa de la diferencia entre fuentes sin comprobar.

## 03-11-26 03:00 — Censo 2024 como sexta fuente
- **Contexto / Discusión:** el usuario propuso revisar el censo para ver qué parte de la población está en cada actividad. Trae actividad a 1 dígito y lugar de trabajo, pero no carrera. Se aclaró que pesca y turismo eran solo un ejemplo.
- **Acción / Cambio realizado:** descarga oficial en parquet (`src/Scrapers/CENSO/`), con `.venv` y pyarrow. Salida agregada en CSV a pedido del usuario. Comparación con la tabla 1: correlación 0,95 en veces, 83,0% coincide en estar sobre o bajo el promedio; diferencias de tamaño en 6 actividades.
- **Estado:** verificado (12/12 controles contra el manual).

## 02-11-26 21:45 — Tablas 1 a 4 y afinidad
- **Contexto / Discusión:** se descartaron el top de carreras por región (0 de 336 combinaciones con 5 carreras y 60 casos) y el "calce" por carrera. Dilema afinidad frente a volumen: se muestran % y titulados, ordenados por %.
- **Acción / Cambio realizado:** `Concentracion_Region_Actividad/` (ENE, 336 filas), `Areas_Por_Actividad/` (210), `Carreras_Por_Actividad/` (2,162; 107 afines, 50 indicios visibles, 196 débiles) y `Concentracion_Region_Area/` (160). Un control de la tabla 3 falló por usar el 59,45% antiguo; el método aprobado da 59,35%, comprobado aparte.
- **Estado:** verificado.

## 02-11-26 20:21 — Cambio de alcance: del índice al mapa
- **Contexto / Discusión:** el usuario pidió un mapa por región y carrera. Al revisar se vio que el reparto regional dependía de la sede: Medicina quedaba en cero en Aysén y Ñuble. Se evaluó y descartó la estimación en áreas pequeñas. Carrera × región no pasa el filtro (62 de 3.040 en ocupados). Jubilaciones y vacantes por carrera y región correlacionan 0,84-0,93 con ocupados: casi repiten ese dato. Se retira el índice como resultado.
- **Acción / Cambio realizado:** `src/Analisis/diccionario_atributos_relaciones.md` con relaciones medidas; tabla de control `conteo_instituciones_empleabilidad_titulados`. Se corrigieron cifras preliminares de Medicina (46.271, no 57.800) que incluían personas sin título.
- **Estado:** verificado; archivar lo retirado queda pendiente.

## 02-11-26 17:28 — Normalización, P9 y retiro de P3

- **Contexto / Discusión:** El usuario pidió distinguir público, privado o independiente de minería, finanzas o agro, y normalizar según los glosarios. Se resolvió usar "categoría en la ocupación" y "actividad económica". El proyecto es de portafolio y el índice se llama Índice de Cupos por Carrera. Se corrigió la propuesta de unir `titulo_comun` y `nivel_catalogo`, que son datos distintos.
- **Acción / Cambio realizado:** P9 construido con FF.AA. en `asalariado_publico`. Columnas, carpetas y tablas renombradas en `Analisis/`; `PER_Calculo_Final` pasa a `Indice_Cupos`. Pipeline completo recalculado y comparado con copia: 32 tablas con valores idénticos. Eliminados P3 con sus salidas y definición, y `Titulados/cargar.py`, plantilla vacía sin uso. Se volvió a correr P1, P4 y P7 tras el retiro: salidas idénticas.
- **Estado:** verificado. Pendiente: borrar un CSV con nombre antiguo que estaba abierto en LibreOffice.

## 02-11-26 15:48 — Cambio de objetivo: de probabilidad a indicadores

- **Contexto / Discusión:** El usuario pidió dejar registrado, antes de operar, que no se calculará la probabilidad de las carreras y que el proyecto toma otro rumbo. Se discutió si las vacantes importan: son 74% del numerador y sin ellas 11 de las 20 primeras carreras salen del top 20, pero su reparto por carrera es un supuesto y no mide qué buscan los empleadores.
- **Acción / Cambio realizado:** Pizarra reescrita en visión, avance, roadmap y decisiones. Quedan definidos 3 indicadores: índice de cupos, razón de empleo y perfil laboral. Sin cambios de código en esta entrada.
- **Estado:** verificado como registro. Pendiente: detalle del nuevo rumbo por parte del usuario y nombre del índice.

## 02-11-26 15:45 — Región de trabajo con `b18_region`

- **Contexto / Discusión:** El control por empleador mostró más mineros en la RM que en Antofagasta porque ENE usa residencia. `b18_region` tiene 99,93% válido. Antofagasta tiene 29.722 mineros residentes y 58.460 que trabajan allí.
- **Acción / Cambio realizado:** ENE con `codigo_region_trabajo`; `ocupados_region_sector` con `base_region`; reparto, jubilaciones y vacantes públicas por región de trabajo. Índice: orden nacional 0,999, top 20 igual; cupos en Antofagasta de 15,1 a 17,4 y Aysén de 59,8 a 57,8. El Paso 2 sigue por residencia, con una inconsistencia menor anotada.
- **Estado:** verificado como cálculo. Sin validación independiente, porque CASEN no mide región de trabajo; en región oculta 20,2→20,3.

## 02-11-26 15:20 — Control por empleador y perfil laboral

- **Contexto / Discusión:** El usuario propuso ver cuántos trabajan en lo privado, público e independiente por carrera y sector, y conservar toda celda para que las regiones sumen el total nacional. Se aclaró que una persona encuestada no equivale a una persona real.
- **Acción / Cambio realizado:** `ocupados_region_sector_empleador` con 5 controles en verde. Público: 12,6% de todos los ocupados y cerca de 23% de los titulados. Medición de prueba del perfil laboral: Contador 64,5% privado, 13,1% público y 20,4% independiente; aún sin tabla P9.
- **Estado:** verificado el control; P9 pendiente.

## 02-11-26 14:40 — Sesgo público-privado y reparto de desocupados

- **Contexto / Discusión:** ENADEL no ve el Estado y Medicina daba 8,9 con casi nulo desempleo. El usuario adoptó `per_con_sector_publico` como valor principal y pidió revisar el Paso 2.
- **Acción / Cambio realizado:** `CW_Demanda_Publica/` con razón calibrada por panel ENE. `per_pct` incluye lo público y `per_solo_privado` conserva lo anterior. Paso 2 con mezcla SIES-CASEN y tasa propia solo si difiere claramente. Medicina pasa al puesto 11 de 89; Obstetricia a 88.
- **Estado:** verificado como cálculo. La mejora de −0,41 a −0,51 frente al desempleo es en parte circular; la prueba independiente mejora poco. Se identificó que el empleo público por carrera es medible con CASEN; lo no medible son sus vacantes.

## 02-11-26 14:02 — Primer índice y cambio de probabilidad a indicador

- **Contexto / Discusión:** Se unieron las partes en `PER_Calculo_Final/`. Al ver los resultados, se aceptó que los datos no permiten una probabilidad, sino un indicador comparativo. El usuario lo calificó como un cambio radical, pero adecuado a los datos.
- **Acción / Cambio realizado:** Paso 1 ampliado a 28 columnas, con las 26 anteriores idénticas. Índice nacional con 89 carreras en confianza alta, 101 media y 84 baja. Referencia: 21,3 cupos por 100 competidores. El orden es estable en 4 sensibilidades (correlación 0,94 a 1,00), aunque el valor no lo es. Frente al desempleo de CASEN la correlación es −0,38 en 34 carreras.
- **Estado:** verificado como cálculo; pendiente su lectura. Sesgos abiertos: sector público (Medicina 8,9), carreras que se achican (Secretariado Ejecutivo 367,7) y sede regional (632 combinaciones sin titulados en 2025).

## 02-11-26 14:00 — Pasos 2, 3 y 4 y razón de empleo

- **Contexto / Discusión:** Se ordenó el trabajo en torno a la fórmula tras la aclaración del usuario de que se estaban haciendo cálculos sueltos: cada cálculo debe aportar a una parte de ella. El usuario propuso una razón de empleo por carrera y aprobó el flujo anual en `Titulados` y la suma con sensibilidad para el doble conteo.
- **Acción / Cambio realizado:** Paso 2: 296,875 desocupados de pregrado, 22-54 años, 10 meses × 3/10, reparto por stock. Paso 4: 79,887 vacantes con título (rango hasta 148,927), con tope en 23 empresas. Paso 3: 33,567 jubilaciones por año (45,056 por edad legal), con reparto basado en CASEN. P8 con la razón de empleo: mejora Medicina pero empeora el reparto general (23,3 frente a 24,6 en profesionales), así que queda junto al índice.
- **Estado:** verificado. Supuestos abiertos: igual desempleo entre carreras en el Paso 2 y reemplazo total de cada jubilado en el Paso 3.

## 02-11-26 13:30 — Matriz, perfil y reparto regional

- **Contexto / Discusión:** El usuario aprobó el índice por niveles de confianza con P6 y P7 en lugar de P3, y usar a todos los titulados como base. Propuso usar los ocupados por región y área para complementar: en la prueba superó al ajuste con titulados.
- **Acción / Cambio realizado:** P6 con error por diseño, contrastado con jackknife en 5 celdas (menos de 1% de diferencia). P7 con 93 carreras de perfil propio, 179 de área y nivel y 2 de nivel. `CW_Ocupados_Carrera_Region_Sector` con prueba de región oculta: 49,2 con igual sector, 22,3 con perfil nacional, 20,2 con peso del sector; piso de ruido 12,5. Control `ocupados_region_sector`.
- **Estado:** verificado. La región sigue limitada: la minería de Antofagasta mejora, pero Ing. Comercial sigue baja (10,8% frente a 18,0%).

## 02-11-26 12:45 — P5: carrera de CASEN a catálogo SIES

- **Contexto / Discusión:** `e7` tiene 9,821 textos distintos. Se usa un catálogo según nivel, porque "Enfermería" de un técnico no es la carrera profesional. Se corrigió que `e7` de posgrado suele nombrar el pregrado (solo 18-24% menciona posgrado).
- **Acción / Cambio realizado:** `P5_puente_carrera_casen.py`, con cascada y estado por fila. Asigna 88,4% de las personas. Revisión manual de unas 125 asignaciones: "Gastronomía" caía en "Física y Astronomía" (corregido). 105 personas tienen textos que parecen restos de un corrector automático.
- **Estado:** verificado. Pendiente: los no asignados difieren del resto en 11,4 puntos por sector.

## 02-11-26 12:00 — Puentes con nomenclatura `P<n>_<nombre_tabla>`

- **Contexto / Discusión:** El usuario pidió ordenar `Puentes_de_mapeo/` para que cada script lleve el nombre de la tabla que genera. Se aprobó renombrar también los CSV y conservar la palabra `puente`.
- **Acción / Cambio realizado:** `generar_puentes.py` se dividió en `P1_puente_sectores.py` y `P2_puente_llaves_carrera.py`; los generadores de P3 y P4 se renombraron igual. Se actualizaron `esquema.py`, los 2 cálculos de control y el JOIN del Paso 1. Las 4 tablas de puentes y las 3 tablas dependientes salieron idénticas byte a byte.
- **Estado:** verificado.

## 02-11-26 11:32 — CASEN procesada

- **Contexto / Discusión:** Se aprobó convertir CASEN en una fuente procesada. El universo es e6a 12-15, que coincide exacto con quienes tienen `e7`. Se conservan quienes no tienen título porque su texto ayuda al puente, con `titulo_comun` vacío.
- **Acción / Cambio realizado:** `CASEN/esquema.py` y `procesar.py`; salida `casen_procesado.csv` (61,070×26) con inspección. Se excluyen `o9a`, `o9b`, `o24`, `e9nom` y `e9dir`. Reproduce 30,952 ocupados con título, 3,594,880 expandidos, y 51,0% / 19,7% en grupos 4-9.
- **Estado:** verificado. Pendiente: P5, porque `e7` tiene 9,821 textos distintos; la cobertura de 59,4% con 160 nombres se midió sobre una parte del universo y debe recalcularse.

## 02-11-26 03:32 — CASEN como quinta fuente: el vínculo carrera → sector se puede medir

- **Contexto / Discusión:** ENE y ENADEL no traen carrera. Se revisó documentación de población, empleo y educación (estimador sintético, IPF, estimación en áreas pequeñas, desajuste educativo). CASEN 2024 trae carrera, ocupación y sector en la misma persona. CASEN 2025 no existe y la 2026 entra a terreno en noviembre de 2026.
- **Acción / Cambio realizado:** `CASEN/obtener.py` y glosario en `Datos/datos_externos/glosarios/CASEN/`. Medición con patrones de texto: Medicina 85% en Salud (piloto suponía 52%), Enfermería 79%, Téc. Enfermería 73%, Contador 22% en actividades profesionales y 4% en Salud. Técnicos 51,0% y profesionales 19,7% en grupos 4-9, frente a 53,5% y 20,7% en ENE. Error corregido: `expr` int16 se desbordaba al sumar por grupos.
- **Estado:** pendiente. Los perfiles son preliminares hasta construir P5, y el enfoque del PER sigue sin decidir.

## 02-11-26 02:34 — Cálculos de control y concentración de ENADEL

- **Contexto / Discusión:** El usuario pidió medir personas ocupadas por sector y región. Con ENE, solo 61 de 747 celdas región × sector × título son fiables (57,8% de las personas). ENADEL está muy concentrada: las 10 empresas mayores suman 25,2% de la dotación y 29,1% de las vacantes.
- **Acción / Cambio realizado:** `Calculos_control/titulados_ocupados_region_sector/` (747×12) y `Calculos_control/cobertura_enadel_ene_region_sector/` (336×14; comparable 61, concentrada 9, muestra insuficiente 218, fuera de ENADEL 48). Umbrales de trabajo: 30 empresas y 25% para la mayor.
- **Estado:** verificado. Pendiente: decidir cómo tratar las empresas influyentes.

## 02-11-26 01:52 — Regiones estandarizadas por código

- **Contexto / Discusión:** `region` significaba cosas distintas: código en ENE y nombre en ENADEL y Titulados. Titulados no tenía código y nombraba `LIB. GRAL. B. O'HIGGINS` a la región 6, que por eso no cruzaba con ENE ni ENADEL.
- **Acción / Cambio realizado:** Fuente única `REGIONES` en `comun/normalizador.py`, que reemplaza las listas de ENE y ENADEL. Columnas `codigo_region` y `nombre_region` en ENE, ENADEL (2 tablas), Titulados (→ 29 columnas) y Paso 1 (→ 26). P2 cuenta regiones por código. Regeneradas las salidas de ENE, ENADEL, Titulados, P1, P2 y Paso 1, con sus inspecciones. Sin tocar `regiones_sede` de Empleabilidad ni los datos externos.
- **Estado:** verificado — validaciones en verde; Boletín INE ≤0.08%. Comparación celda por celda con la versión anterior: el único cambio de valores son 6,389 filas de O'Higgins en Titulados y Paso 1; P1 y P2 idénticos. La región de SIES sigue siendo la de la sede.

---

## 02-11-26 01:30 — Piloto: reparto de ocupados por carrera y sector

- **Contexto / Discusión:** ENE y ENADEL tienen sector, pero no carrera. El usuario propuso repartir a los ocupados de cada sector según titulados × empleabilidad, para no dar la misma probabilidad a carreras del mismo sector. Se probó con la ocupación como puente (carrera → CIUO-2 → sector de ENADEL), ajuste iterativo (IPF) contra los totales de ENE y 3 grupos (privado, público, independiente y otros). Corrió en memoria, sin escribir en el proyecto. El puente del piloto es un supuesto escrito a mano; el resto de las carreras usó P3 v1.
- **Lo que funcionó:** Convergencia exacta con los totales ENE. Celdas región × sector × título fiables: 130 de 626, con 79.6% de los ocupados; Salud profesional 13/16 regiones y técnica 7/16. Reparto relativo dentro de Salud profesional: Enfermería 52,757, Medicina 23,953, Kinesiología 19,244.
- **Lo que falló:** Las 10 carreras de salud salen con el mismo perfil (52% en Salud), porque comparten CIUO 22. Medicina en Salud varía de 12% a 56% según el escenario. Asignaciones poco creíbles (9,143 veterinarios en Salud). Validación contra `b1`: técnicos en gran grupo 2, 32.1% predicho vs 7.4% real.
- **Otros hallazgos:** Según ENE, 53.5% de los técnicos y 20.7% de los profesionales ocupados están en los grandes grupos 4 a 9. ENADEL es ciego al empleo público: entre titulados ocupados va de 15.4% en la RM a 50.0% en Aysén (un trimestre, orden de magnitud). Stock SIES / ocupados ENE va de 0.36 en Aysén a 1.42 en Biobío, por usar la región de la sede.
- **Propuesta, sin aprobar:** PER por niveles de confianza: región × título y carrera nacional como resultados medidos; carrera × región solo como estimación en carreras con vínculo fuerte. Alternativa: construir P3 v2 y repetir la prueba.
- **Estado:** verificado como medición; el método no queda validado y la decisión sigue pendiente.

---

## 02-11-26 00:40 — Empleabilidad: metodología vigente y revisión contra los datos

- **Contexto / Discusión:** La metodología 2025-2026 reemplaza a la 2021-2022 como referencia del proyecto; esta última ya no está en `glosarios/EMPLEABILIDAD/`. El enlace del buscador sin `www` entrega una página de mantenimiento; con `www` entrega el documento.
- **Definición confirmada:** Indicador proxy: % de titulados, solo con ingreso anual mayor a $0, cuyos ingresos alcanzan el sueldo mínimo. Cohortes 2021-2023, ingresos 2022-2024, titulados de hasta 30 años. Incluye remuneraciones, honorarios y retiros. Derecho usa el dato del 2º año. No informa cuántos quedan fuera por no tener ingresos; el sector público no se nombra.
- **Mediciones:** Las 1,690 filas del CSV coinciden con la web, sin diferencias, en los 3 tipos de institución. Empleabilidad ponderada: 65.9% al 1er año y 73.5% al 2º (correlación 0.92; 178 filas sin 2º año). Brechas altas en Terapia Ocupacional (49.8 → 72.8), Fonoaudiología (42.8 → 61.8), Nutrición (45.2 → 62.0) y Psicología (62.0 → 78.7).
- **Corrección:** Se retira la hipótesis de un sesgo general por continuidad de estudios: la correlación de −0.16 es efecto de composición (+0.20 en técnicos, −0.05 en profesionales). `pct_continuidad_estudios` queda como columna de contexto, no como ajuste.
- **Propuestas, sin aplicar:** Tratar el indicador como proxy de inserción y no como probabilidad de empleo; decidir 1er o 2º año en el PER; agregar control de encabezados en `Empleabilidad/obtener.py`, que lee las columnas por posición.
- **Acción / Cambio realizado:** Pizarra actualizada. Sin cambios en scripts ni datos.
- **Estado:** verificado

---

## 02-11-26 00:05 — Auditoría de ENADEL y Empleabilidad; metodología MiFuturo

- **Contexto / Discusión:** Cierre de la auditoría por unidad de conteo. Solo medición, sin cambios en scripts ni datos.
- **Hallazgos ENADEL:** Universo = empleadores privados formales: faltan secciones CIIU O, T y U, y su dotación (5.10 M) equivale a ~91% de los asalariados privados ENE (5.58 M). Según ENE JAS 2026, de los ocupados con ed. superior completa, 58.8% son asalariados privados, 22.3% públicos y 18.0% empleadores/cuenta propia. `vacante_2025` lista hasta 3 cargos sin cantidad; `vacante_historica` trae cantidad contratada (95.5%). La suma de `vacantes_proyectadas` pierde 10,792 vacantes (2.1%, 435 empresas) cuando un componente es NA. Solo ~14% de las contrataciones exige ed. superior. Las vacantes no distinguen nuevas de reemplazos: riesgo de doble conteo con jubilación.
- **Hallazgos Empleabilidad:** Según la metodología 2021-2022 (`Datos/datos_externos/glosarios/EMPLEABILIDAD/`), es el % de titulados que, teniendo información de ingresos, obtuvo ingresos ≥ sueldo mínimo en el año siguiente a titularse (datos SII). Junta 3 cohortes, publica desde 25 casos (3 cohortes) o 50 (2), solo pregrado, sin corte regional por protección de datos del SII. Grano verificado: 1,690 filas = 1,690 combinaciones únicas institución × carrera genérica, por lo que `generica` en P2 es el mismo dato medido que `exacto` (66.2% del volumen, con diplomados y posgrados aún incluidos). Cobertura de títulos que compiten: 94.6% del volumen por institución, 97.7% por carrera genérica. Sesgo por continuidad de estudios reconocido por MiFuturo.
- **Acción / Cambio realizado:** Metodología copiada a `glosarios/EMPLEABILIDAD/`. Pizarra actualizada.
- **Estado:** verificado — cohortes confirmadas con la metodología 2025-2026 (→ log 02-11-26 00:40). Las propuestas sobre ENADEL y Empleabilidad siguen sin aplicar.

---

## 01-11-26 23:10 — Auditoría de ENE y P4 v2 con llave de tipo de título

- **Contexto / Discusión:** La anomalía del nivel 8 ("IP" con 0.3% sin terminar) llevó a cruzar `nivel` × `edu2` × `curso`. Patrón determinístico en el 100% de los casos, inferido de microdatos y no documentado por el INE: 7 = técnico con 1-2 años aprobados, 8 = técnico con 3 años, 9 = profesional de cualquier institución. Se descartó la propuesta previa de emparejar por tipo de institución, y se corrigió la afirmación de que `edu2` clasifica todo título de IP como técnico. `cine11_1d` registra el nivel más alto completado.
- **Otros hallazgos:** 324,054 entrevistas = 158,216 personas únicas (hasta 4 veces cada una). El rango 22-54 cubre 89.2% de los desocupados titulados. Con personas únicas, 10 meses y edades 22-54, solo 17 de 47 celdas región × título cumplen el estándar INE (n≥60, gl≥9); postgrado en ninguna región.
- **Decisiones aprobadas:** Paso 2 con llave de tipo de título, edad 22-54 y estrategia (a) de fiabilidad (total regional × mezcla nacional, celda propia solo si es fiable).
- **Acción / Cambio realizado:** Docstring de `ENE/esquema.py` corregido. `generar_puente_p4.py` y `Puentes_de_mapeo/esquema.py` a v2: `nivel_agrupado` → `titulo_comun`, se agregan `significado_ene`, `sies_clasificacion_nivel_1` y `enadel_codigo`; Normalista pasa a No_superior. Ningún otro script usaba `nivel_agrupado`.
- **Estado:** verificado — 5/5 validaciones e inspección 9/9 columnas.

---

## 01-11-26 22:21 — Auditoría de Titulados y ampliación de `procesar.py`

- **Contexto / Discusión:** SIES cuenta titulaciones, no personas. 18.2% son postítulos y posgrados (9.1% diplomados), 2.1% planes de continuidad y 1% licenciaturas no conducentes: doble conteo con cota inferior ≈21%, no medible exacto sin RUT. 8.6% son programas no presenciales, donde la región de la sede no informa residencia. Las "151 duplicadas" del Paso 1 son programas distintos por jornada, plan o sede: falsa alarma. El archivo anual 2025 es idéntico al corte 2025 del histórico.
- **Decisión aprobada (título que compite):** Stock = Técnico de Nivel Superior y Profesional con/sin licenciatura, incluida continuidad. Excluidos: licenciatura no conducente y diplomado. Postítulo, especialidad, magíster y doctorado solo para repartir desocupados ENE de nivel 10-12. El filtro va en `JOINS/`, aún no aplicado.
- **Acción / Cambio realizado:** Borrado `Entrada/titulados_2025.xlsx`. `obtener.py` descarga solo la histórica. `procesar.py` pasa de 19 a 28 columnas (3 de clasificación y 6 de edad).
- **Estado:** verificado — validaciones en verde, 7 rangos de edad = total en 100%, 19 columnas originales idénticas, inspección generada. `obtener.py` probado solo en la detección de enlaces, sin descarga real.

---

## 01-11-26 21:49 — Rediseño del Paso 2 y ampliación de ENE con `termino_nivel`

- **Contexto / Discusión:** Los desocupados ENE no tienen ocupación (`b1` vacía en el 100%) ni campo de estudio, así que `ENE ⋈ P3` es imposible: la carrera debe asignarse con una clave de reparto (estimador sintético). `nivel` no indica titulación: no terminó 34% de nivel 9 y 40% de nivel 7 (JAS). `edu3` = `termino_nivel` (redundante) y `edu2` queda determinado por `nivel`.
- **Revisión de puentes:** P3 es heurístico: 84 ingenierías con las mismas 3 ocupaciones, 32 carreras por defecto a CIUO 24, técnicas asociadas a CIUO profesional, pesos que no suman 1, 621 filas en `pendiente`. Además `b1` de ENE viene a 1 dígito y P3 a 2, lo que limita el Paso 3.
- **Acción / Cambio realizado:** `ENE/esquema.py` y `procesar.py`: `termino_nivel` agregado (28 → 29 columnas), sentinelas 88/99 → NA.
- **Estado:** verificado — validaciones en verde, Boletín INE ≤0.08%. Efecto medido en JAS: 369,689 desocupados titulados de 492,329 (−25%).

---

## 01-11-26 21:26 — Adecuación de la pizarra al formato actualizado de la skill `pizarra`

- **Contexto / Discusión:** La skill `pizarra` se modificó (formato único de fecha `dd-mm-yy`, índice de hitos en una línea, árbol regenerado desde disco). Se compararon los 3 archivos con la skill y se encontraron 7 desajustes; el usuario aprobó aplicar todos y cambiar el guion por espacio en los títulos del log.
- **Acción / Cambio realizado:** (1) Línea 1 de los 3 archivos a `dd-mm-yy`. (2) Títulos del log a `dd-mm-yy hh:mm`. (3) `✅ Completado` reescrito como índice de una línea con evidencia y referencia. (4) Eliminada la copia duplicada de la entrada `31-10-26 02:45`, que contenía hitos antiguos pegados; esos hitos pasaron al índice. (5) Árbol de `Estructura.md` regenerado con `tree` (sin `pizarra/`) y descripciones ajustadas: `cargar.py` solo existe en Titulados, `esquema.py` de puentes en `Puentes_de_mapeo/`, carpetas de pasos 2-5 aún no creadas. (6-7) `PIZARRA.md`: Paso 1 retirado de En curso/Roadmap; próximo paso = Paso 2.
- **Pendiente detectado:** ENADEL, Empleabilidad y la mejora de Titulados no tienen entrada de log propia (hitos marcados `s/f`); P3 y P4 tampoco tienen entrada propia, se referencian a la de su verificación (01-11-26 09:30).
- **Estado:** verificado

---

## 01-11-26 10:45 — Implementación y Validación del Paso 1 (`CW_Empleabilidad_Oferta_Titulados`)

- **Contexto / Discusión:** Arranque de la fase `JOINS/` para construir los 5 subconjuntos intermedios de la fórmula PER. El Paso 1 une la oferta de titulados con el puente P2.
- **Acción / Cambio realizado:** (1) Creado `src/Analisis/JOINS/CW_Empleabilidad_Oferta_Titulados/` con `obtener.py`, `esquema.py` (SSOT), y `crosswalk.py`. (2) Aplicado cruce de doble nivel (exacto y genérico institucional) entre `titulados_procesado.csv` y `puente_llaves_carrera.csv`. (3) Ejecutadas con éxito 4/4 validaciones y exportación a `Salida/oferta_empleabilidad_procesado.csv` (234,074 filas × 25 columnas) con reporte de inspección rigurosa.
- **Estado:** ✅ Verificado — 74.4% de las filas de titulados con empleabilidad al 1er año resuelta.

---

## 01-11-26 09:30 — Reorganización de `src/Analisis/` en `Puentes_de_mapeo/` y `JOINS/`

- **Contexto / Discusión:** Se acordó separar los activos de mapeo (`Puentes_de_mapeo/`) de los subconjuntos de cómputo del PER (`JOINS/`). Cada subconjunto `CW_*` tendrá su propia estructura modular de 3 archivos (`obtener.py`, `esquema.py`, `crosswalk.py` + `Salida/`).
- **Acción / Cambio realizado:** (1) Trasladados y probados `esquema.py`, `generar_puentes.py`, `generar_puente_p3.py`, `generar_puente_p4.py` y sus salidas a `src/Analisis/Puentes_de_mapeo/`. (2) Ajustadas las rutas relativas de `sys.path` y `DIR_SCRAPERS` a `parents[2]`. (3) Verificada la ejecución limpia de todos los generadores y sus reportes de inspección.
- **Estado:** ✅ Verificado — Todos los puentes operativos en `Puentes_de_mapeo/Salida/`. Estructura `JOINS/` lista para recibir los subconjuntos.

---

## 31-10-26 02:45 — Módulo `src/Analisis/` y puentes P1 + P2 implementados

- **Contexto / Discusión:** Se acordó construir el crosswalk por partes como **archivos puente** (activos de datos auditables, no código embebido) en `src/Analisis/` (decisión del usuario), arrancando por P1 (sectores) + P2 (llaves de carrera), P3 a `ciuo_nivel_2` en versión candidata N:N con score (pesos en v2). Llave maestra del cruce T↔E = código de institución, no texto (105/105 códigos MiFuturo presentes en SIES; 98.1% mismo nombre, las 2 diferencias son solo apóstrofes de O'Higgins).
- **Acción / Cambio realizado:** (1) Creado `src/Analisis/esquema.py` — `PUENTE_SECTORES` y `PUENTE_LLAVES_CARRERA` (19 col), catálogos `ORIGEN_LLAVES`/`NIVELES_MATCH`/`FUENTES_EMPLEABILIDAD`, `VALIDACIONES`, y P3 (`PUENTE_CARRERA_OCUPACION`) + P4 (CINE) documentadas como pendientes. (2) Creado `src/Analisis/generar_puentes.py` — P1 transcribe verbatim el Anexo 5 del libro de códigos ENE (CAENES 1-21 ↔ CIIU A-U, 1:1); P2 agrega Titulados al grano `(id_institucion, carrera_norm)`, resuelve empleabilidad en 3 niveles (exacto → media `[inst, genérica]` → media nacional), colapsa las carreras sin valor por debajo de genérica a un residuo `[inst, genérica]` (evita repetir la media nacional) y exporta con `sep=";"` + reportes `inspect_data`.
- **Resultados:** P1 = 21 filas (2/2 validaciones). P2 = 8,623 filas × 19 col, **6/6 validaciones en verde** (PK única, catálogos, rango [0,100] con NA⇔sin_dato, nivel exacto⇒fuente exacto y n=1, total ≥ mayores_40). Cobertura bidireccional: nivel exacto 1,690 / genérica 2,484 / nacional 2,873 / ninguno 1,576; **79.5% del volumen de titulaciones (4,023,223) con empleabilidad resuelta**; las 1,690 filas MiFuturo presentes al 100% con su valor exacto preservado. Verificación independiente: suma de `titulaciones_total` = 4,023,223 = fuente exacta; 289 filas `solo_empleabilidad` (carreras medidas sin titulados 2007-2025).
- **Defectos corregidos durante la construcción:** PK duplicada (las filas con match exacto aparecían en ambos lados → el lado Titulados solo aporta llaves no presentes en MiFuturo), `origen` mal calculado en el colapsado, lambda ambiguo con `pd.NA`, y ruta de `inspect_data` al importarlo desde `src/Analisis/`.
- **Estado:** ✅ Verificado — `Salida/puente_sectores.csv` (21×4) y `Salida/puente_llaves_carrera.csv` (8,623×19) + reportes de inspección.

---

## 31-10-26 02:09 — `esquema.py` y `procesar.py` de ENE implementados y validados

- **Contexto / Discusión:** Se acordó definir primero el esquema ("así veo bien en detalle la tabla que se generará") antes de codificar. Se relevó el dominio de ~40 columnas candidatas en los 8 reportes de inspección, se resolvió la clave primaria real (`idrph` = persona; `id_identificacion` = hogar, NO es PK) y se determinó empíricamente que los 8 CSV son **trimestres móviles solapados** (archivo K = meses K-1..K+1) con la misma entrevista duplicada hasta 3 veces, contenido idéntico y `fact_cal` recalibrado.
- **Acción / Cambio realizado:** (1) Creado `src/Scrapers/ENE/esquema.py` — `ESQUEMA_ENE` (28 columnas), `CLAVE_ENE`, `COLUMNAS_ENTRADA` (proyección `usecols` de 222→28), `SENTINELAS` (88/99/999/0 → NA), 10 reglas `VALIDACIONES` y documentación del panel y la escala de `fact_cal`. (2) Creado `src/Scrapers/ENE/procesar.py` — lectura `sep=";"`/`dtype=str`, validación `mes_central==K` por archivo, dedup con **política "central"** (conservar el `fact_cal` del archivo cuyo `mes_central` = mes de la entrevista; desviación regional ≤1.75% vs ≤4.34% de first/last), reparación de `fact_cal` con coma decimal, derivadas `mes` ("AAAA-MM") y `nombre_region`, sentinela → NA, `reindex(columns=ESQUEMA_ENE)` + tipado estricto, 10 validaciones y exportación con reporte `inspect_data`.
- **Hallazgo metodológico clave:** `fact_cal` **no es un peso mensual sino trimestral** — cadencia de entrevista cada 3 meses (160,236/160,838 huecos = 3 meses), 0% de solape entre meses consecutivos y suma de un archivo = población (20.27M total / 16.62M ≥15). Regla de uso documentada: **niveles ⇒ 3 meses consecutivos (o mes ×3); tasas ⇒ cualquier corte**.
- **Validación contra el dato oficial:** contra Boletín INE n°336 (29-10-2026, trimestre jul-sep 2026): fuerza de trabajo 10,282,930 (+0.00%), ocupadas 9,275,130 (+0.00%), desocupadas 1,007,799 (-0.02%), inactivas 6,421,373 (+0.08%), informales 2,452,190 (+0.03%), tasa desocupación 9.80% (oficial 9.8%), participación 61.56% (61.6%), ocupación 55.53% (55.5%).
- **Verificación adicional:** dtypes == esquema tras releo, PK única (0 duplicados), 10 meses (2025-12…2026-09), 16/16 regiones, 0 sentinelas residuales, cobertura b1 en ocupados 100% (63/140,036 sin dato), `cine11_2d` conserva el cero a la izquierda en el archivo (`01`,`02`,…).
- **Estado:** ✅ Verificado — `Salida/ene_procesado.csv` (324,054×28) + `ene_procesado_inspeccion.txt`.

---

## 29-10-26 23:57 — `procesar.py` de Titulados implementado y verificado

- **Contexto / Discusión:** Con base en el análisis del glosario y la estructura de los 234K registros históricos (2007-2025), se diseñó la reducción de 42 a 18 columnas clave. Se acordó conservar el detalle completo `[anio, region, comuna, institucion, carrera]` en lugar de agregar previamente, y derivar la distribución etaria (`<40` / `≥40`) para la estimación de jubilaciones del PER.
- **Acción / Cambio realizado:** Creado `src/Scrapers/Titulados/procesar.py`. Pipeline con: (1) lectura del Excel histórico; (2) parseo de `AÑO` (`TIT_2025` → `2025`); (3) tipado numérico y conversión de categorías; (4) limpieza de texto y normalización de claves de cruce (`region`, `carrera_generica`); (5) derivación robusta de `titulados_mayores_40` y `titulados_menores_40` garantizando suma exacta; (6) suite de validaciones de integridad; (7) exportación a `Salida/titulados_procesado.csv` (separador `;`, UTF-8).
- **Resultados de validación:** 234,074 filas procesadas. Suma de sexos == total (100.0%), suma de rangos etarios == total (100.0%), cobertura 99.8%-100%. Total histórico de titulados en Chile (2007-2025): 4,023,223 (447,562 mayores de 40 años).
- **Estado:** ✅ Verificado.

---

## 29-10-26 20:35 — `obtener.py` de ENADEL implementado y verificado

- **Contexto / Discusión:** Fuente más sencilla de las 4: WordPress estático con plugin Download Monitor. El enlace del ZIP CSV está directamente en el HTML, sin AJAX ni JavaScript. Se acordó estrategia de 3 niveles: descubrir enlace → descargar ZIP → extraer CSVs, todo idempotente.
- **Acción / Cambio realizado:** Creado `src/Scrapers/ENADEL/obtener.py`: (1) GET página → regex `FORMATO-CSV-ENADEL.*\.zip` en hrefs → URL limpia sin query params; (2) descarga idempotente del ZIP (1.7 MB) a `Entrada/`; (3) extracción idempotente de CSVs con protección path-traversal. El ZIP se conserva como respaldo crudo.
- **Hallazgos para `procesar.py`:** `ENADEL_2025.csv` → 5,604 filas, UTF-8, separador **coma** (no `;`), nulos como `NA` (formato R). Contiene directamente `pond_final` (factor expansión), `reg_encuesta` (región), códigos **CIUO-08** (5 bloques: c1, c3, d1, d15, e13) y **CIIU** (a1_Clase/Grupo/División/Sección) → es la fuente que habilita el crosswalk carrera↔ocupación↔sector.
- **Estado:** ✅ Verificado — ZIP 1.7 MB + CSV 10.9 MB, 5,604 filas.

---

## 29-10-26 20:05 — `obtener.py` de ENE implementado y verificado

- **Contexto / Discusión:** Los microdatos ENE del INE están en una estructura de carpetas Sitefinity que se navega vía cascada de 3 niveles AJAX. El HTML inicial NO contiene los enlaces de descarga (se cargan con jQuery). El usuario confirmó la estrategia: descargar todos los CSV de 2026 disponibles a `Entrada/2026/` como capa cruda, dejando consolidación para `procesar.py`.
- **Acción / Cambio realizado:** Creado `src/Scrapers/ENE/obtener.py` con 4 niveles: (1) GET página principal → extraer GUID de carpeta "BASES DE DATOS" del atributo `data-folder`; (2) POST `hijosCarpeta/` con el GUID → obtener subcarpetas (años) y localizar la del año objetivo; (3) POST `getArchivos/` con GUID del año → lista de archivos (16 = 8 CSV + 8 DTA), filtrar solo `.CSV` y forzar `https://`; (4) descarga idempotente con `stream=True` (~36 MB c/u).
- **Correcciones durante desarrollo:** (a) la primera versión intentaba extraer enlaces con regex directo del HTML → falló porque el bloque `.contNavArchivosDescarga` está vacío en el HTML inicial; (b) el regex del GUID matcheaba el primer `data-folder` de la página en lugar del de "BASES DE DATOS" → se restringió el patrón a no cruzar `</div>` hermanos.
- **Hallazgos para `procesar.py`:** (a) encoding es ASCII, no Latin-1; (b) separador `;`; (c) **el orden de columnas cambia** entre archivos 01-05 y 06-08 (`tipo`/`r_p_c` se intercambian) → debe leerse por nombre, no posición; (d) 96,000-99,000 filas por archivo; (e) archivos 06-08 usan CRLF, 01-05 usan LF.
- **Estado:** ✅ Verificado — 8 CSVs, 291.9 MB en `Entrada/2026/`, todos con contenido válido (~97K filas c/u).

---

## 29-10-26 17:36 — `obtener.py` de Empleabilidad implementado y verificado

- **Contexto / Discusión:** La fuente no expone endpoint JSON con la tabla mostrada en HTML. Se optó por scraping del HTML vía POST al formulario `form_empleabilidad`, más enriquecimiento por AJAX. Se definieron 30 columnas de salida acordadas con el usuario.
- **Acción / Cambio realizado:** Creado `src/Scrapers/Empleabilidad/obtener.py` con 3 niveles: (1) 3 POST por `tipo_institucionEmp` → 1690 filas con `tipo_institucion`, `id_institucion` y `carrera_generica`; (2) 16 llamadas `dcms_ajax_all_filter` → `regiones_sede`; (3) 252 llamadas `detalleEstadisticas` → `ingreso_medio_1..5` + percentiles 10-90 (años 1 y 5).
- **Correcciones durante desarrollo:** (a) `data-order` estaba en la etiqueta de apertura `<td>`, no en el contenido → atributos y contenido se parsean ahora por separado; (b) el catálogo de estadísticas retenía el texto "Ver estadísticas" y `<br/>` en las claves → join en 0%, corregido a 96.6%; (c) se añadió reintento con backoff ante cortes de conexión por rate-limit.
- **Nivel descartado:** `dcms_armado_tabla_empleabilidad` no aporta datos nuevos (campos mal etiquetados, arancel siempre 0) y `dcms_armado_tabla_carrera` solo hacía join en 12.8%. Documentado en el docstring.
- **Estado:** ✅ Verificado — 1690 filas, 30 columnas, cobertura clave 100% en `empleabilidad_1er_anio` (base del PER), 96.6% en ingresos, 93.8% en regiones.

---

## 29-10-26 16:41 — Análisis exploratorio de la fuente de Empleabilidad

- **Contexto / Discusión:** Definición de estrategia. Se revisó `ajax.js` y se confirmó que la tabla se sirve por POST clásico (no AJAX), por lo que no se requiere navegador headless.
- **Acción / Cambio realizado:** Pruebas contra los endpoints reales: verificación de conteos por tipo (176+324+1190=1690), mapa de regiones (107 instituciones, 88/105 cubiertas), catálogo de estadísticas (252 combos), y diagnóstico de integridad de `dcms_armado_tabla_empleabilidad` (177 muestras, 100% de coincidencia con campos base).
- **Estado:** ✅ Verificado

---

## 29-10-26 15:45 — `obtener.py` de Titulados implementado y verificado

- **Contexto / Discusión:** Definición de estrategia de scraping dinámico para mifuturo.cl (evitar URLs hardcodeadas con fechas cambiantes). Se decidió descargar ambas bases: anual y histórica.
- **Acción / Cambio realizado:** Creado `src/Scrapers/Titulados/obtener.py` con detección por regex (`PATRON_ANUAL`, `PATRON_HISTORICA`), descarga a `Entrada/` y validación de presencia de ambos archivos.
- **Estado:** ✅ Verificado (ejecutado con éxito, descarga las 2 bases correctamente)

---

## 29-10-26 15:37 — Inicialización de la pizarra del proyecto

- **Contexto / Discusión:** Definición de la estructura de carpetas y archivos del pipeline PER. Se establece el rol de Data Analyst experto en estadística para toda la sesión.
- **Acción / Cambio realizado:** Se creó la carpeta `pizarra/` con los 3 archivos (`PIZARRA.md`, `Estructura.md`, `logfile.md`). Se mapeó el árbol actual de directorios y se documentó el estado inicial del proyecto.
- **Estado:** ✅ Verificado

---

## 29-10-26 15:00 — Creación de esqueleto ETL de scrapers

- **Contexto / Discusión:** Se decidió implementar un patrón ETL modular de 3 scripts por scraper (`obtener.py`, `procesar.py`, `cargar.py`), cada uno con carpetas `Entrada/` y `Salida/` propias, más un módulo `comun/` con normalizador compartido.
- **Acción / Cambio realizado:** Se eliminaron los `.py` obsoletos de generación anterior. Se crearon 12 scripts stub (3 por cada 4 scrapers) y `comun/normalizador.py`, todos con el formato de cabecera obligatorio.
- **Estado:** ✅ Verificado (esqueleto), 🔴 Lógica ETL pendiente

---

## 29-10-26 14:30 — Definición del contexto analítico del proyecto

- **Contexto / Discusión:** Presentación del proyecto PER (Probabilidad de Empleabilidad Regional Ajustada), sus 4 fuentes de datos oficiales (SIES, MiFuturo, ENE, ENADEL) y la ecuación de cálculo.
- **Acción / Cambio realizado:** Se estableció el rol de Data Analyst experto en estadística y se validó la comprensión de la lógica analítica.
- **Estado:** ✅ Verificado
