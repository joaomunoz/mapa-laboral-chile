/*
<src/Visualizacion/web/js/main.js>

Arranque: llena el selector, dibuja el mapa, conecta los eventos y abre la primera vista. Va al final.
*/
const sel=document.getElementById("actividad");
// Nombres cortos, como en las tablas: con el nombre oficial, 8 de 20 opciones empezaban con "Actividades".
[...DATOS.actividades].sort((a,b)=>a.corto.localeCompare(b.corto,"es")).forEach(a=>{const o=document.createElement("option");o.value=a.ciiu;o.textContent=a.corto;o.title=a.glosa;sel.append(o)});
{const o=document.createElement("option");o.value="";o.textContent="Todas las actividades";sel.prepend(o)}
sel.value="";
sel.onchange=()=>{act=sel.value?porCiiu(sel.value):null;if(!act)reg=null;ficha=null;pintar();if(act)mostrarDetalle()};
const tip=document.getElementById("tip");
const svg=`<svg viewBox="-4 -4 ${GEO.ancho+8} ${GEO.alto+8}" role="group" aria-label="Mapa de Chile por región">`+
 DATOS.orden.map(r=>`<path class="region" data-r="${r}" d="${GEO.trazados[r]}" tabindex="0" role="button" fill-rule="evenodd"></path>`).join("")+
 '<path class="contorno" id="contorno" aria-hidden="true"></path><g id="anotaciones" aria-hidden="true"></g></svg>';
document.getElementById("mapa").innerHTML=svg;
document.querySelectorAll(".region").forEach(p=>{const r=Number(p.dataset.r);
 p.onclick=()=>{if(!act){act=porCiiu(RES.regiones[r].ciiu);sel.value=act.ciiu}reg=r;ficha=null;pintar();mostrarDetalle()};p.onkeydown=e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();p.onclick()}};
 p.onmousemove=e=>{
  if(act){const d=act.regiones[r];tip.innerHTML=`<strong>${nomReg(r)}</strong><br>${vp(d.ocupados,d.pct)} · Chile ${vp(act.nacional.ocupados,act.pct_nacional)}<br>CL ${d.peso_txt}`}
  else{const d=RES.regiones[r],a=porCiiu(d.ciiu);tip.innerHTML=`<strong>${nomReg(r)}</strong><br>Mayor CL: ${esc(a.corto)} (${d.txt})<br>Más ocupados: ${esc(porCiiu(d.mas_personas).corto)}`}
  tip.style.display="block";tip.style.left=Math.min(e.clientX+14,innerWidth-250)+"px";tip.style.top=e.clientY+14+"px"};
 p.onmouseleave=()=>{tip.style.display="none"}});
addEventListener("popstate",()=>{reemplazar=true;leerVista();pintar();if(ficha)document.getElementById("ficha")?.scrollIntoView({block:"nearest"});else if(act)mostrarDetalle();else scrollTo(0,0)});
leerVista();
pintar();
addEventListener("resize",()=>{if(!act)anotarMapa(NOTAS_MAPA)});
