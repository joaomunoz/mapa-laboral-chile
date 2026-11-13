/*
<src/Visualizacion/web/js/vistas/resumen.js>

Vista inicial: Chile y todas las actividades.
*/
// Relación entre las dos realidades, región por región: se escribe desde los datos para no afirmar más de lo que muestran.
function extremosDesoc(){const d=Object.entries(EST.desocupacion_titulo),menor=d.filter(([,v])=>v[0]<v[1]).length;
 // Un rango por grupo, cada uno con sus extremos: con un solo rango (por la tasa con título), Biobío parecía la región
 // con más desocupación sin título, que es La Araucanía, y cuatro cifras en una línea no se leían a simple vista.
 const rango=i=>{const [a,va]=d.reduce((m,x)=>x[1][i]<m[1][i]?x:m),[b,vb]=d.reduce((m,x)=>x[1][i]>m[1][i]?x:m);
  return `de ${num(va[i],1)}% en ${enReg(Number(a))} a ${num(vb[i],1)}% en ${enReg(Number(b))}`};
 return {menor,n:d.length,con:rango(0),sin:rango(1)}}
// En pantallas angostas las columnas por región se desplazan hacia el lado; sin aviso, parecía que el gráfico terminaba
// en la región cortada. Va oculto y se muestra solo si el gráfico no cabe (avisoDesliza, en navegacion.js).
const AVISO_DESLIZA=`<p class="nota evc-aviso" hidden>Desliza el gráfico hacia el lado para ver las 16 regiones.</p>`;
// El título de la sección ya dice en cuántas regiones es menor: el párrafo da solo los dos rangos.
function desocTitulo(){const e=extremosDesoc();
 return `Con título técnico o profesional, la tasa de desocupación va ${e.con}; sin título superior, ${e.sin}.`}
// La ventaja del título a igual edad (Censo 2024): sin esto, la diferencia podría venir de que los sin título son más
// jóvenes. Se compara de 25 a 64; de 15 a 24 es al revés y se dice, para que no se generalice. La tarjeta usa edadIgual().
const edadIgual=()=>{const d=EST.edad;return `No la explica la edad: se mantiene en cada tramo de 25 a 64 años, en ${d.regiones_igual_edad===16?"las 16 regiones":`${d.regiones_igual_edad} de 16 regiones`}`};
function edadDesoc(){const d=EST.edad,c=d.chile,f=t=>`${num(c[t][0],1)}% con título y ${num(c[t][1],1)}% sin título`;
 return `${edadIgual()}. En Chile, de 25 a 34 años, ${f("25-34")}; de 55 a 64, ${f("55-64")}. `+
  `De 15 a 24 es al revés (${f("15-24")}), pero a esa edad están solo el ${num(d.pct_jovenes_con,0)}% de los activos con título.`}
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
  `${compacto?AVISO_DESLIZA:""}<div class="${compacto?"evc-desliza":""}"><div class="evc${compacto?" compacto":""}">`+
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
 ["CASEN 2024",[["sec-area","Área de estudio por actividad"]]],
 ["Encuesta Nacional de Empleo",[["sec-for","Formalidad"],["sec-evo","Cambio 2024–2026"]]]];
const indiceHtml=()=>`<nav class="indice" aria-label="Secciones del resumen">${SECCIONES.map(([f,s])=>
 `<span class="indice-grupo"><span class="indice-fuente">${f}</span>${s.map(([id,t])=>`<button data-ir="${id}">${t}</button>`).join("")}</span>`).join("")}</nav>`;
const encabezado=(id,tema,titulo,primero)=>`${primero?"":'<hr class="separador">'}<div class="sec-cab" id="${id}" tabindex="-1"><p class="tema">${tema}</p><h2>${titulo}</h2></div>`;
const banda=t=>`<p class="banda">${t}</p>`;
// Región con el menor y el mayor valor: los títulos lo escriben desde los datos para no afirmar más de lo que muestran.
function extremos(valor){const r=DATOS.orden.map(k=>[k,valor(k)]).sort((a,b)=>a[1]-b[1]);return [r[0],r[r.length-1]]}
// "en la Metropolitana": el nombre corto de la región no lleva artículo.
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
  `Todos los ocupados incluye al familiar no remunerado, que no es asalariado ni independiente y siempre es informal. `+
  // Las definiciones van junto al gráfico que las usa: antes estaban en la nota de arriba y alejaban el gráfico del título.
  `Asalariado: sector privado, público o servicio doméstico. Independiente: empleador o cuenta propia.</p>`}
// Formalidad por región: barras formal/informal como las de los niveles, de mayor a menor informalidad, con Chile
// primero y una línea en su informalidad; el % de independientes va como cifra. Cada región lleva su ± (95%): se marca
// "sobre Chile" o "bajo Chile" solo si todo su rango queda a ese lado, porque una diferencia de uno o dos puntos puede
// ser de la muestra. La marca va en palabras y no en color: el ocre y el azul ya dicen informal y formal.
const ladoChile=d=>{const c=FOR.chile.inf[1];return d.inf[1]-d.mas>c?"sobre":d.inf[1]+d.mas<c?"bajo":null};
// Grupos de la frase: los más altos son los que no se distinguen de la región más informal (sus rangos se cruzan), y los
// más bajos, los que quedan bajo Chile con todo su rango. Así la frase no elige una "mayor" que la muestra no separa.
function gruposRegion(){const r=Object.entries(FOR.regiones).sort((a,b)=>b[1].inf[1]-a[1].inf[1]),[,top]=r[0];
 return {alto:r.filter(([,d])=>d.inf[1]+d.mas>=top.inf[1]-top.mas).map(([k])=>k),bajo:r.filter(([,d])=>ladoChile(d)==="bajo").reverse().map(([k])=>k)}}
function graficoFormalidadRegion(){const c=FOR.chile,tasa=d=>d.inf[1];
 const filas=DATOS.orden.map(r=>[r,FOR.regiones[r]]).sort((a,b)=>tasa(b[1])-tasa(a[1])||a[0]-b[0]);
 const fila=(t,d,clase,attr)=>{const lado=attr?ladoChile(d):null,tag=attr?"button":"div";
  const partes=[`informal: ${num(d.inf[0])} (${num(d.inf[1],1)}%)`,`formal: ${num(d.for[0])} (${num(d.for[1],1)}%)`,`independientes: ${num(d.ind[0])} (${num(d.ind[1],1)}%)`];
  if(attr)partes.push(`Margen de error: ± ${num(d.mas,1)} puntos (95%)`,lado?`Informalidad ${lado} la de Chile con todo su rango`:"No se distingue de Chile con su margen");
  return `<${tag} class="fo-fila fo-reg${clase}" ${attr}${attr?"":' role="img" tabindex="0"'} data-tip="${`<strong>${t}</strong><br>${partes.join("<br>")}`.replace(/"/g,"&quot;")}" aria-label="${t}: ${partes.join(", ")}">`+
   `<span class="fo-nombre">${t}${lado?` <span class="cl-reg">· ${lado} Chile</span>`:""}</span><span class="fo-ref">${barraFormal(d.inf[1],d.for[1])}<b style="left:${tasa(c)}%"></b></span><span class="fo-miles">${num(d.ind[1],1)}%</span></${tag}>`};
 return `<figure class="graf-fo" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><strong style="color:var(--t1)">Formalidad por región</strong></span>${leyendaFormal}`+
  `<span><span class="ref"></span>Chile: ${num(tasa(c),1)}% informal, ${num(c.for[1],1)}% formal</span></figcaption>`+
  `<div class="fo-fila fo-reg gs-cab" aria-hidden="true"><span class="fo-nombre">Región</span><span>% de los ocupados</span><span class="fo-miles">Indepen&shy;dientes</span></div>`+
  fila("Chile",c," cl-total","")+filas.map(([r,d])=>fila(nomReg(r),d,"",`data-r="${r}"`)).join("")+`</figure>`+
  `<p class="nota" style="margin:2px 0 8px">% de los ocupados de la región, según residencia; a la derecha, el % de independientes, formales e informales. `+
  `Son estimaciones con muestra: "sobre Chile" o "bajo Chile" marca las regiones cuya informalidad queda a ese lado con todo su margen de error (95%), que aparece al pasar el mouse; `+
  `sin marca, la diferencia con Chile puede deberse a la muestra.</p>`}
// Formalidad por actividad: como el gráfico de sexo por actividad, una barra que suma 100% por actividad, de más a menos
// formal, con Chile arriba y su línea; a la derecha, cuántos son, para que Comercio (1,7 millones) no se lea igual que
// Artes. Entran las 20: las más formales tienen tan pocos informales que esa cifra chica no es fiable y se marca, pero la
// barra sí lo es (el ± en puntos es el mismo para formal e informal). Ocre y azul como el resto de la sección.
const ETQ_FIAB={poco_fiable:"poco fiable",no_fiable:"no fiable"};
function actividadesFormalidad(){return Object.entries(FOR.actividades).map(([k,d])=>[porCiiu(k),d]).sort((a,b)=>a[1].inf[1]-b[1].inf[1]||a[0].ciiu.localeCompare(b[0].ciiu))}
// Lo que se ve en el gráfico por actividad, para su título y el párrafo: las que superan 93% formal (es un grupo y no
// una "más formal": Minería, Finanzas y Electricidad se cruzan con su margen) y la más informal, que sí se separa.
function fraseActividad(){const f=actividadesFormalidad(),alto=f.filter(([,d])=>d.for[1]>93),[ai,di]=f[f.length-1];
 return `el empleo formal supera 93% en ${lista(alto.map(([a])=>esc(a.corto)))}; en ${esc(ai.corto)}, ${num(di.inf[1],1)}% es informal`}
// Ser independiente no implica ser informal: dos actividades con el mismo % de independientes (36%) y muy distinta
// informalidad dentro de ellos. Un control verifica que sus rangos de independientes se cruzan y los de informal no.
function fraseIndependientes(){const m=FOR.actividades.M,g=FOR.actividades.G,p=porCiiu("M").corto,c=porCiiu("G").corto;
 return `Ser independiente no implica ser informal: en ${esc(p)} hay tantos independientes como en ${esc(c)} (${num(m.ind[1],1)}% y ${num(g.ind[1],1)}%), `+
  `pero ${num(m.xi[0],1)}% de ellos es informal, frente a ${num(g.xi[0],1)}% en ${esc(c)}.`}
function graficoFormalidadActividad(){const c=FOR.chile,filas=actividadesFormalidad();
 const fila=(t,d,clase,attr)=>{const e=ETQ_FIAB[d.fiab],tag=attr?"button":"div";
  const partes=[`${num(d.ocup)} ocupados`,`formal: ${num(d.for[0])} (${num(d.for[1],1)}%)`,`informal: ${num(d.inf[0])} (${num(d.inf[1],1)}%)${e?`, ${e}`:""}`];
  if(d.mas!=null)partes.push(`Margen de error: ± ${num(d.mas,1)} puntos (95%)`);
  return `<${tag} class="fo-fila fo-reg${clase}" ${attr}${attr?"":' role="img" tabindex="0"'} data-tip="${`<strong>${esc(t)}</strong><br>${partes.join("<br>")}`.replace(/"/g,"&quot;")}" aria-label="${esc(t)}: ${partes.join(", ")}">`+
   `<span class="fo-nombre">${esc(t)}${e?` <span class="cl-reg">· informal ${e}</span>`:""}</span><span class="fo-ref">${barraFormal(d.inf[1],d.for[1])}<b style="left:${c.inf[1]}%"></b></span><span class="fo-miles">${num(d.ocup)}</span></${tag}>`};
 const suma=filas.reduce((s,[,d])=>s+d.ocup,0);
 return `<figure class="graf-fo" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><strong style="color:var(--t1)">Formalidad por actividad: ${fraseActividad()}</strong></span>${leyendaFormal}`+
  `<span><span class="ref"></span>Chile: ${num(c.inf[1],1)}% informal, ${num(c.for[1],1)}% formal</span></figcaption>`+
  `<div class="fo-fila fo-reg gs-cab" aria-hidden="true"><span class="fo-nombre">Actividad</span><span>% de los ocupados</span><span class="fo-miles">Ocupados</span></div>`+
  fila("Chile",c," cl-total","")+filas.map(([a,d])=>fila(a.corto,d,"",`data-a="${a.ciiu}"`)).join("")+`</figure>`+
  `<p class="nota" style="margin:2px 0 8px">% de los ocupados de cada actividad; a la derecha, cuántos son. Las actividades suman ${num(suma)} de ${num(c.ocup)}: `+
  `faltan ${num(c.ocup-suma)} sin actividad informada o en organismos internacionales. Son cifras de la ENE: no coinciden con los ocupados del Censo de la sección Actividades. `+
  `Donde hay muy pocos informales, su % se marca como poco fiable o no fiable; la barra, casi toda formal, sí lo es. El margen de error aparece al pasar el mouse.</p>`}
// Formalidad según ENE: dos ejes y no tres grupos, porque un independiente puede ser formal o informal.
// Tramos de edad de la informalidad de independientes. La frase compara personas de la misma edad: así se ve que la
// diferencia por título no viene de que los sin título sean más jóvenes o mayores. La tarjeta usa solo brechaEdad.
const TRAMOS_FOR=["25-34","35-44","45-54","55-64"];
// La tabla cubre de 18 a 64 años: 18-24 se muestra (marcado donde no es fiable) pero no entra en la frase de igual edad.
// Fuera quedan 15-17 (muy pocos) y 65 o más (edad de jubilación); la nota de la tabla los suma para cuadrar con Chile.
const TRAMOS_TABLA=["18-24",...TRAMOS_FOR];
// Tabla por edad de formales o informales: Chile arriba (la suma de las filas), asalariados e independientes por nivel,
// los tramos en columnas y el total de 18 a 64 al final, para cuadrar en las dos direcciones. Cada celda tiene un dato:
// formal e informal en dos líneas de la misma celda confundían. El ± va al pasar el mouse: dentro de la celda, la tabla
// de informales necesitaba 968 px y a 1400 px hay 860. Es el mismo para formal e informal.
function tablaEdad(informal){const etq={poco_fiable:"poco fiable",no_fiable:"no fiable"};
 const celda=([p,m,fi,nf,ni])=>`<td class="n" data-tip="Margen de error: ± ${num(m,1)} puntos (95%)">${num(informal?ni:nf)} (${num(informal?p:100-p,1)}%)${etq[fi]?` <span class="etiqueta">${etq[fi]}</span>`:""}</td>`;
 const fila=(t,v,clase="")=>{const f=TRAMOS_TABLA.reduce((s,e)=>s+v[e][3],0),i=TRAMOS_TABLA.reduce((s,e)=>s+v[e][4],0),x=informal?i:f;
  return `<tr class="${clase}"><td>${t}</td>${TRAMOS_TABLA.map(e=>celda(v[e])).join("")}<td class="n ini">${num(x)} (${num(100*x/(f+i),1)}%)</td></tr>`};
 return `<div class="tabla-ancha"><table class="tabla-compacta" style="margin-top:8px"><thead><tr><th>${informal?"Informales":"Formales"}<br><span class="nota">ocupados (% del grupo)</span></th>`+
  `${TRAMOS_TABLA.map(e=>`<th class="n">${e} años</th>`).join("")}<th class="n ini">Total<br>18-64 años</th></tr></thead><tbody>`+fila("Chile",FOR.tramos_chile,"total")+
  [["asa","Asalariados"],["inx","Independientes"]].map(([g,t])=>`<tr class="grupo"><td colspan="${2+TRAMOS_TABLA.length}">${t}</td></tr>`+
   NIVELES.map(([k,tn])=>fila(tn,FOR.tramos[g][k])).join("")).join("")+`</tbody></table></div>`}
// Línea de cuadre: la tabla de 18 a 64 más lo que queda fuera da los asalariados e independientes de la tabla por nivel.
function cuadreEdad(informal){const i=informal?1:0,fu=FOR.tramos_fuera,c=FOR.chile,tab=TRAMOS_TABLA.reduce((s,e)=>s+FOR.tramos_chile[e][3+i],0);
 const tot=informal?c.ai[0]+c.xi[0]:c.af[0]+c.xf[0],w=informal?"informales":"formales";
 return `<p class="nota" style="margin:6px 0 0">Cuadre: los ${num(tab)} ${w} de la tabla, más ${num(fu["65+"][i])} de 65 años o más, ${num(fu["15-17"][i])} de 15 a 17 y ${num(fu.sin_nivel[i])} sin nivel de estudios informado, `+
  `son los ${num(tot)} asalariados e independientes ${w} de Chile de la tabla por nivel${informal?`; su informal total suma además ${num(c.fam[0])} familiares no remunerados`:""}.</p>`}
function edadFormalidad(){const r=k=>{const v=TRAMOS_FOR.map(e=>FOR.tramos.inx[k][e][0]);return `de ${num(Math.min(...v),0)}% a ${num(Math.max(...v),0)}%`};
 return `Se mantiene a igual edad: entre los independientes de 25 a 64 años, en cada tramo de 10 años, sin título es informal ${r("Sin_titulo")}, y con título profesional, ${r("Profesional")}. ${brechaEdad()}.`}
// Sin título casi no cambia con la edad; con título profesional es la mitad de 25-34 a 55-64 (los rangos no se cruzan, lo
// controla la generación). Son personas distintas en cada tramo: dice "mayor entre los de más edad", no "baja con los años",
// porque la encuesta no separa la edad de la generación. La tarjeta y la sección usan esta misma frase.
function brechaEdad(){const t=FOR.tramos.inx,v=(k,e)=>num(t[k][e][0],0);
 return `La diferencia es mayor entre los de más edad: de 25 a 34 años, ${v("Sin_titulo","25-34")}% frente a ${v("Profesional","25-34")}%; de 55 a 64, ${v("Sin_titulo","55-64")}% frente a ${v("Profesional","55-64")}%`}
// Grupos de la tabla de "Ver cifras": los mismos tres del gráfico por nivel. Formal e informal van con su % dentro del grupo.
const GRUPOS_FOR=[["Todos los ocupados",d=>[d.ocup,d.for,d.inf]],
 ["Asalariados",d=>[d.asa[0],[d.af[0],100-d.asa[1]],[d.ai[0],d.asa[1]]]],["Independientes",d=>[d.inx[0],[d.xf[0],100-d.inx[1]],[d.xi[0],d.inx[1]]]]];
// Por región, grupos y no extremos: la más y la menos informal no se distinguen de sus vecinas con el margen de error.
function frasesRegion(){const {alto,bajo}=gruposRegion(),rango=g=>{const v=g.map(r=>FOR.regiones[r].inf[1]);return `${num(Math.min(...v),0)}% a ${num(Math.max(...v),0)}%`};
 return `La informalidad es más alta en ${lista(alto.map(enReg))} (${rango(alto)}) y queda bajo la de Chile en ${lista(bajo.map(enReg))} (${rango(bajo)}).`}
function formalidadHtml(){const c=FOR.chile,n=FOR.niveles;
 const celda=v=>`<td class="n">${v?vmil(v):"—"}</td>`;
 const sinFam=NIVELES.filter(([k])=>!n[k].fam).map(([,t])=>t.toLowerCase());
 return `${encabezado("sec-for","Formalidad",`${num(n.Sin_titulo.inx[1],1)}% de los independientes sin título superior tiene empleo informal; con título profesional, ${num(n.Profesional.inx[1],1)}%`,true)}
 <div class="nota">Encuesta Nacional de Empleo (INE), ${PER.ene_actual}. Ocupados de 15 años o más, según región de residencia. Son estimaciones con muestra: las cifras tienen margen de error. `+
  // Sin esta aclaración, los 9,4 millones de ocupados de la ENE parecen contradecir los 8,3 millones del Censo de las pestañas anteriores.
  `Es otra fuente y otro período que el Censo 2024: estima ${enMiles(c.ocup)} de ocupados, frente a los ${enMiles(POB.chile.trabajan)} que contó el Censo, y sus cifras no se mezclan.</div>
 <p style="margin:8px 0 0">En Chile, ${enMiles(c.inf[0])} de ocupados son informales (${num(c.inf[1],1)}%) y ${enMiles(c.for[0])} formales (${num(c.for[1],1)}%). `+
  `Hay ${enMiles(c.asa[0])} de asalariados y ${enMiles(c.inx[0])} de independientes (${num(c.ind[1],1)}% de los ocupados). `+
  `Sin título superior, ${num(n.Sin_titulo.inf[1],1)}% es informal; con título profesional, ${num(n.Profesional.inf[1],1)}%. `+
  // El título y la tarjeta dicen dónde está la diferencia: en asalariados la brecha por título es mucho menor.
  `La diferencia está sobre todo en los independientes (${num(n.Sin_titulo.inx[1],1)}% ± ${num(n.Sin_titulo.inx_mas,1)} y ${num(n.Profesional.inx[1],1)}% ± ${num(n.Profesional.inx_mas,1)}); `+
  `en asalariados es ${num(n.Sin_titulo.asa[1],1)}% y ${num(n.Profesional.asa[1],1)}%. ${edadFormalidad()}</p>
 <p style="margin:8px 0 0">`+
  // Segundo párrafo: dónde (actividad y región). En uno solo, el título y el rubro se leían como una lista sin pausa.
  `Por actividad, ${fraseActividad()}. ${fraseIndependientes()} `+
  `${frasesRegion()}</p>
 ${graficoFormalidadNivel()}
 ${graficoFormalidadActividad()}
 ${graficoFormalidadRegion()}
 <details><summary>Ver cifras</summary>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th>Nivel<br><span class="nota">ocupados (% del grupo)</span></th><th class="n">Total</th><th class="n">Formal</th><th class="n">Informal</th></tr></thead><tbody>`+
  // Un bloque por panel del gráfico, en el mismo orden, como la tabla por edad. Antes eran dos tablas con los mismos ocupados
  // y % de bases distintas (todos los ocupados y el grupo), que se leían como cifras duplicadas; el reparto sobre el total no
  // lo usa ningún gráfico. Los tres bloques lado a lado no cabían a 1400 px con la cifra y su % en una línea.
  GRUPOS_FOR.map(([g,f])=>`<tr class="grupo"><td colspan="4">${g}</td></tr>`+[["Chile",c,"total"],...NIVELES.map(([k,t])=>[t,n[k],""])].map(([t,d,k])=>{
   const [tot,fo,inf]=f(d);return `<tr class="${k}"><td>${t}</td><td class="n">${num(tot)}</td><td class="n">${vmil(fo)}</td><td class="n">${vmil(inf)}</td></tr>`}).join("")).join("")+`</tbody></table></div>
 <p class="nota" style="margin:6px 0 0">Ocupados estimados (% dentro de cada grupo): formal e informal suman 100 en cada uno. Todos los ocupados incluye al familiar no remunerado, que no es asalariado ni independiente y siempre es informal (${vmil(c.fam)} en Chile): por eso no es la suma de los otros dos. Chile incluye además ${num(c.ocup-NIVELES.reduce((s,[k])=>s+n[k].ocup,0))} ocupados sin nivel de estudios informado: por eso supera por poco la suma de los niveles.${
  sinFam.length?` En ${sinFam.join(" y ")} no se muestra aparte porque son menos de 60 personas en la muestra, pero está en el total.`:""} Estas diferencias no indican causa: en los independientes no las explica la edad (ver la tabla por edad), pero pueden influir otras cosas, como el rubro.</p>
 ${tablaEdad(false)}${cuadreEdad(false)}
 ${tablaEdad(true)}${cuadreEdad(true)}
 <p class="nota" style="margin:6px 0 0">Ocupados estimados (% dentro de cada grupo, nivel y edad): formal más informal suman 100. Chile es la suma de las filas de abajo, asalariados e independientes de los tres niveles, con su propio % y margen; Total suma los cinco tramos. El margen de error (95%) de cada celda aparece al pasar el mouse. De 18 a 24 años, los independientes con título son muy pocos en la muestra y no son fiables. Fuera quedan 15 a 17 años y 65 o más, la edad de jubilación: también trabajan y son activos, pero ahí trabajar ya es opcional. La comparación a igual edad del texto usa de 25 a 64.</p>
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
   `<span class="sn-tasas">Desocupación <b>${num(tasa(x),1)}%</b> · tasa de participación <b>${num(x.tasa_participacion,1)}%</b></span></${tag}>`};
 return `<figure class="graf-sn" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><strong style="color:var(--t1)">Situación laboral por región</strong></span>`+
  partes.map(([,n,k])=>`<span><i class="${k}"></i>${n}</span>`).join("")+`</figcaption>`+
  fila("Chile",ch," sn-total","")+filas.map(([r,x])=>fila(nomReg(r),x," sn-region",`data-r="${r}"`)).join("")+`</figure>`+
  `<p class="nota" style="margin:2px 0 8px">% de la población de 15 años o más de cada región, según residencia. Junto a cada barra, las tasas: `+
  `desocupación sobre la fuerza de trabajo (ocupados y desocupados) y participación sobre la población.</p>`}
// Trabajo por región, 2: los que llegan a trabajar menos los que salen, por cada 100 ocupados que viven en la región y
// dicen dónde trabajan. Es una medida directa: el Censo trae región de residencia y de trabajo de cada ocupado, y quienes
// no informan dónde trabajan quedan fuera de la cuenta. Antes se comparaba con Chile suponiendo que esa falta de dato
// pesaba igual en todas las regiones; pesa de 0,6% a 9,0%, y el supuesto invertía el sentido en la Metropolitana, Los
// Ríos, O'Higgins y La Araucanía. Barras desde 0 con dos colores, uno por sentido; la escala es la misma a ambos lados,
// para no agrandar las diferencias chicas, y el centro se corre según el rango, para dar el espacio a las barras.
// (Los dos colores se parecen a los de formal e informal, en otra sección y con su leyenda: excepción medida, ver la nota de
// lectura; el gris chocaba con desocupados y el contorno no se leía a simple vista.)
const netoTraslado=x=>100*(x.llegan-x.salen)/(x.trabajan-x.sin_region_trabajo);
// El signo sale de la cifra publicada, para que una cifra que redondea a 0 no se lea −0,0.
const txtNeto=v=>{const r1=Math.round(10*v)/10;return `${r1>0?"+":r1<0?"−":""}${num(Math.abs(r1),1)}`};
function graficoTraslado(){
 const filas=DATOS.orden.map(r=>[r,POB.regiones[r],netoTraslado(POB.regiones[r])]).sort((a,b)=>b[2]-a[2]||a[0]-b[0]);
 const lo=Math.min(0,Math.floor(filas[filas.length-1][2]/10)*10),hi=Math.max(0,Math.ceil(filas[0][2]/10)*10),cero=100*-lo/(hi-lo),ancho=v=>100*Math.abs(v)/(hi-lo);
 const fila=([r,x,v])=>{const txt=txtNeto(v),t=nomReg(r),d=x.llegan-x.salen;
  const partes=[`Llegan a trabajar ${num(x.llegan)} desde otras regiones`,`Salen a trabajar ${num(x.salen)} a otras regiones`,
   `${d>0?"Llegan":"Salen"} ${num(Math.abs(d))} más de los que ${d>0?"salen":"llegan"}: ${txt} por cada 100 que viven en ella`,`${num(x.sin_region_trabajo)} no informan dónde trabajan`];
  return `<button class="cl-fila tr-fila" data-r="${r}" data-tip="${`<strong>${t}</strong><br>${partes.join("<br>")}`.replace(/"/g,"&quot;")}" aria-label="${t}: ${partes.join(", ")}">`+
   `<span class="cl-nombre">${t}</span><span class="tr-barra" aria-hidden="true"><b style="left:${cero}%"></b>`+
   (v>=0?`<i class="recibe" style="left:${cero}%;width:${ancho(v)}%"></i><span class="cl-valor" style="left:calc(${cero+ancho(v)}% + 6px)">${txt}</span>`
        :`<i class="entrega" style="right:${100-cero}%;width:${ancho(v)}%"></i><span class="cl-valor" style="right:calc(${100-cero+ancho(v)}% + 6px)">${txt}</span>`)+`</span></button>`};
 const [r0,x0]=filas[0],ch=POB.chile,pcs=x=>100*x.sin_region_trabajo/x.trabajan,porSin=DATOS.orden.map(r=>[r,pcs(POB.regiones[r])]).sort((a,b)=>a[1]-b[1]);
 return `<figure class="graf-cl" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><strong style="color:var(--t1)">Llegan o salen a trabajar, por región</strong></span>`+
  `<span><i class="entrega"></i>Salen más de los que llegan</span><span><i class="recibe"></i>Llegan más de los que salen</span></figcaption>`+
  filas.map(fila).join("")+`</figure>`+
  `<p class="nota" style="margin:2px 0 8px">Ocupados que llegan a trabajar a la región menos los que salen a trabajar a otra, por cada 100 que viven en ella y dicen dónde trabajan. `+
  `Por ejemplo, a ${enReg(r0)} llegan ${num(x0.llegan)} y salen ${num(x0.salen)}: ${num(x0.llegan-x0.salen)} más, ${num(filas[0][2],1)} por cada 100. `+
  `No se cuentan los ${num(ch.sin_region_trabajo)} ocupados (${num(pcs(ch),1)}%) que no informan dónde trabajan: van de ${num(porSin[0][1],1)}% en ${enReg(porSin[0][0])} a ${num(porSin.at(-1)[1],1)}% en ${enReg(porSin.at(-1)[0])}.</p>`}
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
  `<p class="nota" style="margin:2px 0 8px">% de la población de 15 años o más con nivel informado, según residencia. Al final de cada barra, profesional y técnico juntos; a la derecha, el resto, sin título superior. `+
  // Los hallazgos dan el % de los ocupados (39,8%): sin esta comparación, las dos cifras parecen contradecirse.
  `Es menos que el ${num(EST.pct_con_titulo,1)}% de los ocupados porque esta base incluye a quienes no trabajan, como jóvenes que aún estudian o personas mayores.</p>`}
// Estudios y trabajo, Chile: una barra 100% por nivel (ocupados, desocupados y fuera de la fuerza de trabajo) con los
// colores de la barra de Población, para comparar los tres repartos sobre un mismo eje. Se descartaron tres gráficos de
// pastel: los ángulos se comparan mal entre pasteles y la tajada de desocupados (5% en los tres) se vería igual.
function barrasNivel(){const partes=[["ocupados","Ocupados","s-trabajan"],["desocupados","Desocupados","s-buscan"],["fuera","Fuera de la fuerza de trabajo","s-no-buscan"]];
 const fila=([k,t])=>{const x=EST.niveles[k],tot=x.ocupados+x.desocupados+x.fuera,pc=v=>100*v/tot;
  const texto=partes.map(([c,n])=>`${n.toLowerCase()} ${num(x[c])} (${num(pc(x[c]),1)}%)`),tasas=`desocupación ${num(x.tasa_desocupacion,1)}%, participación ${num(x.tasa_participacion,1)}%`;
  return `<div class="sn-fila" role="img" tabindex="0" aria-label="${t}: ${texto.join(", ")}; ${tasas}" data-tip="${`<strong>${t}</strong><br>${texto.join("<br>")}`.replace(/"/g,"&quot;")}">`+
   `<span class="sn-nombre">${t}</span><span class="sn-barra" aria-hidden="true">${partes.map(([c,,k])=>`<i class="${k}" style="flex:${x[c]} 0 0">${pc(x[c])>=9?`${num(pc(x[c]),0)}%`:""}</i>`).join("")}</span>`+
   `<span class="sn-tasas">Desocupación <b>${num(x.tasa_desocupacion,1)}%</b> · tasa de participación <b>${num(x.tasa_participacion,1)}%</b></span></div>`};
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
  AVISO_DESLIZA+`<div class="evc-desliza"><div class="evc compacto"><div class="evc-rotulos" aria-hidden="true"><span>Diferencia</span></div>`+
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
// Área de estudio por actividad (CASEN): una actividad cuenta como "de una sola área" solo si todo su rango de 95%
// supera 50%; con el valor puntual entraba Electricidad (54,0%, rango 45,0 a 63,0). La tarjeta, el título y el
// gráfico leen esta misma función, para que no puedan contar cosas distintas.
function areasPrincipales(){const filas=DATOS.actividades.filter(a=>a.areas.length).map(a=>({a,x:a.areas[0]})).sort((p,q)=>q.x.pct-p.x.pct);
 const una=filas.filter(f=>f.x.min>50),dos=una.filter(f=>f.x.en_area_min>50);
 return {filas,una,dos,solo:una.filter(f=>!dos.includes(f))}}
// Barras de una dirección (de qué área vienen los titulados de la actividad) y la otra en la columna de la derecha, como
// cifra: son % de bases distintas, y dos barras lado a lado invitaban a compararlas como si midieran lo mismo.
// Solo se destacan las que superan 50% con todo su rango. El rango no se dibuja: como línea sobre cada barra se leía
// como un trazo suelto (blanco en modo oscuro). Va escrito donde cambia la lectura (cruza 50%) y completo en la tabla.
function graficoAreas(){const {filas}=areasPrincipales(),pos=x=>x;
 const fila=({a,x})=>{const fuerte=x.min>50,cruza=!fuerte&&x.max>50,poco=x.fiab==="poco_fiable";
  const partes=[`${num(x.pct,1)}% de sus titulados estudió ${esc(x.area)} (rango ${num(x.min,1)}% a ${num(x.max,1)}%)`,
   `${num(x.en_area,1)}% de los titulados de esa área trabaja en ${esc(a.corto)} (rango ${num(x.en_area_min,1)}% a ${num(x.en_area_max,1)}%)`];
  if(cruza)partes.push("El rango cruza 50%: no se puede afirmar que sea más de la mitad");
  if(poco)partes.push("Poco fiable: léelo con cautela");
  return `<button class="cl-fila ar-fila" data-a="${a.ciiu}" data-tip="${`<strong>${esc(a.corto)}</strong><br>${partes.join("<br>")}`.replace(/"/g,"&quot;")}" aria-label="${esc(a.corto)}: ${partes.join(", ")}">`+
   `<span class="cl-nombre">${esc(a.corto)} <span class="cl-reg">· ${esc(x.corto)}${poco?" · poco fiable":""}</span></span>`+
   `<span class="cl-barra ar-barra" aria-hidden="true"><i class="${fuerte?"ar-si":"ar-no"}" style="width:${pos(x.pct)}%"></i>`+
   `<b style="left:${pos(50)}%"></b>`+
   // El aviso va junto a la cifra y no junto al nombre, donde partía la fila en dos líneas. La escala va de 0 a 100%,
   // la natural de un %, y deja a la derecha de las barras grises espacio para el aviso sin tapar la columna.
   `<span class="cl-valor" style="left:calc(${pos(x.pct)}% + 6px)">${num(x.pct,1)}%${cruza?' <span class="cl-reg">· rango cruza 50%</span>':""}</span></span><span class="gs-num">${x.en_area_min>50?`<strong>${num(x.en_area,1)}%</strong>`:`${num(x.en_area,1)}%`}</span></button>`};
 return `<figure class="graf-cl" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><strong style="color:var(--t1)">Área principal de los titulados de cada actividad</strong></span>`+
  `<span><i class="ar-si"></i>Más de la mitad, con todo el rango</span><span><i class="ar-no"></i>No alcanza o el rango cruza 50%</span><span><span class="ref"></span>50%</span></figcaption>`+
  `<div class="cl-fila ar-fila gs-cab" aria-hidden="true"><span class="cl-nombre">Actividad · área principal</span><span>% de sus titulados que estudió esa área</span><span class="gs-num">% del área que trabaja ahí</span></div>`+
  filas.map(fila).join("")+`</figure>`+
  `<p class="nota" style="margin:2px 0 8px">Titulados técnicos y profesionales ocupados, dato nacional. Barra: % de los titulados de la actividad que estudió en su área principal; `+
  `se destaca si todo su rango de 95% supera 50%. A la derecha, la otra dirección: % de los titulados de esa área que trabaja en la actividad; en negrita, más de la mitad con todo su rango. Son bases distintas: no se suman ni se comparan entre sí.</p>`}
// Cifras del gráfico, en dos bloques que siguen las dos direcciones: los titulados de la actividad y los del área. Los que
// estudiaron el área y trabajan en la actividad son el numerador de ambos %, pero la cifra va una sola vez: repetida en las
// dos columnas confundía. El ejemplo de la nota la une con el segundo %. El rango de 95% va como margen de error (±, la
// mitad del rango; es simétrico salvo 0,1 por redondeo): dos columnas de "rango" no se entendían.
function tablaAreas(){const {filas}=areasPrincipales(),mas=(min,max)=>num((max-min)/2,1),e=filas[0];
 const pct=(p,min,max)=>`${num(p,1)}% ± ${mas(min,max)}`;
 return `<details><summary>Ver cifras</summary><div class="nota">Titulados técnicos y profesionales ocupados, dato nacional. Se lee por bloques, cada uno con su base. `+
  `Ejemplo: en ${esc(e.a.corto)} trabajan ${num(e.a.tit_casen)} titulados y ${num(e.x.tit)} de ellos estudiaron ${esc(e.x.area)} (${num(e.x.pct,1)}%). `+
  `Esos mismos ${num(e.x.tit)} son el ${num(e.x.en_area,1)}% de los ${num(e.x.tit_area)} titulados de esa área que trabajan en Chile. `+
  `Por eso los dos % no se comparan entre sí. ± es el margen de error: con 95% de confianza, el valor real está en ese rango.</div>`+
  `<div class="tabla-ancha"><table class="ar-tabla" style="margin-top:8px"><thead><tr><th rowspan="2">Actividad</th><th rowspan="2">Área de estudio principal</th>`+
  `<th colspan="2" class="bloque ini">Titulados ocupados en la actividad</th><th colspan="2" class="bloque ini">Titulados de esa área en Chile</th></tr>`+
  `<tr><th class="n ini">Total</th><th class="n">Estudiaron esa área</th><th class="n ini">Total</th><th class="n">% que trabaja en esta actividad</th></tr></thead><tbody>`+
  filas.map(({a,x})=>`<tr><td>${esc(a.corto)}</td><td>${esc(x.area)}${x.fiab==="poco_fiable"?' <span class="etiqueta">poco fiable</span>':""}</td>`+
   `<td class="n ini">${num(a.tit_casen)}</td><td class="n">${num(x.tit)} (${pct(x.pct,x.min,x.max)})</td>`+
   `<td class="n ini">${num(x.tit_area)}</td><td class="n">${pct(x.en_area,x.en_area_min,x.en_area_max)}</td></tr>`).join("")+
  `</tbody></table></div></details>`}
function areasHtml(){const {filas,una,dos,solo}=areasPrincipales(),c=solo[0];
 const conMasCarreras=[...DATOS.actividades].sort((a,b)=>b.afines.length-a.afines.length).slice(0,3);
 // Cuántas afines salen del área principal: dice de dónde viene la cantidad, que sola parecía un ranking de vínculo.
 const deArea=a=>a.afines.filter(f=>DATOS.fichas[f.c].area===a.areas[0]?.area).length;
 return `${encabezado("sec-area","Área de estudio por actividad",`En ${una.length} de ${filas.length} actividades, más de la mitad de los titulados viene de una sola área de estudio`,true)}
 <div class="nota">CASEN 2024 (${PER.casen}).</div>
 ${graficoAreas()}
 ${tablaAreas()}
 <p style="margin:8px 0 0">Solo en ${lista(dos.map(({a,x})=>`${esc(a.corto)} (${esc(x.corto)})`))} la relación va en las dos direcciones: además, más de la mitad de los titulados de esa área trabaja ahí. `+
  (c?`${esc(c.a.corto)}, en cambio, recibe ${num(c.x.pct,1)}% de sus titulados de ${esc(c.x.corto)}, pero reúne solo ${num(c.x.en_area,1)}% de esa área.`:"")+`</p>
 <div class="aviso">Dice de dónde vienen los titulados de cada actividad, no si ejercen lo que estudiaron: la actividad es el rubro del empleador, no la tarea. Que una actividad mezcle áreas no significa que acepte cualquier carrera.</div>
 <p class="invita"><strong>Elige una actividad</strong> para ver sus áreas y carreras afines. Con más carreras afines: `+
  `${conMasCarreras.map(a=>`<button class="enlace" data-a="${a.ciiu}">${esc(a.corto)}</button> (${a.afines.length}; ${deArea(a)} de ${esc(a.areas[0].corto)})`).join(" &nbsp;·&nbsp; ")}.</p>`}
function vistaResumen(){
 const ch=POB.chile,sH=POB.sexo.hombres,sM=POB.sexo.mujeres;
 const sinRegion=DATOS.actividades.filter(a=>a.pct_sin_region>=10).sort((a,b)=>b.pct_sin_region-a.pct_sin_region);
 const corto=c=>esc(porCiiu(c).corto),[d1]=RES.mas_desiguales;
 // El título nombra lo que muestran los dos gráficos de la sección: mujeres por actividad y la mayor concentración.
 const porMujeres=[...DATOS.actividades].sort((a,b)=>b.sexo.pct_m-a.sexo.pct_m),mMax=porMujeres[0],mMin=porMujeres[porMujeres.length-1];
 const [desMin,desMax]=extremos(r=>POB.regiones[r].tasa_desocupacion),[titMin,titMax]=extremos(r=>pctTitulo(EDU[r])),e=extremosDesoc();
 return `<h2>Chile · Todas las actividades</h2>${indiceHtml()}
 ${banda("Censo 2024")}
 ${encabezado("sec-pob","Población",`Trabaja el ${num(ch.pct_trabajan,1)}% de las ${num(ch.total)} personas de 15 años o más`,true)}
 <details><summary>Ver población y fuerza de trabajo</summary>
 <div class="barra-poblacion" role="img" aria-label="${num(ch.pct_trabajan,1)}% ocupados, ${num(ch.pct_buscan,1)}% desocupados, `+
  `${num(ch.pct_no_buscan,1)}% fuera de la fuerza de trabajo, ${num(ch.pct_sin_dato,1)}% sin dato">${
  [["s-trabajan",ch.trabajan],["s-buscan",ch.buscan],["s-no-buscan",ch.no_buscan],["s-sin-dato",ch.sin_dato]].map(([k,v])=>`<i class="${k}" style="flex:${v} 0 0"></i>`).join("")
 }</div>
 <div class="nota">Entre paréntesis, % de la población de 15 años o más de cada columna. `+
  // Sin esto, el % de desocupados (sobre la población) se confundía con la tasa de desocupación, que va dos filas abajo.
  `Por eso los desocupados son ${num(ch.pct_buscan,1)}% y la tasa de desocupación es ${num(ch.tasa_desocupacion,1)}%: la tasa se calcula solo sobre ocupados y desocupados.</div>
 <div class="tabla-ancha"><table><thead><tr><th>Grupo</th><th class="n">Total</th><th class="n">Hombres</th><th class="n">Mujeres</th></tr></thead><tbody>
 <tr class="total"><td>Población total</td><td class="n">${num(POB.poblacion_total)}</td><td class="n">${num(sH.poblacion_total)}</td><td class="n">${num(sM.poblacion_total)}</td></tr>
 <tr><td>Menores de 15 años</td><td class="n">${num(POB.menores_15)}</td><td class="n">${num(sH.menores_15)}</td><td class="n">${num(sM.menores_15)}</td></tr>
 <tr class="total"><td>Población de 15 años o más</td><td class="n">${num(ch.total)}</td><td class="n">${num(sH.total)}</td><td class="n">${num(sM.total)}</td></tr>
 ${filasSituacion(ch,sH,sM,true)}
 </tbody></table></div>
 <div class="aviso">Estar fuera de la fuerza de trabajo no equivale a desempleo. El Censo registra la actividad solo de los ocupados.</div></details>
 ${encabezado("sec-act","Actividades",`Las mujeres son ${num(mMax.sexo.pct_m,1)}% de los ocupados en ${esc(mMax.corto)} y ${num(mMin.sexo.pct_m,1)}% en ${esc(mMin.corto)}; ${corto(d1.ciiu)} es la más concentrada, con CL ${d1.txt} en ${enReg(d1.r)}`)}
 <div class="nota">Ocupados (participación), según lugar de trabajo. `+
  `Suman ${num(RES.total)} de ${num(ch.trabajan)}: se excluyen ${num(ch.trabajan-RES.total)} sin región de trabajo o actividad, o en organismos internacionales. `+
  // La ficha de cada región muestra la base de la participación; sin esto, sus dos totales de Chile parecían contradecirse.
  `La participación se calcula sobre ${num(BASE.chile)}, que incluye a los ${num(BASE.chile-RES.total)} de organismos internacionales.</div>
 ${graficoSexo()}
 <p class="invita"><strong>Elige una actividad</strong> para ver en qué regiones se concentra y sus carreras afines, con títulos, empleabilidad e ingresos.</p>
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
  `</tbody></table></div>
 <div class="nota" style="margin-top:10px">Traslado entre regiones: ocupados que viven en la región, menos los que no informan dónde trabajan y los que salen, más los que llegan, da los que trabajan en ella.</div>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th>Región</th><th class="n">Viven en ella</th><th class="n">No informan dónde trabajan</th>`+
  `<th class="n">Salen</th><th class="n">Llegan</th><th class="n">Trabajan en ella</th><th class="n">Neto por cada 100</th></tr></thead><tbody>`+
  [["Chile",ch,"total"],...DATOS.orden.map(r=>[DATOS.regiones[r],POB.regiones[r],""])].map(([t,d,k])=>
   `<tr class="${k}"><td>${esc(t)}</td><td class="n">${num(d.trabajan)}</td><td class="n">${num(d.sin_region_trabajo)}</td><td class="n">${num(d.salen)}</td>`+
   `<td class="n">${num(d.llegan)}</td><td class="n">${num(d.lugar_trabajo)}</td><td class="n">${k?num(0,1):txtNeto(netoTraslado(d))}</td></tr>`).join("")+
  `</tbody></table></div></details>
 <div class="aviso">La tasa depende de la edad de la población de cada región: por sí sola no basta para comparar el empleo.</div>
 ${encabezado("sec-edu","Educación por región",`Población de 15 años o más con título técnico o profesional: de ${num(titMin[1],1)}% en ${enReg(titMin[0])} a ${num(titMax[1],1)}% en ${enReg(titMax[0])}`)}
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
 <p style="margin:8px 0 0">${desocTitulo()} ${edadDesoc()}</p>
 <p style="margin:8px 0 0">Tienen título técnico o profesional ${num(EST.pct_con_titulo,1)}% de los ocupados: ${num(EST.sexo.mujeres,1)}% de las mujeres y ${num(EST.sexo.hombres,1)}% de los hombres.</p>
 ${barrasNivel()}
 ${columnasTitulo()}
 ${tablaEstudios()}
 <p class="nota" style="margin:6px 0 0">Estas diferencias no indican causa: no las explica la edad, pero pueden influir otras cosas. `+
  `La comparación por edad deja fuera a quienes no tienen edad en el Censo: ${num(EST.edad.sin_edad[1],0)}% de los activos en ${enReg(EST.edad.sin_edad[0])}, y ${num(EST.edad.sin_edad[2],1)}% o menos en las demás regiones.</p>
 <hr class="separador">${banda("CASEN 2024")}
 ${areasHtml()}
 <hr class="separador">${banda("Encuesta Nacional de Empleo (INE)")}
 ${formalidadHtml()}
 ${evolucionHtml()}`}
