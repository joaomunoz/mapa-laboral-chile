/*
<src/Visualizacion/web/js/mapa.js>

Mapa, leyenda, lista de regiones y cabecera de cada vista.
*/
const relleno=d=>d.clase==null?"var(--sd)":`var(--c${d.clase})`;
const ordenar=(a,b)=>(b.peso??-1)-(a.peso??-1);
// Punto del borde de una región a una altura dada, para que la línea toque el territorio y no su recuadro.
function bordeRegion(p,y,lado){
 const c=p.getBBox(),q=p.ownerSVGElement.createSVGPoint();q.y=y;
 const paso=lado==="izq"?1:-1;
 for(let x=lado==="izq"?c.x:c.x+c.width;x>=c.x&&x<=c.x+c.width;x+=paso){q.x=x;if(p.isPointInFill(q))return x}
 return lado==="izq"?c.x:c.x+c.width}
let NOTAS_MAPA=[];
// El mapa cambia de tamaño con la ventana: se escala en unidades del SVG para que la letra siempre mida lo mismo en pantalla.
function anotarMapa(notas){
 const g=document.getElementById("anotaciones"),svgMapa=g.ownerSVGElement,k=svgMapa.viewBox.baseVal.width/svgMapa.getBoundingClientRect().width,linea=14*k;
 g.innerHTML=notas.map(([r,lado,t,d,v])=>{
  const p=document.querySelector(`.region[data-r="${r}"]`),c=p.getBBox(),y=c.y+c.height/2,b=bordeRegion(p,y,lado),s=lado==="izq"?-1:1,x=b+s*16*k,anc=lado==="izq"?"end":"start",tx=x+s*4*k;
  return `<g class="anotacion"><line x1="${b}" y1="${y}" x2="${x}" y2="${y}" stroke-width="${k}"></line>`+
   `<text x="${tx}" y="${y-linea+4*k}" text-anchor="${anc}" font-size="${12*k}"><tspan class="a-t">${t}</tspan>`+
   `<tspan x="${tx}" dy="${linea}">${esc(d)}</tspan><tspan class="a-d" x="${tx}" dy="${linea}">CL hasta ${v}</tspan></text></g>`}).join("")}
function pintarResumen(){
 const colores=Object.entries(RES.colores),ch=POB.chile;
 document.getElementById("t-mapa").textContent="13 de 16 regiones se especializan en minería, agricultura o administración pública";
 document.getElementById("n-mapa").textContent="Actividad con mayor CL, según región de trabajo. No es la actividad con más ocupados.";
 document.getElementById("leyenda").className="leyenda-cat";
 document.getElementById("leyenda").innerHTML=colores.map(([c,i])=>`<div><i class="muestra" style="background:var(--k${i})"></i>${esc(porCiiu(c).corto)}</div>`).join("")+`<div>Color suave: CL menor a ${RES.corte_suave}</div>`;
 document.getElementById("ejes").hidden=true;
 document.querySelectorAll(".region").forEach(p=>{const r=Number(p.dataset.r),d=RES.regiones[r],a=porCiiu(d.ciiu);
  p.style.fill=`var(--k${RES.colores[d.ciiu]})`;p.style.opacity=d.suave?.45:1;
  p.setAttribute("aria-label",`${DATOS.regiones[r]}: mayor CL en ${a.corto}, ${d.txt}`);p.setAttribute("aria-pressed",false)});
 document.getElementById("contorno").setAttribute("d","");
 document.getElementById("lectura").innerHTML=`<strong>${num(POB.poblacion_total)}</strong> habitantes · ${num(ch.total)} de 15 años o más · Tasa de ocupación <strong>${num(ch.pct_trabajan,1)}%</strong>`;
 document.getElementById("n-lista").textContent="Primero, la actividad con mayor CL; debajo, la que tiene más ocupados. Elige una región para ver sus valores.";
 const orden=Object.entries(RES.regiones).map(([r,d])=>[Number(r),d]).sort((a,b)=>b[1].peso-a[1].peso);
 const rm=POB.regiones[13],sx=POB.sexo,cl=r=>RES.regiones[r].txt;
 const principal=document.getElementById("principal");principal.hidden=false;document.getElementById("kpis-t").hidden=false;document.getElementById("cabecera").classList.add("con-resumen");
 const ed=extremosDesoc();
 const porTitulo=[...DATOS.actividades].sort((a,b)=>conTitulo(a.niveles)-conTitulo(b.niveles)),tMin=porTitulo[0],tMax=porTitulo[porTitulo.length-1];
 const todas=Object.entries(RES.regiones),patron=todas.filter(([,d])=>["B","A","O"].includes(d.ciiu)),brecha=sx.hombres.tasa_participacion-sx.mujeres.tasa_participacion;
 principal.innerHTML=[
  [`${num(rm.pct_lugar_trabajo,1)}%`,"de los ocupados está en la Metropolitana",
   `${num(rm.lugar_trabajo)} de ${num(ch.lugar_trabajo)}, según lugar de trabajo. `+
   `Tiene más ocupados en ${RES.n_metropolitana} de ${DATOS.actividades.length} actividades.`],
  [`${patron.length} de ${todas.length}`,"regiones se especializan en minería, agricultura o administración pública",
   "Según su mayor CL. Metropolitana, Valparaíso y Biobío se distinguen por otras actividades."],
  [deCada10(EST.pct_con_titulo),"ocupados tiene título técnico o profesional",
   `${num(EST.pct_con_titulo,1)}%, según residencia. Por actividad, de ${deCada10(conTitulo(tMin.niveles))} en ${esc(tMin.corto)} (${num(conTitulo(tMin.niveles),1)}%) `+
   `a ${deCada10(conTitulo(tMax.niveles))} en ${esc(tMax.corto)} (${num(conTitulo(tMax.niveles),1)}%), según lugar de trabajo.`],
  [`${ed.menor} de ${ed.n}`,"regiones tienen menor desocupación con título técnico o profesional",
   `Con y sin título, ${ed.rango}. No indica causa: la edad también influye.`],
  [`${num(brecha,1)} puntos`,"de brecha en la tasa de participación",
   `${num(sx.hombres.tasa_participacion,1)}% en hombres y ${num(sx.mujeres.tasa_participacion,1)}% en mujeres; el Censo no indica su causa. `+
   `Con título: ${num(EST.sexo.mujeres,1)}% de las mujeres ocupadas y ${num(EST.sexo.hombres,1)}% de los hombres.`]]
  .map(([v,t,d])=>`<div class="kpi"><b>${v}</b><span class="kpi-t">${t}</span><span class="nota">${d}</span></div>`).join("");
 anotarMapa(NOTAS_MAPA=[[2,"izq","Norte","Minería",cl(2)],[7,"der","Centro-sur","Agricultura y pesca",cl(7)],[11,"der","Extremos","Administración pública",cl(11)]]);
 document.getElementById("lista").innerHTML=orden.map(([r,d])=>{
  const a=porCiiu(d.ciiu),v=a.regiones[r],ap=porCiiu(d.mas_personas),vm=ap.regiones[r];
  const valores=`Mayor CL: ${a.corto}, ${vp(v.ocupados,v.pct)}. Más ocupados: ${ap.corto}, ${vp(vm.ocupados,vm.pct)}. `+
   `Total región: ${num(POB.regiones[r].lugar_trabajo)} (${num(POB.regiones[r].pct_lugar_trabajo,1)}%).`;
  return `<button data-r="${r}" class="fila-resumen" aria-pressed="false" title="${esc(valores)}" aria-label="${esc(nomReg(r)+". "+valores+" CL "+d.txt)}">`+
   `<i class="franja${d.suave?" suave":""}" style="background:var(--k${RES.colores[d.ciiu]})"></i>`+
   `<span>${nomReg(r)}<small class="r-cl">${esc(a.corto)}</small><small>Más ocupados: ${esc(ap.corto)}</small></span>`+
   `<span class="v">CL ${d.txt}</span></button>`}).join("");
 document.querySelectorAll("#lista button").forEach(b=>b.onclick=()=>{const r=Number(b.dataset.r);act=porCiiu(RES.regiones[r].ciiu);sel.value=act.ciiu;reg=r;ficha=null;pintar();mostrarDetalle()});
 detalle();
}
function pintar(){
 if(!act){pintarResumen();return}
 document.getElementById("t-mapa").textContent="CL por región";
 document.getElementById("n-mapa").textContent="Según región de trabajo.";
 document.getElementById("leyenda").className="leyenda";
 document.getElementById("leyenda").innerHTML=DATOS.tramos.map((r,i)=>`<div><i style="background:var(--c${i})"></i><span>${r}</span></div>`).join("");
 document.getElementById("ejes").hidden=false;
 document.getElementById("n-lista").textContent="Ordenadas por CL. Ocupados (participación), según lugar de trabajo.";
 document.querySelectorAll(".region").forEach(p=>{const r=Number(p.dataset.r),d=act.regiones[r];p.style.fill=relleno(d);p.style.opacity=1;p.setAttribute("aria-label",`${DATOS.regiones[r]}: CL ${d.peso_txt}, ${LECT[d.lectura]}`);p.setAttribute("aria-pressed",r===reg)});
 // Se dibuja aparte: mover la región elegida al frente le quitaría el foco a quien navega con teclado.
 document.getElementById("contorno").setAttribute("d",reg==null?"":GEO.trazados[reg]);
 const foco=document.activeElement?.closest?.("#lista button")?.dataset.r;
 const orden=Object.entries(act.regiones).map(([r,d])=>[Number(r),d]).sort((a,b)=>ordenar(a[1],b[1]));
 document.getElementById("anotaciones").innerHTML="";document.getElementById("principal").hidden=true;document.getElementById("kpis-t").hidden=true;document.getElementById("cabecera").classList.remove("con-resumen");
 const max=orden[0][1].peso??1,mejor=orden[0],conc=orden.filter(([,d])=>d.lectura==="concentra"),mp=act.nacional.mas_personas;
 document.getElementById("lectura").innerHTML=`<strong>${esc(act.glosa)}:</strong> mayor CL en <strong>${nomReg(mejor[0])}</strong>, `+
  `donde su participación es ${mejor[1].peso_txt} veces la de Chile, y más ocupados en <strong>${nomReg(mp.r)}</strong> (${num(mp.n)}). `+
  (conc.length===0?"Ninguna región con CL de 1,2 o más.":conc.length===1?"1 región con CL de 1,2 o más.":conc.length+" regiones con CL de 1,2 o más.");
 document.getElementById("lista").innerHTML=
  `<button data-r="${CHILE}" aria-pressed="${reg==null}" class="chile"><span>Chile<small>${vp(act.nacional.ocupados,act.pct_nacional)} · CL 1,00</small></span></button>`+
  orden.map(([r,d])=>`<button data-r="${r}" aria-pressed="${r===reg}"><span>${nomReg(r)}<small>${vp(d.ocupados,d.pct)}</small></span>`+
   `<span class="barra"><i style="width:${100*(d.peso??0)/max}%;background:${relleno(d)}"></i></span><span class="v">CL ${d.peso_txt}</span></button>`).join("");
 document.querySelectorAll("#lista button").forEach(b=>b.onclick=()=>{const r=Number(b.dataset.r);reg=r===CHILE?null:r;ficha=null;pintar();mostrarDetalle()});
 if(foco)document.querySelector(`#lista button[data-r="${foco}"]`)?.focus();
 detalle();
}
