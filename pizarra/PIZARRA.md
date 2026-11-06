(PIZARRA.md Actualizada el 06-11-26)

# 🧙 PIZARRA — Mapa Laboral de Chile

> Tablero vivo del proyecto. Bitácora ejecutiva para entender rápidamente el estado actual y los siguientes pasos.

**Contexto activo:** rama `main`, solo local, sin repositorio remoto. `.venv/` para leer parquet y generar el mapa. Carpeta renombrada a `Mapa_Laboral_Chile`. En claude-mem, el historial previo sigue bajo el proyecto `Proyecto Probabilidad_carreras`.

---

## 🎯 Visión

Proyecto de portafolio: un **mapa interactivo de Chile** para quien quiere conocer la situación laboral y educacional del país: dónde se concentra cada actividad económica, cómo se distribuye el trabajo por sexo y nivel de estudios, y qué carreras están más ligadas a cada actividad.

**Flujo:** partes en el resumen de la población y las 20 actividades → eliges una actividad → ves el resumen de Chile y el mapa coloreado según cuánto pesa en cada región → haces clic en una región y ves sus estadísticas → ves las carreras afines a nivel nacional → abres la ficha de una carrera.

**Cambio de alcance (02 y 03-11-26):** se retiró el Índice de Cupos. Carrera × región no es medible: de 3.040 combinaciones, solo 62 pasan el filtro en ocupados y 0 en desocupados. El proyecto muestra solo lo medido, y cada dato conserva su fuente.

| Capa | Pregunta | Fuente | Alcance |
|---|---|---|---|
| **Concentración** | ¿Qué actividad pesa más en cada región? | Censo 2024; ENE como contraste | Regional, donde está el trabajo |
| **Formación** | ¿De qué áreas vienen sus titulados? | CASEN 2024 | Nacional |
| **Carreras afines** | ¿Qué carreras dependen más de esa actividad? | CASEN 2024 | Nacional |
| **Situación por nivel** | ¿Cuántos técnicos y profesionales trabajan o están desocupados? | Censo 2024; ENE como contraste | Regional y nacional |
| **Ficha de carrera** | Títulos 2007-2025 y de 2025, empleabilidad (con rango entre instituciones) e ingresos | SIES y MiFuturo | Nacional |

---

## 📊 Avance general estimado: ~98%

> Se mantiene en ~98%: el mapa se depuró con el criterio "mostrar solo lo necesario" y mejoró su navegación. Faltan licencia, repetir la prueba en clon limpio y decidir la publicación.

| Área | Avance | Estado | Notas |
|---|---|---|---|
| Fuentes y scrapers | 100% | 🟢 | 5 fuentes: Censo, ENE, CASEN, SIES y MiFuturo |
| Procesamiento `procesar.py` | 95% | 🟢 | Pendiente menor en MiFuturo, que no afecta al mapa |
| Puentes `src/Analisis/` | 100% | 🟢 | P1, P5 y P9 alimentan el mapa; P6 es control de sesgo |
| Tablas del mapa | 100% | 🟢 | Censo, áreas, carreras y situación por nivel; ENE como contraste |
| Revisión de MiFuturo | 95% | 🟢 | Años de ingreso y edad (titulados de hasta 30 años) confirmados; percentiles descartados por no ser necesarios |
| Mapa interactivo | 98% | 🟢 | Depurado y con navegación por enlace el 06-11-26; falta revisar la bajada animada en un celular real |
| Nota de lectura | 100% | 🟢 | `Salida/nota_de_lectura.md` |
| Saneamiento | 100% | 🟢 | Lo retirado salió del proyecto; queda en la etiqueta `indice-cupos` |
| Git | 90% | 🟡 | Historial local; falta decidir si se sube a GitHub |
| README y presentación | 90% | 🟡 | Resumen, objetivo, límites, metodología y fuentes; falta enlace para ver el mapa y licencia |

---

## 🔶 En curso / parcial

- **Criterio vigente, "mostrar solo lo necesario":** cada dato debe ayudar a responder cómo es la situación laboral y educacional de Chile, o la relación entre actividad y educación. Al revisar, se prefiere quitar antes que agregar.
- **Pendientes menores de evaluaciones anteriores:** el título del mapa repite el segundo hallazgo; leyenda con tonos suaves y peso del negro en la barra de población.
- **Dos decisiones del usuario:** mostrar valores o solo porcentajes en los títulos por sexo, porque restando se deduce la categoría no binaria o indefinida; y cómo mostrar ocupados en la tabla regional de nivel por sexo, donde la tasa usa residencia.
- **Revisión externa:** falta mostrarle el mapa a alguien que no lo conozca, y revisar en un celular real la bajada automática al resultado.
- **Comparación Censo y ENE:** el patrón regional coincide (correlación 0,95 en las 209 combinaciones fiables en ENE; 0,94 en las 336), pero el tamaño difiere en Minería, Electricidad, Serv. administrativos, Adm. pública, Enseñanza y Salud, y también las tasas de desocupación. La causa no está comprobada; el mapa lo avisa.

---

## ⏳ Pendiente — Roadmap

1. **Terminar la revisión del mapa:** cabecera entre 1000 y 1100 px, espacio vacío bajo 1290 px, título del mapa en tres líneas, confirmar el criterio de "menos de 10" y lo que el usuario pida.
2. **Fórmula oficial de las tasas:** confirmar si el INE incluye a las personas sin dato (ocupación 54,4% o 54,8%; también afecta a participación).
3. **Licencia del proyecto:** propuesta MIT para el código y CC BY 4.0 para el análisis, sin decidir. Revisar que las condiciones de las fuentes permitan redistribuir las tablas derivadas.
4. **Repetir la prueba en clon limpio:** la última es del 03-11-26, anterior a la versión actual.
5. **Subir a GitHub,** si el usuario lo decide: elegir público o privado, y GitHub Pages para ver el mapa sin descargarlo.
6. **Opcional, selector de cantidad o peso:** en pausa, porque la vista nacional ya muestra ambas lecturas.
7. **Ajustes menores:** `ARAUCANIA` en `regiones_sede`, Programas de Formación Pedagógica fuera de P9.

---

## 🧭 Decisiones de arquitectura clave

**Alcance y fuentes**
- **Solo datos medidos en el mapa:** se descartaron la probabilidad, el Índice de Cupos y el reparto sintético carrera × región, porque suponen la misma mezcla en todas las regiones. Alternativa de respaldo: estimación por área, rotulada, si se valida.
- **Censo como capa principal, ENE como contraste:** el censo cubre las 336 combinaciones y ENE deja 112 sin muestra. No se mezclan sus cifras. El contraste de Minería favorece al censo (268 mil frente a 156 mil de ENE; estudios sectoriales van de 200 a 286 mil), aunque no lo confirma.
- **CASEN es la única fuente que une carrera y actividad, y solo a nivel nacional:** ENE, ENADEL y el censo no traen carrera. El puente con el censo sería una estimación, y queda fuera del mapa.
- **ENADEL retirado:** sus vacantes solo son fiables en 26 de 280 combinaciones. Ninguna fuente mide demanda por carrera.
- **Sede fuera del análisis:** la región de Titulados es la sede, no el trabajo.
- **Región según lo que representa:** Censo y ENE permiten región de trabajo; CASEN solo residencia. Por eso el vínculo con carreras es nacional.

**Criterios (de trabajo, no estándares externos)**
- **Filtro de fiabilidad en encuestas:** n ≥ 60, gl ≥ 9 y CV ≤ 30 (poco fiable sobre 15), con linealización de Taylor y todo el diseño muestral.
- **Lectura del censo:** `concentra` desde 1,2 veces y `bajo_lo_nacional` hasta 0,8; `base_pequena` bajo 60 personas. Sin error de muestreo no sirve la regla del rango.
- **Afinidad:** al menos 10% de los ocupados de la carrera en la actividad y el doble de lo normal. Con muestra insuficiente y 10 casos o más es `indicio_sin_muestra`; con menos, `indicio_debil`, que no se muestra.
- **Quien trabaja en varias comunas queda sin región,** igual que la matriz del INE. Afecta a Transporte, Construcción y Electricidad, y el mapa lo avisa.
- **MiFuturo:** los ingresos de cada año vienen de cohortes distintas, así que no se presentan como evolución. La empleabilidad mide ingresos sobre el sueldo mínimo. Con 1 o 2 instituciones hay alerta (56 carreras).

**Datos y técnica**
- **Censo agregado en CSV:** 15,2 millones de personas pasan a 14.793 filas, sin perder totales, porque no usa factores de expansión. El parquet original queda en `Entrada/`.
- **Cartografía en script propio:** `CENSO/obtener_cartografia.py` va separado de `obtener.py`, porque quien solo regenera el mapa no necesita los microdatos de personas. Baja el zip completo (795 MB) en vez de pedir por rangos solo la capa (89 MB): gasta más datos, pero requiere menos código para un paso poco frecuente.
- **Mapa autónomo:** una sola página HTML, sin servidor ni dependencias, con bordes oficiales simplificados por cobertura. Rapa Nui y Juan Fernández no se dibujan.
- **Escala de color fija:** rojo más que el país, azul menos, gris similar; se compara entre actividades.
- **Color y lectura con el CL de 2 decimales que se muestra (06-11-26):** la tabla del Censo y el mapa redondean con la misma función de Python, así el color nunca contradice la cifra (La Araucanía en Agricultura, 1,5976, se lee 1,60 y va en el tramo de 1,6). Se descartó mostrar más decimales, una precisión que el dato no tiene: los ocupados sin región de trabajo mueven el CL más que eso. Cambiaron 6 de 336 tramos de color y 4 lecturas. Un control detiene la generación si color y lectura se contradicen.
- **Lenguaje técnico con valores absolutos:** términos estándar (CL, ocupados, tasas), con glosario al pie y formato `valor (n%)`. Se descartó "peso" y explicar cada cifra en frases, porque generaba más texto y ocultaba los valores que originan el CL.
- **Sexo en tabla aparte; género sin abrir:** `censo_por_sexo.csv` no altera la tabla validada. `div_genero` es sensible y está suprimido para 633.803 ocupados, así que solo aparece como nota nacional. Se descartó una tercera columna por actividad, porque no sería confiable.
- **Cabecera con el nombre del proyecto y hallazgos aparte:** el título dice qué es la página, y los hallazgos van en indicadores y en el título del mapa, junto a su evidencia. Se descartó el título con el hallazgo, por pedido del usuario. Se usa "13 de 16 regiones" en vez de "13 de las otras 15", que confundía. Se descartó "cada región tiene su propia especialización", porque 16 regiones comparten 6 actividades. Esas afirmaciones están escritas a mano, y varios controles detienen la generación si los datos dejan de respaldarlas.
- **Nivel de estudios por actividad, sin tasas:** el Censo registra la actividad solo de quienes trabajan, así que la desocupación por actividad no existe y no se estima. Lo que no cambia con la actividad queda plegado en la región, para que no parezca propio de ella.
- **Selector fijo a la izquierda:** no se mueve entre vistas, y va alineado con el título y el mapa. Se descartó dejarlo a la derecha por preferencia estética del usuario, y cambiarlo de lado entre vistas porque saltaba después del primer clic.
- **Mapa de 149 × 760 px como mínimo:** Chile mide unas 5 veces su ancho, así que no cabe entero en una pantalla baja sin volverse difícil de leer. Se descartó el ajuste total a la ventana (97 px de ancho).
- **Público y cierre:** el mapa responde a quien quiere conocer la situación laboral y educacional de Chile. El bloque "Estudios y trabajo" reemplaza un cierre orientado a una decisión de negocio, que habría que inventar. Las tablas centrales no se pliegan, porque este público viene a consultarlas; solo se pliega el contexto general, como "Población y fuerza de trabajo".
- **Mostrar solo lo necesario (06-11-26):** un dato entra si responde la pregunta del proyecto. Por eso salieron los ocupados esperados, la región con más ocupados por actividad (Metropolitana en 18 de 20) y "titulados que no trabajan", que medía lo mismo que la empleabilidad con otra fuente y edad. Se descartaron los percentiles de ingreso y una tabla de educación por región, que duplicaba "Estudios y trabajo". Cada tema va en una sola sección.
- **% con título en la tabla de Actividades:** muestra en la vista general la relación actividad-educación, el aporte del proyecto. Se calcula desde personas, por lugar de trabajo, y la nota explica por qué da 39,6% y no 39,8%.
- **Vista en la dirección de la página:** `#actividad/región/carrera` hace funcionar el botón "atrás", sobre todo en celular, y permite enlazar una vista. Al cargar o al volver se reemplaza la entrada del historial, para no repetir pasos. La página baja al resultado solo si quedó fuera de la vista, en vez de usar un ancho fijo, porque entre 900 y 1290 px el detalle también queda bajo el mapa.
- **Sin íconos de información:** las notas van visibles junto a su tabla. Un ícono con texto emergente no funciona en pantallas táctiles y escondería justo las aclaraciones que evitan errores de lectura.
- **Sin barra en las tarjetas de regiones (06-11-26):** la barra gris del total de ocupados no tenía rótulo y no decía nada en la tarjeta. El total queda en el texto emergente, en "Situación laboral por región" y en el hallazgo del 42,1%.
- **Títulos por sexo en la tabla de carreras:** usan el mismo filtro de pregrado terminal que el total, y evitan leer un archivo que no está en el repositorio. Por carrera solo van hombres y mujeres.
- **CASEN no se abre por sexo y CL tampoco:** la mayoría de las relaciones carrera-actividad no alcanzaría el mínimo de casos, y el CL por sexo suma una lectura más difícil a una tabla pensada para aclarar el cálculo.
- **Resumen como vista inicial:** da el panorama antes del detalle, con la población de 15 años o más, las 20 actividades y lo que distingue a cada región. Se descartó un bloque fijo sobre el mapa, porque alargaba todas las vistas.
- **Quienes no trabajan, solo por Chile y región:** el Censo pregunta la actividad solo a quienes trabajan, así que abrirlo por actividad sería inventar la cifra. Se usa 15 años o más con aviso; se descartó por ahora un rango de 25 a 59 años, que exigía ampliar la tabla del Censo.
- **Colores del resumen elegidos por vecindad:** 6 colores sin rojo ni azul, que ya significan más y menos que Chile. No pasan el validador comparados todos entre sí, pero sí entre actividades de regiones vecinas (ΔE 8,4 o más con daltonismo). Bajo 1,6 veces van más suaves.
- **Población total como constante:** `censo_procesado.csv` solo trae 15 años o más, y regenerar el mapa no debe exigir los microdatos. Un control la compara con el parquet si está disponible.
- **Modo oscuro y claro:** la página sigue el modo del sistema, así que ambos se revisan. Las notas usan el gris más contrastado, porque llevan advertencias.
- **Desocupados por nivel y región, no por actividad ni carrera:** un desocupado no tiene actividad registrada. "Titulados que no trabajan" (22 a 54 años) sigue en la tabla de carreras, pero salió de la ficha el 06-11-26.
- **Git:** quedan fuera los datos crudos y los microdatos, que se regeneran. Los scripts no llevan fecha en su cabecera, porque git ya la registra.
- **Matriz P6 retirada:** ninguna tabla la leía, porque P9 mide el perfil por su cuenta. P6 queda como `P6_control_no_asignados`, con el control de sesgo y las funciones de error y fiabilidad que usa P9. Se descartó conservarla, porque contradecía el criterio de dejar solo lo que produce el mapa.
- **Etiqueta en vez de carpeta de archivo:** lo retirado salió del proyecto para que solo se vea lo que produce el mapa, y se recupera con la etiqueta de git `indice-cupos`. Se descartó mantener `Archivo/` a la vista porque obligaba a conservar P2, P4, P7, P8 y ENADEL sin uso. Tras borrar, la cadena se regeneró completa y `index.html` salió idéntico.
- **Actividad U fuera de la lista:** se conserva en la tabla, porque con unas 2.800 personas distorsionaba la lectura de la Metropolitana.
- **Nombres según glosarios:** `categoria_ocupacion` y `actividad_*`. `Scrapers/` conserva los nombres de cada fuente; `Analisis/` usa los normalizados.
- **Región = `codigo_region` + `nombre_region`:** fuente única en `comun/normalizador.py`; los cruces se hacen por código.
- **Módulos por tabla:** cada una con `obtener.py`, `esquema.py` y `crosswalk.py` o `procesar.py`, más `Salida/` auditada con `inspect_data.py`.
- **`Titulo que compite`:** Técnico de Nivel Superior y Profesional con o sin licenciatura; postítulo y posgrado no cuentan como títulos 2025.
- **ENE:** 8 trimestres solapados pasan a 324.054 entrevistas con el peso del mes central; reproduce el boletín INE (ver anexo).
- **FF.AA. en `asalariado_publico`:** son funcionarios públicos; CASEN y ENE difieren 0,8% al incluirlas.
- **Fuentes sin datos de terceros en los cálculos:** las cifras sectoriales de Minería solo sirven de contraste.

---

## 🔜 Próximo paso inmediato

Elegir la licencia y repetir la prueba en clon limpio antes de publicar, y decidir si se sube a GitHub.

---

## 📎 Anexo — Validación contra el dato oficial (Boletín INE n°336, JAS 2026)

Prueba de exactitud de `Salida/ene_procesado.csv` contra el boletín oficial del INE
(Edición n°336, 29-10-2026, trimestre móvil julio–septiembre 2026; recetas §7 del libro de
códigos: `cae_especifico` 1-7 ocupados, 8-9 desocupados, 1-9 fuerza de trabajo).

| Indicador | INE oficial | Nuestra salida | desv. |
|---|---:|---:|---:|
| Fuerza de trabajo | 10.282.718 | 10.282.930 | +0.00% |
| Ocupadas | 9.274.742 | 9.275.130 | +0.00% |
| Desocupadas | 1.007.976 | 1.007.799 | −0.02% |
| Ocupadas informales | 2.451.443 | 2.452.190 | +0.03% |
| Tasa de desocupación | 9,8% | 9,80% | exacta |

> **Interpretación:** la deduplicación (782,303 → 324,054 entrevistas), la política de peso
> "central" y la limpieza de sentinelas reproducen la estadística oficial con desviación
> ≤0.08%. Este chequeo queda embebido como **validación 9** en `src/Scrapers/ENE/procesar.py`
> (constantes `INE_JAS_2026` / `MESES_JAS_2026`), por lo que el pipeline falla si se rompe.
