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
// "Dentro del margen" y no "sin cambio claro": dice por qué no se afirma un cambio, aunque las columnas difieran.
const LECT_EVO={sube:"Sube",baja:"Baja",sin_cambio_claro:"Dentro del margen"};
const NIVEL_EVO={Profesional:"profesionales",Tecnico:"técnicos",Sin_titulo:"sin título superior"};
const ppTxt=v=>(v>0?"+":v<0?"−":"")+num(Math.abs(v),1);
function frasesEvolucion(){const c=EVO.chile,niv=Object.entries(EVO.niveles),regs=Object.entries(EVO.regiones);
 const chile=c.lect==="sin_cambio_claro"?`La tasa de desocupación pasó de ${num(c.t24,1)}% en 2024 a ${num(c.t26,1)}% en 2026, un cambio dentro del margen de error.`
  :`La tasa de desocupación ${c.lect==="sube"?"subió":"bajó"} de ${num(c.t24,1)}% en 2024 a ${num(c.t26,1)}% en 2026 (${ppTxt(c.dif)} pp).`;
 const grupo=(l,v)=>{const x=niv.filter(([,d])=>d.lect===l);return x.length?`${v} en ${lista(x.map(([k,d])=>`${NIVEL_EVO[k]} (${ppTxt(d.dif)} pp)`))}.`:""};
 const quietos=niv.filter(([,d])=>d.lect==="sin_cambio_claro");
 const niveles=[grupo("sube","Subió"),grupo("baja","Bajó"),quietos.length?`En ${lista(quietos.map(([k])=>NIVEL_EVO[k]))}, el cambio queda dentro del margen de error.`:""].filter(Boolean).join(" ");
 const porLect=l=>regs.filter(([,d])=>d.lect===l).sort((a,b)=>b[1].dif-a[1].dif).map(([r])=>nomReg(r));
 const sube=porLect("sube"),baja=porLect("baja"),resto=regs.length-sube.length-baja.length;
 const regiones=[sube.length?`Subió en ${sube.length} ${sube.length===1?"región":"regiones"}: ${lista(sube)}.`:"",
  baja.length?`Bajó en ${baja.length} ${baja.length===1?"región":"regiones"}: ${lista(baja)}.`:"",
  resto?`En ${sube.length||baja.length?"las otras ":"las "}${resto}, el cambio queda dentro del margen de error.`:""].filter(Boolean).join(" ");
 return {chile,niveles,regiones}}
// Columnas agrupadas, 2024 y 2026 por grupo, en una misma escala desde 0. Énfasis por lectura: los grupos que suben
// llevan ocre y azul, y los que quedan dentro del margen van en gris, para que el gráfico diga solo cuáles cambiaron
// sin que haya que leer el rango (la lectura la sigue decidiendo el rango del 95%). Bajo cada grupo va solo el cambio:
// las tasas, el rango y la lectura escrita están en el globo y en la tabla "Ver cifras", porque una cifra en cada
// marca no se lee. Con 17 grupos (modo compacto) los nombres van a 45° y en pantallas angostas el gráfico se desliza.
function columnasEvolucion(titulo,grupos,tope,compacto){const pos=x=>100*x/tope,marcas=Array.from({length:tope/4+1},(_,k)=>4*k);
 const grupo=([t,d,clase,attr])=>{const partes=[`${num(d.t24,1)}% en 2024 y ${num(d.t26,1)}% en 2026`,`cambio ${ppTxt(d.dif)} pp (rango del 95%: ${ppTxt(d.min)} a ${ppTxt(d.max)} pp)`,LECT_EVO[d.lect].toLowerCase()];
  const gris=d.lect==="sin_cambio_claro",col=(v,k)=>`<span class="evc-col ${gris?"g"+k.slice(1):k}" style="height:${pos(v)}%">${compacto?"":`<em>${num(v,1)}%</em>`}</span>`;
  const tag=attr?"button":"div";
  return `<${tag} class="evc-grupo${clase}" ${attr||""}${attr?"":' role="img" tabindex="0"'} data-tip="${`<strong>${t}</strong><br>${partes.join("<br>")}`.replace(/"/g,"&quot;")}" aria-label="${t}: ${partes.join(", ")}">`+
   `<span class="evc-cols" aria-hidden="true">${col(d.t24,"a24")}${col(d.t26,"a26")}</span><span class="evc-nombre"><span>${t}</span></span>`+
   `<span class="evc-dif">${ppTxt(d.dif)}${compacto?"":" pp"}</span></${tag}>`};
 const hayGris=grupos.some(([,d])=>d.lect==="sin_cambio_claro");
 return `<figure class="graf-ev" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><strong style="color:var(--t1)">${titulo}</strong></span>`+
  `<span><i class="a24"></i>2024</span><span><i class="a26"></i>2026</span>${hayGris?`<span><i class="g24"></i><i class="g26"></i>Dentro del margen de error</span>`:""}</figcaption>`+
  `<div class="${compacto?"evc-desliza":""}"><div class="evc${compacto?" compacto":""}">`+
  (compacto?`<div class="evc-rotulos" aria-hidden="true"><span>Cambio</span></div>`:"")+
  `<div class="evc-grilla" aria-hidden="true">${marcas.map(m=>`<span style="bottom:${pos(m)}%"><small>${m}%</small></span>`).join("")}</div>`+
  grupos.map(grupo).join("")+`</div></div></figure>`}
// Tabla gemela de los dos gráficos: todas las cifras, para quien no ve el gráfico o quiere el detalle sin pasar el mouse.
function tablaEvolucion(filas){const c=EVO.chile;
 const tr=(t,d,k)=>`<tr class="${k}"><td>${t}</td><td class="n">${num(d.t24,1)}%</td><td class="n">${num(d.t26,1)}%</td>`+
  `<td class="n">${ppTxt(d.dif)} pp</td><td class="n">${ppTxt(d.min)} a ${ppTxt(d.max)}</td><td>${LECT_EVO[d.lect]}</td></tr>`;
 return `<details><summary>Ver cifras</summary><div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th></th><th class="n">2024</th><th class="n">2026</th>`+
  `<th class="n">Cambio</th><th class="n">Rango del cambio (95%)</th><th>Lectura</th></tr></thead><tbody>`+
  tr("Chile",c,"total")+NIVELES.map(([k,t])=>tr(t,EVO.niveles[k],"")).join("")+filas.map(([r,d],i)=>tr(nomReg(r),d,i?"":"sep")).join("")+`</tbody></table></div></details>`}
function graficosEvolucion(filas){const c=EVO.chile,todos=[c,...Object.values(EVO.niveles),...filas.map(([,d])=>d)];
 const tope=Math.ceil(Math.max(...todos.flatMap(d=>[d.t24,d.t26]))/4)*4;
 return columnasEvolucion("Por nivel de estudios",[["Chile",c," evc-total"],...NIVELES.map(([k,t])=>[t,EVO.niveles[k],""])],tope)+
  columnasEvolucion("Por región",[["Chile",c," evc-total",""],...filas.map(([r,d])=>[nomReg(r),d,"",`data-r="${r}"`])],tope,true)+tablaEvolucion(filas)}
function evolucionHtml(){const f=frasesEvolucion(),c=EVO.chile;
 const filas=Object.entries(EVO.regiones).sort((a,b)=>b[1].dif-a[1].dif||a[0]-b[0]);
 const titulo=c.lect==="sin_cambio_claro"?`La desocupación pasó de ${num(c.t24,1)}% en 2024 a ${num(c.t26,1)}% en 2026, dentro del margen de error`
  :`La desocupación ${c.lect==="sube"?"subió":"bajó"} de ${num(c.t24,1)}% en 2024 a ${num(c.t26,1)}% en 2026`;
 return `${encabezado("sec-evo","Cambio 2024–2026",titulo)}<div class="nota">Encuesta Nacional de Empleo (INE), ${PER.ene_evolucion}. `+
  `Son los mismos meses en ambos años, para que no cuente la estacionalidad, y es otra fuente que el Censo: sus cifras no se mezclan.</div>
 <p style="margin:8px 0 0">Cambio de ${ppTxt(c.dif)} pp, con un rango de ${ppTxt(c.min)} a ${ppTxt(c.max)} pp. ${f.niveles}</p>
 <p style="margin:8px 0 0">${f.regiones}</p>
 ${graficosEvolucion(filas)}
 <p class="nota" style="margin:6px 0 0">Tasa según región de residencia, en una misma escala desde 0; bajo cada grupo, el cambio en pp. La lectura usa el rango del cambio con 95% de confianza, que está en "Ver cifras" y al pasar el mouse: `+
  `"sube" si el rango entero queda sobre cero; "dentro del margen" si incluye el cero, porque la diferencia puede deberse a la muestra. `+
  `Por región no se separa por nivel de estudios: la ENE no tiene muestra suficiente.</p>`}
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
// Una barra formal/informal: lo informal va primero, para que comparta la base y se compare entre filas, y ambas partes
// llevan su color y su %, porque son las dos mitades que se leen (solo el informal dejaba la otra mitad sin cifra).
// Bajo 9% la cifra no cabe en el tramo y queda en el globo.
const barraFormal=(inf,form)=>`<span class="fo-barra" aria-hidden="true"><i class="fo-inf" style="flex:${inf} 0 0">${inf>=9?`${num(inf,1)}%`:""}</i>`+
 `<i class="fo-for" style="flex:${form} 0 0">${form>=9?`${num(form,1)}%`:""}</i></span>`;
const leyendaFormal=`<span><i class="fo-inf"></i>Informal</span><span><i class="fo-for"></i>Formal</span>`;
// Formalidad por nivel: tres gráficos con la misma escala. "Todos los ocupados" lleva las cifras del título (incluye al
// familiar no remunerado, siempre informal); "Asalariados" e "Independientes" miden la informalidad dentro de cada
// grupo, que el reparto sobre el total no deja ver: 69,2% de los independientes sin título es informal, frente a 22,6%
// de los profesionales. Cuántos son va al lado: los asalariados son tres veces los independientes.
// Se descartaron las barras divergentes con el reparto completo: mostraban cuánto pesa cada grupo, no qué tan informal es.
function graficoFormalidadNivel(){const filas=[["Chile",FOR.chile," cl-total"],...NIVELES.map(([k,t])=>[t,FOR.niveles[k],""])];
 const grupos=[["Todos los ocupados","ocupados",d=>[d.ocup,d.inf[1],d.for[1]]],
  ["Asalariados","asalariados",d=>[d.asa[0],d.asa[1],100-d.asa[1]]],["Independientes","independientes",d=>[d.inx[0],d.inx[1],100-d.inx[1]]]];
 const panel=([titulo,grupo,valor])=>`<div class="fo-panel"><p class="fo-titulo">${titulo}</p>`+filas.map(([t,d,clase])=>{const [miles,inf,form]=valor(d);
  const partes=[`${num(miles)} ${grupo}`,`${num(inf,1)}% informal`,`${num(form,1)}% formal`];
  return `<div class="fo-fila${clase}" role="img" tabindex="0" data-tip="${`<strong>${titulo}, ${t}</strong><br>${partes.join("<br>")}`.replace(/"/g,"&quot;")}" aria-label="${titulo}, ${t}: ${partes.join(", ")}">`+
   `<span class="fo-nombre">${t}</span>${barraFormal(inf,form)}<span class="fo-miles">${enMiles(miles)}</span></div>`}).join("")+`</div>`;
 return `<figure class="graf-fo" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><strong style="color:var(--t1)">Formalidad por nivel de estudios, Chile</strong></span>${leyendaFormal}</figcaption>`+
  `<div class="fo-paneles">${grupos.map(panel).join("")}</div></figure>`+
  `<p class="nota" style="margin:2px 0 8px">% de los ocupados, de los asalariados y de los independientes de cada nivel; a la derecha, cuántos son. `+
  `Todos los ocupados incluye al familiar no remunerado, que no es asalariado ni independiente y siempre es informal.</p>`}
// Formalidad por región: barras formal/informal como las de los niveles, de mayor a menor informalidad, con Chile
// primero y una línea en su informalidad; el % de independientes va como cifra. No se pinta énfasis sobre o bajo Chile:
// no hay margen de error por región y una diferencia de uno o dos puntos puede deberse a la muestra.
function graficoFormalidadRegion(){const c=FOR.chile,tasa=d=>d.inf[1];
 const filas=DATOS.orden.map(r=>[r,FOR.regiones[r]]).sort((a,b)=>tasa(b[1])-tasa(a[1])||a[0]-b[0]);
 const fila=(t,d,clase,attr)=>{const partes=[`informal: ${num(d.inf[0])} (${num(d.inf[1],1)}%)`,`formal: ${num(d.for[0])} (${num(d.for[1],1)}%)`,`independientes: ${num(d.ind[0])} (${num(d.ind[1],1)}%)`],tag=attr?"button":"div";
  return `<${tag} class="fo-fila fo-reg${clase}" ${attr}${attr?"":' role="img" tabindex="0"'} data-tip="${`<strong>${t}</strong><br>${partes.join("<br>")}`.replace(/"/g,"&quot;")}" aria-label="${t}: ${partes.join(", ")}">`+
   `<span class="fo-nombre">${t}</span><span class="fo-ref">${barraFormal(d.inf[1],d.for[1])}<b style="left:${tasa(c)}%"></b></span><span class="fo-miles">${num(d.ind[1],1)}%</span></${tag}>`};
 return `<figure class="graf-fo" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><strong style="color:var(--t1)">Formalidad por región</strong></span>${leyendaFormal}`+
  `<span><span class="ref"></span>Chile: ${num(tasa(c),1)}% informal, ${num(c.for[1],1)}% formal</span></figcaption>`+
  `<div class="fo-fila fo-reg gs-cab" aria-hidden="true"><span class="fo-nombre">Región</span><span>% de los ocupados</span><span class="fo-miles">Indepen&shy;dientes</span></div>`+
  fila("Chile",c," cl-total","")+filas.map(([r,d])=>fila(nomReg(r),d,"",`data-r="${r}"`)).join("")+`</figure>`+
  `<p class="nota" style="margin:2px 0 8px">% de los ocupados de la región, según residencia; a la derecha, el % de independientes, formales e informales. `+
  `Son estimaciones con muestra: una diferencia de uno o dos puntos entre regiones puede deberse a ella.</p>`}
// Formalidad según ENE: dos ejes y no tres grupos, porque un independiente puede ser formal o informal.
function formalidadHtml(){const c=FOR.chile,n=FOR.niveles,[rMin,rMax]=extremos(r=>FOR.regiones[r].inf[1]);
 const celda=v=>`<td class="n">${v?vmil(v):"—"}</td>`;
 // Con cifras completas, la tabla por nivel (7 columnas) no cabía en pantalla: el % va bajo cada cifra.
 const celda2=v=>`<td class="n">${v?`${num(v[0])}<br><span class="pct-bajo">${num(v[1],1)}%</span>`:"—"}</td>`;
 const fila=(t,d,k)=>`<tr class="${k}"><td>${t}</td>${["af","ai","xf","xi","fam","for","inf"].map(x=>celda2(d[x])).join("")}</tr>`;
 const sinFam=NIVELES.filter(([k])=>!n[k].fam).map(([,t])=>t.toLowerCase());
 return `${encabezado("sec-for","Formalidad",`Sin título superior, ${num(n.Sin_titulo.for[1],1)}% tiene empleo formal y ${num(n.Sin_titulo.inf[1],1)}% informal; con título profesional, ${num(n.Profesional.for[1],1)}% y ${num(n.Profesional.inf[1],1)}%`,true)}
 <div class="nota">Encuesta Nacional de Empleo (INE), ${PER.ene_actual}. Ocupados según región de residencia. Son estimaciones con muestra: las cifras tienen margen de error. `+
  `Independiente: empleador o cuenta propia. Asalariado: sector privado, público o servicio doméstico.</div>
 <p style="margin:8px 0 0">En Chile, ${enMiles(c.inf[0])} de ocupados son informales (${num(c.inf[1],1)}%) y ${enMiles(c.for[0])} formales (${num(c.for[1],1)}%). `+
  `Hay ${enMiles(c.asa[0])} de asalariados y ${enMiles(c.inx[0])} de independientes (${num(c.ind[1],1)}% de los ocupados). `+
  `La informalidad va de ${num(rMin[1],1)}% en ${enReg(rMin[0])} a ${num(rMax[1],1)}% en ${enReg(rMax[0])}.</p>
 ${graficoFormalidadNivel()}
 ${graficoFormalidadRegion()}
 <details><summary>Ver cifras</summary>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th rowspan="2">Nivel<br><span class="nota">ocupados (%)</span></th><th colspan="2" class="bloque ini">Asalariado</th><th colspan="2" class="bloque ini">Independiente</th>`+
  `<th rowspan="2" class="n bloque ini">Familiar no remunerado</th><th colspan="2" class="bloque ini">En total</th></tr>`+
  `<tr><th class="n ini">Formal</th><th class="n">Informal</th><th class="n ini">Formal</th><th class="n">Informal</th><th class="n ini">Formal</th><th class="n">Informal</th></tr></thead><tbody>`+
  fila("Chile",c,"total")+NIVELES.map(([k,t])=>fila(t,n[k],"")).join("")+`</tbody></table></div>
 <p class="nota" style="margin:6px 0 0">Ocupados estimados (% de cada fila). Formal e informal en total suman 100; el familiar no remunerado siempre es informal y entra en el informal total.${
  sinFam.length?` En ${sinFam.join(" y ")}, el familiar no remunerado no se muestra (—) porque son menos de 60 personas en la muestra: por eso ahí las cinco primeras columnas no llegan a 100, y el informal total es algo mayor que la suma de asalariado e independiente informal (la diferencia es ese familiar, menos de 0,5%).`:""} Estas diferencias no indican causa: la edad, por ejemplo, también influye.</p>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th rowspan="2">Nivel</th><th colspan="3" class="bloque ini">Asalariados</th><th colspan="3" class="bloque ini">Independientes</th></tr>`+
  `<tr><th class="n ini">Total</th><th class="n">Formal</th><th class="n">Informal</th><th class="n ini">Total</th><th class="n">Formal</th><th class="n">Informal</th></tr></thead><tbody>`+
  // Los ocupados formal e informal son los de la tabla de arriba; el % se calcula dentro del grupo y suma 100.
  [["Chile",c,"total"],...NIVELES.map(([k,t])=>[t,n[k],""])].map(([t,d,k])=>`<tr class="${k}"><td>${t}</td>`+
   [["asa","af","ai"],["inx","xf","xi"]].map(([g,f,i])=>`<td class="n">${num(d[g][0])}</td>${celda2([d[f][0],100-d[g][1]])}${celda2([d[i][0],d[g][1]])}`).join("")+`</tr>`).join("")+`</tbody></table></div>
 <p class="nota" style="margin:6px 0 0">Ocupados estimados (% dentro de cada grupo): formal e informal suman 100 en asalariados y en independientes. Son los mismos ocupados de la tabla de arriba; cambia la base del %, que aquí es el grupo y no todos los ocupados.</p>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th>Región<br><span class="nota">ocupados (%)</span></th><th class="n">Formal</th><th class="n">Informal</th><th class="n">Independientes</th></tr></thead><tbody>`+
  [["Chile",c,"total"],...DATOS.orden.map(r=>[DATOS.regiones[r],FOR.regiones[r],""])].map(([t,d,k])=>
   `<tr class="${k}"><td>${esc(t)}</td>${celda(d.for)}${celda(d.inf)}${celda(d.ind)}</tr>`).join("")+`</tbody></table></div>
 <p class="nota" style="margin:6px 0 0">Ocupados estimados (% de la región); formal e informal suman 100. Por región no se separan las cuatro casillas: en las regiones chicas quedarían con poca muestra.</p></details>`}
// Hombres y mujeres por actividad, en barras que suman 100% ordenadas por % de mujeres: el largo de cada barra es el
// reparto, no el tamaño, para que Comercio no aplaste al resto. Arriba, todas las actividades juntas, que es también
// la línea punteada: se usa la misma base que las barras (7,4 millones), para que la fila de arriba sea su suma.
function graficoSexo(){
 const tot=DATOS.actividades.reduce((s,a)=>({h:s.h+a.sexo.h,m:s.m+a.sexo.m}),{h:0,m:0}),n=tot.h+tot.m;
 const niveles=NIVELES.map((_,i)=>[DATOS.actividades.reduce((t,a)=>t+a.niveles[i][0],0)]);
 const todas={corto:"Todas las actividades",niveles,nacional:{ocupados:n},pct_nacional:100,sexo:{h:tot.h,m:tot.m,pct_h:100*tot.h/n,pct_m:100*tot.m/n}};
 const ch=POB.chile.trabajan,mCh=POB.sexo.mujeres.trabajan;
 // El total va primero en el globo: las dos partes se entienden mejor sabiendo a qué suman.
 const fila=(a,clase,attr)=>{const s=a.sexo,tit=`${num(conTitulo(a.niveles),1)}%`,ocu=vp(a.nacional.ocupados,a.pct_nacional);
  const partes=[`${num(a.nacional.ocupados)} ocupados`,`${num(s.m)} mujeres (${num(s.pct_m,1)}%)`,`${num(s.h)} hombres (${num(s.pct_h,1)}%)`,`${tit} con título técnico o profesional`];
  const etiqueta=`${esc(a.corto)}: ${partes.join(", ")}`,globo=`<strong>${esc(a.corto)}</strong><br>${partes.join("<br>")}`,tag=attr?"button":"div";
  return `<${tag} class="gs-fila${clase}" ${attr} data-tip="${globo.replace(/"/g,"&quot;")}" aria-label="${etiqueta}"${attr?"":' role="img" tabindex="0"'}><span class="gs-nombre">${esc(a.corto)}</span>`+
   `<span class="gs-pct">${num(s.pct_m,1)}%</span><span class="gs-barra" aria-hidden="true"><i class="m" style="flex:${s.pct_m} 0 0"></i><i class="h" style="flex:${s.pct_h} 0 0"></i>`+
   `<b style="left:${todas.sexo.pct_m}%"></b></span><span class="gs-pct h">${num(s.pct_h,1)}%</span>`+
   // En celular las dos cifras bajan a una línea propia y llevan su rótulo, porque ahí no se ve el encabezado.
   `<span class="gs-extra"><span class="gs-num gs-tit"><span class="gs-et">Con título </span>${tit}</span><span class="gs-num"><span class="gs-et">Ocupados </span>${ocu}</span></span></${tag}>`};
 return `<figure class="graf-sexo" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><i style="background:var(--muj)"></i>Mujeres</span>`+
  `<span><i style="background:var(--hom)"></i>Hombres</span><span><span class="ref"></span>Todas las actividades</span></figcaption>`+
  `<div class="gs-fila gs-cab" aria-hidden="true"><span class="gs-nombre">Actividad</span><span></span><span></span><span></span>`+
  `<span class="gs-extra"><span class="gs-num gs-tit">Con título técnico o profesional</span><span class="gs-num">Ocupados (participación)</span></span></div>`+
  fila(todas," gs-total","")+[...DATOS.actividades].sort((a,b)=>b.sexo.pct_m-a.sexo.pct_m).map(a=>fila(a,"",`data-a="${a.ciiu}"`)).join("")+`</figure>`+
  `<p class="nota" style="margin:2px 0 8px">Mujeres y hombres: % sobre los ocupados de cada actividad, según lugar de trabajo; con todos los ocupados, incluidos ${num(ch-n)} sin región de trabajo o actividad, `+
  `${num(100*mCh/ch,1)}% son mujeres. Con título: % de los ocupados con nivel informado (el ${num(EST.pct_con_titulo,1)}% de los hallazgos cuenta por residencia).</p>`}
// Barras horizontales: lo que se lee es cada actividad con su región y su CL, no cuántas caen en un tramo.
function graficoCL(){
 const filas=DATOS.actividades.map(a=>({a,r:a.nacional.mas_peso.r,v:a.regiones[a.nacional.mas_peso.r]})).sort((x,y)=>y.v.peso-x.v.peso);
 // Escala desde 0 hasta el entero sobre el mayor CL: una barra desde 0 no exagera las diferencias.
 const tope=Math.ceil(filas[0].v.peso),pos=x=>100*x/tope;
 return `<figure class="graf-cl" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><strong style="color:var(--t1)">Región donde más pesa cada actividad</strong></span>`+
  `<span><span class="ref"></span>CL 1: pesa lo mismo que en Chile</span></figcaption>`+
  // Fila de referencia: en Chile toda actividad tiene CL 1, porque Chile es la base con que se compara cada región.
  `<div class="cl-fila cl-total" role="img" tabindex="0" aria-label="Chile: CL 1 en todas las actividades, es la base de comparación" `+
  `data-tip="<strong>Chile</strong><br>CL 1 en todas las actividades:<br>es la base con que se compara cada región"><span class="cl-nombre">Chile <span class="cl-reg">· todas las actividades</span></span>`+
  `<span class="cl-barra" aria-hidden="true"><i style="width:${pos(1)}%"></i><b style="left:${pos(1)}%"></b><span class="cl-valor" style="left:calc(${pos(1)}% + 6px)">1,00</span></span></div>`+
  filas.map(({a,r,v})=>{const partes=[`${nomReg(r)}: CL ${v.peso_txt}`,`pesa ${v.peso_txt} veces su peso en Chile`,`${num(v.ocupados)} ocupados (${part(v.pct)} de los ocupados de la región)`];
   // El símbolo solo no se lee en voz alta: el aviso va también en palabras en el globo y la descripción.
   if(a.alerta_fuente)partes.push("⚠ Censo y ENE difieren en el tamaño de esta actividad");
   return `<button class="cl-fila" data-a="${a.ciiu}" data-tip="${`<strong>${esc(a.corto)}</strong><br>${partes.join("<br>")}`.replace(/"/g,"&quot;")}" aria-label="${esc(a.corto)}, ${partes.join(", ")}">`+
    `<span class="cl-nombre">${esc(a.corto)}${a.alerta_fuente?' <span class="cl-alerta">⚠</span>':""} <span class="cl-reg">· ${nomReg(r)}</span></span>`+
    `<span class="cl-barra" aria-hidden="true"><i style="width:${pos(v.peso)}%"></i><b style="left:${pos(1)}%"></b>`+
    // La cifra va pegada al extremo de su barra: en una columna aparte quedaba lejos de las barras cortas.
    `<span class="cl-valor" style="left:calc(${pos(v.peso)}% + 6px)">${v.peso_txt}</span></span></button>`}).join("")+
  `</figure><p class="nota" style="margin:2px 0 8px">CL: cuántas veces pesa la actividad en la región respecto de su peso en Chile, según lugar de trabajo. `+
  `Un CL alto en una región pequeña puede corresponder a pocos ocupados: sus cifras se ven al pasar el mouse. ⚠ Censo y ENE difieren en el tamaño de esta actividad.</p>`}
// Trabajo por región, 1: una barra 100% por región con el mismo formato y colores que "Situación laboral por nivel de
// estudios", para que la población se lea igual en ambas secciones. Incluye el tramo sin dato, porque los % de la tabla
// se calculan sobre toda la población de 15 años o más. Va de mayor a menor desocupación, como dice el título, y las
// tasas van escritas al lado: el tramo de desocupados (4% a 6%) es delgado y su largo solo no basta para comparar.
function graficoSituacionRegion(){const ch=POB.chile,tasa=d=>d.tasa_desocupacion;
 const partes=[["trabajan","Ocupados","s-trabajan"],["buscan","Desocupados","s-buscan"],["no_buscan","Fuera de la fuerza de trabajo","s-no-buscan"],["sin_dato","Sin dato","s-sin-dato"]];
 const filas=DATOS.orden.map(r=>[r,POB.regiones[r]]).sort((a,b)=>tasa(b[1])-tasa(a[1])||a[0]-b[0]);
 const fila=(t,x,clase,attr)=>{const pc=v=>100*v/x.total,tag=attr?"button":"div";
  const texto=[`${num(x.total)} personas de 15 años o más`,...partes.map(([c,n])=>`${n.toLowerCase()} ${num(x[c])} (${num(pc(x[c]),1)}%)`)];
  const tasas=`desocupación ${num(tasa(x),1)}%, participación ${num(x.tasa_participacion,1)}%`;
  return `<${tag} class="sn-fila${clase}" ${attr}${attr?"":' role="img" tabindex="0"'} aria-label="${t}: ${texto.join(", ")}; ${tasas}" data-tip="${`<strong>${t}</strong><br>${texto.join("<br>")}`.replace(/"/g,"&quot;")}">`+
   `<span class="sn-nombre">${t}</span><span class="sn-barra" aria-hidden="true">${partes.map(([c,,k])=>`<i class="${k}" style="flex:${x[c]} 0 0">${pc(x[c])>=9?`${num(pc(x[c]),0)}%`:""}</i>`).join("")}</span>`+
   `<span class="sn-tasas">Desocupación <b>${num(tasa(x),1)}%</b> · participación <b>${num(x.tasa_participacion,1)}%</b></span></${tag}>`};
 return `<figure class="graf-sn" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><strong style="color:var(--t1)">Situación laboral por región</strong></span>`+
  partes.map(([,n,k])=>`<span><i class="${k}"></i>${n}</span>`).join("")+`</figcaption>`+
  fila("Chile",ch," sn-total","")+filas.map(([r,x])=>fila(nomReg(r),x," sn-region",`data-r="${r}"`)).join("")+`</figure>`+
  `<p class="nota" style="margin:2px 0 8px">% de la población de 15 años o más de cada región, según residencia. Junto a cada barra, las tasas: `+
  `desocupación sobre la fuerza de trabajo (ocupados y desocupados) y participación sobre la población.</p>`}
// Trabajo por región, 2: cuántos trabajan en la región por cada uno que vive en ella, frente a Chile. Se compara con
// Chile y no se resta directo porque 5,8% de los ocupados no tiene región de trabajo: con la resta, toda región parecería
// entregar trabajadores. Supone que esa falta de dato pesa igual en cada región. Barras desde un centro (igual que
// Chile) con dos colores, uno por sentido. La escala es la misma a ambos lados, para no agrandar las diferencias chicas,
// y el centro se corre a la izquierda porque ninguna región baja de −10%: así el espacio va a las barras.
function graficoTraslado(){const ch=POB.chile,base=ch.lugar_trabajo/ch.trabajan,dif=x=>100*(x.lugar_trabajo/x.trabajan/base-1);
 const filas=DATOS.orden.map(r=>[r,POB.regiones[r],dif(POB.regiones[r])]).sort((a,b)=>b[2]-a[2]||a[0]-b[0]);
 const lo=Math.min(0,Math.floor(filas[filas.length-1][2]/10)*10),hi=Math.max(0,Math.ceil(filas[0][2]/10)*10),cero=100*-lo/(hi-lo),ancho=v=>100*Math.abs(v)/(hi-lo);
 // El signo sale de la cifra publicada: Maule (−0,04) se lee 0,0%, no −0,0%.
 const fila=([r,x,v])=>{const r1=Math.round(10*v)/10,txt=`${r1>0?"+":r1<0?"−":""}${num(Math.abs(r1),1)}%`,t=nomReg(r);
  const partes=[`${num(x.lugar_trabajo)} ocupados trabajan en la región`,`${num(x.trabajan)} ocupados viven en ella`,`${txt} frente a Chile`];
  return `<button class="cl-fila tr-fila" data-r="${r}" data-tip="${`<strong>${t}</strong><br>${partes.join("<br>")}`.replace(/"/g,"&quot;")}" aria-label="${t}: ${partes.join(", ")}">`+
   `<span class="cl-nombre">${t}</span><span class="tr-barra" aria-hidden="true"><b style="left:${cero}%"></b>`+
   (v>=0?`<i class="recibe" style="left:${cero}%;width:${ancho(v)}%"></i><span class="cl-valor" style="left:calc(${cero+ancho(v)}% + 6px)">${txt}</span>`
        :`<i class="entrega" style="right:${100-cero}%;width:${ancho(v)}%"></i><span class="cl-valor" style="right:calc(${100-cero+ancho(v)}% + 6px)">${txt}</span>`)+`</span></button>`};
 return `<figure class="graf-cl" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><strong style="color:var(--t1)">Dónde trabajan los ocupados de cada región</strong></span>`+
  `<span><i class="entrega"></i>Sus ocupados trabajan en otras regiones</span><span><i class="recibe"></i>Recibe ocupados de otras regiones</span></figcaption>`+
  filas.map(fila).join("")+`</figure>`+
  `<p class="nota" style="margin:2px 0 8px">Ocupados que trabajan en la región por cada uno que vive en ella, comparado con Chile (0 = igual que Chile). `+
  `Se compara con Chile porque ${num(100*(1-base),1)}% de los ocupados no tiene región de trabajo informada.</p>`}
// Educación por región: barras apiladas solo con la parte titulada (profesional abajo, técnico encima), de mayor a menor
// % con título, con "sin título superior" como cifra a la derecha para que los tres niveles sumen 100 a la vista.
// Se descartaron las barras 100%: sin título ocupa 67% a 79% de cada barra y la diferencia entre regiones (12 puntos)
// quedaba apretada en un costado. El profesional va primero porque solo el primer tramo comparte la base: es donde
// está casi toda la diferencia (13,4% a 23,1%); el técnico varía poco (7,3% a 12,3%).
function graficoEducacion(){const ch=EDU.chile,tope=Math.ceil(Math.max(...DATOS.orden.map(r=>pctTitulo(EDU[r])))/5)*5,pos=x=>100*x/tope;
 const filas=DATOS.orden.map(r=>[r,EDU[r]]).sort((a,b)=>pctTitulo(b[1])-pctTitulo(a[1])||a[0]-b[0]);
 const fila=(t,v,clase,attr)=>{const tot=v[0]+v[1]+v[2],pc=x=>100*x/tot,tag=attr?"button":"div";
  const partes=[`${num(pctTitulo(v),1)}% con título técnico o profesional`,...NIVELES.map(([,n],i)=>`${n.toLowerCase()}: ${num(v[i])} (${num(pc(v[i]),1)}%)`)];
  return `<${tag} class="cl-fila ed-fila${clase}" ${attr}${attr?"":' role="img" tabindex="0"'} data-tip="${`<strong>${t}</strong><br>${partes.join("<br>")}`.replace(/"/g,"&quot;")}" aria-label="${t}: ${partes.join(", ")}">`+
   `<span class="cl-nombre">${t}</span><span class="cl-barra ed-barra" aria-hidden="true"><i class="ed-pro" style="width:${pos(pc(v[0]))}%"></i>`+
   `<i class="ed-tec" style="left:calc(${pos(pc(v[0]))}% + 2px);width:calc(${pos(pc(v[1]))}% - 2px)"></i><b style="left:${pos(pctTitulo(ch))}%"></b>`+
   `<span class="cl-valor" style="left:calc(${pos(pctTitulo(v))}% + 6px)">${num(pctTitulo(v),1)}%</span></span><span class="gs-num">${num(pc(v[2]),1)}%</span></${tag}>`};
 return `<figure class="graf-cl" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><strong style="color:var(--t1)">Población con título técnico o profesional</strong></span>`+
  `<span><i class="ed-pro"></i>Profesional</span><span><i class="ed-tec"></i>Técnico</span><span><span class="ref"></span>Chile (${num(pctTitulo(ch),1)}%)</span></figcaption>`+
  `<div class="cl-fila ed-fila gs-cab" aria-hidden="true"><span class="cl-nombre">Región</span><span>% con título técnico o profesional</span><span class="gs-num">Sin título superior</span></div>`+
  fila("Chile",ch," cl-total","")+filas.map(([r,v])=>fila(nomReg(r),v,"",`data-r="${r}"`)).join("")+`</figure>`+
  `<p class="nota" style="margin:2px 0 8px">% de la población de 15 años o más con nivel informado, según residencia. Al final de cada barra, profesional y técnico juntos; a la derecha, el resto, sin título superior.</p>`}
// Estudios y trabajo, Chile: una barra 100% por nivel (ocupados, desocupados y fuera de la fuerza de trabajo) con los
// colores de la barra de Población, para comparar los tres repartos sobre un mismo eje. Se descartaron tres gráficos de
// pastel: los ángulos se comparan mal entre pasteles y la tajada de desocupados (5% en los tres) se vería igual.
function barrasNivel(){const partes=[["ocupados","Ocupados","s-trabajan"],["desocupados","Desocupados","s-buscan"],["fuera","Fuera de la fuerza de trabajo","s-no-buscan"]];
 const fila=([k,t])=>{const x=EST.niveles[k],tot=x.ocupados+x.desocupados+x.fuera,pc=v=>100*v/tot;
  const texto=partes.map(([c,n])=>`${n.toLowerCase()} ${num(x[c])} (${num(pc(x[c]),1)}%)`),tasas=`desocupación ${num(x.tasa_desocupacion,1)}%, participación ${num(x.tasa_participacion,1)}%`;
  return `<div class="sn-fila" role="img" tabindex="0" aria-label="${t}: ${texto.join(", ")}; ${tasas}" data-tip="${`<strong>${t}</strong><br>${texto.join("<br>")}`.replace(/"/g,"&quot;")}">`+
   `<span class="sn-nombre">${t}</span><span class="sn-barra" aria-hidden="true">${partes.map(([c,,k])=>`<i class="${k}" style="flex:${x[c]} 0 0">${pc(x[c])>=9?`${num(pc(x[c]),0)}%`:""}</i>`).join("")}</span>`+
   `<span class="sn-tasas">Desocupación <b>${num(x.tasa_desocupacion,1)}%</b> · participación <b>${num(x.tasa_participacion,1)}%</b></span></div>`};
 return `<figure class="graf-sn" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><strong style="color:var(--t1)">Situación laboral por nivel de estudios, Chile</strong></span>`+
  partes.map(([,n,k])=>`<span><i class="${k}"></i>${n}</span>`).join("")+`</figcaption>`+NIVELES.map(fila).join("")+`</figure>`+
  `<p class="nota" style="margin:2px 0 8px">% de la población de 15 años o más de cada nivel. Junto a cada barra, las tasas: desocupación sobre la fuerza de trabajo (ocupados y desocupados) y participación sobre la población.</p>`}
// Columnas agrupadas por región, con y sin título, en el mismo formato que Cambio 2024–2026: escala desde 0, nombres a 45°
// y desplazamiento lateral en pantallas angostas. Bajo cada región va solo la diferencia; las dos tasas están en el globo
// y en "Ver cifras". Se descartó el dumbbell: dos puntos sobre una línea se leían peor que el largo de una barra.
function columnasTitulo(){const filas=Object.entries(EST.desocupacion_titulo).sort((a,b)=>(b[1][1]-b[1][0])-(a[1][1]-a[1][0])||a[0]-b[0]);
 const todos=[EST.desocupacion_titulo_chile,...filas.map(([,v])=>v)].flat(),tope=Math.ceil(Math.max(...todos)/4)*4,pos=x=>100*x/tope;
 const marcas=Array.from({length:tope/4+1},(_,k)=>4*k);
 const grupo=(t,[c,sn],clase,attr)=>{const partes=[`${num(c,1)}% con título técnico o profesional`,`${num(sn,1)}% sin título superior`,`diferencia ${num(sn-c,1)} pp`];
  const tag=attr?"button":"div";
  return `<${tag} class="evc-grupo${clase}" ${attr}${attr?"":' role="img" tabindex="0"'} data-tip="${`<strong>${t}</strong><br>${partes.join("<br>")}`.replace(/"/g,"&quot;")}" aria-label="${t}: ${partes.join(", ")}">`+
   `<span class="evc-cols" aria-hidden="true"><span class="evc-col tcon" style="height:${pos(c)}%"></span><span class="evc-col tsin" style="height:${pos(sn)}%"></span></span>`+
   `<span class="evc-nombre"><span>${t}</span></span><span class="evc-dif">+${num(sn-c,1)}</span></${tag}>`};
 return `<figure class="graf-ev" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><strong style="color:var(--t1)">Tasa de desocupación por región</strong></span>`+
  `<span><i class="tcon"></i>Con título técnico o profesional</span><span><i class="tsin"></i>Sin título superior</span></figcaption>`+
  `<div class="evc-desliza"><div class="evc compacto"><div class="evc-rotulos" aria-hidden="true"><span>Diferencia</span></div>`+
  `<div class="evc-grilla" aria-hidden="true">${marcas.map(m=>`<span style="bottom:${pos(m)}%"><small>${m}%</small></span>`).join("")}</div>`+
  grupo("Chile",EST.desocupacion_titulo_chile," evc-total","")+filas.map(([r,v])=>grupo(nomReg(r),v,"",`data-r="${r}"`)).join("")+`</div></div></figure>`+
  `<p class="nota" style="margin:2px 0 0">Bajo cada región, la diferencia en pp (sin título menos con título). Tasa según región de residencia.</p>`}
// Tabla gemela de los dos gráficos: todas las cifras, para quien no ve el gráfico o quiere el detalle sin pasar el mouse.
function tablaEstudios(){const filas=Object.entries(EST.desocupacion_titulo).sort((a,b)=>(b[1][1]-b[1][0])-(a[1][1]-a[1][0])||a[0]-b[0]);
 const tr=(t,[c,sn],k)=>`<tr class="${k}"><td>${t}</td><td class="n">${num(c,1)}%</td><td class="n">${num(sn,1)}%</td><td class="n">+${num(sn-c,1)} pp</td></tr>`;
 return `<details><summary>Ver cifras</summary>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th>Nivel</th><th class="n">Ocupados</th><th class="n">Desocupados</th><th class="n">Fuera de la fuerza de trabajo</th>`+
  `<th class="n">Tasa de desocupación</th><th class="n">Tasa de participación</th></tr></thead><tbody>${NIVELES.map(([k,t])=>{const x=EST.niveles[k];
   return `<tr><td>${t}</td><td class="n">${num(x.ocupados)} (${num(x.pct,1)}%)</td><td class="n">${num(x.desocupados)}</td><td class="n">${num(x.fuera)}</td>`+
    `<td class="n">${num(x.tasa_desocupacion,1)}%</td><td class="n">${num(x.tasa_participacion,1)}%</td></tr>`}).join("")}</tbody></table></div>
 <p class="nota" style="margin:4px 0 0">Ocupados: entre paréntesis, % del total de ocupados con nivel informado.</p>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th>Región</th><th class="n">Con título técnico o profesional</th><th class="n">Sin título superior</th><th class="n">Diferencia</th></tr></thead><tbody>`+
  tr("Chile",EST.desocupacion_titulo_chile,"total")+filas.map(([r,v])=>tr(nomReg(r),v,"")).join("")+`</tbody></table></div>
 <p class="nota" style="margin:4px 0 0">Tasa de desocupación según región de residencia.</p></details>`}
function vistaResumen(){
 const ch=POB.chile,sH=POB.sexo.hombres,sM=POB.sexo.mujeres;
 const sinRegion=DATOS.actividades.filter(a=>a.pct_sin_region>=10).sort((a,b)=>b.pct_sin_region-a.pct_sin_region);
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
  `Suman ${num(RES.total)} de ${num(ch.trabajan)}: se excluyen ${num(ch.trabajan-RES.total)} sin región de trabajo o actividad, o en organismos internacionales.</div>
 ${graficoSexo()}
 <p class="invita"><strong>Elige una actividad</strong> para ver en qué regiones se concentra y sus carreras afines, con títulos, empleabilidad e ingresos. `+
  `Con más carreras afines: ${conMasCarreras.map(a=>`<button class="enlace" data-a="${a.ciiu}">${esc(a.corto)}</button> (${a.afines.length})`).join(" &nbsp;·&nbsp; ")}.</p>
 ${graficoCL()}
 ${sinRegion.length?`<p class="nota" style="margin:4px 0 0">Subestimadas por ocupados sin región de trabajo `+
  `(${num(sinRegion[sinRegion.length-1].pct_sin_region,1)}% a ${num(sinRegion[0].pct_sin_region,1)}%): ${lista(sinRegion.map(a=>esc(a.corto)))}.</p>`:""}
 ${encabezado("sec-lab","Trabajo por región",`La desocupación va de ${num(desMin[1],1)}% en ${enReg(desMin[0])} a ${num(desMax[1],1)}% en ${enReg(desMax[0])}`)}
 ${graficoSituacionRegion()}
 ${graficoTraslado()}
 <details><summary>Ver cifras</summary>
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
  `</tbody></table></div></details>
 <div class="aviso">La tasa depende de la edad de la población de cada región: por sí sola no basta para comparar el empleo.</div>
 ${encabezado("sec-edu","Educación por región",`Con título técnico o profesional: de ${num(titMin[1],1)}% en ${enReg(titMin[0])} a ${num(titMax[1],1)}% en ${enReg(titMax[0])}`)}
 ${graficoEducacion()}
 <details><summary>Ver cifras</summary>
 <div class="nota">Población de 15 años o más, según región de residencia, con nivel de estudios y situación laboral informados. `+
  `Se excluyen ${num(EST.excluidos.sin_nivel)} sin nivel informado y ${num(EST.excluidos.sin_situacion)} sin situación laboral. Entre paréntesis, % de esa población.</div>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th>Región</th><th class="n">Con nivel informado</th>${NIVELES.map(([,t])=>`<th class="n">${t}</th>`).join("")}`+
  `<th class="n">Con título técnico o profesional</th></tr></thead><tbody>`+
  [["Chile",EDU.chile,"total"],...DATOS.orden.map(r=>[DATOS.regiones[r],EDU[r],""])].map(([t,v,k])=>{const tot=v[0]+v[1]+v[2];
   return `<tr class="${k}"><td>${esc(t)}</td><td class="n">${num(tot)}</td>${v.map(x=>`<td class="n">${num(x)} (${num(100*x/tot,1)}%)</td>`).join("")}`+
    `<td class="n">${num(pctTitulo(v),1)}%</td></tr>`}).join("")+`</tbody></table></div></details>
 <div class="aviso">Incluye a jóvenes que aún estudian: el % con título depende de la edad de la población de cada región.</div>
 ${encabezado("sec-est","Estudios y trabajo",`${e.menor===e.n?`En las ${e.n} regiones`:`En ${e.menor} de ${e.n} regiones`}, menos desocupación con título técnico o profesional`)}
 <div class="nota">Chile, Censo 2024. Según residencia, con nivel de estudios informado: ${num(EST.total)} ocupados.</div>
 <p style="margin:8px 0 0">${desocTitulo()}</p>
 <p style="margin:8px 0 0">Tienen título técnico o profesional ${num(EST.pct_con_titulo,1)}% de los ocupados: ${num(EST.sexo.mujeres,1)}% de las mujeres y ${num(EST.sexo.hombres,1)}% de los hombres.</p>
 ${barrasNivel()}
 ${columnasTitulo()}
 ${tablaEstudios()}
 <p class="nota" style="margin:6px 0 0">Estas diferencias no indican causa: la edad de cada grupo, por ejemplo, también influye.</p>
 <hr class="separador">${banda("Encuesta Nacional de Empleo (INE)")}
 ${formalidadHtml()}
 ${evolucionHtml()}`}
