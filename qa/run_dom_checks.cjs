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
assert.equal(d.querySelectorAll('#age-buttons button').length,6);
assert.equal(d.querySelectorAll('.age-panel').length,5);
assert.equal(d.querySelectorAll('.rank-row').length,9);
assert.equal(api.getDomain().n,38380);
assert(d.getElementById('population-note').textContent.includes('38.380'));
assert(d.getElementById('median').textContent.includes('688.000'));
assert.equal(d.querySelector('[data-age="all"]').textContent,'Total (20+)');
assert(d.getElementById('universe-note').textContent.includes('Excluye a los menores de 20'));
for(const value of ['93.458','38.729','38.380','349'])assert(d.getElementById('universe-counts').textContent.includes(value));
assert.equal(api.meta.n20Plus+api.meta.excludedUnder20,api.meta.nAllOccupied);
assert.equal(api.getState().survivalScale,'linear');
const beforeScale=api.csvText();
d.querySelector('[data-survival-scale="log"]').click();
assert.equal(api.getState().survivalScale,'log');
assert.equal(d.querySelector('[data-survival-scale="log"]').getAttribute('aria-pressed'),'true');
assert.equal(api.csvText(),beforeScale,'Scale is display only');
const ticks=[...d.querySelectorAll('#survival [data-log-tick]')];
assert.deepEqual(ticks.map(t=>+t.dataset.logTick),[.0001,.001,.01,.1,1,10,100]);
const gaps=ticks.slice(1).map((t,i)=>+ticks[i].getAttribute('y')-+t.getAttribute('y'));
assert(gaps.every(g=>Math.abs(g-gaps[0])<1e-8),'Equal log spacing for factors of10');
assert(d.getElementById('survival-scale-note').textContent.includes('×10'));
assert(d.querySelectorAll('#survival .survival-band').length>0);
for(const band of d.querySelectorAll('#survival .survival-band'))assert(/[HV]/.test(band.getAttribute('d'))&&!/[CQ]/.test(band.getAttribute('d')));
api.setState({amount:20000000});
assert(d.querySelector('#survival .survival-selected'),'Positive extreme tail remains visible');
assert.equal(d.querySelectorAll('script[src],link[rel=stylesheet],img[src],iframe').length,0);
assert(!/\bfetch\s*\(|XMLHttpRequest|WebSocket|https?:\/\/[^'"\s]*\.(?:js|css|woff)/.test(html),'No external runtime dependencies');
// Exercise actual controls and representative edge cases.
d.getElementById('occupation').value='6';d.getElementById('occupation').dispatchEvent(new w.Event('change'));
d.querySelector('[data-sex="2"]').click();d.querySelector('[data-age="20_29"]').click();
assert.equal(api.getDomain().n,8);assert.equal(d.getElementById('sample-warning').hidden,false);
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
d.querySelector('[data-age-panel="40_49"]').click();assert.equal(api.getState().age,'40_49');
d.querySelector('[data-rank-occupation="1"]').click();assert.equal(api.getState().occupation,'1');
d.getElementById('rank-metric').value='threshold';d.getElementById('rank-metric').dispatchEvent(new w.Event('change'));assert.equal(api.getState().rank,'threshold');
d.getElementById('about').click();assert.equal(d.getElementById('method-details').open,true);
d.getElementById('print').click();assert.equal(w.printCalls,1);
// All 180 selection domains must render their own denominators and valid SVG geometry.
let checked=0;
for(const scale of ['linear','log'])for(const o of api.meta.occupation)for(const s of api.meta.sex)for(const a of api.meta.age){
 api.setState({occupation:o.id,sex:s.id,age:a.id,survivalScale:scale,amount:[0,1000000,5000000,20000000][checked%4]});
 const dd=api.getDomain(),e=api.eventAt(dd);
 assert(d.getElementById('population-note').textContent.includes(new Intl.NumberFormat('es-CL').format(dd.n)));
 assert.equal(d.getElementById('sample-warning').hidden,!(dd.n<60||dd.df<9));
 if(e.n===0)assert.equal(d.getElementById('threshold-percent').textContent,'Sin casos observados');
 else assert(!d.getElementById('threshold-percent').textContent.includes('Sin casos'));
 assert.equal(d.querySelectorAll('.age-panel').length,5);
 assert.equal(d.querySelectorAll('.rank-row').length,9);
 if(scale==='log')assert.equal(d.querySelectorAll('#survival [data-log-tick]').length,7);
 if(e.n===0)assert.equal(d.querySelectorAll('#survival .survival-selected').length,0);
 for(const svg of d.querySelectorAll('.plot svg,.spark svg')){
  assert(!/NaN|Infinity|undefined/.test(svg.outerHTML));
  for(const el of svg.querySelectorAll('[height],[width]')){for(const key of ['height','width'])if(el.hasAttribute(key))assert(+el.getAttribute(key)>=0);}
 }
 checked++;
}
api.setState({occupation:'2',sex:'2',age:'30_39',amount:2000000,rank:'mean',range:3,survivalScale:'log'});
d.getElementById('save').click();const saved=downloads.at(-1).parts.join('');assert(saved.startsWith('<!doctype html>'));
const reopened=makeDOM(saved),ra=reopened.window.ESI_DASHBOARD;
assert.deepEqual(JSON.parse(JSON.stringify(ra.getState())),JSON.parse(JSON.stringify(api.getState())));
assert.equal(ra.getDomain().n,api.getDomain().n);reopened.window.close();
d.getElementById('export-csv').click();const csv=downloads.at(-1).parts.join('');assert.equal(csv.split('\r\n').length,16);assert(csv.includes('comparacion_edades')&&csv.includes('comparacion_ocupaciones'));assert(csv.includes('2000000'));
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
for(const id of ['distribution','survival'])fs.writeFileSync(path.join(__dirname,`${id}.svg`),d.querySelector(`#${id} svg`).outerHTML);
api.setState({survivalScale:'log'});fs.writeFileSync(path.join(__dirname,'survival_log.svg'),d.querySelector('#survival svg').outerHTML);
const logSnap=d.documentElement.cloneNode(true);logSnap.querySelectorAll('script,.tooltip,noscript').forEach(n=>n.remove());logSnap.querySelector('#toast').remove();fs.writeFileSync(path.join(__dirname,'snapshot_desktop_log.html'),'<!doctype html>\n'+logSnap.outerHTML);
const mobile=makeDOM(html,390);assert(mobile.window.ESI_DASHBOARD);const ms=mobile.window.document.documentElement.cloneNode(true);ms.querySelectorAll('script,.tooltip,noscript').forEach(n=>n.remove());ms.querySelector('#toast').remove();fs.writeFileSync(path.join(__dirname,'snapshot_mobile.html'),'<!doctype html>\n'+ms.outerHTML);
mobile.window.ESI_DASHBOARD.setState({survivalScale:'log'});const mlog=mobile.window.document.documentElement.cloneNode(true);mlog.querySelectorAll('script,.tooltip,noscript').forEach(n=>n.remove());mlog.querySelector('#toast').remove();fs.writeFileSync(path.join(__dirname,'snapshot_mobile_log.html'),'<!doctype html>\n'+mlog.outerHTML);
mobile.window.close();
const report={pass:true,domainScaleCombinationsRendered:checked,domainsRendered:checked/2,scales:['linear','log'],controls:'occupation, sex, age, amount input, slider, quick amounts, range, ranking, survival scale, reset, help, keyboard tooltip',equalLogTickSpacing:true,constantLogAxisAcrossGroups:true,stepConfidenceBand:true,noNetworkDependencies:true,savedHTMLReopenedWithScale:true,csvExportRows:15,scaleDoesNotChangeCSV:true,explicit20PlusUniverse:true,emptyTailNotReportedAsPopulationZero:true,finiteSVGGeometry:true,jsErrors:errors,verificationLimit:'DOM tests via jsdom. No real browser test of the local dashboard. Static layout inspected using native HTML-to-PDF rendering, not a browser screenshot.'};
fs.writeFileSync(path.join(__dirname,'validacion_interfaz.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));w.close();
