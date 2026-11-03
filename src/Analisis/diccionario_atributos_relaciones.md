# Diccionario de atributos laborales y educacionales

Actualizado 03-11-26

Reúne las columnas laborales y educacionales de las tablas procesadas de cada fuente, y cómo se relacionan entre sí. Los ejemplos son valores reales de las tablas. Las coberturas de la sección de relaciones se midieron con los datos el 02-11-26. Se limpió el 03-11-26 para dejar solo las fuentes del mapa; lo retirado sigue en la etiqueta de git `indice-cupos`.

## Tablas

| Nombre | Archivo | Fuente | Una fila es | Filas | ¿Trae carrera? |
|---|---|---|---|---:|---|
| **CASEN** | `Scrapers/CASEN/Salida/casen_procesado.csv` | Encuesta CASEN 2024 | Una persona que asiste o asistió a educación superior | 61.070 | Sí, en texto libre |
| **Censo** | `Scrapers/CENSO/Salida/censo_procesado.csv` | Censo 2024, INE | Un grupo de personas con las mismas características (sumar `personas`) | 14.793 | No, solo nivel de título |
| **ENE** | `Scrapers/ENE/Salida/ene_procesado.csv` | Encuesta Nacional de Empleo, INE (dic 2025 a sep 2026) | Una entrevista | 324.054 | No, solo nivel educativo |
| **MiFuturo** | `Scrapers/Empleabilidad/Salida/empleabilidad_procesado.csv` | MiFuturo, Mineduc | Una institución y carrera genérica | 1.690 | Sí |
| **Titulados** | `Scrapers/Titulados/Salida/titulados_procesado.csv` | SIES, Mineduc (2007-2025) | Un grupo de títulos por año, sede, institución y carrera | 234.074 | Sí |

---

## 1. Atributos laborales

### CASEN

| Columna | Concepto | Ejemplo |
|---|---|---|
| `activ` | Condición de actividad | `1` = Ocupado; `2` = Desocupado; `3` = Inactivo |
| `o15` | Categoría en la ocupación | `3` = Sector público; `5` = Sector privado; `2` = Cuenta propia; `8` = FF.AA. y del Orden |
| `oficio1_08` | Ocupación, gran grupo CIUO-08 | `2` = Profesionales; `0` = FF.AA. |
| `oficio4_08` | Ocupación exacta, CIUO-08 a 4 dígitos | `2634` = Psicólogos |
| `rama1` | Actividad económica, CAENES (1 a 21) | `16` = Enseñanza; `17` = Salud |
| `rama4` | Actividad económica a 4 dígitos | `8501`, `8601` |
| `yoprcor` | Ingreso de la ocupación principal, corregido | `1000000` |

### Censo

| Columna | Concepto | Ejemplo |
|---|---|---|
| `sit_fuerza_trabajo` | Situación en la fuerza de trabajo | `1` = Ocupado; `2` = Desocupado; `3` = Fuera de la fuerza de trabajo |
| `actividad_ciiu` | Actividad económica, sección CIIU | `B` = Explotación de minas y canteras |
| `codigo_region_trabajo` | Región donde está el empleo | `2` = Antofagasta |
| `p44_lug_trab` | Lugar de trabajo | `3` = Otra comuna; `5` = Varias comunas |
| `personas` | Personas con esas características | `85` |

### ENE

| Columna | Concepto | Ejemplo |
|---|---|---|
| `activ` | Condición de actividad | `1` = Ocupado; `2` = Desocupado; `3` = Fuera de la fuerza de trabajo |
| `cae_general` | Situación de empleo, resumida | `1` = Ocupado tradicional; `4` = Cesante; `9` = Inactivo habitual |
| `cae_especifico` | Situación de empleo, detallada (0 a 28) | Ocupados `1` a `7`; desocupados `8` y `9` |
| `codigo_region_trabajo` | Región donde está el empleo | `2` = Antofagasta |
| `b1` | Ocupación, gran grupo CIUO-08 | `2` = Profesionales; `10` = FF.AA. |
| `categoria_ocupacion` | Categoría en la ocupación (CISE-93) | `3` = Asalariado privado; `4` = Asalariado público; `2` = Cuenta propia |
| `ciso1` | Tipo de ocupación, CISO-18 | `1` = Independiente; `2` = Dependiente |
| `ciso2` | Categoría de ocupación, CISO-18 | `1` = Empleador; `4` = Asalariado privado; `5` = Asalariado público |
| `ocup_form` | Formalidad de la ocupación | `1` = Formal; `2` = Informal |
| `sector` | Sector institucional | `1` = Formal; `2` = Informal; `3` = Hogares empleadores |
| `r_p_rev4cl_caenes` | Actividad económica, CAENES (1 a 21) | `2` = Explotación de minas y canteras |
| `habituales` | Horas habituales de trabajo a la semana | `44` |
| `tpi` | Tiempo parcial involuntario | `0` = No; `1` = Sí |

### MiFuturo

| Columna | Concepto | Ejemplo |
|---|---|---|
| `empleabilidad_1er_anio` | % con empleo al primer año de titulación | `79.7` |
| `empleabilidad_2do_anio` | % con empleo al segundo año de titulación | `80.2` |
| `ingreso_medio_1er_anio` a `ingreso_medio_5to_anio` | Ingreso medio, del año 1 al 5 tras titularse | `998896` a `1395488` (Psicología) |
| `percentil_10_anio_1` a `percentil_90_anio_1` | Distribución del ingreso al año 1 (p10, p25, p50, p75, p90) | p50 = `880598` |
| `percentil_10_anio_5` a `percentil_90_anio_5` | Distribución del ingreso al año 5 (p10, p25, p50, p75, p90) | p50 = `1220001` |

Los ingresos y percentiles repiten unos 249 valores en 1.690 filas, por lo que no se publican por institución; la distinción parece ser por tipo de institución y carrera. También hay una duda pendiente sobre el rótulo de los años en la fuente.

### Titulados

No tiene columnas laborales.

---

## 2. Atributos educacionales

### CASEN

| Columna | Concepto | Ejemplo |
|---|---|---|
| `asiste` | Si asiste actualmente a un establecimiento educacional | `1` = Sí; `2` = No |
| `e6a` | Nivel educacional más alto al que asiste o asistió | `12` = Técnico superior; `13` = Profesional; `14` = Magíster; `15` = Doctorado |
| `e6c_completo` | Si completó ese nivel | `1` = Sí; `2` = No |
| `titulo_comun` | Título obtenido, llave común del proyecto (derivada) | `Profesional`, `Tecnico_Superior`, `Magister`, `Doctorado` |
| `e7` | Carrera, tal como la declaró la persona | `Técnico(a) en enfermería` |
| `carrera_normalizada` | `e7` en mayúsculas y sin tildes (derivada) | `TECNICO(A) EN ENFERMERIA` |
| `cinef13_area` | Campo amplio de estudio, CINE-F 2013 (1 a 10) | `1` = Salud y Bienestar |
| `cinef13_subarea` | Campo específico de estudio (1 a 27) | `15` |
| `e8` | Tipo de institución | `1` = CFT; `2` = IP; `5` = Universidad estatal; `7` = Universidad extranjera |

### Censo

| Columna | Concepto | Ejemplo |
|---|---|---|
| `nivel_titulo` | Título más alto (derivada) | `Tecnico`, `Profesional`, `Sin_titulo` |

### ENE

| Columna | Concepto | Ejemplo |
|---|---|---|
| `nivel` | Nivel educacional más alto aprobado (0 a 14) | `9` = Profesional, aunque la glosa oficial diga "Universitario" |
| `termino_nivel` | Si terminó ese nivel | `1` = Sí; `2` = No |
| `estudia_actual` | Si está estudiando actualmente | `1` = Sí; `2` = No |
| `cine11_1d` | Nivel más alto completado, CINE 2011 (escala INE) | `3` = Técnico; `4` = Profesional; `5` = Magíster; `6` = Doctorado |
| `cine11_2d` | Nivel CINE 2011 a 2 dígitos | `46` |

### MiFuturo

| Columna | Concepto | Ejemplo |
|---|---|---|
| `id_institucion` | Código de la institución | `111` |
| `institucion` | Nombre de la institución | `IP DUOC UC` |
| `tipo_institucion` | Tipo de institución | `Universidad`, `Instituto Profesional`, `Centro de Formación Técnica` |
| `carrera` | Nombre de la carrera en esa institución | `Psicología` |
| `carrera_generica` | Carrera agrupada, según Mineduc | `PSICOLOGIA` |
| `regiones_sede` | Regiones con sede, separadas por `\|` | `VALPARAISO\|METROPOLITANA\|BIOBIO` |

### Titulados

| Columna | Concepto | Ejemplo |
|---|---|---|
| `anio` | Año de titulación | `2025` |
| `comuna` | Comuna de la sede | `PROVIDENCIA` |
| `codigo_institucion` | Código de la institución | `143` |
| `institucion` | Nombre de la institución | `IP AIEP` |
| `tipo_institucion` | Tipo de institución | `Universidades`, `Institutos Profesionales`, `Centros de Formación Técnica` |
| `carrera` | Nombre de la carrera en esa institución | `PSICOLOGIA` |
| `carrera_generica` | Carrera agrupada, según Mineduc | `PSICOLOGIA` |
| `cine13_area` | Campo amplio de estudio, CINE-F 2013 | `Ciencias Sociales, Periodismo e Información` |
| `cine13_subarea` | Campo específico de estudio | `Ciencias Sociales y del Comportamiento` |
| `nivel_carrera` | Nivel de la carrera | `Carreras Profesionales`, `Carreras Técnicas`, `Postítulo`, `Magister`, `Doctorado` |
| `carrera_clasificacion_nivel_1` | Clasificación del título | `Profesional Con Licenciatura`, `Técnico de Nivel Superior` |
| `tipo_plan` | Tipo de plan de estudios | `Plan Regular`, `Plan Especial`, `Plan Regular de Continuidad` |
| `modalidad` | Modalidad | `Presencial`, `No Presencial`, `Semipresencial` |
| `duracion_semestres` | Duración de la carrera | `10` |
| `total_titulaciones` | Títulos entregados | `3` |
| `titulaciones_mujeres`, `titulaciones_hombres`, `titulaciones_nb` | Títulos según sexo | `2`, `1`, `0` |
| `titulados_15_19` a `titulados_mayores_40` | Títulos por tramo de edad | `titulados_25_29` = `2` |
| `titulados_menores_40` | Títulos a menores de 40 años | `3` |
| `titulados_edad_sin_info` | Títulos sin edad informada | `0` |
| `edad_promedio` | Edad promedio al titularse | `26` |

---

## 3. Relaciones entre tablas

Ninguna fuente comparte un identificador de persona: las relaciones unen **categorías** (carrera, nivel, actividad, región), no a la misma persona. Solo `id_institucion` y `carrera_generica` unen registros equivalentes de forma directa.

Los puentes están en `Analisis/Puentes_de_mapeo/Salida/`: P1 = actividades, P5 = carrera de CASEN.

### 3.1 Directas: los valores coinciden

```text
<carrera_generica(MiFuturo) -> carrera_generica(Titulados)>             190 de 190 carreras de MiFuturo
<id_institucion(MiFuturo) -> codigo_institucion(Titulados)>             105 de 105 instituciones de MiFuturo
<id_institucion + carrera_generica(MiFuturo) -> codigo_institucion + carrera_generica(Titulados)>   1.690 de 1.690 filas
<rama1(CASEN) -> r_p_rev4cl_caenes(ENE)>                                21 de 21 actividades
<activ(CASEN) -> activ(ENE)>                                            mismos 3 códigos
```

### 3.2 Con conversión: el concepto es el mismo, pero el código difiere

```text
<oficio1_08(CASEN) -> b1(ENE)>                            9 códigos comunes; FF.AA. es 0 en CASEN y 10 en ENE
<cinef13_area(CASEN) -> cine13_area(Titulados)>           10 de 10 áreas; código contra texto, sin tabla oficial; 99,4% de coincidencia
<o15(CASEN) -> categoria_ocupacion(ENE)>                  se agrupan: público (3, 4, 8 -> 4), privado (5 -> 3), independiente (1, 2 -> 1, 2), otros (6, 7, 9 -> 5, 6, 7)
<tipo_institucion(MiFuturo) -> tipo_institucion(Titulados)>   singular contra plural; mejor usar id_institucion
<regiones_sede(MiFuturo) -> nombre_region(Titulados)>     hay que separar por "|"; ARAUCANIA debe pasar a LA ARAUCANIA
```

### 3.3 Por puente: se necesita una tabla intermedia

```text
<e6a + carrera_normalizada(CASEN) -> e6a + carrera_normalizada(P5)>     88,4% de las personas se asigna a una carrera
<carrera_generica(P5) -> carrera_generica(Titulados)>                   completa el paso de CASEN a Titulados
<carrera_generica(P5) -> carrera_generica(MiFuturo)>                    completa el paso de CASEN a MiFuturo


<r_p_rev4cl_caenes(ENE) -> actividad_caenes(P1)>                        21 de 21 actividades
<actividad_caenes(P1) -> actividad_ciiu(P1) -> actividad_ciiu(Censo)>   traduce el código de ENE y CASEN a la letra del censo
<rama1(CASEN) -> actividad_caenes(P1)>                                  21 de 21 actividades

```

Cadenas completas:

```text
<e7(CASEN) -> carrera_normalizada(CASEN) -> carrera_generica(P5) -> carrera_generica(Titulados) -> carrera_generica(MiFuturo)>
```

### 3.4 Geográficas: el código coincide, pero el significado cambia

Todas tienen las 16 regiones. Hay que cuidar **qué lugar representa cada una**:

| Columna | Tabla | Significa |
|---|---|---|
| `codigo_region` | CASEN | Donde **vive** la persona |
| `codigo_region` | ENE | Donde **vive** la persona |
| `codigo_region_trabajo` | ENE y Censo | Donde **trabaja** la persona |
| `codigo_region` | Censo | Donde **vive** la persona |
| `codigo_region` | Titulados | Donde está la **sede** de la institución |
| `regiones_sede` | MiFuturo | Todas las **sedes** de la institución o carrera |

```text
<codigo_region(CASEN) -> codigo_region(ENE)>                    ambas: donde vive
<codigo_region(Titulados) -> codigo_region(CASEN)>              misma numeración, distinto significado: sede contra residencia
```

### 3.5 Comparables, pero no unibles fila a fila

```text
<yoprcor(CASEN) ~ ingreso_medio_1er_anio a 5to_anio(MiFuturo)>    ingresos; se comparan solo agregados por carrera; CASEN incluye todas las edades
<activ(CASEN) ~ empleabilidad_1er_anio(MiFuturo)>                 empleo; miden poblaciones distintas: todos los titulados contra recién titulados
<edad + sexo(CASEN) ~ edad + sexo(ENE)>                           mismas variables de persona; solo se comparan por grupos
<edad + sexo(CASEN) ~ titulados por tramo y sexo(Titulados)>      Titulados ya viene agregado, y su edad es al titularse
```

### 3.6 Sin relación útil demostrada

```text
cinef13_subarea(CASEN) y cine13_subarea(Titulados)  27 códigos contra 29 textos, sin tabla de equivalencia
carrera(MiFuturo) y carrera(Titulados)              0 coincidencias directas; usar carrera_generica
```

Sin par en otra fuente:

- **ENE:** `cae_general`, `cae_especifico`, `ciso1`, `ciso2`, `ocup_form`, `sector`, `habituales`, `tpi`, `termino_nivel`, `estudia_actual`, `cine11_2d`.
- **MiFuturo:** `empleabilidad_2do_anio` y percentiles de ingreso.
- **Titulados:** `tipo_plan`, `modalidad`, `duracion_semestres`, `comuna`.
- **CASEN:** `asiste`, `e6c_completo`, `e8`.
