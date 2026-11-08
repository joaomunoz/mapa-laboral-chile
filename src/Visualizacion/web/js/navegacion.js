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
function detalle(){
 guardarVista();
 let h=!act?vistaResumen():`<button class="enlace volver" id="volver">← Todas las actividades</button>`+(reg==null?vistaChile():vistaRegion())+bloqueCarreras();
 if(act&&ficha)h+=fichaHtml(ficha);
 const e=document.getElementById("detalle");e.innerHTML=h;
 document.getElementById("volver")?.addEventListener("click",()=>{act=null;reg=null;ficha=null;sel.value="";pintar();sel.focus()});
 e.querySelectorAll("[data-a]").forEach(b=>b.onclick=()=>{act=porCiiu(b.dataset.a);sel.value=act.ciiu;ficha=null;pintar();sel.focus({preventScroll:true});mostrarDetalle()});
 e.querySelectorAll("button[data-r]").forEach(b=>b.onclick=()=>{reg=Number(b.dataset.r);ficha=null;pintar();document.querySelector(`#lista button[data-r="${reg}"]`)?.focus({preventScroll:true});mostrarDetalle()});
 e.querySelectorAll("[data-c]").forEach(b=>b.onclick=()=>{ficha=b.dataset.c;detalle();document.getElementById("ficha")?.scrollIntoView({behavior:"smooth",block:"nearest"});e.querySelector(".cerrar")?.focus()});
 // El índice mueve el foco a la sección, para que el teclado y el lector de pantalla sigan desde ahí.
 e.querySelectorAll("[data-ir]").forEach(b=>b.onclick=()=>{const s=document.getElementById(b.dataset.ir);
  s.scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth",block:"start"});s.focus({preventScroll:true})});
 e.querySelector(".cerrar")?.addEventListener("click",()=>{const previa=ficha;ficha=null;detalle();e.querySelector(`[data-c="${CSS.escape(previa)}"]`)?.focus()});
}
