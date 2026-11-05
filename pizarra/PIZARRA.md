(PIZARRA.md Actualizada el 04-11-26)

# 🧙 PIZARRA — Mapa Laboral de Chile

> Tablero vivo del proyecto. Bitácora ejecutiva para entender rápidamente el estado actual y los siguientes pasos.

**Contexto activo:** rama `main`, solo local, sin repositorio remoto. `.venv/` para leer parquet y generar el mapa. Carpeta renombrada a `Mapa_Laboral_Chile`. En claude-mem, el historial previo sigue bajo el proyecto `Proyecto Probabilidad_carreras`.

---

## 🎯 Visión

Proyecto de portafolio: un **mapa interactivo de Chile** que muestra dónde se concentra cada actividad económica y qué carreras están más ligadas a ella.

**Flujo:** partes en el resumen de la población y las 20 actividades → eliges una actividad → ves el resumen de Chile y el mapa coloreado según cuánto pesa en cada región → haces clic en una región y ves sus estadísticas → ves las carreras afines a nivel nacional → abres la ficha de una carrera.

**Cambio de alcance (02 y 03-11-26):** se retiró el Índice de Cupos. Carrera × región no es medible: de 3.040 combinaciones, solo 62 pasan el filtro en ocupados y 0 en desocupados. El proyecto muestra solo lo medido, y cada dato conserva su fuente.

| Capa | Pregunta | Fuente | Alcance |
|---|---|---|---|
| **Concentración** | ¿Qué actividad pesa más en cada región? | Censo 2024; ENE como contraste | Regional, donde está el trabajo |
| **Formación** | ¿De qué áreas vienen sus titulados? | CASEN 2024 | Nacional |
| **Carreras afines** | ¿Qué carreras dependen más de esa actividad? | CASEN 2024 | Nacional |
| **Situación por nivel** | ¿Cuántos técnicos y profesionales trabajan o están desocupados? | Censo 2024; ENE como contraste | Regional y nacional |
| **Ficha de carrera** | Títulos, empleabilidad, ingresos y titulados que no trabajan | SIES, MiFuturo y CASEN | Nacional |

---

## 📊 Avance general estimado: ~98%

> Sube desde ~97%: el detalle de región muestra su cálculo, el sexo llega a regiones, niveles y carreras, y la vista inicial se reordenó para lectura ejecutiva. Falta cerrar la narrativa y probar con mouse y teclado.

| Área | Avance | Estado | Notas |
|---|---|---|---|
| Fuentes y scrapers | 100% | 🟢 | 5 fuentes: Censo, ENE, CASEN, SIES y MiFuturo |
| Procesamiento `procesar.py` | 95% | 🟢 | Pendiente menor en MiFuturo, que no afecta al mapa |
| Puentes `src/Analisis/` | 100% | 🟢 | P1, P5 y P9 alimentan el mapa; P6 es control de sesgo |
| Tablas del mapa | 100% | 🟢 | Censo, áreas, carreras y situación por nivel; ENE como contraste |
| Revisión de MiFuturo | 90% | 🟢 | Años de ingreso confirmados; rótulo de percentiles sin confirmar, y el mapa no los usa |
| Mapa interactivo | 97% | 🟡 | Prioridades 1 a 4 de la auditoría aplicadas; faltan la 5 y la 6, y probar esta versión con mouse y teclado reales |
| Nota de lectura | 100% | 🟢 | `Salida/nota_de_lectura.md` |
| Saneamiento | 100% | 🟢 | Lo retirado salió del proyecto; queda en la etiqueta `indice-cupos` |
| Git | 90% | 🟡 | Historial local; falta decidir si se sube a GitHub |
| README y presentación | 75% | 🟡 | README con captura; falta enlace para ver el mapa y licencia |

---

## 🔶 En curso / parcial

- **Auditoría narrativa:** prioridades 1 a 4 aplicadas. Quedan la 5 (actividad con más ocupados por región) y la 6 (tablas plegadas y cierre con carreras afines); el cierre exige definir quién es el ejecutivo y qué decide.
- **Evaluación anterior, prioridad media:** siguen sin aplicar leyenda con tonos suaves, peso del negro en la barra, "Sin dato", Metropolitana atenuada, frase de cada actividad, nombres unificados, "CL 1,598", nivel de estudios y "Lectura".
- **Dos decisiones del usuario:** mostrar valores o solo porcentajes en los títulos por sexo, porque restando se deduce la categoría no binaria o indefinida; y cómo mostrar ocupados en la tabla regional de nivel por sexo, donde la tasa usa residencia.
- **Revisión del mapa por el usuario:** el 04-11-26 informó que hasta ese momento funcionaba con mouse y teclado, antes del resumen ejecutivo. Esta versión solo se probó con eventos simulados y capturas. Falta mostrársela a alguien que no la conozca.
- **Comparación Censo y ENE:** el patrón regional coincide (correlación 0,95 en las 209 combinaciones fiables en ENE; 0,94 en las 336), pero el tamaño difiere en Minería, Electricidad, Serv. administrativos, Adm. pública, Enseñanza y Salud, y también las tasas de desocupación. La causa no está comprobada; el mapa lo avisa.

---

## ⏳ Pendiente — Roadmap

1. **Terminar la revisión del mapa:** prioridades 5 y 6, espacio vacío bajo 1290 px y lo que el usuario pida.
2. **README:** cambiar el ejemplo de Biobío en Salud, porque la cifra es solo del Censo (1,21; 0,85 en ENE), y alinear "pesa" con el lenguaje de CL.
3. **Fórmula oficial de las tasas:** confirmar si el INE incluye a las personas sin dato (ocupación 54,4% o 54,8%; también afecta a participación).
4. **Tabla Actividades:** decidir si se quita el % de los bloques regionales, porque está al límite de ancho.
5. **Licencia del proyecto.**
6. **Subir a GitHub,** si el usuario lo decide: elegir público o privado, y GitHub Pages para ver el mapa sin descargarlo.
7. **Opcional, selector de cantidad o peso:** en pausa, porque la vista nacional ya muestra ambas lecturas.
8. **Ajustes menores:** `ARAUCANIA` en `regiones_sede`, Programas de Formación Pedagógica fuera de P9.

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
- **Color y cifra se calculan en Python con el valor sin redondear:** si se redondea antes, un 1,2024 cae en el tramo equivocado. Un control detiene la generación si el color y la lectura se contradicen.
- **Lenguaje técnico con valores absolutos:** términos estándar (CL, ocupados, tasas), con glosario al pie y formato `valor (n%)`. Se descartó "peso" y explicar cada cifra en frases, porque generaba más texto y ocultaba los valores que originan el CL.
- **Sexo en tabla aparte; género sin abrir:** `censo_por_sexo.csv` no altera la tabla validada. `div_genero` es sensible y está suprimido para 633.803 ocupados, así que solo aparece como nota nacional. Se descartó una tercera columna por actividad, porque no sería confiable.
- **Título con el hallazgo y frases protegidas:** responde con 4 de cada 10 ocupados y 13 de 15 regiones. Se descartó "cada región tiene su propia especialización", porque 16 regiones comparten 6 actividades. Esas afirmaciones están escritas a mano, y varios controles detienen la generación si los datos dejan de respaldarlas.
- **Selector fijo a la izquierda:** no se mueve entre vistas, y va alineado con el título y el mapa. Se descartó dejarlo a la derecha por preferencia estética del usuario, y cambiarlo de lado entre vistas porque saltaba después del primer clic.
- **Mapa de 149 × 760 px como mínimo:** Chile mide unas 5 veces su ancho, así que no cabe entero en una pantalla baja sin volverse difícil de leer. Se descartó el ajuste total a la ventana (97 px de ancho).
- **Barra gris en las tarjetas:** compensa que la superficie no muestra cuántas personas trabajan en cada región. Los valores quedan en el texto emergente y en el detalle.
- **Títulos por sexo en la tabla de carreras:** usan el mismo filtro de pregrado terminal que el total, y evitan leer un archivo que no está en el repositorio. Por carrera solo van hombres y mujeres.
- **CASEN no se abre por sexo y CL tampoco:** la mayoría de las relaciones carrera-actividad no alcanzaría el mínimo de casos, y el CL por sexo suma una lectura más difícil a una tabla pensada para aclarar el cálculo.
- **Resumen como vista inicial:** da el panorama antes del detalle, con la población de 15 años o más, las 20 actividades y lo que distingue a cada región. Se descartó un bloque fijo sobre el mapa, porque alargaba todas las vistas.
- **Quienes no trabajan, solo por Chile y región:** el Censo pregunta la actividad solo a quienes trabajan, así que abrirlo por actividad sería inventar la cifra. Se usa 15 años o más con aviso; se descartó por ahora un rango de 25 a 59 años, que exigía ampliar la tabla del Censo.
- **Colores del resumen elegidos por vecindad:** 6 colores sin rojo ni azul, que ya significan más y menos que Chile. No pasan el validador comparados todos entre sí, pero sí entre actividades de regiones vecinas (ΔE 8,4 o más con daltonismo). Bajo 1,6 veces van más suaves.
- **Población total como constante:** `censo_procesado.csv` solo trae 15 años o más, y regenerar el mapa no debe exigir los microdatos. Un control la compara con el parquet si está disponible.
- **Modo oscuro y claro:** la página sigue el modo del sistema, así que ambos se revisan. Las notas usan el gris más contrastado, porque llevan advertencias.
- **Desocupados por nivel y región, no por actividad ni carrera:** un desocupado no tiene actividad registrada. "Titulados que no trabajan" se mide de 22 a 54 años, porque con todas las edades pesan los jubilados.
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

Definir quién es el ejecutivo y qué decide con el mapa, para el cierre de la prioridad 6. Probar con mouse y teclado, y corregir el ejemplo de Biobío en el README. Luego, agregar la licencia y decidir si se sube a GitHub.

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
