/*
<src/Visualizacion/web/js/formato.js>

Cómo se escriben cifras, nombres y porcentajes en la página.
*/
const num=(x,d=0)=>x==null?"sin dato":Number(x).toLocaleString("es-CL",{minimumFractionDigits:d,maximumFractionDigits:d});
const pesos=x=>x==null?"Sin dato":"$"+num(x);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const nom=c=>DATOS.fichas[c]?.nombre??c;
const nomReg=r=>esc(DATOS.regiones[r]);
// Bajo 10 lleva dos decimales: en actividades pequeñas, con uno solo no se ve la diferencia entre la región y Chile.
const part=p=>num(p,p!=null&&p<10?2:1)+"%";
// Formato único: ocupados por lugar de trabajo y, entre paréntesis, su participación.
const vp=(v,p)=>`${num(v)} (${part(p)})`;
const lista=x=>x.length<2?x.join(""):x.slice(0,-1).join(", ")+" y "+x[x.length-1];
// % con título técnico o profesional, desde las personas y no desde los porcentajes ya redondeados.
const conTitulo=filas=>100*(filas[0][0]+filas[1][0])/(filas[0][0]+filas[1][0]+filas[2][0]);
// "4 de cada 10" se entiende más rápido que un porcentaje; la cifra exacta queda al lado.
const deCada10=p=>`${Math.round(p/10)} de cada 10`;
const CHICA=60;
const chica=v=>v<CHICA?" *":"";
const celdaNivel=(v,p)=>v==null?"menos de 10":`${num(v)} (${num(p,1)}%)${chica(v)}`;
