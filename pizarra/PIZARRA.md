(PIZARRA.md Actualizada el 03-11-26)

# 🧙 PIZARRA — Mapa Laboral de Chile

> Tablero vivo del proyecto. Bitácora ejecutiva para entender rápidamente el estado actual y los siguientes pasos.

**Contexto activo:** rama `main`, solo local, sin repositorio remoto. `.venv/` para leer parquet y generar el mapa. Carpeta renombrada a `Mapa_Laboral_Chile`. En claude-mem, el historial previo sigue bajo el proyecto `Proyecto Probabilidad_carreras`.

---

## 🎯 Visión

Proyecto de portafolio: un **mapa interactivo de Chile** que muestra dónde se concentra cada actividad económica y qué carreras están más ligadas a ella.

**Flujo:** eliges una actividad → ves el resumen de Chile y el mapa coloreado según cuánto la concentra cada región → haces clic en una región y ves sus estadísticas → ves las carreras afines a nivel nacional → abres la ficha de una carrera.

**Cambio de alcance (02 y 03-11-26):** se retiró el Índice de Cupos. Carrera × región no es medible: de 3.040 combinaciones, solo 62 pasan el filtro en ocupados y 0 en desocupados. El proyecto muestra solo lo medido, y cada dato conserva su fuente.

| Capa | Pregunta | Fuente | Alcance |
|---|---|---|---|
| **Concentración** | ¿Qué actividad pesa más en cada región? | Censo 2024; ENE como contraste | Regional, donde está el trabajo |
| **Formación** | ¿De qué áreas vienen sus titulados? | CASEN 2024 | Nacional |
| **Carreras afines** | ¿Qué carreras dependen más de esa actividad? | CASEN 2024 | Nacional |
| **Situación por nivel** | ¿Cuántos técnicos y profesionales trabajan o están desocupados? | Censo 2024; ENE como contraste | Regional y nacional |
| **Ficha de carrera** | Títulos, empleabilidad, ingresos y titulados que no trabajan | SIES, MiFuturo y CASEN | Nacional |

---

## 📊 Avance general estimado: ~94%

> Sube desde ~92%: ya existe el README y el mapa se regenera desde un clon limpio. Falta la presentación visual y decidir la publicación.

| Área | Avance | Estado | Notas |
|---|---|---|---|
| Fuentes y scrapers | 100% | 🟢 | 5 fuentes: Censo, ENE, CASEN, SIES y MiFuturo |
| Procesamiento `procesar.py` | 95% | 🟢 | Pendiente menor en MiFuturo, que no afecta al mapa |
| Puentes `src/Analisis/` | 100% | 🟢 | P1, P5 y P9 alimentan el mapa; P6 es control de sesgo |
| Tablas del mapa | 100% | 🟢 | Censo, áreas, carreras y situación por nivel; ENE como contraste |
| Revisión de MiFuturo | 90% | 🟢 | Años de ingreso confirmados; rótulo de percentiles sin confirmar, y el mapa no los usa |
| Mapa interactivo | 90% | 🟡 | Revisión de código aplicada; falta la revisión del usuario con mouse y teclado reales |
| Nota de lectura | 100% | 🟢 | `Salida/nota_de_lectura.md` |
| Saneamiento | 100% | 🟢 | Lo retirado salió del proyecto; queda en la etiqueta `indice-cupos` |
| Git | 90% | 🟡 | Historial local; falta decidir si se sube a GitHub |
| README y presentación | 60% | 🟡 | README escrito; falta captura, enlace para ver el mapa y licencia |

---

## 🔶 En curso / parcial

- **Revisión del mapa por el usuario:** el usuario ya usa el mapa y reportó observaciones, pero sigue sin probarse de forma completa con mouse y teclado reales. La automatización de navegador falló; se probó con eventos por código y capturas.
- **Comparación Censo y ENE:** el patrón regional coincide (correlación 0,95 en las 209 combinaciones fiables en ENE; 0,94 en las 336), pero el tamaño difiere en Minería, Electricidad, Serv. administrativos, Adm. pública, Enseñanza y Salud, y también las tasas de desocupación. La causa no está comprobada; el mapa lo avisa.

---

## ⏳ Pendiente — Roadmap

1. **Terminar la revisión del mapa** y ajustar lo que el usuario pida.
2. **Presentación para portafolio:** captura del mapa y licencia.
3. **Subir a GitHub,** si el usuario lo decide: elegir público o privado, y GitHub Pages para ver el mapa sin descargarlo.
4. **Opcional, selector de cantidad o peso:** en pausa, porque la vista nacional ya muestra ambas lecturas.
5. **Ajustes menores:** `ARAUCANIA` en `regiones_sede`, Programas de Formación Pedagógica fuera de P9.

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
- **Chile como vista inicial:** muestra juntas la región con más personas y la región donde más pesa, que son lecturas distintas de "concentrar". Por eso el selector quedó en pausa.
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

Que el usuario termine de revisar `src/Visualizacion/Mapa_Actividades/Salida/index.html`. Luego, agregar la captura y la licencia al README, y decidir si se sube a GitHub.

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
