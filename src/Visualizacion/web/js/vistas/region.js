/*
<src/Visualizacion/web/js/vistas/region.js>

Vista de una actividad en una región, con la situación laboral y por nivel de toda la región.
*/
// Ocupados, desocupados y tasa van según residencia: los desocupados no tienen lugar de trabajo, y con ocupados
// por lugar de trabajo la cuenta desocupados / (ocupados + desocupados) no reproducía la tasa.
function tablaNivelSexo(x){
 return `<h3>Por sexo</h3>`+
  `<div class="tabla-ancha"><table class="tabla-compacta" style="margin-top:6px"><thead><tr><th rowspan="2">Nivel</th><th colspan="2" class="bloque ini">Ocupados</th>`+
  `<th colspan="2" class="bloque ini">Desocupados</th><th colspan="2" class="bloque ini">Tasa de desocupación</th></tr>`+
  `<tr>${"<th class=\"n ini\">Hombres</th><th class=\"n\">Mujeres</th>".repeat(3)}</tr></thead><tbody>`+
  NIVELES.map(([k,t])=>{const s=x(k);
   return `<tr><td>${t}</td><td class="n ini">${num(s.oh)}</td><td class="n">${num(s.om)}</td><td class="n ini">${num(s.dh)}</td><td class="n">${num(s.dm)}</td>`+
    `<td class="n ini">${num(s.th,1)}%</td><td class="n">${num(s.tm,1)}%</td></tr>`}).join("")+`</tbody></table></div>`}
// Desocupación por nivel en la región. Chile va como número y no como línea: con una línea distinta en cada fila y su
// valor solo en el globo, el lector no sabía qué marcaba. Un color por nivel, los mismos del gráfico de nivel de estudios
// de arriba: con el verde de "con título" del resumen, técnico salía verde aquí y oliva arriba.
// La diferencia se calcula con las tasas ya redondeadas, para que la resta del lector coincida con la columna.
const DIF_CASI_IGUAL=0.5;
const difNivel=x=>Math.round((x.tasa-x.nacional)*10)/10;
// Lectura de la región: el Censo no tiene error muestral, así que toda diferencia es real; bajo 0,5 pp se lee "casi igual"
// para no destacar diferencias mínimas (Valparaíso técnico y sin título: 0,0 pp).
function lecturaDesocNivel(reg){const g={menor:[],mayor:[],igual:[]},quien={Profesional:"profesionales",Tecnico:"técnicos",Sin_titulo:"quienes no tienen título superior"};
 NIVELES.forEach(([k])=>{const d=difNivel(DATOS.niveles[reg][k]);g[Math.abs(d)<DIF_CASI_IGUAL?"igual":d<0?"menor":"mayor"].push(quien[k])});
 const lista=a=>a.length>1?a.slice(0,-1).join(", ")+" y "+a.at(-1):a[0],usadas=[["menor","menor"],["mayor","mayor"],["igual","casi igual"]].filter(([k])=>g[k].length);
 // Solo la primera parte dice "que en Chile"; repetido en cada parte, la frase se alargaba sin agregar nada.
 const partes=usadas.map(([k,e],i)=>`${e}${i?"":" que en Chile"} ${g[k].length===3?"en los 3 niveles":"entre "+lista(g[k])}`);
 const t=NIVELES.map(([k])=>DATOS.niveles[reg][k].tasa),baja=t[0]<t[1]&&t[1]<t[2];
 return {frase:`La desocupación es ${partes.length>1?partes.slice(0,-1).join(", ")+", y "+partes.at(-1):partes[0]}.`+(baja?" Con más estudios, la tasa es más baja.":""),g,baja}}
function graficoDesocNivel(reg){const filas=NIVELES.map(([k,t],i)=>[t,DATOS.niveles[reg][k],["ed-pro","ed-tec","tsin"][i]]);
 const tope=Math.ceil(Math.max(...filas.map(([,x])=>x.tasa))/4)*4,pos=v=>100*v/tope;
 const signo=d=>d>0?`+${num(d,1)}`:d<0?`−${num(-d,1)}`:num(0,1);
 return `<figure class="graf-cl" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><strong style="color:var(--t1)">Tasa de desocupación · ${nomReg(reg)} y Chile</strong></span></figcaption>`+
  `<div class="cl-fila dn-fila gs-cab" aria-hidden="true"><span class="cl-nombre">Nivel</span><span>${nomReg(reg)}</span>`+
  `<span class="gs-extra"><span class="gs-num">Chile</span><span class="gs-num">Diferencia</span></span></div>`+
  filas.map(([t,x,c])=>{const d=difNivel(x),partes=[`${nomReg(reg)}: ${num(x.tasa,1)}%`,`Chile: ${num(x.nacional,1)}%`,`diferencia: ${signo(d)} pp`,`${num(x.desocupados)} desocupados y ${num(x.ocupados)} ocupados`];
   return `<div class="cl-fila dn-fila" role="img" tabindex="0" data-tip="${`<strong>${t}</strong><br>${partes.join("<br>")}`.replace(/"/g,"&quot;")}" aria-label="${t}: ${partes.join(", ")}">`+
    `<span class="cl-nombre">${t}</span><span class="cl-barra" aria-hidden="true"><i class="${c}" style="width:${pos(x.tasa)}%"></i>`+
    `<span class="cl-valor" style="left:calc(${pos(x.tasa)}% + 6px)">${num(x.tasa,1)}%</span></span>`+
    `<span class="gs-extra"><span class="gs-num"><span class="gs-et">Chile </span>${num(x.nacional,1)}%</span><span class="gs-num"><span class="gs-et">Diferencia </span>${signo(d)} pp</span></span></div>`}).join("")+`</figure>`}
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
 h+=`<hr class="separador">${perfilEstudios(d.niveles,`${nomReg(reg)} · ${act.corto}`,nomReg(reg),`${act.corto} en Chile`,act.niveles.map(f=>f[1]))}`;
 h+=`<hr class="separador">`;
 h+=`<h2>Desocupación por nivel de estudios</h2><div class="nota">${nomReg(reg)}, todas las actividades: no cambia según la actividad elegida. Personas que viven en la región; arriba, los ocupados se cuentan donde trabajan. Tasa = desocupados / (ocupados + desocupados).</div><p class="lectura" style="margin:8px 0 0">${lecturaDesocNivel(reg).frase}</p>${graficoDesocNivel(reg)}
 <details><summary>Ver cifras</summary><p class="nota" style="margin:6px 0 0">Tasa en ENE: ${PER.ene_contraste}, los meses del Censo.</p>
 <table style="margin-top:8px"><thead><tr><th>Nivel</th><th class="n">Ocupados</th><th class="n">Desocupados</th><th class="n">Tasa de desocupación</th>`+
  `<th class="n">Tasa en Chile</th><th class="n">Tasa en ENE</th></tr></thead><tbody>`+
  NIVELES.map(([k,t])=>{const x=DATOS.niveles[reg][k];
   return `<tr><td>${t}</td><td class="n">${num(x.ocupados)}</td><td class="n">${num(x.desocupados)}</td><td class="n">${num(x.tasa,1)}%</td><td class="n">${num(x.nacional,1)}%</td>`+
    `<td class="n" ${x.ene==null?'title="ENE sin muestra suficiente"':""}>${x.ene==null?"sin muestra":num(x.ene,1)+"%"+(x.ene_poco?" *":"")}</td></tr>`}).join("")+
  `</tbody></table>${NIVELES.some(([k])=>DATOS.niveles[reg][k].ene_poco)?'<p class="nota" style="margin:6px 0 0">* ENE poco fiable.</p>':""}`+
  tablaNivelSexo(k=>DATOS.niveles[reg][k].sexo)+"</details>";
 h+=`<details style="margin-top:14px"><summary>Toda la región, situación laboral, según residencia</summary><div class="nota" style="margin-top:6px">`+
  `${nomReg(reg)}, todas las actividades: no cambia según la actividad elegida. Población de 15 años o más, según región de residencia. `+
  `Entre paréntesis, % de la población de 15 años o más de cada columna.</div>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th>Grupo</th><th class="n">Total</th><th class="n">Hombres</th><th class="n">Mujeres</th></tr></thead><tbody>`+
  `<tr class="total"><td>Población de 15 años o más</td><td class="n">${num(pr.total)}</td><td class="n">${num(pr.sexo.hombres.total)}</td><td class="n">${num(pr.sexo.mujeres.total)}</td></tr>`+
  `${filasSituacion(pr,pr.sexo.hombres,pr.sexo.mujeres,false)}</tbody></table></div></details>`;
 return h}
