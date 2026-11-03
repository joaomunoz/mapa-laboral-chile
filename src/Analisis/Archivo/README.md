# Archivo: Índice de Cupos y repartos por carrera y región

Tablas del enfoque anterior del proyecto, retiradas el 03-11-26. Ya no alimentan el mapa. Se conservan para consultar el método y comparar resultados.

## Por qué se retiraron
- **Carrera × región no es medible:** de 3.040 combinaciones, solo 62 pasan el filtro de fiabilidad en ocupados y 0 en desocupados.
- **El reparto dependía de un supuesto débil:** usaba la región de la sede de titulación, y dejaba a Medicina en cero en Aysén y Ñuble.
- **Jubilaciones y vacantes casi repetían el dato de ocupados:** correlación de 0,84 a 0,93 por carrera y región.

## Contenido
| Carpeta | Qué calculaba |
|---|---|
| `Indice_Cupos/` | Índice de Cupos por carrera y región |
| `CW_Ocupados_Carrera_Region_Actividad/` | Reparto de ocupados por carrera, región y actividad |
| `CW_Competencia_Desocupados/` | Reparto de desocupados por carrera y región |
| `CW_Demanda_Jubilacion/` | Cupos por jubilación |
| `CW_Demanda_Empresarial/` | Vacantes privadas estimadas con ENADEL |
| `CW_Demanda_Publica/` | Vacantes públicas estimadas con ENE |
| `CW_Empleabilidad_Oferta_Titulados/` | Cruce de titulados y empleabilidad |

## Cómo volver a ejecutarlas
Las rutas internas funcionan desde esta carpeta. El orden es: `CW_Empleabilidad_Oferta_Titulados`, `CW_Ocupados_Carrera_Region_Actividad`, `CW_Competencia_Desocupados`, `CW_Demanda_Jubilacion`, `CW_Demanda_Empresarial`, `CW_Demanda_Publica` e `Indice_Cupos`.

Para el resultado vigente, ver `src/Visualizacion/Mapa_Actividades/`.
