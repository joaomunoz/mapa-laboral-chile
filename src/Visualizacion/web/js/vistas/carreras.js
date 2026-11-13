/*
<src/Visualizacion/web/js/vistas/carreras.js>

Carreras afines de la actividad y ficha de cada carrera.
*/
// Las carreras van bajo su nivel, junto a los ocupados de ese nivel en el lugar elegido: así se ve a cuánta gente
// se refiere cada lista y que las carreras no describen a quienes no tienen título superior. El Censo no trae la
// carrera, por eso la nota aclara que esos ocupados no son titulados de las carreras listadas. El lugar y la fuente
// van en la misma fila y en la columna: la cifra regional del Censo quedaba junto a la nacional de la CASEN y se leían como una sola.
const NIVEL_GRUPO={Profesional:"Título profesional",Tecnico:"Título técnico",Sin_titulo:"Sin título superior"};
function bloqueCarreras(){
 const lugar=reg==null?"Chile":nomReg(reg),filas=reg==null?act.niveles:act.regiones[reg].niveles;
 // En la región va como subtítulo del detalle, al mismo nivel que "Nivel de estudios"; en Chile sigue siendo una sección.
 const t=reg==null?"h2":"h3";
 let h=`<hr class="separador"><${t}>Carreras afines</${t}><div class="nota">Agrupadas por nivel del título. `+
  `Las carreras son un dato nacional de la CASEN 2024 (${PER.casen})${reg==null?"":` y no indican titulados en ${lugar}`}. Los titulados son personas estimadas por la CASEN, no títulos del SIES. `+
  `Junto a cada nivel, los ocupados de ${esc(act.corto)} en ${lugar} con ese nivel (Censo, lugar de trabajo); no indican de qué carrera son.</div>`;
 if(act.afines.length){
  h+=`<table style="margin-top:8px"><thead><tr><th>Carrera</th><th class="n">De sus titulados que trabajan, % en esta actividad</th>`+
   `<th class="n">Titulados que trabajan en la actividad, en todo Chile (CASEN)</th></tr></thead><tbody>`+NIVELES.map(([k],i)=>{
   const f=filas[i],grupo=`<tr class="grupo"><td colspan="3">${NIVEL_GRUPO[k]} <span class="nota">· en ${lugar}, ${num(f[0])} ocupados de ${esc(act.corto)} con este nivel (${num(f[1],1)}%; Censo)</span></td></tr>`;
   if(k==="Sin_titulo")return grupo+`<tr><td colspan="3" class="nota">Las carreras afines no describen a este grupo.</td></tr>`;
   const cs=act.afines.filter(c=>DATOS.fichas[c.c].nivel===k);
   return grupo+(cs.length?cs.map(c=>
     `<tr><td><button class="enlace" data-c="${esc(c.c)}">${esc(nom(c.c))}</button>${c.fiab==="poco_fiable"?'<span class="etiqueta">poco fiable</span>':""}</td>`+
     `<td class="n" title="Intervalo de 95%: ${num(c.min,1)}% a ${num(c.max,1)}%">${num(c.pct,1)}%</td><td class="n">${num(c.tit)}</td></tr>`).join(""):
    `<tr><td colspan="3" class="nota">Sin carreras afines con dato fiable.</td></tr>`)}).join("")+"</tbody></table>"}
 else h+=`<p class="nota">Sin carreras afines con dato fiable.</p>`;
 if(act.indicios.length){const por=NIVELES.slice(0,2).map(([k,t])=>[t,act.indicios.filter(c=>DATOS.fichas[c.c].nivel===k)]).filter(([,cs])=>cs.length);
  h+=`<details ${act.afines.length?"":"open"}><summary>Posibles vínculos, con muestra insuficiente (${act.indicios.length})</summary>${
   por.map(([t,cs])=>`<p style="margin:6px 0 0"><strong>${t}:</strong> ${cs.map(c=>`<button class="enlace" data-c="${esc(c.c)}">${esc(nom(c.c))}</button>`).join(" &nbsp;·&nbsp; ")}</p>`).join("")
  }</details>`}
 if(act.areas.length)h+=`<h3>Área de estudio de los titulados ocupados</h3><div class="nota">CASEN 2024, dato nacional.</div>${circuloAreas()}`;
 return h}
// Composición por área de los titulados ocupados de la actividad: un circular, idea del usuario, porque responde "de
// qué áreas se compone" y tiene de 2 a 5 partes. Van las áreas con muestra suficiente (hasta 4) y el resto junto en
// "Otras áreas": cada una de esas, sola, no es fiable. El margen de error va escrito en el rótulo, no cabe en la forma.
// Grados del morado de "área" y gris con rayas para "Otras áreas" (ver base.css). Empieza a las 12 en sentido del reloj.
function circuloAreas(){const t=act.areas.reduce((s,a)=>s+a.pct,0),resto=Math.round((100-t)*10)/10,tr=act.tit_casen-act.areas.reduce((s,a)=>s+a.tit,0);
 const partes=[...act.areas.map((a,i)=>({nombre:a.area,pct:a.pct,mas:(a.max-a.min)/2,tit:a.tit,rango:`${num(a.min,1)}% a ${num(a.max,1)}%`,poco:a.fiab==="poco_fiable",fondo:`var(--ar${i+1})`})),
  {nombre:"Otras áreas",pct:resto,tit:tr,otras:true,fondo:"url(#ar-rayas)"}];
  let ang=0;
 const xy=g=>`${(Math.sin(g)).toFixed(4)} ${(-Math.cos(g)).toFixed(4)}`;
 const desc=p=>[`${num(p.pct,1)}% de los titulados ocupados`+(p.otras?"":` (entre ${p.rango})`),`${num(p.tit)} titulados`].concat(p.poco?["poco fiable"]:[]);
 const tajadas=partes.map(p=>{const g=2*Math.PI*p.pct/100,d=`M0 0L${xy(ang)}A1 1 0 ${g>Math.PI?1:0} 1 ${xy(ang+g)}Z`;ang+=g;
  return `<path d="${d}" fill="${p.fondo}" stroke="var(--sup)" stroke-width="2" vector-effect="non-scaling-stroke" tabindex="0" `+
   `data-tip="${`<strong>${esc(p.nombre)}</strong><br>${desc(p).join("<br>")}`.replace(/"/g,"&quot;")}" aria-label="${esc(p.nombre)}: ${desc(p).join(", ")}"></path>`}).join("");
 const rotulo=p=>`<li><i style="background:${p.otras?"var(--area-no)":p.fondo}"${p.otras?' class="ar-rayas"':""}></i><span>${esc(p.nombre)}${p.poco?' <span class="etiqueta">poco fiable</span>':""}</span>`+
  `<b>${num(p.pct,1)}%</b><span class="nota">${p.otras?"":`±${num(p.mas,1)}`}</span></li>`;
 return `<figure class="ar-circulo"><svg viewBox="-1.02 -1.02 2.04 2.04" role="img" aria-label="Área de estudio de los titulados ocupados de ${esc(act.corto)}: ${partes.map(p=>`${p.nombre} ${num(p.pct,1)}%`).join(", ")}">`+
  `<defs><pattern id="ar-rayas" width="0.09" height="0.09" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="0.09" height="0.09" fill="var(--sup)"/><rect width="0.045" height="0.09" fill="var(--area-no)"/></pattern></defs>${tajadas}</svg>`+
  `<ul class="ar-rotulos">${partes.map(rotulo).join("")}</ul></figure>`+
  `<p class="nota" style="margin:2px 0 8px">% de los titulados ocupados de la actividad; ± margen de error (95%). Otras áreas: las que, solas, no tienen muestra suficiente.</p>`+
  `<details><summary>Ver cifras</summary><table style="margin-top:8px"><thead><tr><th>Área</th><th class="n">%</th><th class="n">Rango 95%</th><th class="n">Titulados ocupados</th></tr></thead><tbody>${
   partes.map(p=>`<tr><td>${esc(p.nombre)}${p.poco?'<span class="etiqueta">poco fiable</span>':""}</td><td class="n">${num(p.pct,1)}%</td><td class="n">${p.otras?"":p.rango}</td><td class="n">${num(p.tit)}</td></tr>`).join("")
  }</tbody></table></details>`}
// El promedio esconde cuánto pesa la institución: en 79 de 115 carreras la más alta y la más baja se separan
// 20 puntos o más de empleabilidad. Con 1 o 2 instituciones no hay rango y basta el aviso de pocas instituciones.
const varia=(r,f)=>r?`; varía entre ${f(r[0])} y ${f(r[1])} según institución`:"";
function fichaHtml(c){const f=DATOS.fichas[c];
 return `<div class="fichero" id="ficha"><button class="cerrar" aria-label="Cerrar ficha">✕</button><h2>${esc(f.nombre)}</h2><div class="nota">${esc(f.area)} · ${f.nivel==="Tecnico"?"Técnico":"Profesional"} · dato nacional</div>
 <div class="datos"><div class="dato"><b>${num(f.tit_hist)}</b><span>títulos entre 2007 y 2025**</span></div><div class="dato"><b>${num(f.tit)}</b><span>títulos en 2025: ${num(f.tit_h)} hombres (${num(f.pct_tit_h,1)}%) y ${num(f.tit_m)} mujeres (${num(f.pct_tit_m,1)}%)**</span></div>
 <div class="dato"><b>${num(f.emp,1)}%</b><span>empleabilidad al 1er año*${varia(f.emp_r,v=>num(v,1)+"%")}</span></div>
 <div class="dato"><b>${pesos(f.ing1)}</b><span>ingreso medio al 1er año</span></div><div class="dato"><b>${pesos(f.ing5)}</b><span>ingreso medio al 5° año</span></div>
</div>
 ${f.alerta_inst?`<div class="aviso">Basado en ${f.inst===1?"1 institución":f.inst+" instituciones"}: describe más a ${f.inst===1?"esa institución":"esas instituciones"} que a la carrera.</div>`:""}
 ${f.actividades.length?`<h3>Actividades afines</h3><div>${f.actividades.map(a=>`${esc(a[1])} <span class="nota">${num(a[2],1)}%</span>`).join(" &nbsp;·&nbsp; ")}</div>`:""}
 <p class="nota" style="margin:10px 0 0">*Titulados con ingresos iguales o superiores al sueldo mínimo. `+
  `La empleabilidad es el promedio de ${f.inst===1?"1 institución":f.inst+" instituciones"}, ponderado por sus títulos de 2021-2023${f.emp_r?"; el rango va de la institución más baja a la más alta":""}. `+
  `Los ingresos se publican por tipo de institución (universidad, IP o CFT), no por institución. `+
  `Empleo e ingresos medidos de 2022 a 2024. Ingresos brutos mensuales, en pesos de septiembre de 2025; el 1er y el 5° año son generaciones distintas (2021-2023 y 2017-2019), no una evolución. Fuente: MiFuturo.<br>`+
  `**Titulaciones, no personas: una persona puede tener más de un título. El total 2007-2025 incluye a quienes hoy no trabajan, migraron o se jubilaron. Son años académicos: 2025 va de marzo de 2025 a febrero de 2026. Fuente: SIES. `+
  `El registro incluye ${num(DATOS.titulos_nb)} titulaciones no binarias o indefinidas en las carreras de este mapa, que no se abren por carrera.</p></div>`}
