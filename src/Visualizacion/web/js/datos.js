/*
<src/Visualizacion/web/js/datos.js>

Datos que inserta generar_mapa.py y el estado de la vista (actividad, región y ficha elegidas).
*/
const DATOS=__DATOS__;const GEO=__GEO__;
const NIVELES=[["Profesional","Profesional"],["Tecnico","Técnico"],["Sin_titulo","Sin título superior"]];
const LECT={concentra:"sobre Chile (CL de 1,2 o más)",similar:"similar a Chile (CL entre 0,8 y 1,2)",bajo_lo_nacional:"bajo Chile (CL de 0,8 o menos)",base_pequena:"base pequeña (menos de 60 ocupados)",sin_muestra:"sin muestra suficiente"};
const CHILE=0;
const RES=DATOS.resumen,POB=DATOS.poblacion,EST=DATOS.estudios,EDU=EST.educacion,EVO=DATOS.evolucion,PER=DATOS.periodos;
const porCiiu=c=>DATOS.actividades.find(a=>a.ciiu===c);
const BASE=DATOS.base_ocupados;
let act=null,reg=null,ficha=null; // act null es el resumen de todas las actividades; reg null es la vista de Chile.
