/*
<src/Visualizacion/web/js/vistas/actividad.js>

Vista de una actividad en Chile, con su perfil de estudios y avisos.
*/
// Perfil de cada actividad. Sin tasas: el Censo registra la actividad solo de quienes trabajan.
function perfilEstudios(filas,lugar,rotulo,comparacion){
 const hayChicas=filas.some(f=>f[2]!=null&&f[2]<CHICA||f[3]!=null&&f[3]<CHICA);
 return `<h2>Nivel de estudios de los ocupados</h2><div class="nota">${esc(lugar)}. Según lugar de trabajo, con nivel informado. Entre paréntesis, % de cada columna. El Censo registra la actividad solo de quienes trabajan: no hay desocupación por actividad.</div>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th>Nivel</th><th class="n">Ocupados</th><th class="n">Hombres</th><th class="n">Mujeres</th><th class="n">${esc(rotulo)}</th></tr></thead><tbody>${
  NIVELES.map(([,t],i)=>{const f=filas[i];
   return `<tr><td>${t}</td><td class="n">${num(f[0])} (${num(f[1],1)}%)</td><td class="n">${celdaNivel(f[2],f[4])}</td>`+
    `<td class="n">${celdaNivel(f[3],f[5])}</td><td class="n">${num(comparacion[i],1)}%</td></tr>`}).join("")
 }</tbody></table></div>${hayChicas?NOTA_CHICA:""}`}
function avisos(){let h="";
 if(act.alerta_fuente)h+=`<div class="aviso">Censo y ENE difieren en el tamaño de esta actividad: usa los ocupados solo como referencia.</div>`;
 if(act.pct_sin_region>=10)h+=`<div class="aviso">${num(act.pct_sin_region,1)}% de los ocupados de esta actividad no tiene región de trabajo: esta cifra está subestimada.</div>`;
 return h}
// Una línea de la ENE, aparte de las cifras del Censo; solo si la muestra la sostiene.
function informalidadActividad(){const f=FOR.actividades[act.ciiu];if(!f)return "";
 return `<p class="nota" style="margin:8px 0 0">Según la ENE de ${PER.ene_actual}, ${enMiles(f.inf[0])} de sus ocupados son informales (${num(f.inf[1],1)}%) y ${enMiles(f.for[0])} formales (${num(f.for[1],1)}%); `+
  `en Chile, ${num(FOR.chile.inf[1],1)}% y ${num(FOR.chile.for[1],1)}%.${f.ind==null?"":` ${enMiles(f.ind[0])} son independientes (${num(f.ind[1],1)}%).`}</p>`}
function vistaChile(){const n=act.nacional;
 return `<h2>Chile · ${esc(act.corto)}</h2><div class="nota">${act.glosa!==act.corto?`Nombre oficial: ${esc(act.glosa)}. `:""}Censo 2024.</div>
 <div class="datos"><div class="dato"><b>${vp(n.ocupados,act.pct_nacional)}</b><span>ocupados (participación), según lugar de trabajo</span></div>
 <div class="dato"><b>${n.conc}</b><span>${n.conc===1?"región con CL de 1,2 o más":"regiones con CL de 1,2 o más"}</span></div>`+
  // Las cantidades por sexo viven aquí: el gráfico del resumen las muestra solo al pasar el mouse.
  `<div class="dato"><b>${num(act.sexo.m)} (${num(act.sexo.pct_m,1)}%)</b><span>mujeres</span></div>`+
  `<div class="dato"><b>${num(act.sexo.h)} (${num(act.sexo.pct_h,1)}%)</b><span>hombres</span></div></div>
 ${informalidadActividad()}${avisos()}<details><summary>Contraste con ENE</summary><p class="nota" style="margin:6px 0 0">Censo, incluidos ocupados sin región de trabajo: ${num(n.censo_total)}. ENE de ${PER.ene_contraste}, los meses del Censo: ${num(n.ene_ocupados)} (participación ${part(n.ene_pct)}).</p></details>
 <hr class="separador">${perfilEstudios(act.niveles,`Chile · ${act.corto}`,"Todas las actividades",DATOS.perfil_estudios.todas)}`}
