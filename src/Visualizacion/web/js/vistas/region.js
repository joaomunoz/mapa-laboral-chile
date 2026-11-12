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
// Barra rosa/azul del detalle de región: el mismo componente y colores que "Hombres y mujeres por actividad" del
// resumen, idea del usuario. Cada fila es su propio 100% y la línea es la referencia de cada gráfico. La usan la
// actividad (por lugar de trabajo) y toda la región (por residencia): una sola función para que se lean igual.
// et: rótulo de la cifra cuando el celular oculta la cabecera. filas: [rótulo, mujeres, hombres, texto de la columna, clase]; las de mujeres u hombres nulos (menos de 10) se avisan.
function figuraSexo(titulo,refTexto,ref,cabecera,et,filas){
 const fila=([t,m,hh,extra,clase])=>{
  if(m==null||hh==null)return `<div class="gs-fila gs-region${clase}"><span class="gs-nombre">${esc(t)}</span><span class="nota" style="grid-column:2/5">Menos de 10 personas: ver cifras</span></div>`;
  const n=m+hh,pm=100*m/n,ph=100-pm,partes=[extra,`${num(m)} mujeres (${num(pm,1)}%)`,`${num(hh)} hombres (${num(ph,1)}%)`];
  return `<div class="gs-fila gs-region${clase}" role="img" tabindex="0" data-tip="${`<strong>${esc(t)}</strong><br>${partes.join("<br>")}`.replace(/"/g,"&quot;")}" aria-label="${esc(t)}: ${partes.join(", ")}">`+
   `<span class="gs-nombre">${esc(t)}</span><span class="gs-pct">${num(pm,1)}%</span><span class="gs-barra" aria-hidden="true"><i class="m" style="flex:${pm} 0 0"></i><i class="h" style="flex:${ph} 0 0"></i>`+
   `<b style="left:${ref}%"></b></span><span class="gs-pct h">${num(ph,1)}%</span>`+
   `<span class="gs-extra"><span class="gs-num"><span class="gs-et">${et} </span>${extra}</span></span></div>`};
 return `<figure class="graf-sexo" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><strong style="color:var(--t1)">${titulo}</strong></span>`+
  `<span><i style="background:var(--muj)"></i>Mujeres</span><span><i style="background:var(--hom)"></i>Hombres</span><span><span class="ref"></span>${refTexto} (${num(ref,1)}% mujeres)</span></figcaption>`+
  `<div class="gs-fila gs-region gs-cab" aria-hidden="true"><span class="gs-nombre"></span><span></span><span></span><span></span><span class="gs-extra"><span class="gs-num">${cabecera}</span></span></div>`+
  filas.map(fila).join("")+`</figure>`}
// La actividad: en Chile y en la región, frente a todas las actividades de la región. Las tres cifras cuentan a los
// ocupados donde trabajan, como la tabla del CL: la línea es la fila A. Así se ve si la actividad tiene más o menos
// mujeres que la región en general (Hogares en O'Higgins: 89,0% frente a 42,1%).
function graficoSexoActividad(d,bs){
 return figuraSexo(`% de mujeres y de hombres · ${esc(act.corto)}`,`Todas las actividades de ${nomReg(reg)}`,100*bs.m/(bs.h+bs.m),"Ocupados","Ocupados",[
  [`${act.corto} en Chile`,act.sexo.m,act.sexo.h,num(act.sexo.m+act.sexo.h)," gs-total"],
  [`${act.corto} en ${nomReg(reg)}`,d.m,d.h,num(d.ocupados),""]])}
// Toda la región, por residencia. La línea es el % de mujeres en la población de 15 años o más: se lee de inmediato que
// las mujeres pesan menos entre los ocupados y más entre quienes están fuera. Sin dato (menos de 1%) queda solo en
// "Ver cifras": su reparto por sexo no dice nada. Las tasas no son partes de un todo y van en la frase de lectura. Al no
// usar el gris de "fuera de la fuerza de trabajo", no choca con el gris de "sin título" del gráfico siguiente.
function graficoSexoRegion(reg){const pr=POB.regiones[reg],H=pr.sexo.hombres,M=pr.sexo.mujeres;
 const filas=[["Población de 15 años o más","total"," gs-total"],["Ocupados que viven en la región","trabajan",""],["Desocupados","buscan",""],["Fuera de la fuerza de trabajo","no_buscan",""]];
 return figuraSexo(`% de mujeres y de hombres · todas las actividades de ${nomReg(reg)}`,"Población de 15 años o más",100*M.total/pr.total,"Personas (% del total)","Personas",
  filas.map(([t,k,clase])=>{const n=H[k]+M[k];return [t,M[k],H[k],num(n)+(k==="total"?"":` (${num(100*n/pr.total,1)}%)`),clase]}))}
// Concilia los ocupados de "Toda la región" (viven en ella) con la fila A del CL (trabajan en ella, con actividad
// informada); el lector veía dos cifras de "ocupados" y creía que una estaba mal. El traslado es neto: incluye a quienes
// no informan región de trabajo, por eso en Chile tampoco es cero.
function conciliaOcupados(reg){const pr=POB.regiones[reg],a=BASE.regiones[reg],t=pr.trabajan-pr.lugar_trabajo,s=pr.lugar_trabajo-a;
 const sin=`${num(s)} trabajan en la región sin actividad informada y no entran en A`;
 return `Aquí, ${num(pr.trabajan)} ocupados viven en ${nomReg(reg)}; en la fila A de arriba, ${num(a)} trabajan en ella con actividad informada. `+(t>=0?
  `La diferencia tiene dos partes: salen a trabajar a otras regiones ${num(t)} ocupados más de los que llegan (incluye a quienes no informan dónde trabajan), y ${sin}.`:
  `La fila A es mayor porque llegan a trabajar desde otras regiones ${num(-t)} ocupados más de los que salen; en cambio, ${sin}.`)}
// Lectura con las tasas, que no caben en la barra. La brecha es la misma de la portada (participación de hombres menos
// la de mujeres, con tasas redondeadas). Bajo 0,5 se lee "similar" o "casi igual", el mismo umbral de la desocupación por nivel.
const brecha=x=>Math.round((x.hombres.tasa_participacion-x.mujeres.tasa_participacion)*10)/10;
function lecturaSexoRegion(reg){const s=POB.regiones[reg].sexo,b=brecha(s),bc=brecha(POB.sexo),d=Math.round((b-bc)*10)/10;
 const th=s.hombres.tasa_desocupacion,tm=s.mujeres.tasa_desocupacion,dd=Math.round((th-tm)*10)/10;
 const comp=Math.abs(d)<DIF_CASI_IGUAL?`similar a la de Chile (${num(bc,1)})`:`${d>0?"mayor":"menor"} que en Chile (${num(bc,1)})`;
 const desoc=Math.abs(dd)<DIF_CASI_IGUAL?`casi igual en hombres y mujeres (${num(th,1)}% y ${num(tm,1)}%)`:
  dd>0?`mayor en hombres (${num(th,1)}%) que en mujeres (${num(tm,1)}%)`:`mayor en mujeres (${num(tm,1)}%) que en hombres (${num(th,1)}%)`;
 return `La tasa de participación es ${num(s.hombres.tasa_participacion,1)}% en hombres y ${num(s.mujeres.tasa_participacion,1)}% en mujeres: una brecha de ${num(b,1)} puntos, ${comp}. La desocupación es ${desoc}.`}
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
 <tr><td>A. Ocupados que trabajan en la región, con actividad informada</td><td></td><td class="n ini">${num(BASE.regiones[reg])}</td><td class="n">${num(bs.h)}</td>`+
  `<td class="n">${num(bs.m)}</td><td class="n ini">${num(BASE.chile)}</td><td class="n">${num(BASE.sexo.chile.h)}</td><td class="n">${num(BASE.sexo.chile.m)}</td></tr>
 <tr><td>B. Ocupados en la actividad</td><td></td><td class="n ini">${num(d.ocupados)}</td><td class="n">${celdaSexo(d.h)}</td><td class="n">${celdaSexo(d.m)}</td><td class="n ini">${num(n.ocupados)}</td><td class="n">${num(act.sexo.h)}</td><td class="n">${num(act.sexo.m)}</td></tr>
 <tr><td>C. Participación</td><td>B ÷ A</td><td class="n ini">${part(d.pct)}</td><td class="n">${partSexo(d.pct_h)}</td><td class="n">${partSexo(d.pct_m)}</td><td class="n ini">${part(act.pct_nacional)}</td><td class="n">${part(act.sexo.part_h)}</td><td class="n">${part(act.sexo.part_m)}</td></tr>
 <tr class="total"><td>D. CL</td><td>C ÷ C de Chile</td><td class="n ini">${d.peso_txt}</td><td></td><td></td><td class="n ini">1,00</td><td></td><td></td></tr></tbody></table></div>
 ${[d.h,d.m].some(v=>v!=null&&v<CHICA)?NOTA_CHICA:""}
 <p class="nota" style="margin:6px 0 0">Lectura: ${LECT[d.lectura]}. A incluye organismos internacionales.</p>`+avisos()+
  `<details><summary>Contraste con ENE</summary><p class="nota" style="margin:6px 0 0">CL en ENE de ${PER.ene_contraste}: ${d.ene_peso_txt}, ${LECT[d.ene_lectura]??d.ene_lectura}.</p></details>`;
 // Justo bajo la tabla: las cifras por sexo de B ya están ahí; el gráfico las compara con toda la región (fila A).
 h+=`<h3>Hombres y mujeres en ${esc(act.corto)}</h3>${graficoSexoActividad(d,bs)}`;
 if(otras.length)h+=`<h3>Otras actividades con CL de 1,2 o más</h3><table><thead><tr><th>Actividad</th><th class="n">Ocupados (participación)</th><th class="n">Chile</th><th class="n">CL</th></tr></thead><tbody>${
  otras.slice(0,5).map(a=>{const v=a.regiones[reg];
   return `<tr><td><button class="enlace" data-a="${a.ciiu}">${esc(a.corto)}</button></td><td class="n">${vp(v.ocupados,v.pct)}</td>`+
    `<td class="n">${vp(a.nacional.ocupados,a.pct_nacional)}</td><td class="n">${v.peso_txt}</td></tr>`}).join("")
 }</tbody></table>`;
 h+=`<hr class="separador">${perfilEstudios(d.niveles,`${nomReg(reg)} · ${act.corto}`,nomReg(reg),`${act.corto} en Chile`,act.niveles.map(f=>f[1]))}`;
 // Un solo encabezado para lo que es de toda la región: antes cada sección repetía la base y que no cambia con la actividad.
 h+=`<hr class="separador"><h2>${nomReg(reg)}, todas las actividades</h2><div class="nota">No cambia según la actividad elegida. `+
  `Personas de 15 años o más que viven en la región. ${conciliaOcupados(reg)}</div>`;
 h+=`<h3>Hombres y mujeres en cada grupo, todas las actividades</h3><p class="lectura" style="margin:6px 0 0">${lecturaSexoRegion(reg)}</p>${graficoSexoRegion(reg)}`+
  `<details><summary>Ver cifras</summary><div class="nota" style="margin-top:6px">Entre paréntesis, % de la población de 15 años o más de cada columna.</div>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th>Grupo</th><th class="n">Total</th><th class="n">Hombres</th><th class="n">Mujeres</th></tr></thead><tbody>`+
  `<tr class="total"><td>Población de 15 años o más</td><td class="n">${num(pr.total)}</td><td class="n">${num(pr.sexo.hombres.total)}</td><td class="n">${num(pr.sexo.mujeres.total)}</td></tr>`+
  `${filasSituacion(pr,pr.sexo.hombres,pr.sexo.mujeres,false)}</tbody></table></div></details>`;
 h+=`<h3>Desocupación por nivel de estudios</h3><p class="lectura" style="margin:6px 0 0">${lecturaDesocNivel(reg).frase}</p>${graficoDesocNivel(reg)}`+
  `<p class="nota" style="margin:2px 0 8px">Tasa = desocupados / (ocupados + desocupados).</p>
 <details><summary>Ver cifras</summary><p class="nota" style="margin:6px 0 0">Tasa en ENE: ${PER.ene_contraste}, los meses del Censo.</p>
 <table style="margin-top:8px"><thead><tr><th>Nivel</th><th class="n">Ocupados</th><th class="n">Desocupados</th><th class="n">Tasa de desocupación</th>`+
  `<th class="n">Tasa en Chile</th><th class="n">Tasa en ENE</th></tr></thead><tbody>`+
  NIVELES.map(([k,t])=>{const x=DATOS.niveles[reg][k];
   return `<tr><td>${t}</td><td class="n">${num(x.ocupados)}</td><td class="n">${num(x.desocupados)}</td><td class="n">${num(x.tasa,1)}%</td><td class="n">${num(x.nacional,1)}%</td>`+
    `<td class="n" ${x.ene==null?'title="ENE sin muestra suficiente"':""}>${x.ene==null?"sin muestra":num(x.ene,1)+"%"+(x.ene_poco?" *":"")}</td></tr>`}).join("")+
  `</tbody></table>${NIVELES.some(([k])=>DATOS.niveles[reg][k].ene_poco)?'<p class="nota" style="margin:6px 0 0">* ENE poco fiable.</p>':""}`+
  tablaNivelSexo(k=>DATOS.niveles[reg][k].sexo)+"</details>";
 return h}
