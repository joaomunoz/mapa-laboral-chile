/*
<src/Visualizacion/web/js/formato.js>

Cómo se escriben cifras, nombres y porcentajes en la página.
*/
const num=(x,d=0)=>x==null?"sin dato":Number(x).toLocaleString("es-CL",{minimumFractionDigits:d,maximumFractionDigits:d});
const pesos=x=>x==null?"Sin dato":"$"+num(x);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const nom=c=>DATOS.fichas[c]?.nombre??c;
const nomReg=r=>esc(DATOS.regiones[r]);
// Para frases: "en la Metropolitana", como se dice; en títulos, listas y tablas va el nombre solo (nomReg).
const enReg=r=>(Number(r)===13?"la ":"")+nomReg(r);
// Bajo 10 lleva dos decimales: en actividades pequeñas, con uno solo no se ve la diferencia entre la región y Chile.
const part=p=>num(p,p!=null&&p<10?2:1)+"%";
// Formato único: ocupados por lugar de trabajo y, entre paréntesis, su participación.
const vp=(v,p)=>`${num(v)} (${part(p)})`;
// Cifras de la ENE en miles: es una estimación con muestra, y la unidad aparentaría una exactitud que no tiene.
const vmil=([n,p])=>`${num(n)} (${num(p,1)}%)`;  // En tablas: ocupados estimados (% de la fila), en unidades
// En texto y gráficos, la ENE se redondea a mil o a millón: es una estimación con muestra y se lee mejor así.
const enMiles=n=>n>=1e6?`${num(n/1e6,1)} millones`:`${num(n/1000,0)} mil`;
const lista=x=>x.length<2?x.join(""):x.slice(0,-1).join(", ")+" y "+x[x.length-1];
// % con título técnico o profesional, desde las personas y no desde los porcentajes ya redondeados.
const conTitulo=filas=>100*(filas[0][0]+filas[1][0])/(filas[0][0]+filas[1][0]+filas[2][0]);
// "4 de cada 10" se entiende más rápido que un porcentaje; la cifra exacta queda al lado.
const deCada10=p=>`${Math.round(p/10)} de cada 10`;
const CHICA=60;
const chica=v=>v<CHICA?" *":"";
// El Censo cuenta personas, no estima con muestra: el riesgo de una cifra chica es que unas pocas personas mueven mucho su %.
const NOTA_CHICA=`<p class="nota" style="margin:6px 0 0">* Menos de ${CHICA} personas: es un conteo del Censo, pero con tan pocas, unas pocas personas cambian mucho el %. Léelo con cautela.</p>`;
const celdaNivel=(v,p)=>v==null?"menos de 10":`${num(v)} (${num(p,1)}%)${chica(v)}`;
// Misma regla en el detalle de región: bajo 10 la cifra no viene en los datos, y su participación tampoco.
const celdaSexo=v=>v==null?"menos de 10":num(v)+chica(v);
const partSexo=p=>p==null?"–":part(p);
