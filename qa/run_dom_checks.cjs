const fs=require('fs');
const path=require('path');
const assert=require('assert/strict');
const {JSDOM,VirtualConsole}=require('jsdom');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'Ingresos_Chile_ESI2025.html'),'utf8');
const errors=[],downloads=[];
const makeDOM=(source,width=1440)=>{
 const console=new VirtualConsole();console.on('jsdomError',e=>errors.push(e.message));
 return new JSDOM(source,{runScripts:'dangerously',url:'file:///Ingresos_Chile_ESI2025.html',pretendToBeVisual:true,virtualConsole:console,beforeParse(w){
   w.HTMLElement.prototype.scrollIntoView=function(){};
   w.HTMLElement.prototype.getBoundingClientRect=function(){let x=0,y=0,ww=width;if(this.id==='distribution')ww=width<800?width-70:width*.55-80;if(this.id==='survival')ww=width-130;if(this.className==='spark')ww=width<520?(width-70)/2:width<1150?(width-160)/3:(width-180)/5;return{width:ww,height:0,left:x,top:y,right:x+ww,bottom:y};};
   w.URL.createObjectURL=b=>{downloads.push(b);return'blob:offline-test';};w.URL.revokeObjectURL=()=>{};
   w.Blob=class{constructor(parts,opts){this.parts=parts;this.type=opts.type;}};
   w.HTMLAnchorElement.prototype.click=function(){};
   w.print=()=>{w.printCalls=(w.printCalls||0)+1;};
 }});
};
const dom=makeDOM(html),w=dom.window,d=w.document,api=w.ESI_DASHBOARD;
assert(api,'App initialized');
assert.equal(d.querySelectorAll('#occupation option').length,10);
const ageIds=['15_19','20_24','25_29','30_34','35_39','40_44','45_49','50_54','55_59','60_64','65_69','70_74','75_mas'];
assert.deepEqual([...d.querySelectorAll('#age-buttons button')].map(b=>b.dataset.age),['all',...ageIds]);
assert.deepEqual([...d.querySelectorAll('.age-panel')].map(b=>b.dataset.agePanel),ageIds);
assert.equal(d.querySelectorAll('.rank-row').length,9);
assert.equal(api.getDomain().n,38729);
assert.equal(api.getDomain().n,api.meta.nAllOccupied);
assert.equal(api.getDomain().median,680000);
assert(Math.abs(api.getDomain().mean-962944.6993)<.001);
assert(d.getElementById('population-note').textContent.includes('38.729'));
assert(d.getElementById('median').textContent.includes('680.000'));
assert.equal(d.querySelector('[data-age="all"]').textContent,'Todas las edades');
assert(d.getElementById('universe-note').textContent.includes('desde los 15 años'));
for(const value of ['93.458','38.729','349'])assert(d.getElementById('universe-counts').textContent.includes(value));
assert.equal(api.getDomain('all','all','15_19').n,api.meta.n15To19);
assert.equal(api.getDomain('all','all','15_19').median,300000);
assert(Math.abs(api.getDomain('all','all','15_19').mean-337981.9329)<.001);
assert.equal(api.getState().survivalScale,'linear');
const beforeScale=api.csvText();
d.querySelector('[data-survival-scale="log"]').click();
assert.equal(api.getState().survivalScale,'log');
assert.equal(d.querySelector('[data-survival-scale="log"]').getAttribute('aria-pressed'),'true');
assert.equal(api.csvText(),beforeScale,'Scale is display only');
const ticks=[...d.querySelectorAll('#survival [data-log-tick]')];
assert.equal(+ticks.at(-1).dataset.logTick,100);
assert(ticks.slice(1).every((t,i)=>Math.abs(+t.dataset.logTick/+ticks[i].dataset.logTick-10)<1e-9));
const gaps=ticks.slice(1).map((t,i)=>+ticks[i].getAttribute('y')-+t.getAttribute('y'));
assert(gaps.every(g=>Math.abs(g-gaps[0])<1e-8),'Equal log spacing for factors of10');
assert(d.getElementById('survival-scale-note').textContent.includes('×10'));
assert(d.querySelectorAll('#survival .survival-band').length>0);
for(const band of d.querySelectorAll('#survival .survival-band'))assert(/[HV]/.test(band.getAttribute('d'))&&!/[CQ]/.test(band.getAttribute('d')));
api.setState({amount:20000000});
assert(d.querySelector('#survival .survival-selected'),'Positive extreme tail remains visible');
assert.equal(d.querySelectorAll('script[src],link[rel=stylesheet],img[src]:not([src^="data:image/"]),iframe').length,0);
assert(!/\bfetch\s*\(|XMLHttpRequest|WebSocket|https?:\/\/[^'"\s]*\.(?:js|css|woff)/.test(html),'No external runtime dependencies');
// Income bars use the all-Chile median even when filtering sex or age.
const nationalMedian=api.getDomain('all','all','all').median;
for(const [sex,age,metric] of [['all','all','median'],['2','75_mas','median'],['1','35_39','mean']]){
 api.setState({occupation:'2',sex,age,rank:metric});
 assert.equal(d.querySelector('#rank-reference .cargo-row-head b').textContent,'1×');
 const rows=[...d.querySelectorAll('#occupation-ranking .rank-row')];
 assert.equal(rows.length,9);
 const values=rows.map(row=>api.getDomain(row.dataset.rankOccupation,sex,age)[metric]);
 assert.deepEqual(values,[...values].sort((a,b)=>b-a));
 const maximum=Math.max(nationalMedian,...values);
 assert(Math.abs(parseFloat(d.querySelector('#rank-reference .rank-fill').style.width)-100*nationalMedian/maximum)<1e-8);
 for(const [i,row] of rows.entries()){
  const value=values[i],sample=api.getDomain(row.dataset.rankOccupation,sex,age);
  assert.equal(+row.dataset.multiple,value/nationalMedian);
  assert.equal(+row.dataset.value,value);
  assert(Math.abs(parseFloat(row.querySelector('.rank-fill').style.width)-100*value/maximum)<1e-8);
  assert.equal(!!row.querySelector('.limited-text'),metric==='median'?sample.n<60||sample.df<9:sample.meanQ<2);
 }
 assert.equal(d.querySelector('#occupation-ranking [aria-pressed="true"]').dataset.rankOccupation,'2');
}
api.setState({occupation:'all',sex:'all',age:'all',amount:20000000,rank:'threshold'});
assert(!d.querySelector('#occupation-ranking [data-multiple]'));
assert(d.querySelector('#rank-reference .rank-fill').style.width.endsWith('%'));
assert(d.getElementById('rank-title').textContent.includes('$20.000.000'));
for(const row of d.querySelectorAll('#occupation-ranking .rank-row')){
 const e=api.eventAt(api.getDomain(row.dataset.rankOccupation,'all','all'));
 if(!e.n){assert.equal(row.querySelector('.rank-value').textContent,'Sin casos observados');assert(!row.hasAttribute('data-value'));}
 else assert.equal(parseFloat(row.querySelector('.rank-fill').style.width),e.p);
}
api.setState({rank:'median'});
// Exercise actual controls and representative edge cases.
d.getElementById('occupation').value='6';d.getElementById('occupation').dispatchEvent(new w.Event('change'));
d.querySelector('[data-sex="2"]').click();d.querySelector('[data-age="20_24"]').click();
assert.equal(api.getDomain().n,2);assert.equal(d.getElementById('sample-warning').hidden,false);
assert.equal(d.getElementById('threshold-percent').textContent,'Sin casos observados');
assert(!d.getElementById('threshold-people').textContent.includes('0 personas'));
assert(d.getElementById('distribution-note').textContent.includes('No se observaron casos'));
assert.equal(d.querySelectorAll('#survival .survival-curve,#survival .survival-band,#survival .survival-selected').length,0);
assert(d.querySelector('#survival svg').textContent.includes('Sin casos observados'));
assert(d.getElementById('survival-scale-note').textContent.includes('Desde $1.000.000 no hay casos observados'));
d.getElementById('amount').value='1234567';d.getElementById('amount').dispatchEvent(new w.Event('change'));
assert.equal(api.getState().amount,1250000);
d.getElementById('amount').value='';d.getElementById('amount').dispatchEvent(new w.Event('change'));
assert.equal(api.getState().amount,1250000);
api.setState({amount:-100000});assert.equal(api.getState().amount,0);
assert.equal(api.eventAt(api.getDomain()).p,100);
api.setState({amount:99999999});assert.equal(api.getState().amount,20000000);
d.querySelector('[data-amount="2000000"]').click();assert.equal(api.getState().amount,2000000);
d.getElementById('amount-slider').value=5000000;d.getElementById('amount-slider').dispatchEvent(new w.Event('input'));assert.equal(api.getState().amount,5000000);
d.querySelector('[data-range="21"]').click();assert.equal(api.getState().range,21);assert.equal(d.querySelectorAll('#distribution rect').length,210);
d.querySelector('[data-age-panel="40_44"]').click();assert.equal(api.getState().age,'40_44');
d.querySelector('[data-rank-occupation="1"]').click();assert.equal(api.getState().occupation,'1');
d.getElementById('rank-metric').value='threshold';d.getElementById('rank-metric').dispatchEvent(new w.Event('change'));assert.equal(api.getState().rank,'threshold');
const helpLink=d.getElementById('about');
assert.equal(helpLink.tagName,'A');assert.equal(helpLink.target,'_blank');
assert.equal(d.querySelector(helpLink.hash).closest('details').id,'method-details');
d.getElementById('print').click();assert.equal(w.printCalls,1);
// No respondents is different from real observations below the threshold or at $0.
const emptyKeys=new Set(['1|all|15_19','1|1|15_19','1|2|15_19','8|2|15_19']);
const csvRow=text=>text.split('";"').map((v,i,a)=>v.replace(i===0?/^"/:i===a.length-1?/"$/:/^$/,''));
const rowForSelection=()=>csvRow(api.csvText().split('\r\n')[1]);
for(const key of emptyKeys){
 const [occupation,sex,age]=key.split('|');api.setState({occupation,sex,age,rank:'median',amount:0});
 const e=api.eventAt(api.getDomain());assert.equal(e.n,0);assert.equal(e.p,null);assert.equal(e.persons,null);
 assert.equal(d.getElementById('threshold-percent').textContent,'Sin observaciones');
 assert.equal(d.getElementById('population-note').textContent,'0 encuestados en este grupo.');
 for(const id of ['median','mean','population'])assert.equal(d.getElementById(id).textContent,'—');
 assert.equal(d.querySelectorAll('#distribution rect,#survival .survival-curve,#survival .survival-selected').length,0);
 assert.match(d.getElementById('distribution').textContent,/Sin observaciones/);
 assert(d.querySelector('#age-profile-context').textContent.includes('15–19 años'));
 const firstRow=d.querySelector('#age-profile-table tbody tr');
 assert.equal(firstRow.cells[1].textContent,'—');assert.equal(firstRow.cells[5].textContent,'0');
 assert.equal(firstRow.cells[6].textContent,'Sin observaciones');
 assert(!d.querySelector('#age-peaks').textContent.includes('15–19'));
 assert.equal(d.querySelector('[data-rank-occupation="'+occupation+'"] .rank-value').textContent,'Sin observaciones');
 assert.equal(d.querySelector('[data-rank-occupation="'+occupation+'"] .rank-n').textContent,'');
 for(const tr of d.querySelectorAll('#sex-comparison tbody tr')){
  assert.equal(tr.cells[1].textContent,'Sin observaciones');
  if(occupation==='1')assert.equal(tr.cells[2].textContent,'Sin observaciones');
 }
 const chart=d.querySelector('#age-profile svg'),tip=d.querySelector('#age-profile .tooltip');
 for(const [key,expected] of [['Home','15–19 años'],['ArrowRight','20–24 años'],['End','75 años o más']]){
  chart.dispatchEvent(new w.KeyboardEvent('keydown',{key,bubbles:true}));
  assert.equal(tip.querySelector('strong').textContent,expected);
  if(key==='Home')assert.equal(tip.textContent,expected+'Sin observaciones');
 }
 chart.dispatchEvent(new w.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
 assert(!tip.classList.contains('visible'));
 const selected=rowForSelection();assert.equal(selected[4],'0');assert.equal(selected[14],'0');
 for(const c of [5,6,7,8,9,10,12,13,15,16])assert.equal(selected[c],'');
 assert.equal(selected[17],'Sin observaciones');
}
// The young cohort keeps all nine rows; the gold 1× bar always uses all Chile.
for(const metric of ['median','mean','threshold']){
 api.setState({occupation:'8',sex:'2',age:'15_19',amount:1000000,rank:metric});
 const rows=[...d.querySelectorAll('[data-rank-occupation]')];
 assert.equal(rows.length,9);
 const realValues=[];
 for(const row of rows){
  const dd=api.getDomain(row.dataset.rankOccupation,'2','15_19');
  if(!dd.n){assert(!row.hasAttribute('data-value'));assert.equal(row.querySelector('.rank-value').textContent,'Sin observaciones');continue;}
  const evt=api.eventAt(dd);
  if(metric==='threshold'&&!evt.n){assert(!row.hasAttribute('data-value'));assert.equal(row.querySelector('.rank-value').textContent,'Sin casos observados');continue;}
  const value=metric==='threshold'?evt.p:dd[metric];
  realValues.push(value);assert.equal(+row.dataset.value,value);
  if(metric==='threshold')assert(!row.hasAttribute('data-multiple'));
  else assert.equal(+row.dataset.multiple,value/nationalMedian);
 }
 assert.deepEqual(realValues,[...realValues].sort((a,b)=>b-a));
}
api.setState({occupation:'4',sex:'2',age:'75_mas',amount:0});
assert.equal(api.getDomain().n,1);
assert(d.getElementById('median').textContent.includes('$0'));
assert(d.getElementById('mean').textContent.includes('$0'));
assert(d.getElementById('threshold-percent').textContent.includes('100%'));
assert(d.getElementById('sample-warning').textContent.includes('Muestra limitada'));
assert.equal(rowForSelection()[6],'0');
assert.equal(d.querySelector('#age-profile .age-median-point[data-age-id="75_mas"]').dataset.value,'0');

// All 420 selection domains on both scales; no empty age can create a point or peak.
let checked=0;
const foundEmpty=new Set();
for(const scale of ['linear','log'])for(const o of api.meta.occupation)for(const s of api.meta.sex)for(const a of api.meta.age){
 api.setState({occupation:o.id,sex:s.id,age:a.id,survivalScale:scale,amount:[0,1000000,5000000,20000000][checked%4]});
 const dd=api.getDomain(),e=api.eventAt(dd);
 assert(d.getElementById('population-note').textContent.includes(new Intl.NumberFormat('es-CL').format(dd.n)));
 assert.equal(d.getElementById('sample-warning').hidden,!(dd.n<60||dd.df<9));
 if(!dd.n){foundEmpty.add([o.id,s.id,a.id].join('|'));assert.equal(d.getElementById('threshold-percent').textContent,'Sin observaciones');}
 else if(!e.n)assert.equal(d.getElementById('threshold-percent').textContent,'Sin casos observados');
 else assert(!d.getElementById('threshold-percent').textContent.includes('Sin'));
 assert.equal(d.querySelectorAll('.age-panel').length,13);
 assert.equal(d.querySelectorAll('.rank-row').length,9);
 assert.deepEqual([...d.querySelectorAll('#age-profile [data-age-tick]')].map(t=>t.dataset.ageTick),ageIds);
 const measured=ageIds.filter(age=>api.getDomain(o.id,s.id,age).n>0);
 for(const field of ['median','mean']){
  const points=[...d.querySelectorAll('#age-profile .age-'+field+'-point')];
  assert.deepEqual(points.map(p=>p.dataset.ageId),measured);
  for(const point of points)assert.equal(+point.dataset.value,api.getDomain(o.id,s.id,point.dataset.ageId)[field]);
 }
 if(scale==='log')assert.equal(d.querySelectorAll('#survival [data-log-tick]').length,ticks.length);
 if(e.n===0)assert.equal(d.querySelectorAll('#survival .survival-selected').length,0);
 for(const svg of d.querySelectorAll('.plot svg,.spark svg')){
  assert(!/NaN|Infinity|undefined/.test(svg.outerHTML));
  for(const el of svg.querySelectorAll('[height],[width]')){for(const key of ['height','width'])if(el.hasAttribute(key))assert(+el.getAttribute(key)>=0);}
 }
 checked++;
}
assert.equal(checked,840);assert.deepEqual(foundEmpty,emptyKeys);
api.setState({occupation:'8',sex:'2',age:'15_19',amount:2000000,rank:'mean',range:3,survivalScale:'log'});
d.getElementById('save').click();const saved=downloads.at(-1).parts.join('');assert(saved.startsWith('<!doctype html>'));
const reopened=makeDOM(saved),ra=reopened.window.ESI_DASHBOARD;
assert.deepEqual(JSON.parse(JSON.stringify(ra.getState())),JSON.parse(JSON.stringify(api.getState())));
assert.equal(ra.getDomain().n,0);
assert.equal(reopened.window.document.getElementById('threshold-percent').textContent,'Sin observaciones');reopened.window.close();
d.getElementById('export-csv').click();const csv=downloads.at(-1).parts.join('');
const exported=csv.split('\r\n');assert.equal(exported.length,26);
assert.equal(exported.filter(s=>s.startsWith('"comparacion_edades"')).length,13);
assert(csv.includes('comparacion_ocupaciones')&&csv.includes('2000000')&&csv.includes('percentil25_clp')&&csv.includes('percentil75_clp'));
d.getElementById('reset').click();assert.equal(api.getState().occupation,'all');assert.equal(api.getState().sex,'all');assert.equal(api.getState().age,'all');assert.equal(api.getState().amount,1000000);assert.equal(api.getState().survivalScale,'linear');
const graph=d.querySelector('#distribution svg');graph.dispatchEvent(new w.KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));assert(d.querySelector('#distribution .tooltip').classList.contains('visible'));
const width=+graph.getAttribute('viewBox').split(' ')[2];
for(let bin=0;bin<30;bin++){
 graph.dispatchEvent(new w.MouseEvent('pointermove',{clientX:46+(bin+.5)*(width-60)/30,clientY:100}));
 assert(d.querySelector('#distribution .tooltip strong').textContent.startsWith('$'+new Intl.NumberFormat('es-CL').format(bin*100000)+' a menos de'));
}
assert.equal(errors.length,0,errors.join('\n'));
// Save hydrated snapshots for non-browser PDF/SVG layout inspection.
const snap=w.document.documentElement.cloneNode(true);snap.querySelectorAll('script,.tooltip,noscript').forEach(n=>n.remove());snap.querySelector('#toast').remove();snap.querySelector('#method-details').removeAttribute('open');
fs.writeFileSync(path.join(__dirname,'snapshot_desktop.html'),'<!doctype html>\n'+snap.outerHTML);
for(const id of ['distribution','survival','age-profile'])fs.writeFileSync(path.join(__dirname,`${id}.svg`),d.querySelector(`#${id} svg`).outerHTML);
api.setState({survivalScale:'log'});fs.writeFileSync(path.join(__dirname,'survival_log.svg'),d.querySelector('#survival svg').outerHTML);
const logSnap=d.documentElement.cloneNode(true);logSnap.querySelectorAll('script,.tooltip,noscript').forEach(n=>n.remove());logSnap.querySelector('#toast').remove();fs.writeFileSync(path.join(__dirname,'snapshot_desktop_log.html'),'<!doctype html>\n'+logSnap.outerHTML);
const mobile=makeDOM(html,390);assert(mobile.window.ESI_DASHBOARD);const ms=mobile.window.document.documentElement.cloneNode(true);ms.querySelectorAll('script,.tooltip,noscript').forEach(n=>n.remove());ms.querySelector('#toast').remove();fs.writeFileSync(path.join(__dirname,'snapshot_mobile.html'),'<!doctype html>\n'+ms.outerHTML);
mobile.window.ESI_DASHBOARD.setState({survivalScale:'log'});const mlog=mobile.window.document.documentElement.cloneNode(true);mlog.querySelectorAll('script,.tooltip,noscript').forEach(n=>n.remove());mlog.querySelector('#toast').remove();fs.writeFileSync(path.join(__dirname,'snapshot_mobile_log.html'),'<!doctype html>\n'+mlog.outerHTML);
mobile.window.close();
const report={pass:true,fiveYearAgeBands:true,ageProfileValuesMatchAllDomains:true,ageProfilePercentiles:'P25–P75, dispersion not confidence',domainScaleCombinationsRendered:checked,domainsRendered:checked/2,scales:['linear','log'],controls:'occupation, sex, age, amount input, slider, quick amounts, range, ranking, survival scale, reset, help, keyboard tooltip',equalLogTickSpacing:true,constantLogAxisAcrossGroups:true,stepConfidenceBand:true,noNetworkDependencies:true,savedHTMLReopenedWithScale:true,csvExportRows:exported.length-1,scaleDoesNotChangeCSV:true,allReferenceWorkers:true,ageFilterIncludes15To19:true,emptyGroupCount:foundEmpty.size,emptyGroupsDifferFromObservedZeroAndNoHits:true,emptyTailNotReportedAsPopulationZero:true,finiteSVGGeometry:true,jsErrors:errors,verificationLimit:'DOM and SVG checks via jsdom; this test does not assess pixel layout or measure a real device.'};
fs.writeFileSync(path.join(__dirname,'validacion_interfaz.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));w.close();
