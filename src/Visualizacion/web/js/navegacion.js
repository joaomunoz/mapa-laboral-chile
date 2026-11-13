/*
<src/Visualizacion/web/js/navegacion.js>

La vista vive en la dirección de la página: guardarla, leerla y dibujar el detalle.
*/
function mostrarDetalle(){const e=document.getElementById("detalle"),t=e.getBoundingClientRect().top;
 if(t<0||t>innerHeight-120)e.scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth",block:"start"})}
// La vista vive en la dirección (#actividad/región/carrera): así "atrás" vuelve paso a paso, sobre todo en celular,
// y se puede compartir un enlace a una vista. Al cargar o al volver se reemplaza en vez de agregar, para no duplicar pasos.
let reemplazar=true;
const vistaHash=()=>act?"#"+[act.ciiu,reg??"",ficha?encodeURIComponent(ficha):""].join("/").replace(/\/+$/,""):"";
function guardarVista(){const h=vistaHash();
 if(h!==location.hash){const url=h||location.pathname+location.search;try{history[reemplazar?"replaceState":"pushState"](null,"",url)}catch{location.hash=h}}
 reemplazar=false}
function leerVista(){const [c,r,f]=location.hash.slice(1).split("/");
 act=DATOS.actividades.find(a=>a.ciiu===c)||null;
 reg=act&&r&&act.regiones[Number(r)]?Number(r):null;
 const k=f?decodeURIComponent(f):null;ficha=act&&k&&DATOS.fichas[k]?k:null;
 sel.value=act?act.ciiu:""}
// Muestra el aviso de cada gráfico de columnas solo si no cabe en el ancho disponible.
function avisoDesliza(){document.querySelectorAll(".evc-desliza").forEach(d=>{const a=d.previousElementSibling;if(a?.classList.contains("evc-aviso"))a.hidden=d.scrollWidth<=d.clientWidth+1})}
function detalle(){
 guardarVista();
 // El panel se redibuja bajo el puntero: sin esto, el texto emergente del gráfico quedaría fijo en pantalla.
 document.getElementById("tip").style.display="none";
 // El botón sube un nivel y dice adónde: de la región a Chile con la misma actividad, y de ahí al resumen. Antes, desde
 // la región saltaba directo al resumen y no había cómo subir un solo nivel salvo la tarjeta "Chile" de la lista.
 let h=!act?vistaResumen():`<button class="enlace volver" id="volver">← Chile · ${reg==null?"Todas las actividades":esc(act.corto)}</button>`+(reg==null?vistaChile()+bloqueCarreras():vistaRegion());
 if(act&&ficha)h+=fichaHtml(ficha);
 const e=document.getElementById("detalle");e.innerHTML=h;avisoDesliza();
 document.getElementById("volver")?.addEventListener("click",()=>{ficha=null;
  if(reg!=null){reg=null;pintar();document.querySelector(`#lista button[data-r="${CHILE}"]`)?.focus({preventScroll:true});mostrarDetalle()}
  else{act=null;sel.value="";pintar();sel.focus()}});
 e.querySelectorAll("[data-a]").forEach(b=>b.onclick=()=>{act=porCiiu(b.dataset.a);sel.value=act.ciiu;ficha=null;pintar();sel.focus({preventScroll:true});mostrarDetalle()});
 e.querySelectorAll("button[data-r]").forEach(b=>b.onclick=()=>{reg=Number(b.dataset.r);ficha=null;pintar();document.querySelector(`#lista button[data-r="${reg}"]`)?.focus({preventScroll:true});mostrarDetalle()});
 e.querySelectorAll("[data-c]").forEach(b=>b.onclick=()=>{ficha=b.dataset.c;detalle();document.getElementById("ficha")?.scrollIntoView({behavior:"smooth",block:"nearest"});e.querySelector(".cerrar")?.focus()});
 // Texto emergente del gráfico de hombres y mujeres, con el mismo globo que el mapa.
 e.querySelectorAll("[data-tip]").forEach(b=>{b.onmousemove=ev=>{tip.innerHTML=b.dataset.tip;tip.style.display="block";
  tip.style.left=Math.min(ev.clientX+14,innerWidth-250)+"px";tip.style.top=ev.clientY+14+"px"};b.onmouseleave=()=>{tip.style.display="none"}});
 // El índice mueve el foco a la sección, para que el teclado y el lector de pantalla sigan desde ahí.
 e.querySelectorAll("[data-ir]").forEach(b=>b.onclick=()=>{const s=document.getElementById(b.dataset.ir);
  s.scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth",block:"start"});s.focus({preventScroll:true})});
 e.querySelector(".cerrar")?.addEventListener("click",()=>{const previa=ficha;ficha=null;detalle();e.querySelector(`[data-c="${CSS.escape(previa)}"]`)?.focus()});
}
