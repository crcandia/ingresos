// Exercise scroll-driven storytelling separately from survey filtering.
const {JSDOM}=require('jsdom'),fs=require('fs'),path=require('path'),assert=require('assert/strict');
const html=fs.readFileSync(path.join(__dirname,'../Ingresos_Chile_ESI2025.html'),'utf8');
const raw=new JSDOM(html);assert.equal(raw.window.document.querySelectorAll('.story-step').length,4);
assert(raw.window.document.querySelector('.cover-definition').textContent.includes('cotizaciones e impuestos'));
const document=raw.window.document;
assert.equal(document.getElementById('cover-finding').textContent,'7 de cada 10 ganan menos que el promedio.');
assert(document.querySelector('.cover-figure-detail > p').textContent.includes('68,5%'));
const refs=JSON.parse(fs.readFileSync(path.join(__dirname,'../fuentes/referencias_salariales.json'),'utf8'));
const careers=refs.filter(ref=>ref.paso===2);
const narrative=document.getElementById('sueldos-por-carrera');
const tableRows=[...narrative.querySelectorAll('tbody tr')];
assert.equal(careers.length,20);
assert.equal(tableRows.length,careers.length);
const careerFigure=document.querySelector('#comparador-carreras .comparison-figure');
assert.equal(careerFigure.closest('details').querySelector('summary').textContent,'Comparar las 20 carreras');
assert.equal(careerFigure.querySelectorAll('li:not(.cargo-reference)').length,careers.length);
assert.equal(narrative.querySelectorAll(':scope > p > a[href^="https://lixandria.cl/preferences/"], :scope > figure a[href^="https://lixandria.cl/preferences/"]').length,4);
for(const ref of careers){
  assert.equal(ref.consulta.campo,'tercer_ano');
  const expected='https://lixandria.cl/preferences/'+ref.lixandria_id+'%7C%7C0';
  const links=[...narrative.querySelectorAll('a')].filter(link=>link.textContent===ref.nombre);
  assert(links.length>0 && links.every(link=>link.href===expected),ref.nombre);
  assert(careerFigure.querySelector('a[href="'+expected+'"]'),ref.nombre);
  const row=tableRows.find(tr=>tr.querySelector('th').textContent===ref.nombre);
  assert(row.cells[1].textContent.includes(new Intl.NumberFormat('es-CL').format(ref.pesos)));
}
assert.equal(new Set(careers.map(ref=>ref.lixandria_id)).size,careers.length);
assert.equal(narrative.querySelector('a[href="https://lixandria.cl/preferences/63%7C%7C0"]').textContent,'Ingeniería Comercial');
assert(narrative.textContent.includes('$976.000') && narrative.textContent.includes('$1.396.000'));
assert(narrative.textContent.includes('31 de 100') && narrative.textContent.includes('18 de 100'));
const roles=refs.filter(ref=>ref.paso===10);
const salaries=document.getElementById('sueldos-de-altos-cargos');
const caseRows=[...salaries.querySelectorAll('tbody tr')];
assert.equal(caseRows.length,roles.length);
assert.equal(roles.length,14);
const salaryFigure=salaries.querySelector('.comparison-figure');
assert.equal(salaryFigure.querySelectorAll('li:not(.cargo-reference)').length,roles.length);
assert(roles.filter(r=>r.eleccion_popular).length>=5);
assert(roles.some(r=>r.habitantes_censo2024<15000)&&roles.some(r=>r.habitantes_censo2024>250000));
for(const role of roles){
 const row=caseRows.find(el=>el.querySelector('th').textContent.includes(role.nombre));
 assert(row && row.querySelector('a').href === role.url,role.nombre);
 assert(row.cells[1].textContent.includes(role.periodo),role.nombre);
 const graphRow=[...salaryFigure.querySelectorAll('li')].find(el=>el.querySelector('.cargo-row-head span').textContent===(role.etiqueta_grafico||role.nombre));
 assert(graphRow && graphRow.textContent.includes(role.periodo),role.nombre);
}
for(const figure of [careerFigure,salaryFigure]){
 const bars=[...figure.querySelectorAll('li[data-multiple]')];
 const base=bars.find(el=>el.classList.contains('cargo-reference'));
 const width=el=>parseFloat(el.querySelector('.cargo-track i').style.width);
 assert.equal(Number(base.dataset.multiple),1);
 assert(Math.abs(Math.max(...bars.map(width))-100)<.0001);
 for(const el of bars)assert(Math.abs(width(el)/width(base)-Number(el.dataset.multiple))<.0003);
}
assert(salaries.textContent.includes('12 casos') && salaries.textContent.includes('6 casos'));
assert(salaries.textContent.includes('Ningún caso en la muestra'));
assert(Math.abs(+salaries.querySelector('.cargo-reference').dataset.multiple-1)<.0001);
assert(salaries.querySelector('#public-salary-title').textContent.includes('19 veces'));
const careerDots=narrative.querySelector('.career-people');
assert.equal(careerDots.querySelectorAll('circle').length,100);
assert.equal(careerDots.querySelectorAll('.career-dot-both').length,18);
assert.equal(careerDots.querySelectorAll('.career-dot-first-only').length,13);
const band=[...document.querySelectorAll('.income-band-key [data-share]')].map(b=>Number(b.dataset.share));
assert.equal(band.length,5);
assert(Math.abs(band.reduce((sum,x)=>sum+x,0)-100)<.00001);
assert(Math.abs(band[0]-1.1723)<.0001);
assert(document.getElementById('story-title').textContent.includes('de menor a mayor'));
const art=document.querySelector('.cover-illustration');
const bytes=fs.readFileSync(path.join(__dirname,'../site/assets/ingresos-chile-trabajo.webp'));
assert.equal(art.getAttribute('src'),'data:image/webp;base64,'+bytes.toString('base64'));
assert(document.querySelector('.footer-footnote a[rel~="author"]'));
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
 const survey=app.getDomain('all','all','all');assert(Math.abs(rates[0]-21.076)<.001);assert(Math.abs(rates[1]-50.02536)<.001);
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
