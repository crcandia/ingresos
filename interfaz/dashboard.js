(() => {
 'use strict';
 const DATA=JSON.parse(document.getElementById('dashboard-data').textContent);
 const INITIAL=JSON.parse(document.getElementById('initial-state').textContent);
 const DEFAULT={occupation:'all',sex:'all',age:'all',amount:1000000,range:3,rank:'median',survivalScale:'linear'};
 const $=id=>document.getElementById(id);
 const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const num=(x,d=0)=>new Intl.NumberFormat('es-CL',{minimumFractionDigits:0,maximumFractionDigits:d}).format(x);
 const money=x=>'$'+num(Math.round(x/1000)*1000);
 const exactMoney=x=>'$'+num(Math.round(x));
 const pct=x=>num(x,x>0&&x<.01?4:x<1?2:1)+'%';
 const people=x=>num(Math.round(x/(x<1000?10:100))*(x<1000?10:100)|| (x>0?1:0));
 const label=(kind,id)=>DATA.meta[kind].find(x=>x.id===String(id))?.label||'';
 const ageShort=id=>id==='all'?'Total (20+)':id==='60_mas'?'60+':label('age',id).replace(' años','');
 const valid=(key,value)=>key==='occupation'?DATA.meta.occupation.some(x=>x.id===value):key==='sex'?DATA.meta.sex.some(x=>x.id===value):DATA.meta.age.some(x=>x.id===value);
 const state={...DEFAULT};
 for(const k of ['occupation','sex','age'])if(valid(k,INITIAL[k]))state[k]=INITIAL[k];
 if(Number.isFinite(INITIAL.amount))state.amount=Math.max(0,Math.min(20000000,Math.round(INITIAL.amount/50000)*50000));
 if([3,21].includes(INITIAL.range))state.range=INITIAL.range;
 if(['median','mean','threshold'].includes(INITIAL.rank))state.rank=INITIAL.rank;
 if(['linear','log'].includes(INITIAL.survivalScale))state.survivalScale=INITIAL.survivalScale;
 const domain=(occupation=state.occupation,sex=state.sex,age=state.age)=>DATA.domains[`${occupation}|${sex}|${age}`];
 const poorDomain=d=>d.n<60||d.df<9;
 const eventAt=(d,amount=state.amount)=>{const i=Math.max(0,Math.min(420,Math.round(amount/50000)));return{p:d.curve.p[i],n:d.curve.n[i],lo:d.curve.lo[i],hi:d.curve.hi[i],q:d.curve.q[i],persons:d.N*d.curve.p[i]/100};};
 const sufficientText='Cumple el criterio de precisión';
 const qualityText=e=>e.q===0?'Sin casos observados':e.q===1?'Exploratorio':sufficientText;
 const roundUp=x=>{if(x<=0)return 1;const exp=10**Math.floor(Math.log10(x)),v=x/exp;return (v<=1?1:v<=2?2:v<=2.5?2.5:v<=5?5:10)*exp;};
 const color={ink:'#193d3b',muted:'#61716d',teal:'#216c63',gold:'#a66b2d',line:'#e5e9e1',pale:'#e2ece4'};
 // One logarithmic range for every group, including all positive CI endpoints.
 // No pseudocount or substituted positive value is used for observed zeros.
 const logMinExponent=Math.min(-1,...Object.values(DATA.domains).map(d=>Math.floor(Math.log10(Math.min(...[...d.curve.p.slice(20),...d.curve.lo.slice(20)].filter(v=>Number.isFinite(v)&&v>0))))));
 function svgShell(w,h,title,body,desc=''){return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" role="img" tabindex="0" aria-label="${esc(title)}"><title>${esc(title)}</title><desc>${esc(desc)}</desc>${body}</svg>`;}
 function txt(x,y,s,anchor='start',size=10,fill=color.muted,extra=''){return `<text x="${x}" y="${y}" text-anchor="${anchor}" font-family="Arial,sans-serif" font-size="${size}" fill="${fill}" ${extra}>${esc(s)}</text>`;}
 function line(x1,y1,x2,y2,stroke=color.line,extra=''){return `<line x1="${x1}" x2="${x2}" y1="${y1}" y2="${y2}" stroke="${stroke}" ${extra}/>`;}
 function chartWidth(el,fallback){return Math.max(250,Math.floor(el.getBoundingClientRect().width||fallback));}
 function makeTooltip(el,svg,read,{left,right,w,maxIndex,minIndex=0,intervals=false}){
   let tip=document.createElement('div');tip.className='tooltip';tip.setAttribute('role','status');tip.setAttribute('aria-live','polite');el.appendChild(tip);let active=minIndex;
   function show(i,cx,cy){active=i;tip.innerHTML=read(i);tip.classList.add('visible');const tw=tip.offsetWidth||220;tip.style.left=Math.max(0,Math.min(w-tw,cx+12))+'px';tip.style.top=Math.max(4,cy-56)+'px';}
   svg.addEventListener('pointermove',e=>{const rect=svg.getBoundingClientRect();const px=(e.clientX-rect.left)*(w/(rect.width||w));const f=(px-left)/(w-left-right);const i=intervals?minIndex+Math.floor(f*(maxIndex-minIndex+1)):Math.round(minIndex+f*(maxIndex-minIndex));if(i>=minIndex&&i<=maxIndex&&f>=0&&f<=1)show(i,px,e.clientY-rect.top);else tip.classList.remove('visible');});
   svg.addEventListener('pointerleave',()=>tip.classList.remove('visible'));
   svg.addEventListener('blur',()=>tip.classList.remove('visible'));
   svg.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','Home','End','Escape'].includes(e.key))return;e.preventDefault();if(e.key==='Escape'){tip.classList.remove('visible');return;}active=e.key==='Home'?minIndex:e.key==='End'?maxIndex:Math.max(minIndex,Math.min(maxIndex,active+(e.key==='ArrowRight'?1:-1)));show(active,left+(active-minIndex)/(maxIndex-minIndex)*(w-left-right),90);});
 }
 function renderDistribution(d){
   const el=$('distribution'),w=chartWidth(el,750),h=285,L=46,R=14,T=24,B=45,plotW=w-L-R,plotH=h-T-B,xmax=state.range*1e6;
   const bins=d.hist.slice(0,Math.round(xmax/100000)),ymax=roundUp(Math.max(...bins)*1.12),x=v=>L+v/xmax*plotW,y=v=>T+plotH-v/ymax*plotH;
   let body=txt(L,12,'% del grupo','start',10);
   for(let i=0;i<=4;i++){const v=ymax*i/4;body+=line(L,y(v),w-R,y(v));body+=txt(L-9,y(v)+3,num(v,v<1?2:1)+'%','end',10);}
   const step=state.range===3?(w<430?1:.5):(w<500?5:1);
   for(let v=0;v<=state.range;v+=step)body+=txt(x(v*1e6),h-B+19,'$'+num(v,1)+'M','middle',10);
   body+=txt(L+plotW/2,h-5,'Ingreso neto mensual (millones de pesos)','middle',10);
   bins.forEach((v,i)=>{body+=`<rect x="${x(i*100000)+.5}" y="${y(v)}" width="${Math.max(.3,plotW/bins.length-1)}" height="${Math.max(0,v/ymax*plotH)}" fill="${i*100000>=state.amount?color.teal:'#94b4a6'}"/>`;});
   for(const [value,c,dash] of [[d.median,color.teal,'5 4'],[d.mean,color.gold,'2 3']])if(value>=0&&value<=xmax)body+=line(x(value),T,x(value),h-B,c,`stroke-width="1.6" stroke-dasharray="${dash}"`);
   el.innerHTML=svgShell(w,h,'Distribución del ingreso del grupo seleccionado',body,'Intervalos de $100.000. Usa las flechas del teclado para consultar cada intervalo.');
   makeTooltip(el,el.querySelector('svg'),i=>`<strong>${exactMoney(i*100000)} a menos de ${exactMoney((i+1)*100000)}</strong><br>`+(bins[i]>0?`≈ ${pct(bins[i])} del grupo<br>≈ ${people(d.N*bins[i]/100)} personas`:'Sin casos observados en este intervalo.'),{left:L,right:R,w,maxIndex:bins.length-1,intervals:true});
   const outside=eventAt(d,3000000);
   $('distribution-note').textContent='Cada barra reúne $100.000. '+(state.range===3?(outside.n?`Fuera de esta vista: ≈ ${pct(outside.p)} gana $3 millones o más.`:'No se observaron casos de $3 millones o más en este grupo.'):'Se muestra el rango completo de ingresos observados.')+' Tonos oscuros: intervalos completos a partir del monto consultado.';
 }
 function renderSurvival(d){
   const el=$('survival'),w=chartWidth(el,1220),h=260,L=68,R=17,T=26,B=44,plotW=w-L-R,plotH=h-T-B,min=20,max=420,isLog=state.survivalScale==='log';
   const maxCI=Math.max(...d.curve.hi.slice(min).filter(Number.isFinite),...d.curve.p.slice(min));
   const ymax=isLog?100:Math.min(100,roundUp(maxCI*1.08)),x=i=>L+(i-min)/(max-min)*plotW;
   const y=v=>isLog?T+(2-Math.log10(v))/(2-logMinExponent)*plotH:T+plotH-v/ymax*plotH;
   const positive=i=>d.curve.n[i]>0&&d.curve.p[i]>0;
   const chunksOf=indices=>{const chunks=[];for(const i of indices){if(!chunks.length||i!==chunks.at(-1).at(-1)+1)chunks.push([]);chunks.at(-1).push(i);}return chunks;};
   const indices=Array.from({length:max-min+1},(_,i)=>i+min),positivePoints=indices.filter(positive),firstZero=indices.find(i=>d.curve.n[i]===0);
   const stepPath=(c,values)=>c.map((i,j)=>`${j?'H':'M'}${x(i)}${j?'V':','}${y(values[i])}`).join('');
   let body=txt(L,12,'% del grupo con ese ingreso o más','start',w<400?9:10);
   const yticks=isLog?Array.from({length:3-logMinExponent},(_,j)=>10**(logMinExponent+j)):Array.from({length:5},(_,j)=>ymax*j/4);
   for(const v of yticks){body+=line(L,y(v),w-R,y(v));body+=txt(L-9,y(v)+3,num(v,isLog?Math.max(0,-logMinExponent):v<1?2:1)+'%','end',10,'#61716d',`data-log-tick="${isLog?v:''}"`);}
   const ticks=w<600?[1,5,10,15,20]:Array.from({length:21},(_,i)=>i+1);
   for(const v of ticks)body+=txt(x(v*20),h-B+18,'$'+v+'M','middle',10);
   body+=txt(L+plotW/2,h-4,'Ingreso neto mensual (millones de pesos)','middle',10);
   const band=positivePoints.filter(i=>Number.isFinite(d.curve.lo[i])&&Number.isFinite(d.curve.hi[i])&&(!isLog||(d.curve.lo[i]>0&&d.curve.hi[i]>0)));
   // Both boundaries use the same step geometry as the central estimate.
   // Split on missing endpoints, nonpositive log bounds, or unobserved tails.
   for(const c of chunksOf(band)){
     const last=c.at(-1);let path=stepPath(c,d.curve.hi)+`L${x(last)},${y(d.curve.lo[last])}`;
     for(const i of c.slice(0,-1).reverse())path+=`V${y(d.curve.lo[i])}H${x(i)}`;
     body+=`<path class="survival-band" d="${path}Z" fill="${color.teal}" opacity=".12"/>`;
   }
   for(const c of chunksOf(positivePoints)){
     let solid='';for(let j=1;j<c.length;j++)if(d.curve.q[c[j-1]]===2&&d.curve.q[c[j]]===2)solid+=stepPath([c[j-1],c[j]],d.curve.p);
     body+=`<path class="survival-curve" d="${stepPath(c,d.curve.p)}" fill="none" stroke="${color.teal}" stroke-width="1.8" stroke-dasharray="5 4"/><path class="survival-solid" d="${solid}" fill="none" stroke="${color.teal}" stroke-width="2"/>`;
     if(c.length===1)body+=`<circle class="survival-point" cx="${x(c[0])}" cy="${y(d.curve.p[c[0]])}" r="2.5" fill="${color.teal}"/>`;
   }
   if(!positivePoints.length){body+=txt(L+plotW/2,T+plotH/2-6,'Sin casos observados','middle',12,color.ink)+txt(L+plotW/2,T+plotH/2+13,'desde $1 millón en este grupo','middle',10);}
   const selected=Math.round(state.amount/50000);if(selected>=min&&selected<=max){body+=line(x(selected),T,x(selected),h-B,color.gold,'stroke-dasharray="3 4"');if(positive(selected))body+=`<circle class="survival-selected" cx="${x(selected)}" cy="${y(d.curve.p[selected])}" r="4" fill="${color.gold}" stroke="white" stroke-width="1.5"/>`;}
   const scaleNote=isLog?`Escala logarítmica del porcentaje: cada marca sube ×10. Mismo eje de ${num(10**logMinExponent,-logMinExponent)}% a 100% para todos los grupos.`:'Escala lineal del porcentaje. El eje vertical se ajusta al grupo seleccionado.';
   const tailNote=firstZero!==undefined?` Desde ${exactMoney(firstZero*50000)} no hay casos observados. La curva se interrumpe, sin asumir ausencia en la población.`:'';
   const clippedNote=isLog&&positivePoints.some(i=>d.curve.lo[i]===0)?' Los límites del intervalo iguales a cero no son representables en escala logarítmica.':'';
   $('survival-scale-note').textContent=scaleNote+tailNote+clippedNote;
   el.innerHTML=svgShell(w,h,`Proporción que gana cada monto o más, desde un millón de pesos. Escala ${isLog?'logarítmica':'lineal'}`,body,scaleNote+' Línea continua para mayor respaldo muestral y discontinua para precisión limitada. Las flechas consultan umbrales de $50.000.'+tailNote+clippedNote);
   makeTooltip(el,el.querySelector('svg'),i=>{const e=eventAt(d,i*50000);return `<strong>≥ ${exactMoney(i*50000)}</strong><br>${e.n?`≈ ${pct(e.p)} · ≈ ${people(e.persons)} personas`:'Sin casos observados'}<br>${num(e.n)} ${e.n===1?'encuestado':'encuestados'} · ${qualityText(e)}`;},{left:L,right:R,w,maxIndex:max,minIndex:min});
 }
 function renderThreshold(d){
   const e=eventAt(d);
   $('amount').value=state.amount;$('amount-slider').value=state.amount;
   document.querySelectorAll('[data-amount]').forEach(b=>{b.classList.toggle('active',+b.dataset.amount===state.amount);b.setAttribute('aria-pressed',String(+b.dataset.amount===state.amount));});
   $('threshold-percent').classList.toggle('no-cases',e.n===0);
   $('threshold-percent').innerHTML=e.n?`<span class="approx">≈</span>${pct(e.p)}`:'Sin casos observados';
   $('threshold-people').textContent=e.n?`≈ ${people(e.persons)} personas del grupo`:'La muestra no permite cuantificar esta cola.';
   $('threshold-interval').textContent=Number.isFinite(e.lo)&&Number.isFinite(e.hi)?`IC 95% de la proporción: ${pct(e.lo)} a ${pct(e.hi)}`:'Intervalo de confianza no estimable en este punto.';
   $('threshold-quality').className='quality-box '+(e.q===2?'sufficient':'limited');
   $('threshold-quality').innerHTML=`<strong>${qualityText(e)}</strong><br>${num(e.n)} de ${num(d.n)} encuestados cumplen el umbral.${e.q===0?' No implica que no existan personas con esos ingresos.':e.q===1?' Interpreta la cifra con cautela.':''}`;
 }
 function miniHist(d,ymax,w=210){
   const h=93,L=25,R=4,T=5,B=22,xx=i=>L+i/30*(w-L-R),yy=v=>h-B-v/ymax*(h-B-T);
   let b=line(L,h-B,w-R,h-B,color.line)+line(L,yy(ymax),w-R,yy(ymax),color.line)+txt(L-4,yy(ymax)+3,num(ymax)+'%','end',8)+txt(L-4,h-B+3,'0','end',8);
   for(let i=0;i<30;i++)b+=`<rect x="${xx(i)+.2}" y="${yy(d.hist[i])}" width="${Math.max(.4,(w-L-R)/30-.8)}" height="${Math.max(0,h-B-yy(d.hist[i]))}" fill="${i*100000>=state.amount?color.teal:'#8fae9f'}"/>`;
   for(let i=0;i<=3;i++)b+=txt(xx(i*10),h-5,'$'+i+'M','middle',10);
   return svgShell(w,h,'Distribución de ingresos hasta tres millones',b,'La escala vertical es la misma en las cinco tarjetas.');
 }
 function renderAges(){
   const ages=DATA.meta.age.filter(a=>a.id!=='all'),ds=ages.map(a=>domain(state.occupation,state.sex,a.id));
   const ymax=roundUp(Math.max(...ds.flatMap(d=>d.hist.slice(0,30)))*1.05);
   $('age-context').textContent=label('occupation',state.occupation)+' · '+label('sex',state.sex)+'. Histogramas hasta $3 millones, con la misma escala vertical.';
   $('age-panels').innerHTML=ages.map((a,i)=>{const d=ds[i],e=eventAt(d),q=poorDomain(d)||e.q<2;return `<button class="age-panel" data-age-panel="${a.id}" aria-pressed="${a.id===state.age}" aria-label="Explorar ${esc(a.label)}. Mediana aproximada ${money(d.median)}. ${num(d.n)} encuestados."><div class="age-header"><span>${esc(a.label)}</span><span aria-hidden="true">↗</span></div><div class="age-median">≈ ${money(d.median)}</div><p class="age-meta">Ingreso mediano<br>Promedio ≈ ${money(d.mean)}${d.meanQ<2?' · exploratorio':''}</p><div class="spark">${miniHist(d,ymax)}</div><div class="age-threshold"><span class="label">Gana ≥ ${exactMoney(state.amount)}</span><strong>${e.n?'≈ '+pct(e.p):'Sin casos'}</strong><small>${e.n?'≈ '+people(e.persons)+' personas':'No equivale a cero en la población'}<br>${num(d.n)} encuestados en el grupo</small></div>${q?`<span class="limited-tag">${poorDomain(d)?'Muestra del grupo limitada':e.n?'Umbral exploratorio':'Sin casos para este umbral'}</span>`:''}</button>`;}).join('');
   // Match each sparkline to its actual container without shrinking axis text.
   $('age-panels').querySelectorAll('.spark').forEach((el,i)=>{el.innerHTML=miniHist(ds[i],ymax,Math.max(115,Math.round(el.getBoundingClientRect().width||180)));});
   // The card is the keyboard action. Nested sparkline SVGs need no extra tab stop.
   $('age-panels').querySelectorAll('svg').forEach(s=>s.removeAttribute('tabindex'));
 }
 function renderRanking(){
   $('occupation-context').textContent=label('age',state.age)+' · '+label('sex',state.sex)+'. '+(state.rank==='threshold'?'Personas que ganan ≥ '+exactMoney(state.amount)+', dentro de cada ocupación.':'Misma edad y sexo en las nueve ocupaciones.');
   const rows=DATA.meta.occupation.filter(o=>o.id!=='all').map(o=>{const d=domain(o.id,state.sex,state.age),e=eventAt(d);return{o,d,e,v:state.rank==='threshold'?e.p:d[state.rank]};}).sort((a,b)=>b.v-a.v);
   const max=Math.max(...rows.map(r=>r.v),1);
   $('occupation-ranking').innerHTML=rows.map(({o,d,e,v})=>{const limited=state.rank==='threshold'?e.q<2:state.rank==='mean'?d.meanQ<2:poorDomain(d);const no=state.rank==='threshold'&&e.n===0;return `<button class="rank-row ${o.id===state.occupation?'active':''}" data-rank-occupation="${o.id}" aria-label="Seleccionar ${esc(o.label)}. ${no?'Sin casos observados':state.rank==='threshold'?'Aproximadamente '+pct(v):'Aproximadamente '+money(v)}"><span class="rank-label">${esc(o.label)}</span><span class="rank-track" aria-hidden="true"><span class="rank-fill" style="display:block;width:${Math.max(0,v/max*100)}%"></span></span><span class="rank-value">${no?'Sin casos':'≈ '+(state.rank==='threshold'?pct(v):money(v))}${limited&&!no?'*':''}</span><span class="rank-n">n = ${num(d.n)}${limited?'<span class="limited-text">Exploratorio</span>':''}</span></button>`;}).join('');
 }
 function render(){
   const d=domain();
   $('occupation').value=state.occupation;$('rank-metric').value=state.rank;
   for(const b of document.querySelectorAll('[data-sex]'))b.setAttribute('aria-pressed',String(b.dataset.sex===state.sex));
   for(const b of document.querySelectorAll('[data-age]'))b.setAttribute('aria-pressed',String(b.dataset.age===state.age));
   for(const b of document.querySelectorAll('[data-range]'))b.setAttribute('aria-pressed',String(+b.dataset.range===state.range));
   for(const b of document.querySelectorAll('[data-survival-scale]'))b.setAttribute('aria-pressed',String(b.dataset.survivalScale===state.survivalScale));
   $('selection-label').textContent=[label('occupation',state.occupation),label('sex',state.sex),label('age',state.age)].join('  ·  ');
   $('median').innerHTML='<span class="approx">≈</span>'+money(d.median);
   $('mean').innerHTML='<span class="approx">≈</span>'+money(d.mean);
   $('population').innerHTML='<span class="approx">≈</span>'+people(d.N);
   $('mean-note').textContent=Number.isFinite(d.meanLo)&&Number.isFinite(d.meanHi)?`IC 95%: ${money(d.meanLo)} a ${money(d.meanHi)}${d.meanQ<2?' · Exploratorio':''}`:'Intervalo de confianza no estimable.';
   $('population-note').textContent=num(d.n)+' encuestados en este grupo.';
   $('sample-warning').hidden=!poorDomain(d);
   $('sample-warning').textContent=`Muestra limitada: este grupo tiene ${num(d.n)} encuestados y ${num(d.df)} grados de libertad. Sus cifras son exploratorias. Las colas de ingresos pueden apoyarse en muy pocas observaciones.`;
   renderThreshold(d);renderDistribution(d);renderSurvival(d);renderAges();renderRanking();
 }
 function setState(change){
   for(const k of ['occupation','sex','age'])if(change[k]!==undefined&&valid(k,String(change[k])))state[k]=String(change[k]);
   if(change.amount!==undefined&&Number.isFinite(Number(change.amount)))state.amount=Math.max(0,Math.min(20000000,Math.round(Number(change.amount)/50000)*50000));
   if([3,21].includes(change.range))state.range=change.range;
   if(['median','mean','threshold'].includes(change.rank))state.rank=change.rank;
   if(['linear','log'].includes(change.survivalScale))state.survivalScale=change.survivalScale;
   render();
 }
 function toast(message){$('toast').textContent=message;$('toast').classList.add('visible');clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('toast').classList.remove('visible'),3600);}
 function download(name,content,type){const blob=new Blob([content],{type}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 function csvText(){
   const rows=[['vista','ocupacion','sexo','edad','encuestados_grupo','personas_expandidas_grupo','ingreso_mediano_clp','ingreso_promedio_clp','ee_media_clp','umbral_clp','porcentaje_mayor_o_igual_umbral','personas_mayor_o_igual_umbral','encuestados_mayor_o_igual_umbral','ic95_inferior_porcentaje','ic95_superior_porcentaje','precision_umbral']];
   function add(view,o,s,a){const d=domain(o,s,a),e=eventAt(d);rows.push([view,label('occupation',o),label('sex',s),label('age',a),d.n,d.N,d.median,d.mean,d.meanSE,state.amount,e.p,e.persons,e.n,e.lo,e.hi,qualityText(e)]);}
   add('seleccion',state.occupation,state.sex,state.age);
   for(const a of DATA.meta.age.filter(x=>x.id!=='all'))add('comparacion_edades',state.occupation,state.sex,a.id);
   for(const o of DATA.meta.occupation.filter(x=>x.id!=='all'))add('comparacion_ocupaciones',o.id,state.sex,state.age);
   return '\uFEFF'+rows.map(r=>r.map(v=>'"'+String(v===null?'':v).replace(/"/g,'""')+'"').join(';')).join('\r\n');
 }
 $('occupation').innerHTML=DATA.meta.occupation.map(o=>`<option value="${o.id}">${esc(o.label)}</option>`).join('');
 $('age-buttons').innerHTML=DATA.meta.age.map(a=>`<button data-age="${a.id}" aria-pressed="false" aria-label="${esc(a.label)}">${ageShort(a.id)}</button>`).join('');
 $('universe-counts').textContent=`“Total (20+)” agrupa los cinco tramos, no toda la muestra ESI. El archivo original contiene ${num(DATA.meta.nSourceRecords)} registros. De ellos, ${num(DATA.meta.nAllOccupied)} son ocupados de referencia de todas las edades. Este dashboard incluye ${num(DATA.meta.n20Plus)} de 20 años o más y excluye ${num(DATA.meta.excludedUnder20)} menores de 20. Los filtros de ocupación y sexo reducen ese universo.`;
 $('occupation').addEventListener('change',e=>setState({occupation:e.target.value}));
 $('sex-buttons').addEventListener('click',e=>{const b=e.target.closest('[data-sex]');if(b)setState({sex:b.dataset.sex});});
 $('age-buttons').addEventListener('click',e=>{const b=e.target.closest('[data-age]');if(b)setState({age:b.dataset.age});});
 $('range-buttons').addEventListener('click',e=>{const b=e.target.closest('[data-range]');if(b)setState({range:+b.dataset.range});});
 $('survival-scale-buttons').addEventListener('click',e=>{const b=e.target.closest('[data-survival-scale]');if(b)setState({survivalScale:b.dataset.survivalScale});});
 $('amount').addEventListener('change',e=>{const raw=Number(e.target.value);if(!Number.isFinite(raw)||e.target.value.trim()===''){e.target.value=state.amount;return;}setState({amount:raw});if(raw!==state.amount)toast('Monto ajustado a '+exactMoney(state.amount)+'. Las consultas usan pasos de $50.000.');});
 $('amount-slider').addEventListener('input',e=>setState({amount:+e.target.value}));
 $('quick-amounts').addEventListener('click',e=>{const b=e.target.closest('[data-amount]');if(b)setState({amount:+b.dataset.amount});});
 $('age-panels').addEventListener('click',e=>{const b=e.target.closest('[data-age-panel]');if(b){setState({age:b.dataset.agePanel});$('explorar').scrollIntoView?.({behavior:'smooth',block:'start'});$('age-buttons').querySelector(`[data-age="${state.age}"]`)?.focus({preventScroll:true});}});
 $('occupation-ranking').addEventListener('click',e=>{const b=e.target.closest('[data-rank-occupation]');if(b){setState({occupation:b.dataset.rankOccupation});$('explorar').scrollIntoView?.({behavior:'smooth',block:'start'});$('occupation').focus({preventScroll:true});}});
 $('rank-metric').addEventListener('change',e=>setState({rank:e.target.value}));
 $('reset').addEventListener('click',()=>setState(DEFAULT));
 $('about').addEventListener('click',()=>{$('method-details').open=true;$('method').scrollIntoView?.({behavior:'smooth',block:'start'});$('method-details').querySelector('summary').focus({preventScroll:true});});
 $('export-csv').addEventListener('click',()=>{download('ingresos_ESI2025_vista.csv',csvText(),'text/csv;charset=utf-8');toast('Datos de esta vista descargados. Las cifras del CSV conservan la precisión del cálculo.');});
 $('save').addEventListener('click',()=>{const clone=document.documentElement.cloneNode(true);clone.querySelector('#initial-state').textContent=JSON.stringify(state);clone.querySelectorAll('.tooltip,[data-web-analytics],script[src*="googletagmanager.com"],script[src*="google-analytics.com"]').forEach(t=>t.remove());clone.querySelector('meta[http-equiv="Content-Security-Policy"]').setAttribute('content',"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data: blob:; connect-src 'none'; base-uri 'none'; form-action 'none'");clone.querySelector('#privacy-note').textContent='Archivo autocontenido. Funciona sin conexión y no envía información.';clone.querySelector('#toast').classList.remove('visible');download('Ingresos_Chile_ESI2025.html','<!doctype html>\n'+clone.outerHTML,'text/html;charset=utf-8');toast('Copia guardada con tus filtros. Comparte ese archivo para abrirlo sin conexión.');});
 $('print').addEventListener('click',()=>{const old=$('method-details').open;$('method-details').open=true;window.print();$('method-details').open=old;});
 let resizeTimer;window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{renderDistribution(domain());renderSurvival(domain());renderAges();},150);});
 render();
 window.ESI_DASHBOARD=Object.freeze({getState:()=>({...state}),setState,eventAt,getDomain:domain,csvText,render,meta:DATA.meta});
})();
