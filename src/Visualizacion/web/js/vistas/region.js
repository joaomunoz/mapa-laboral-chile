/*
<src/Visualizacion/web/js/vistas/region.js>

Vista de una actividad en una región, con la situación laboral y por nivel de toda la región.
*/
// La tasa siempre usa residencia, aunque los ocupados de la región se muestren por lugar de trabajo.
function tablaNivelSexo(x,rotulo){
 return `<h3>Por sexo</h3><div class="nota">Tasa de desocupación según residencia.</div>`+
  `<div class="tabla-ancha"><table class="tabla-compacta" style="margin-top:6px"><thead><tr><th rowspan="2">Nivel</th><th colspan="2" class="bloque ini">${rotulo}</th>`+
  `<th colspan="2" class="bloque ini">Desocupados</th><th colspan="2" class="bloque ini">Tasa de desocupación</th></tr>`+
  `<tr>${"<th class=\"n ini\">Hombres</th><th class=\"n\">Mujeres</th>".repeat(3)}</tr></thead><tbody>`+
  NIVELES.map(([k,t])=>{const s=x(k);
   return `<tr><td>${t}</td><td class="n ini">${num(s.oh)}</td><td class="n">${num(s.om)}</td><td class="n ini">${num(s.dh)}</td><td class="n">${num(s.dm)}</td>`+
    `<td class="n ini">${num(s.th,1)}%</td><td class="n">${num(s.tm,1)}%</td></tr>`}).join("")+`</tbody></table></div>`}
function filasSituacion(t,h,m,conMuestra){
 const etiqueta=(k,e)=>conMuestra?`<span class="celda-muestra"><i class="muestra ${k}"></i>${e}</span>`:e;
 return [["s-trabajan","Ocupados","trabajan","pct_trabajan"],["s-buscan","Desocupados","buscan","pct_buscan"],
   ["s-no-buscan","Fuera de la fuerza de trabajo","no_buscan","pct_no_buscan"],["s-sin-dato","Sin dato","sin_dato","pct_sin_dato"]]
   .map(([k,e,v,p])=>`<tr><td>${etiqueta(k,e)}</td>${[t,h,m].map(d=>`<td class="n">${num(d[v])} (${num(d[p],1)}%)</td>`).join("")}</tr>`).join("")+
  [["Tasa de desocupación","tasa_desocupacion"],["Tasa de participación","tasa_participacion"]]
   .map(([e,v])=>`<tr><td>${e}</td>${[t,h,m].map(d=>`<td class="n">${num(d[v],1)}%</td>`).join("")}</tr>`).join("")}
function vistaRegion(){
 const d=act.regiones[reg],n=act.nacional,bs=BASE.sexo.regiones[reg],pr=POB.regiones[reg],
  otras=DATOS.actividades.filter(a=>a.ciiu!==act.ciiu&&a.regiones[reg].lectura==="concentra").sort((a,b)=>ordenar(a.regiones[reg],b.regiones[reg]));
 // El título usa el nombre del selector: con el oficial, el usuario no reconocía la actividad que eligió.
 let h=`<h2>${nomReg(reg)} · ${esc(act.corto)}</h2><div class="nota">${act.glosa!==act.corto?`Nombre oficial: ${esc(act.glosa)}. `:""}Censo 2024, según región de trabajo.</div>${RES.regiones[reg].ciiu===act.ciiu?
  `<p class="nota" style="margin:6px 0 0">${esc(act.corto)} es la actividad con mayor CL de ${nomReg(reg)}. Para ver otra, elígela en Actividad, arriba.</p>`:""}
 <div class="tabla-ancha"><table class="tabla-compacta" style="margin-top:10px"><thead><tr><th rowspan="2">Indicador</th><th rowspan="2">Cálculo</th>`+
  `<th colspan="3" class="bloque ini">${nomReg(reg)}</th><th colspan="3" class="bloque ini">Chile</th></tr>`+
  `<tr><th class="n ini">Total</th><th class="n">Hombres</th><th class="n">Mujeres</th><th class="n ini">Total</th><th class="n">Hombres</th><th class="n">Mujeres</th></tr></thead><tbody>
 <tr><td>A. Total de ocupados (lugar de trabajo, con actividad informada; incluye organismos internacionales)</td><td></td><td class="n ini">${num(BASE.regiones[reg])}</td><td class="n">${num(bs.h)}</td>`+
  `<td class="n">${num(bs.m)}</td><td class="n ini">${num(BASE.chile)}</td><td class="n">${num(BASE.sexo.chile.h)}</td><td class="n">${num(BASE.sexo.chile.m)}</td></tr>
 <tr><td>B. Ocupados en la actividad</td><td></td><td class="n ini">${num(d.ocupados)}</td><td class="n">${celdaSexo(d.h)}</td><td class="n">${celdaSexo(d.m)}</td><td class="n ini">${num(n.ocupados)}</td><td class="n">${num(act.sexo.h)}</td><td class="n">${num(act.sexo.m)}</td></tr>
 <tr><td>C. Participación</td><td>B ÷ A</td><td class="n ini">${part(d.pct)}</td><td class="n">${partSexo(d.pct_h)}</td><td class="n">${partSexo(d.pct_m)}</td><td class="n ini">${part(act.pct_nacional)}</td><td class="n">${part(act.sexo.part_h)}</td><td class="n">${part(act.sexo.part_m)}</td></tr>
 <tr class="total"><td>D. CL</td><td>C ÷ C de Chile</td><td class="n ini">${d.peso_txt}</td><td></td><td></td><td class="n ini">1,00</td><td></td><td></td></tr></tbody></table></div>
 ${[d.h,d.m].some(v=>v!=null&&v<CHICA)?NOTA_CHICA:""}
 <p class="nota" style="margin:6px 0 0">Lectura: ${LECT[d.lectura]}.</p>`+avisos()+
  `<details><summary>Contraste con ENE</summary><p class="nota" style="margin:6px 0 0">CL en ENE de ${PER.ene_contraste}: ${d.ene_peso_txt}, ${LECT[d.ene_lectura]??d.ene_lectura}.</p></details>`;
 if(otras.length)h+=`<h3>Otras actividades con CL de 1,2 o más</h3><table><thead><tr><th>Actividad</th><th class="n">Ocupados (participación)</th><th class="n">Chile</th><th class="n">CL</th></tr></thead><tbody>${
  otras.slice(0,5).map(a=>{const v=a.regiones[reg];
   return `<tr><td><button class="enlace" data-a="${a.ciiu}">${esc(a.corto)}</button></td><td class="n">${vp(v.ocupados,v.pct)}</td>`+
    `<td class="n">${vp(a.nacional.ocupados,a.pct_nacional)}</td><td class="n">${v.peso_txt}</td></tr>`}).join("")
 }</tbody></table>`;
 h+=`<hr class="separador">${perfilEstudios(d.niveles,`${nomReg(reg)} · ${act.corto}`,`${act.corto} en Chile`,act.niveles.map(f=>f[1]))}`;
 h+=`<hr class="separador"><details><summary>Toda la región, situación laboral</summary><div class="nota" style="margin-top:6px">`+
  `${nomReg(reg)}, todas las actividades: no cambia según la actividad elegida. Población de 15 años o más, según región de residencia. `+
  `Entre paréntesis, % de la población de 15 años o más de cada columna.</div>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th>Grupo</th><th class="n">Total</th><th class="n">Hombres</th><th class="n">Mujeres</th></tr></thead><tbody>`+
  `<tr class="total"><td>Población de 15 años o más</td><td class="n">${num(pr.total)}</td><td class="n">${num(pr.sexo.hombres.total)}</td><td class="n">${num(pr.sexo.mujeres.total)}</td></tr>`+
  `${filasSituacion(pr,pr.sexo.hombres,pr.sexo.mujeres,false)}</tbody></table></div></details>`;
 h+=`<details style="margin-top:14px"><summary>Toda la región, por nivel de estudios</summary><div class="nota" style="margin-top:6px">${nomReg(reg)}, todas las actividades: no cambia según la actividad elegida. Desocupados según residencia. Tasa en ENE: ${PER.ene_contraste}, los meses del Censo.</div>
 <table style="margin-top:8px"><thead><tr><th>Nivel</th><th class="n">Ocupados (lugar de trabajo)</th><th class="n">Desocupados</th><th class="n">Tasa de desocupación</th>`+
  `<th class="n">Tasa en Chile</th><th class="n">Tasa en ENE</th></tr></thead><tbody>`+
  NIVELES.map(([k,t])=>{const x=DATOS.niveles[reg][k];
   return `<tr><td>${t}</td><td class="n">${num(x.trabajo)}</td><td class="n">${num(x.desocupados)}</td><td class="n">${num(x.tasa,1)}%</td><td class="n">${num(x.nacional,1)}%</td>`+
    `<td class="n" ${x.ene==null?'title="ENE sin muestra suficiente"':""}>${x.ene==null?"sin muestra":num(x.ene,1)+"%"+(x.ene_poco?" *":"")}</td></tr>`}).join("")+
  `</tbody></table>${NIVELES.some(([k])=>DATOS.niveles[reg][k].ene_poco)?'<p class="nota" style="margin:6px 0 0">* ENE poco fiable.</p>':""}`+
  tablaNivelSexo(k=>DATOS.niveles[reg][k].sexo,"Ocupados (lugar de trabajo)")+"</details>";
 return h}
