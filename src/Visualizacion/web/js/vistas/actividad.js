/*
<src/Visualizacion/web/js/vistas/actividad.js>

Vista de una actividad en Chile, con su perfil de estudios y avisos.
*/
// Perfil de cada actividad. Sin tasas: el Censo registra la actividad solo de quienes trabajan.
// Gráfico con el mismo formato y colores que "Población con título" del resumen: la barra es profesional más técnico y
// la línea es la comparación, para que el nivel se lea igual en todo el mapa. Hombres y mujeres van en filas propias:
// la diferencia entre ellos (Minería en Antofagasta: 25% y 43% profesionales) se perdía entre las columnas de la tabla.
// Si un sexo tiene un nivel con menos de 10 personas, su suma no se puede mostrar y la fila lo dice en vez de la barra.
function graficoPerfil(filas,corto,rotulo,comparacion){
 const grupos=[[rotulo,comparacion," cl-total",null],[corto,filas.map(f=>f[1]),"",filas.map(f=>f[0])],
  ["Hombres",filas.map(f=>f[4]),"",filas.map(f=>f[2])],["Mujeres",filas.map(f=>f[5]),"",filas.map(f=>f[3])]];
 const con=v=>v[0]+v[1],ref=con(comparacion),validos=grupos.filter(g=>g[1].every(x=>x!=null));
 const tope=Math.ceil(Math.max(...validos.map(g=>con(g[1])))/5)*5,pos=x=>100*x/tope;
 const fila=([t,v,clase,n])=>{
  if(v.some(x=>x==null))return `<div class="cl-fila ed-fila" role="img" tabindex="0" aria-label="${t}: algún nivel tiene menos de 10 personas"><span class="cl-nombre">${t}</span>`+
   `<span class="nota">Algún nivel tiene menos de 10 personas: ver cifras</span><span class="gs-num"></span></div>`;
  const chica=n&&n.reduce((a,b)=>a+b,0)<CHICA?" *":"";
  const partes=[`${num(con(v),1)}% con título técnico o profesional`,...NIVELES.map(([,e],i)=>`${e.toLowerCase()}: ${n?num(n[i])+" ":""}(${num(v[i],1)}%)`)];
  return `<div class="cl-fila ed-fila${clase}" role="img" tabindex="0" data-tip="${`<strong>${t}</strong><br>${partes.join("<br>")}`.replace(/"/g,"&quot;")}" aria-label="${t}: ${partes.join(", ")}">`+
   `<span class="cl-nombre">${t}${chica}</span><span class="cl-barra ed-barra" aria-hidden="true"><i class="ed-pro" style="width:${pos(v[0])}%"></i>`+
   `<i class="ed-tec" style="left:calc(${pos(v[0])}% + 2px);width:calc(${pos(v[1])}% - 2px)"></i><b style="left:${pos(ref)}%"></b>`+
   `<span class="cl-valor" style="left:calc(${pos(con(v))}% + 6px)">${num(con(v),1)}%</span></span><span class="gs-num">${num(v[2],1)}%</span></div>`};
 return `<figure class="graf-cl" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda">`+
  `<span><i class="ed-pro"></i>Profesional</span><span><i class="ed-tec"></i>Técnico</span><span><span class="ref"></span>${esc(rotulo)} (${num(ref,1)}%)</span></figcaption>`+
  `<div class="cl-fila ed-fila gs-cab" aria-hidden="true"><span class="cl-nombre">Grupo</span><span>% con título técnico o profesional</span><span class="gs-num">Sin título superior</span></div>`+
  grupos.map(fila).join("")+`</figure>`}
function perfilEstudios(filas,lugar,corto,rotulo,comparacion,t="h2"){
 const hayChicas=filas.some(f=>f[2]!=null&&f[2]<CHICA||f[3]!=null&&f[3]<CHICA);
 return `<${t}>Nivel de estudios de los ocupados</${t}><div class="nota">Según lugar de trabajo, con nivel informado. El Censo registra la actividad solo de quienes trabajan: no hay desocupación por actividad.</div>`+
  graficoPerfil(filas,corto,rotulo,comparacion)+
  `<p class="nota" style="margin:2px 0 8px">% de los ocupados de cada grupo. Al final de cada barra, profesional y técnico juntos; a la derecha, el resto, sin título superior.</p>`+
  ([2,3].some(k=>filas.every(f=>f[k]!=null)&&filas.reduce((a,f)=>a+f[k],0)<CHICA)?NOTA_CHICA:"")+
  `<details><summary>Ver cifras</summary><div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th>Nivel</th><th class="n">Ocupados</th><th class="n">Hombres</th><th class="n">Mujeres</th><th class="n">${esc(rotulo)}</th></tr></thead><tbody>${
  NIVELES.map(([,t],i)=>{const f=filas[i];
   return `<tr><td>${t}</td><td class="n">${num(f[0])} (${num(f[1],1)}%)</td><td class="n">${celdaNivel(f[2],f[4])}</td>`+
    `<td class="n">${celdaNivel(f[3],f[5])}</td><td class="n">${num(comparacion[i],1)}%</td></tr>`}).join("")
 }</tbody></table></div><p class="nota" style="margin:4px 0 0">${esc(lugar)}. Entre paréntesis, % de cada columna.</p>${hayChicas?NOTA_CHICA:""}</details>`}
function avisos(){let h="";
 if(act.alerta_fuente)h+=`<div class="aviso">Censo y ENE difieren en el tamaño de esta actividad: usa los ocupados solo como referencia.</div>`;
 if(act.pct_sin_region>=10)h+=`<div class="aviso">${num(act.pct_sin_region,1)}% de los ocupados de esta actividad no tiene región de trabajo: esta cifra está subestimada.</div>`;
 return h}
// Una línea de la ENE, aparte de las cifras del Censo; solo si la muestra la sostiene.
// El informal de las actividades muy formales es una cifra chica que no es fiable: se escribe con su etiqueta, como en el resumen.
function informalidadActividad(){const f=FOR.actividades[act.ciiu];if(!f)return "";const e=ETQ_FIAB[f.fiab];
 return `<p class="nota" style="margin:8px 0 0">Según la ENE de ${PER.ene_actual}, ${enMiles(f.inf[0])} de sus ocupados son informales (${num(f.inf[1],1)}%${e?`, ${e}`:""}) y ${enMiles(f.for[0])} formales (${num(f.for[1],1)}%); `+
  `en Chile, ${num(FOR.chile.inf[1],1)}% y ${num(FOR.chile.for[1],1)}%.${f.ind==null?"":` ${enMiles(f.ind[0])} son independientes (${num(f.ind[1],1)}%).`}</p>`}
function vistaChile(){const n=act.nacional;
 return `<h2>Chile · ${esc(act.corto)}</h2><div class="nota">${act.glosa!==act.corto?`Nombre oficial: ${esc(act.glosa)}. `:""}Censo 2024.</div>
 <div class="datos"><div class="dato"><b>${vp(n.ocupados,act.pct_nacional)}</b><span>ocupados (participación), según lugar de trabajo</span></div>
 <div class="dato"><b>${n.conc}</b><span>${n.conc===1?"región con CL de 1,2 o más":"regiones con CL de 1,2 o más"}</span></div>`+
  // Las cantidades por sexo viven aquí: el gráfico del resumen las muestra solo al pasar el mouse.
  `<div class="dato"><b>${num(act.sexo.m)} (${num(act.sexo.pct_m,1)}%)</b><span>mujeres</span></div>`+
  `<div class="dato"><b>${num(act.sexo.h)} (${num(act.sexo.pct_h,1)}%)</b><span>hombres</span></div></div>
 ${informalidadActividad()}${avisos()}<details><summary>Contraste con ENE</summary><p class="nota" style="margin:6px 0 0">Censo, incluidos ocupados sin región de trabajo: ${num(n.censo_total)}. ENE de ${PER.ene_contraste}, los meses del Censo: ${num(n.ene_ocupados)} (participación ${part(n.ene_pct)}).</p></details>
 <hr class="separador">${perfilEstudios(act.niveles,`Chile · ${act.corto}`,act.corto,"Todas las actividades",DATOS.perfil_estudios.todas)}`}
