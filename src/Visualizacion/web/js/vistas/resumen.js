/*
<src/Visualizacion/web/js/vistas/resumen.js>

Vista inicial: Chile y todas las actividades.
*/
// Relación entre las dos realidades, región por región: se escribe desde los datos para no afirmar más de lo que muestran.
function extremosDesoc(){const d=Object.entries(EST.desocupacion_titulo),menor=d.filter(([,v])=>v[0]<v[1]).length;
 const [a,va]=d.reduce((m,x)=>x[1][0]<m[1][0]?x:m),[b,vb]=d.reduce((m,x)=>x[1][0]>m[1][0]?x:m);
 return {menor,n:d.length,rango:`de ${num(va[0],1)}% frente a ${num(va[1],1)}% en ${nomReg(Number(a))} a ${num(vb[0],1)}% frente a ${num(vb[1],1)}% en ${nomReg(Number(b))}`}}
function desocTitulo(){const e=extremosDesoc();
 return `${e.menor===e.n?`En las ${e.n} regiones`:`En ${e.menor} de ${e.n} regiones`}, la tasa de desocupación es menor con título técnico o profesional que sin título superior: va ${e.rango}.`}
// Evolución según ENE: las frases salen de la lectura de cada fila, que solo dice "sube" o "baja" si el rango
// entero queda a un lado del cero.
const LECT_EVO={sube:"Sube",baja:"Baja",sin_cambio_claro:"Sin cambio claro"};
const NIVEL_EVO={Profesional:"profesionales",Tecnico:"técnicos",Sin_titulo:"sin título superior"};
const ppTxt=v=>(v>0?"+":v<0?"−":"")+num(Math.abs(v),1);
function frasesEvolucion(){const c=EVO.chile,niv=Object.entries(EVO.niveles),regs=Object.entries(EVO.regiones);
 const chile=c.lect==="sin_cambio_claro"?`La tasa de desocupación pasó de ${num(c.t24,1)}% en 2024 a ${num(c.t26,1)}% en 2026, sin un cambio claro.`
  :`La tasa de desocupación ${c.lect==="sube"?"subió":"bajó"} de ${num(c.t24,1)}% en 2024 a ${num(c.t26,1)}% en 2026 (${ppTxt(c.dif)} pp).`;
 const grupo=(l,v)=>{const x=niv.filter(([,d])=>d.lect===l);return x.length?`${v} en ${lista(x.map(([k,d])=>`${NIVEL_EVO[k]} (${ppTxt(d.dif)} pp)`))}.`:""};
 const quietos=niv.filter(([,d])=>d.lect==="sin_cambio_claro");
 const niveles=[grupo("sube","Subió"),grupo("baja","Bajó"),quietos.length?`En ${lista(quietos.map(([k])=>NIVEL_EVO[k]))} no hay un cambio claro.`:""].filter(Boolean).join(" ");
 const porLect=l=>regs.filter(([,d])=>d.lect===l).sort((a,b)=>b[1].dif-a[1].dif).map(([r])=>nomReg(r));
 const sube=porLect("sube"),baja=porLect("baja"),resto=regs.length-sube.length-baja.length;
 const regiones=[sube.length?`Subió en ${sube.length} ${sube.length===1?"región":"regiones"}: ${lista(sube)}.`:"",
  baja.length?`Bajó en ${baja.length} ${baja.length===1?"región":"regiones"}: ${lista(baja)}.`:"",
  resto?`En ${sube.length||baja.length?"las otras ":"las "}${resto} no hay un cambio claro.`:""].filter(Boolean).join(" ");
 return {chile,niveles,regiones}}
function evolucionHtml(){const f=frasesEvolucion(),c=EVO.chile;
 const filas=Object.entries(EVO.regiones).sort((a,b)=>b[1].dif-a[1].dif||a[0]-b[0]);
 const tr=(t,d,k)=>`<tr class="${k}"><td>${t}</td><td class="n">${num(d.t24,1)}%</td><td class="n">${num(d.t26,1)}%</td>`+
  `<td class="n">${ppTxt(d.dif)} pp</td><td class="n">${ppTxt(d.min)} a ${ppTxt(d.max)}</td><td>${LECT_EVO[d.lect]}</td></tr>`;
 const titulo=c.lect==="sin_cambio_claro"?`La desocupación no muestra un cambio claro entre 2024 y 2026 (${num(c.t24,1)}% y ${num(c.t26,1)}%)`
  :`La desocupación ${c.lect==="sube"?"subió":"bajó"} de ${num(c.t24,1)}% en 2024 a ${num(c.t26,1)}% en 2026`;
 return `${encabezado("sec-evo","Cambio 2024–2026",titulo)}<div class="nota">Encuesta Nacional de Empleo (INE), ${PER.ene_evolucion}. `+
  `Son los mismos meses en ambos años, para que no cuente la estacionalidad, y es otra fuente que el Censo: sus cifras no se mezclan.</div>
 <p style="margin:8px 0 0">Cambio de ${ppTxt(c.dif)} pp, con un rango de ${ppTxt(c.min)} a ${ppTxt(c.max)} pp. ${f.niveles}</p>
 <p style="margin:8px 0 0">${f.regiones}</p>
 <details><summary>Ver por región</summary>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th>Región</th><th class="n">2024</th><th class="n">2026</th><th class="n">Cambio</th>`+
  `<th class="n">Rango del cambio (95%)</th><th>Lectura</th></tr></thead><tbody>`+
  tr("Chile",c,"total")+filas.map(([r,d])=>tr(nomReg(r),d,"")).join("")+`</tbody></table></div>
 <p class="nota" style="margin:6px 0 0">Tasa según región de residencia. "Sin cambio claro": el rango del cambio incluye el cero, así que la diferencia cabe en el margen de error. `+
  `Por región no se separa por nivel de estudios: la ENE no tiene muestra suficiente.</p></details>`}
// Navegación del resumen: un índice arriba y, en cada sección, el tema en pequeño y el hallazgo como título. Así quien
// solo lee los títulos se lleva lo principal, y la tabla queda como evidencia. Los botones desplazan sin tocar la
// dirección: ahí vive la vista elegida (#actividad/región/carrera) y un ancla la borraría.
const SECCIONES=[["Censo 2024",[["sec-pob","Población"],["sec-act","Actividades"],["sec-lab","Trabajo por región"],["sec-edu","Educación por región"],["sec-est","Estudios y trabajo"]]],
 ["Encuesta Nacional de Empleo",[["sec-for","Formalidad"],["sec-evo","Cambio 2024–2026"]]]];
const indiceHtml=()=>`<nav class="indice" aria-label="Secciones del resumen">${SECCIONES.map(([f,s])=>
 `<span class="indice-grupo"><span class="indice-fuente">${f}</span>${s.map(([id,t])=>`<button data-ir="${id}">${t}</button>`).join("")}</span>`).join("")}</nav>`;
const encabezado=(id,tema,titulo,primero)=>`${primero?"":'<hr class="separador">'}<div class="sec-cab" id="${id}" tabindex="-1"><p class="tema">${tema}</p><h2>${titulo}</h2></div>`;
const banda=t=>`<p class="banda">${t}</p>`;
// Región con el menor y el mayor valor: los títulos lo escriben desde los datos para no afirmar más de lo que muestran.
function extremos(valor){const r=DATOS.orden.map(k=>[k,valor(k)]).sort((a,b)=>a[1]-b[1]);return [r[0],r[r.length-1]]}
// "en la Metropolitana": el nombre corto de la región no lleva artículo.
const enReg=r=>(Number(r)===13?"la ":"")+nomReg(r);
const pctTitulo=v=>100*(v[0]+v[1])/(v[0]+v[1]+v[2]);
// Formalidad según ENE: dos ejes y no tres grupos, porque un independiente puede ser formal o informal.
function formalidadHtml(){const c=FOR.chile,n=FOR.niveles,[rMin,rMax]=extremos(r=>FOR.regiones[r].inf);
 const fila=(t,d,k)=>`<tr class="${k}"><td>${t}</td>${["af","ai","xf","xi","fam"].map(x=>`<td class="n">${num(d[x],1)}%</td>`).join("")}<td class="n">${num(d.inf,1)}%</td></tr>`;
 return `${encabezado("sec-for","Formalidad",`Sin título superior, ${num(n.Sin_titulo.inf,1)}% trabaja en la informalidad; con título profesional, ${num(n.Profesional.inf,1)}%`,true)}
 <div class="nota">Encuesta Nacional de Empleo (INE), ${PER.ene_actual}. Ocupados según región de residencia. `+
  `Independiente: empleador o cuenta propia. Asalariado: sector privado, público o servicio doméstico.</div>
 <p style="margin:8px 0 0">En Chile, ${num(c.inf,1)}% de los ocupados es informal. Los independientes son ${num(c.ind,1)}%: `+
  `${num(c.xi,1)}% informales y ${num(c.xf,1)}% formales. La informalidad va de ${num(rMin[1],1)}% en ${enReg(rMin[0])} a ${num(rMax[1],1)}% en ${enReg(rMax[0])}.</p>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th rowspan="2">Nivel</th><th colspan="2" class="bloque ini">Asalariado</th><th colspan="2" class="bloque ini">Independiente</th>`+
  `<th rowspan="2" class="n bloque ini">Familiar no remunerado</th><th rowspan="2" class="n bloque ini">Informal en total</th></tr>`+
  `<tr><th class="n ini">Formal</th><th class="n">Informal</th><th class="n ini">Formal</th><th class="n">Informal</th></tr></thead><tbody>`+
  fila("Chile",c,"total")+NIVELES.map(([k,t])=>fila(t,n[k],"")).join("")+`</tbody></table></div>
 <p class="nota" style="margin:6px 0 0">% de los ocupados de cada fila; las cinco primeras columnas suman 100. Estas diferencias no indican causa: la edad, por ejemplo, también influye.</p>
 <details><summary>Ver por región</summary>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th>Región</th><th class="n">Informal</th><th class="n">Independientes</th></tr></thead><tbody>`+
  [["Chile",c,"total"],...DATOS.orden.map(r=>[DATOS.regiones[r],FOR.regiones[r],""])].map(([t,d,k])=>
   `<tr class="${k}"><td>${esc(t)}</td><td class="n">${num(d.inf,1)}%</td><td class="n">${num(d.ind,1)}%</td></tr>`).join("")+`</tbody></table></div>
 <p class="nota" style="margin:6px 0 0">Por región no se separan las cuatro casillas: en las regiones chicas quedarían con poca muestra.</p></details>`}
function vistaResumen(){
 const orden=[...DATOS.actividades].sort((a,b)=>b.nacional.ocupados-a.nacional.ocupados);
 const ch=POB.chile,sH=POB.sexo.hombres,sM=POB.sexo.mujeres;
 const sinRegion=DATOS.actividades.filter(a=>a.pct_sin_region>=10).sort((a,b)=>b.pct_sin_region-a.pct_sin_region);
 const totalNiveles=NIVELES.map((_,i)=>[DATOS.actividades.reduce((t,a)=>t+a.niveles[i][0],0)]);
 const conMasCarreras=[...DATOS.actividades].sort((a,b)=>b.afines.length-a.afines.length).slice(0,3);
 const corto=c=>esc(porCiiu(c).corto),me=RES.mayor_empleador,[d1,d2]=RES.mas_desiguales;
 const [desMin,desMax]=extremos(r=>POB.regiones[r].tasa_desocupacion),[titMin,titMax]=extremos(r=>pctTitulo(EDU[r])),e=extremosDesoc();
 return `<h2>Chile · Todas las actividades</h2>${indiceHtml()}
 ${banda("Censo 2024")}
 ${encabezado("sec-pob","Población",`Trabaja el ${num(ch.pct_trabajan,1)}% de las ${num(ch.total)} personas de 15 años o más`,true)}
 <details><summary>Ver población y fuerza de trabajo</summary>
 <div class="barra-poblacion" role="img" aria-label="${num(ch.pct_trabajan,1)}% ocupados, ${num(ch.pct_buscan,1)}% desocupados, `+
  `${num(ch.pct_no_buscan,1)}% fuera de la fuerza de trabajo, ${num(ch.pct_sin_dato,1)}% sin dato">${
  [["s-trabajan",ch.trabajan],["s-buscan",ch.buscan],["s-no-buscan",ch.no_buscan],["s-sin-dato",ch.sin_dato]].map(([k,v])=>`<i class="${k}" style="flex:${v} 0 0"></i>`).join("")
 }</div>
 <div class="nota">Entre paréntesis, % de la población de 15 años o más de cada columna.</div>
 <div class="tabla-ancha"><table><thead><tr><th>Grupo</th><th class="n">Total</th><th class="n">Hombres</th><th class="n">Mujeres</th></tr></thead><tbody>
 <tr class="total"><td>Población total</td><td class="n">${num(POB.poblacion_total)}</td><td class="n">${num(sH.poblacion_total)}</td><td class="n">${num(sM.poblacion_total)}</td></tr>
 <tr><td>Menores de 15 años</td><td class="n">${num(POB.menores_15)}</td><td class="n">${num(sH.menores_15)}</td><td class="n">${num(sM.menores_15)}</td></tr>
 <tr class="total"><td>Población de 15 años o más</td><td class="n">${num(ch.total)}</td><td class="n">${num(sH.total)}</td><td class="n">${num(sM.total)}</td></tr>
 ${filasSituacion(ch,sH,sM,true)}
 </tbody></table></div>
 <div class="aviso">Estar fuera de la fuerza de trabajo no equivale a desempleo. El Censo registra la actividad solo de los ocupados.</div></details>
 ${encabezado("sec-act","Actividades",`${corto(me.ciiu)} es la que más emplea en ${me.n} de 16 regiones; las más concentradas son ${corto(d1.ciiu)}, seguida de ${corto(d2.ciiu)}`)}
 <div class="nota">Ocupados (participación), según lugar de trabajo. `+
  `Suman ${num(RES.total)} de ${num(ch.trabajan)}: se excluyen ${num(ch.trabajan-RES.total)} sin región de trabajo o actividad, o en organismos internacionales. `+
  `Hombres y mujeres: % sobre los ocupados de la actividad. Con título: % de sus ocupados con nivel informado; `+
  `en todas las actividades, ${num(conTitulo(totalNiveles),1)}% (el ${num(EST.pct_con_titulo,1)}% de los hallazgos cuenta por residencia).</div>
 <p class="invita"><strong>Elige una actividad</strong> para ver en qué regiones se concentra y sus carreras afines, con títulos, empleabilidad e ingresos. `+
  `Con más carreras afines: ${conMasCarreras.map(a=>`<button class="enlace" data-a="${a.ciiu}">${esc(a.corto)}</button> (${a.afines.length})`).join(" &nbsp;·&nbsp; ")}.</p>
 <div class="tabla-ancha"><table class="tabla-compacta" style="margin-top:8px"><thead><tr><th rowspan="2">Actividad</th><th colspan="3" class="bloque ini">Chile</th>`+
  `<th rowspan="2" class="n bloque ini">Con título técnico o profesional</th><th colspan="3" class="bloque ini">Región con mayor CL</th></tr>`+
  `<tr><th class="n ini">Ocupados</th><th class="n">Hombres</th><th class="n">Mujeres</th><th class="ini">Región</th><th class="n">Ocupados</th><th class="n">CL</th></tr></thead><tbody>`+
  orden.map(a=>{const n=a.nacional,v=a.regiones[n.mas_peso.r];
   return `<tr><td><button class="enlace" data-a="${a.ciiu}">${esc(a.corto)}</button>${a.alerta_fuente?' <span title="Censo y ENE difieren en el tamaño de esta actividad">⚠</span>':""}</td>`+
    `<td class="n ini">${vp(n.ocupados,a.pct_nacional)}</td><td class="n">${num(a.sexo.h)} (${num(a.sexo.pct_h,1)}%)</td><td class="n">${num(a.sexo.m)} (${num(a.sexo.pct_m,1)}%)</td>`+
    `<td class="n ini">${num(conTitulo(a.niveles),1)}%</td><td class="ini">${nomReg(n.mas_peso.r)}</td><td class="n">${vp(v.ocupados,v.pct)}</td><td class="n">${n.mas_peso.txt}</td></tr>`}).join("")+
  `</tbody></table></div>
 <p class="nota" style="margin:8px 0 0">CL: cuántas veces pesa la actividad en la región respecto de su peso en Chile. ⚠ Censo y ENE difieren en el tamaño de esta actividad.</p>
 ${sinRegion.length?`<p class="nota" style="margin:4px 0 0">Subestimadas por ocupados sin región de trabajo `+
  `(${num(sinRegion[sinRegion.length-1].pct_sin_region,1)}% a ${num(sinRegion[0].pct_sin_region,1)}%): ${lista(sinRegion.map(a=>esc(a.corto)))}.</p>`:""}
 ${encabezado("sec-lab","Trabajo por región",`La desocupación va de ${num(desMin[1],1)}% en ${enReg(desMin[0])} a ${num(desMax[1],1)}% en ${enReg(desMax[0])}`)}
 <div class="nota">Población de 15 años o más, según región de residencia. Entre paréntesis, % de esa población. `+
  `Ocupados (lugar de trabajo) cuenta a quienes trabajan en la región, vivan o no en ella. `+
  `En Chile suma menos que por residencia porque ${num(100*(ch.trabajan-ch.lugar_trabajo)/ch.trabajan,1)}% de los ocupados no tiene región de trabajo.</div>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th>Región</th><th class="n">15 años o más</th><th class="n">Ocupados (residencia)</th>`+
  `<th class="n">Ocupados (lugar de trabajo)</th><th class="n">Desocupados</th><th class="n">Fuera de la fuerza de trabajo</th>`+
  `<th class="n">Tasa de desocupación</th><th class="n">Tasa de participación</th></tr></thead><tbody>`+
  [["Chile",ch,"total"],...DATOS.orden.map(r=>[DATOS.regiones[r],POB.regiones[r],""])].map(([t,d,k])=>
   `<tr class="${k}"><td>${esc(t)}</td><td class="n">${num(d.total)}</td><td class="n">${num(d.trabajan)} (${num(d.pct_trabajan,1)}%)</td><td class="n">${num(d.lugar_trabajo)}</td>`+
   `<td class="n">${num(d.buscan)} (${num(d.pct_buscan,1)}%)</td><td class="n">${num(d.no_buscan)} (${num(d.pct_no_buscan,1)}%)</td>`+
   `<td class="n">${num(d.tasa_desocupacion,1)}%</td><td class="n">${num(d.tasa_participacion,1)}%</td></tr>`).join("")+
  `</tbody></table></div>
 <div class="aviso">La tasa depende de la edad de la población de cada región: por sí sola no basta para comparar el empleo.</div>
 ${encabezado("sec-edu","Educación por región",`Con título técnico o profesional: de ${num(titMin[1],1)}% en ${enReg(titMin[0])} a ${num(titMax[1],1)}% en ${enReg(titMax[0])}`)}
 <div class="nota">Población de 15 años o más, según región de residencia, con nivel de estudios y situación laboral informados. `+
  `Se excluyen ${num(EST.excluidos.sin_nivel)} sin nivel informado y ${num(EST.excluidos.sin_situacion)} sin situación laboral. Entre paréntesis, % de esa población.</div>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th>Región</th><th class="n">Con nivel informado</th>${NIVELES.map(([,t])=>`<th class="n">${t}</th>`).join("")}`+
  `<th class="n">Con título técnico o profesional</th></tr></thead><tbody>`+
  [["Chile",EDU.chile,"total"],...DATOS.orden.map(r=>[DATOS.regiones[r],EDU[r],""])].map(([t,v,k])=>{const tot=v[0]+v[1]+v[2];
   return `<tr class="${k}"><td>${esc(t)}</td><td class="n">${num(tot)}</td>${v.map(x=>`<td class="n">${num(x)} (${num(100*x/tot,1)}%)</td>`).join("")}`+
    `<td class="n">${num(pctTitulo(v),1)}%</td></tr>`}).join("")+`</tbody></table></div>
 <div class="aviso">Incluye a jóvenes que aún estudian: el % con título depende de la edad de la población de cada región.</div>
 ${encabezado("sec-est","Estudios y trabajo",`${e.menor===e.n?`En las ${e.n} regiones`:`En ${e.menor} de ${e.n} regiones`}, menos desocupación con título técnico o profesional`)}
 <div class="nota">Chile, Censo 2024. Según residencia, con nivel de estudios informado: ${num(EST.total)} ocupados.</div>
 <p style="margin:8px 0 0">${desocTitulo()}</p>
 <p style="margin:8px 0 0">Tienen título técnico o profesional ${num(EST.pct_con_titulo,1)}% de los ocupados: ${num(EST.sexo.mujeres,1)}% de las mujeres y ${num(EST.sexo.hombres,1)}% de los hombres.</p>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th>Nivel</th><th class="n">Ocupados</th><th class="n">Tasa de desocupación</th><th class="n">Tasa de participación</th></tr></thead><tbody>${
  NIVELES.map(([k,t])=>{const x=EST.niveles[k];
   return `<tr><td>${t}</td><td class="n">${num(x.ocupados)} (${num(x.pct,1)}%)</td><td class="n">${num(x.tasa_desocupacion,1)}%</td><td class="n">${num(x.tasa_participacion,1)}%</td></tr>`}).join("")
 }</tbody></table></div>
 <p class="nota" style="margin:6px 0 0">Estas diferencias no indican causa: la edad de cada grupo, por ejemplo, también influye.</p>
 <hr class="separador">${banda("Encuesta Nacional de Empleo (INE)")}
 ${formalidadHtml()}
 ${evolucionHtml()}`}
