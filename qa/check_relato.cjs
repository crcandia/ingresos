// Exercise scroll-driven storytelling separately from survey filtering.
const {JSDOM}=require('jsdom'),fs=require('fs'),path=require('path'),assert=require('assert/strict');
const html=fs.readFileSync(path.join(__dirname,'../Ingresos_Chile_ESI2025.html'),'utf8');
const raw=new JSDOM(html);assert.equal(raw.window.document.querySelectorAll('.story-step').length,4);
assert(raw.window.document.querySelector('.cover-definition').textContent.includes('cotizaciones e impuestos'));
const document=raw.window.document;
const refs=JSON.parse(fs.readFileSync(path.join(__dirname,'../fuentes/referencias_salariales.json'),'utf8'));
const careers=refs.filter(ref=>ref.paso===2);
const narrative=document.getElementById('sueldos-por-carrera');
const tableRows=[...narrative.querySelectorAll('tbody tr')];
assert.equal(tableRows.length,8);
assert.equal(narrative.querySelectorAll(':scope > p > a[href^="https://lixandria.cl/preferences/"]').length,4);
for(const ref of careers){
  assert.equal(ref.consulta.campo,'tercer_ano');
  const expected='https://lixandria.cl/preferences/'+ref.lixandria_id+'%7C%7C0';
  const links=[...narrative.querySelectorAll('a')].filter(link=>link.textContent===ref.nombre);
  assert(links.length>0 && links.every(link=>link.href===expected),ref.nombre);
  const row=tableRows.find(tr=>tr.querySelector('th').textContent===ref.nombre);
  assert(row.cells[1].textContent.includes(new Intl.NumberFormat('es-CL').format(ref.pesos)));
}
assert.equal(new Set(careers.map(ref=>ref.lixandria_id)).size,careers.length);
assert.equal(narrative.querySelector('a[href="https://lixandria.cl/preferences/63%7C%7C0"]').textContent,'Ingeniería Comercial');
assert(narrative.textContent.includes('$976.000') && narrative.textContent.includes('$1.396.000'));
assert(narrative.textContent.includes('31 de 100') && narrative.textContent.includes('18 de 100'));
assert(document.getElementById('public-salary-title').closest('section').textContent.includes('12 casos'));
assert(document.querySelector('.footer-footnote a[rel="author"]'));
assert(document.querySelector(document.querySelector('.footnote-source').getAttribute('href')));
assert(document.querySelector('a[href="#sueldos-por-carrera"]'));
for(const width of [390,1280]){
 let fn;const dom=new JSDOM(html,{runScripts:'dangerously',pretendToBeVisual:true,beforeParse(w){
 Object.defineProperty(w,'innerWidth',{value:width});w.IntersectionObserver=class{constructor(cb){fn=cb}observe(){}};
 w.requestAnimationFrame=cb=>{cb();return 1};
 }});
 const w=dom.window,d=w.document,app=w.ESI_DASHBOARD,steps=[...d.querySelectorAll('.story-step')];
 let offset=0;steps.forEach((el,i)=>el.getBoundingClientRect=()=>({top:(i-offset)*800}));
 const before=app.getState();fn([{isIntersecting:true}]);
 assert.deepEqual(steps.map(x=>x.id),['relato-minimo','relato-mediana','relato-millones','relato-altos']);
 const rates=[...d.querySelectorAll('.rate-list li')].map(x=>+x.dataset.rate);
 const survey=app.getDomain('all','all','all');assert(Math.abs(rates[0]-78.924)<.001);assert(rates[1]>=50&&rates[1]<51);
 assert.deepEqual(rates.slice(2),[1,2,3,4,6,8,10].map(n=>survey.curve.p[n*20]));
 assert.equal(steps[3].querySelectorAll('.rate-list li').length,3);
 for(const row of d.querySelectorAll('.rate-list li')){const scale=row.closest('#relato-altos')?100:1;assert.equal(row.querySelectorAll('circle').length,100);assert.equal(row.querySelectorAll('circle[fill="#22694f"]').length,Math.round(+row.dataset.rate*scale));}
 for(offset of [0,1,2,3,2,0]){w.dispatchEvent(new w.Event('scroll'));assert.equal(d.querySelector('.story-step.current'),steps[offset]);assert.equal(d.querySelector('.story-index a[aria-current]').hash,'#'+steps[offset].id);assert.deepEqual(app.getState(),before);}
 app.setState({age:'35_39',amount:2000000});assert.equal(app.getState().age,'35_39');assert(d.getElementById('survival-example').textContent.includes('35'));assert.equal(d.querySelector('.income-row.median strong').textContent,'≈ $688.000');app.setState({occupation:'2',age:'35_39',sex:'2'});
 const scoped=app.getDomain('2','2','35_39');const occ=d.querySelector('[data-rank-occupation="2"]');
 const fmt=(n,k)=>new Intl.NumberFormat('es-CL',{maximumFractionDigits:k}).format(n);
 assert(occ.querySelector('.rank-n').textContent.includes(fmt(scoped.N/survey.N*100,scoped.N/survey.N<.01?2:1)+'% del total nacional'));
 const sexTable=d.getElementById('sex-comparison');assert(sexTable.textContent.includes(fmt(Math.round(scoped.median/1000)*1000,0)));
 const prior=sexTable.innerHTML;app.setState({sex:'1'});assert.equal(sexTable.innerHTML,prior);assert(d.getElementById('occupation-context').textContent.includes('Hombres'));
 dom.window.close();
}
raw.window.close();console.log('PASS: story forward/back, national estimates, filters independent and text readable without JS.');
