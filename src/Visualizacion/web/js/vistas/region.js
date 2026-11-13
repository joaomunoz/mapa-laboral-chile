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
 const usadas=[["menor","menor"],["mayor","mayor"],["igual","casi igual"]].filter(([k])=>g[k].length);
 // Solo la primera parte dice "que en Chile"; repetido en cada parte, la frase se alargaba sin agregar nada.
 const partes=usadas.map(([k,e],i)=>`${e}${i?"":" que en Chile"} ${g[k].length===3?"en los 3 niveles":"entre "+lista(g[k])}`);
 const t=NIVELES.map(([k])=>DATOS.niveles[reg][k].tasa),baja=t[0]<t[1]&&t[1]<t[2];
 return {frase:`La desocupación es ${partes.length>1?partes.slice(0,-1).join(", ")+", y "+partes.at(-1):partes[0]}.`+(baja?" Con más estudios, la tasa es más baja.":""),g,baja}}
function graficoDesocNivel(reg){const filas=NIVELES.map(([k,t],i)=>[t,DATOS.niveles[reg][k],["ed-pro","ed-tec","tsin"][i]]);
 const tope=Math.ceil(Math.max(...filas.flatMap(([,x])=>[x.tasa,x.nacional]))/4)*4,pos=v=>100*v/tope;
 const signo=d=>d>0?`+${num(d,1)}`:d<0?`−${num(-d,1)}`:num(0,1);
 // La tasa de Chile va como línea en cada barra, igual que la comparación de los demás gráficos del detalle: así se ve
 // si la región está sobre o bajo Chile sin cruzar columnas. Las columnas Chile y Diferencia quedan con la cifra exacta.
 return `<figure class="graf-cl" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><span class="ref"></span>Chile</span></figcaption>`+
  `<div class="cl-fila dn-fila gs-cab" aria-hidden="true"><span class="cl-nombre">Nivel</span><span>${nomReg(reg)}</span>`+
  `<span class="gs-extra"><span class="gs-num">Chile</span><span class="gs-num">Diferencia</span></span></div>`+
  filas.map(([t,x,c])=>{const d=difNivel(x),partes=[`${nomReg(reg)}: ${num(x.tasa,1)}%`,`Chile: ${num(x.nacional,1)}%`,`diferencia: ${signo(d)} pp`,`${num(x.desocupados)} desocupados y ${num(x.ocupados)} ocupados`];
   return `<div class="cl-fila dn-fila" role="img" tabindex="0" data-tip="${`<strong>${t}</strong><br>${partes.join("<br>")}`.replace(/"/g,"&quot;")}" aria-label="${t}: ${partes.join(", ")}">`+
    `<span class="cl-nombre">${t}</span><span class="cl-barra" aria-hidden="true"><i class="${c}" style="width:${pos(x.tasa)}%"></i><b style="left:${pos(x.nacional)}%"></b>`+
    `<span class="cl-valor" style="left:calc(${pos(x.tasa)}% + 6px)">${num(x.tasa,1)}%</span></span>`+
    `<span class="gs-extra"><span class="gs-num"><span class="gs-et">Chile </span>${num(x.nacional,1)}%</span><span class="gs-num"><span class="gs-et">Diferencia </span>${signo(d)} pp</span></span></div>`}).join("")+`</figure>`}
// Barra rosa/azul del detalle de región: el mismo componente y colores que "Hombres y mujeres por actividad" del
// resumen, idea del usuario. Cada fila es su propio 100% y la línea es la referencia de cada gráfico. La usan la
// actividad (por lugar de trabajo) y toda la región (por residencia): una sola función para que se lean igual.
// et: rótulo de la cifra cuando el celular oculta la cabecera. filas: [rótulo, mujeres, hombres, texto de la columna, clase]; las de mujeres u hombres nulos (menos de 10) se avisan.
function figuraSexo(refTexto,ref,cabecera,et,filas){
 const fila=([t,m,hh,extra,clase])=>{
  if(m==null||hh==null)return `<div class="gs-fila gs-region${clase}"><span class="gs-nombre">${esc(t)}</span><span class="nota" style="grid-column:2/5">Menos de 10 personas: ver cifras</span></div>`;
  const n=m+hh,pm=100*m/n,ph=100-pm,partes=[extra,`${num(m)} mujeres (${num(pm,1)}%)`,`${num(hh)} hombres (${num(ph,1)}%)`];
  return `<div class="gs-fila gs-region${clase}" role="img" tabindex="0" data-tip="${`<strong>${esc(t)}</strong><br>${partes.join("<br>")}`.replace(/"/g,"&quot;")}" aria-label="${esc(t)}: ${partes.join(", ")}">`+
   `<span class="gs-nombre">${esc(t)}</span><span class="gs-pct">${num(pm,1)}%</span><span class="gs-barra" aria-hidden="true"><i class="m" style="flex:${pm} 0 0"></i><i class="h" style="flex:${ph} 0 0"></i>`+
   `<b style="left:${ref}%"></b></span><span class="gs-pct h">${num(ph,1)}%</span>`+
   `<span class="gs-extra"><span class="gs-num"><span class="gs-et">${et} </span>${extra}</span></span></div>`};
 return `<figure class="graf-sexo" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda">`+
  `<span><i style="background:var(--muj)"></i>Mujeres</span><span><i style="background:var(--hom)"></i>Hombres</span><span><span class="ref"></span>${refTexto} (${num(ref,1)}% mujeres)</span></figcaption>`+
  `<div class="gs-fila gs-region gs-cab" aria-hidden="true"><span class="gs-nombre"></span><span></span><span></span><span></span><span class="gs-extra"><span class="gs-num">${cabecera}</span></span></div>`+
  filas.map(fila).join("")+`</figure>`}
// La actividad: en Chile y en la región, frente a todas las actividades de la región. Las tres cifras cuentan a los
// ocupados donde trabajan, como la tabla del CL: la línea es la fila A. Así se ve si la actividad tiene más o menos
// mujeres que la región en general (Hogares en O'Higgins: 89,0% frente a 42,1%).
function graficoSexoActividad(d,bs){
 return figuraSexo(`Todas las actividades de ${enReg(reg)}`,100*bs.m/(bs.h+bs.m),"Ocupados","Ocupados",[
  [`${act.corto} en Chile`,act.sexo.m,act.sexo.h,num(act.sexo.m+act.sexo.h)," gs-total"],
  // Con menos de 60 mujeres u hombres, la fila lleva el mismo "*" que la tabla del CL y que el gráfico de estudios.
  [`${act.corto} en ${enReg(reg)}${[d.h,d.m].some(v=>v!=null&&v<CHICA)?" *":""}`,d.m,d.h,num(d.ocupados),""]])}
// Toda la región, por residencia. La línea es el % de mujeres en la población de 15 años o más: se lee de inmediato que
// las mujeres pesan menos entre los ocupados y más entre quienes están fuera. Sin dato (menos de 1%) queda solo en
// "Ver cifras": su reparto por sexo no dice nada. Las tasas no son partes de un todo y van en la frase de lectura. Al no
// usar el gris de "fuera de la fuerza de trabajo", no choca con el gris de "sin título" del gráfico siguiente.
function graficoSexoRegion(reg){const pr=POB.regiones[reg],H=pr.sexo.hombres,M=pr.sexo.mujeres;
 const filas=[["Población de 15 años o más","total"," gs-total"],["Ocupados que viven en la región","trabajan",""],["Desocupados","buscan",""],["Fuera de la fuerza de trabajo","no_buscan",""]];
 return figuraSexo("Población de 15 años o más",100*M.total/pr.total,"Personas (% del total)","Personas",
  filas.map(([t,k,clase])=>{const n=H[k]+M[k];return [t,M[k],H[k],num(n)+(k==="total"?"":` (${num(100*n/pr.total,1)}%)`),clase]}))}
// Concilia las cifras de ocupados de la región con el traslado medido: viven en ella, menos quienes no informan dónde
// trabajan y quienes trabajan en otra región, más los que llegan, da los que trabajan en ella (la cifra del hallazgo de la
// Metropolitana); de esos, la fila A informa su actividad. Antes se suponía la falta de región igual en todas partes.
function conciliaOcupados(reg){const pr=POB.regiones[reg],a=BASE.regiones[reg],R=enReg(reg);
 return `En este gráfico, ${num(pr.trabajan)} ocupados viven en ${R}. De ellos, ${num(pr.sin_region_trabajo)} no informan dónde trabajan y ${num(pr.salen)} trabajan en otra región; `+
  `desde otras llegan ${num(pr.llegan)}: ${num(pr.lugar_trabajo)} trabajan en ${R}. De esos, ${num(a)} informan su actividad: son la fila A de la tabla del inicio.`}
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
// CL de las 20 actividades de la región: responde "qué distingue a esta región", no solo qué se concentra (la tabla
// anterior mostraba de 1 a 5 actividades sobre 1,2 y ocultaba las que están bajo Chile, 121 de 320 casos). La línea en 1
// es Chile, que siempre vale 1. Escala logarítmica, porque el CL es un cociente: 0,5 y 2 quedan a igual distancia de 1,
// y Minería en Antofagasta (8,06) no aplasta al resto. El dominio es fijo, de 1/16 a 16 (los 320 CL van de 0,07 a 8,06),
// para que la escala no cambie al pasar de una región a otra. Los colores son los 7 tramos del mapa.
const CL_MIN=1/16,CL_MAX=16,CL_MARCAS=[0.125,0.25,0.5,1,2,4,8];
const posCL=v=>100*Math.log(v/CL_MIN)/Math.log(CL_MAX/CL_MIN);
const porCLRegion=reg=>[...DATOS.actividades].sort((a,b)=>ordenar(a.regiones[reg],b.regiones[reg]));
function graficoCLRegion(reg){const uno=posCL(1);
 const fila=a=>{const v=a.regiones[reg],x=posCL(v.peso),sel=a.ciiu===act.ciiu;
  const partes=[`CL ${v.peso_txt}: ${LECT[v.lectura]}`,`${num(v.ocupados)} ocupados (${part(v.pct)} de los ocupados de la región)`,`En Chile, ${part(a.pct_nacional)}`];
  return `<button class="cl-fila clr-fila${sel?" clr-sel":""}" data-a="${a.ciiu}" data-tip="${`<strong>${esc(a.corto)}</strong><br>${partes.join("<br>")}`.replace(/"/g,"&quot;")}" aria-label="${esc(a.corto)}${sel?" (elegida)":""}, ${partes.join(", ")}">`+
   `<span class="cl-nombre">${esc(a.corto)}</span><span class="cl-barra clr-barra" aria-hidden="true">`+
   `<i style="left:${Math.min(x,uno)}%;width:${Math.abs(x-uno)}%;background:${relleno(v)}" class="${v.peso<1?"izq":""}"></i><b style="left:${uno}%"></b>`+
   `<span class="cl-valor" style="${v.peso<1?`right:calc(${100-x}% + 6px)`:`left:calc(${x}% + 6px)`}">${v.peso_txt}</span></span></button>`};
 return `<figure class="graf-cl" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda">`+
  `<span><span class="ref"></span>CL 1: pesa lo mismo que en Chile</span><span>Color: tramo del mapa</span></figcaption>`+
  `<div class="cl-fila clr-fila gs-cab" aria-hidden="true"><span class="cl-nombre"></span><span class="clr-eje">${
   CL_MARCAS.map(m=>`<span style="left:${posCL(m)}%">${num(m,m<0.25?3:m<1?2:0).replace(/0+$/,"").replace(/,$/,"")}</span>`).join("")}</span></div>`+
  porCLRegion(reg).map(fila).join("")+`</figure>`}
// La frase usa los mismos cortes del mapa (LECT): 1,2 o más, entre 0,8 y 1,2, y 0,8 o menos.
function lecturaCLRegion(reg){const n=DATOS.actividades.length,g=k=>porCLRegion(reg).filter(a=>a.regiones[reg].lectura===k);
 const sobre=g("concentra"),sim=g("similar").length,bajo=g("bajo_lo_nacional").length;
 const txt=lista(sobre.map(a=>`${esc(a.corto)} (${a.regiones[reg].peso_txt})`));
 return `En ${enReg(reg)}, `+(sobre.length?`${sobre.length===1?"1 actividad pesa":`${sobre.length} de las ${n} actividades pesan`} más que en Chile (CL de 1,2 o más): ${txt}. `:`ninguna de las ${n} actividades tiene CL de 1,2 o más. `)+
  `${sobre.length?"Otras ":"Hay "}${sim} ${sim===1?"es similar":"son similares"} a Chile y ${bajo} ${bajo===1?"está":"están"} bajo Chile (CL de 0,8 o menos).`}
function vistaRegion(){
 const d=act.regiones[reg],n=act.nacional,bs=BASE.sexo.regiones[reg],pr=POB.regiones[reg];
 // El título usa el nombre del selector: con el oficial, el usuario no reconocía la actividad que eligió.
 let h=`<h2>${nomReg(reg)} · ${esc(act.corto)}</h2><div class="nota">${act.glosa!==act.corto?`Nombre oficial: ${esc(act.glosa)}. `:""}Censo 2024, según región de trabajo.</div>${RES.regiones[reg].ciiu===act.ciiu?
  `<p class="nota" style="margin:6px 0 0">${esc(act.corto)} es la actividad con mayor CL de ${enReg(reg)}. Para ver otra, elígela en el gráfico del CL, más abajo.</p>`:""}
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
 // Orden por tema, como pidió el usuario: CL, hombres y mujeres, nivel de estudios y carreras. Cada tema junta la
 // actividad y toda la región, que se comparan entre sí; una nota corta dice cuándo la sección es de toda la región.
 // (Se probó ordenar por alcance y separaba lo que se lee junto: el nivel de los ocupados quedaba lejos de la desocupación por nivel.)
 h+=`<h3>CL de las ${DATOS.actividades.length} actividades en ${enReg(reg)}</h3><div class="nota">Toda la región: no cambia según la actividad elegida; según lugar de trabajo.</div><p class="lectura lectura-sec" style="margin:6px 0 0">${lecturaCLRegion(reg)}</p>${graficoCLRegion(reg)}`+
  `<p class="nota" style="margin:2px 0 8px">CL: cuántas veces pesa la actividad en la región respecto de su peso en Chile, según lugar de trabajo. Escala logarítmica: 0,5 (la mitad que en Chile) y 2 (el doble) quedan a la misma distancia de 1.</p>`+
  `<details><summary>Ver cifras</summary><table style="margin-top:8px"><thead><tr><th>Actividad</th><th class="n">Ocupados (participación)</th><th class="n">Chile</th><th class="n">CL</th></tr></thead><tbody>${
  porCLRegion(reg).map(a=>{const v=a.regiones[reg];
   return `<tr><td><button class="enlace" data-a="${a.ciiu}">${esc(a.corto)}</button></td><td class="n">${vp(v.ocupados,v.pct)}</td>`+
    `<td class="n">${vp(a.nacional.ocupados,a.pct_nacional)}</td><td class="n">${v.peso_txt}</td></tr>`}).join("")
 }</tbody></table></details>`;
 h+=`<hr class="separador">`;
 // Las cifras por sexo de B están en la tabla; el gráfico las compara con toda la región (fila A).
 h+=`<h3>Hombres y mujeres en ${esc(act.corto)}</h3>${graficoSexoActividad(d,bs)}`;
 h+=`<h3>Hombres y mujeres en cada grupo, todas las actividades</h3><div class="nota">Toda la región: no cambia según la actividad elegida; personas de 15 años o más que viven en la región.</div><p class="lectura lectura-sec" style="margin:6px 0 0">${lecturaSexoRegion(reg)}</p>${graficoSexoRegion(reg)}<p class="nota" style="margin:2px 0 8px">${conciliaOcupados(reg)}</p>`+
  `<details><summary>Ver cifras</summary><div class="nota" style="margin-top:6px">Entre paréntesis, % de la población de 15 años o más de cada columna.</div>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th>Grupo</th><th class="n">Total</th><th class="n">Hombres</th><th class="n">Mujeres</th></tr></thead><tbody>`+
  `<tr class="total"><td>Población de 15 años o más</td><td class="n">${num(pr.total)}</td><td class="n">${num(pr.sexo.hombres.total)}</td><td class="n">${num(pr.sexo.mujeres.total)}</td></tr>`+
  `${filasSituacion(pr,pr.sexo.hombres,pr.sexo.mujeres,false)}</tbody></table></div></details>`;
 h+=`<hr class="separador">`;
 h+=perfilEstudios(d.niveles,`${nomReg(reg)} · ${act.corto}`,nomReg(reg),`${act.corto} en Chile`,act.niveles.map(f=>f[1]),"h3");
 h+=`<h3>Desocupación por nivel de estudios</h3><div class="nota">Toda la región: no cambia según la actividad elegida; según residencia, con nivel informado.</div><p class="lectura lectura-sec" style="margin:6px 0 0">${lecturaDesocNivel(reg).frase}</p>${graficoDesocNivel(reg)}`+
  `<p class="nota" style="margin:2px 0 8px">Tasa = desocupados / (ocupados + desocupados).</p>
 <details><summary>Ver cifras</summary><p class="nota" style="margin:6px 0 0">Tasa en ENE: ${PER.ene_contraste}, los meses del Censo.</p>
 <table style="margin-top:8px"><thead><tr><th>Nivel</th><th class="n">Ocupados</th><th class="n">Desocupados</th><th class="n">Tasa de desocupación</th>`+
  `<th class="n">Tasa en Chile</th><th class="n">Tasa en ENE</th></tr></thead><tbody>`+
  NIVELES.map(([k,t])=>{const x=DATOS.niveles[reg][k];
   return `<tr><td>${t}</td><td class="n">${num(x.ocupados)}</td><td class="n">${num(x.desocupados)}</td><td class="n">${num(x.tasa,1)}%</td><td class="n">${num(x.nacional,1)}%</td>`+
    `<td class="n" ${x.ene==null?'title="ENE sin muestra suficiente"':""}>${x.ene==null?"sin muestra":num(x.ene,1)+"%"+(x.ene_poco?" *":"")}</td></tr>`}).join("")+
  `</tbody></table>${NIVELES.some(([k])=>DATOS.niveles[reg][k].ene_poco)?'<p class="nota" style="margin:6px 0 0">* ENE poco fiable.</p>':""}`+
  tablaNivelSexo(k=>DATOS.niveles[reg][k].sexo)+"</details>";
 h+=bloqueCarreras();
 return h}
