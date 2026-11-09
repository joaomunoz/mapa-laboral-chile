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
// Formalidad según ENE: dos ejes y no tres grupos, porque un independiente puede ser formal o informal.
function formalidadHtml(){const c=FOR.chile,n=FOR.niveles,[rMin,rMax]=extremos(r=>FOR.regiones[r].inf[1]);
 const celda=v=>`<td class="n">${v?vmil(v):"—"}</td>`;
 const fila=(t,d,k)=>`<tr class="${k}"><td>${t}</td>${["af","ai","xf","xi","fam","for","inf"].map(x=>celda(d[x])).join("")}</tr>`;
 const sinFam=NIVELES.filter(([k])=>!n[k].fam).map(([,t])=>t.toLowerCase());
 return `${encabezado("sec-for","Formalidad",`Sin título superior, ${num(n.Sin_titulo.inf[1],1)}% trabaja en la informalidad; con título profesional, ${num(n.Profesional.inf[1],1)}%`,true)}
 <div class="nota">Encuesta Nacional de Empleo (INE), ${PER.ene_actual}. Ocupados según región de residencia, en miles (es una estimación con muestra). `+
  `Independiente: empleador o cuenta propia. Asalariado: sector privado, público o servicio doméstico.</div>
 <p style="margin:8px 0 0">En Chile, ${enMiles(c.inf[0])} de ocupados son informales (${num(c.inf[1],1)}%) y ${enMiles(c.for[0])} formales (${num(c.for[1],1)}%). `+
  `Los independientes son ${enMiles(c.ind[0])} (${num(c.ind[1],1)}%): ${num(c.xi[1],1)}% informales y ${num(c.xf[1],1)}% formales. `+
  `La informalidad va de ${num(rMin[1],1)}% en ${enReg(rMin[0])} a ${num(rMax[1],1)}% en ${enReg(rMax[0])}.</p>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th rowspan="2">Nivel<br><span class="nota">miles (%)</span></th><th colspan="2" class="bloque ini">Asalariado</th><th colspan="2" class="bloque ini">Independiente</th>`+
  `<th rowspan="2" class="n bloque ini">Familiar no remunerado</th><th colspan="2" class="bloque ini">En total</th></tr>`+
  `<tr><th class="n ini">Formal</th><th class="n">Informal</th><th class="n ini">Formal</th><th class="n">Informal</th><th class="n ini">Formal</th><th class="n">Informal</th></tr></thead><tbody>`+
  fila("Chile",c,"total")+NIVELES.map(([k,t])=>fila(t,n[k],"")).join("")+`</tbody></table></div>
 <p class="nota" style="margin:6px 0 0">Miles de ocupados (% de cada fila). Las cinco primeras columnas suman 100, y también formal e informal en total; el familiar no remunerado siempre es informal.${
  sinFam.length?` Familiar no remunerado sin dato (—) en ${sinFam.join(" y ")}: son menos de 60 personas en la muestra.`:""} Estas diferencias no indican causa: la edad, por ejemplo, también influye.</p>
 <details><summary>Ver por región</summary>
 <div class="tabla-ancha"><table style="margin-top:8px"><thead><tr><th>Región<br><span class="nota">miles (%)</span></th><th class="n">Formal</th><th class="n">Informal</th><th class="n">Independientes</th></tr></thead><tbody>`+
  [["Chile",c,"total"],...DATOS.orden.map(r=>[DATOS.regiones[r],FOR.regiones[r],""])].map(([t,d,k])=>
   `<tr class="${k}"><td>${esc(t)}</td>${celda(d.for)}${celda(d.inf)}${celda(d.ind)}</tr>`).join("")+`</tbody></table></div>
 <p class="nota" style="margin:6px 0 0">Miles de ocupados (% de la región); formal e informal suman 100. Por región no se separan las cuatro casillas: en las regiones chicas quedarían con poca muestra.</p></details>`}
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
// Dumbbell por región: el largo de la línea es la diferencia entre sin título y con título, que es el hallazgo. No parte
// en 0, porque lo que se compara es la distancia entre los dos puntos; el eje muestra las cifras. Bajo cada fila, solo la
// diferencia: las dos tasas van en el globo y en "Ver cifras".
function dumbbellTitulo(){const filas=Object.entries(EST.desocupacion_titulo).sort((a,b)=>(b[1][1]-b[1][0])-(a[1][1]-a[1][0])||a[0]-b[0]);
 const todos=[EST.desocupacion_titulo_chile,...filas.map(([,v])=>v)].flat(),lo=Math.floor(Math.min(...todos)/2)*2,hi=Math.ceil(Math.max(...todos)/2)*2,pos=x=>100*(x-lo)/(hi-lo);
 const marcas=Array.from({length:(hi-lo)/2+1},(_,k)=>lo+2*k);
 const fila=(t,[c,sn],clase,attr)=>{const dif=sn-c,partes=[`${num(c,1)}% con título técnico o profesional`,`${num(sn,1)}% sin título superior`,`diferencia ${num(dif,1)} pp`];
  const tag=attr?"button":"div";
  return `<${tag} class="db-fila${clase}" ${attr}${attr?"":' role="img" tabindex="0"'} aria-label="${t}: ${partes.join(", ")}" data-tip="${`<strong>${t}</strong><br>${partes.join("<br>")}`.replace(/"/g,"&quot;")}">`+
   `<span class="db-nombre">${t}</span><span class="db-pista" aria-hidden="true"><i class="db-linea" style="left:${pos(c)}%;width:${pos(sn)-pos(c)}%"></i>`+
   `<i class="db-punto db-con" style="left:${pos(c)}%"></i><i class="db-punto db-sin" style="left:${pos(sn)}%"></i></span><span class="db-dif">+${num(dif,1)} pp</span></${tag}>`};
 return `<figure class="graf-db" style="margin-left:0;margin-right:0"><figcaption class="gs-leyenda"><span><strong style="color:var(--t1)">Tasa de desocupación por región</strong></span>`+
  `<span><i class="db-punto db-con ley"></i>Con título técnico o profesional</span><span><i class="db-punto db-sin ley"></i>Sin título superior</span></figcaption>`+
  `<div class="db-fila db-eje" aria-hidden="true"><span></span><span class="db-pista">${marcas.map(m=>`<span style="left:${pos(m)}%">${m}%</span>`).join("")}</span><span class="db-dif">Diferencia</span></div>`+
  fila("Chile",EST.desocupacion_titulo_chile," db-total","")+filas.map(([r,v])=>fila(nomReg(r),v,"",`data-r="${r}"`)).join("")+`</figure>`}
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
 ${barrasNivel()}
 ${dumbbellTitulo()}
 ${tablaEstudios()}
 <p class="nota" style="margin:6px 0 0">Estas diferencias no indican causa: la edad de cada grupo, por ejemplo, también influye.</p>
 <hr class="separador">${banda("Encuesta Nacional de Empleo (INE)")}
 ${formalidadHtml()}
 ${evolucionHtml()}`}
