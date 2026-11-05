// Exercise scroll-driven storytelling separately from survey filtering.
const {JSDOM}=require('jsdom'),fs=require('fs'),path=require('path'),zlib=require('zlib'),assert=require('assert/strict');
const html=fs.readFileSync(path.join(__dirname,'../Ingresos_Chile_ESI2025.html'),'utf8');
const raw=new JSDOM(html);assert.equal(raw.window.document.querySelectorAll('.story-step').length,4);
assert(raw.window.document.querySelector('.cover-definition').textContent.includes('cotizaciones e impuestos'));
const document=raw.window.document;
const refs=JSON.parse(fs.readFileSync(path.join(__dirname,'../fuentes/referencias_salariales.json'),'utf8'));
// Independently reconstruct the national denominator, including all reference occupants.
const csv=zlib.gunzipSync(fs.readFileSync(path.join(__dirname,'../datos/esi2025_columnas_necesarias.csv.gz'))).toString().trimEnd().split(/\r?\n/);
const fields=csv.shift().split(','),col=name=>{const i=fields.indexOf(name);assert(i>=0,name);return i};
const status=col('ocup_ref'),age=col('edad'),income=col('ing_t_p'),weight=col('fact_cal_esi');
const people=csv.map(line=>line.split(',')).filter(row=>+row[status]===1)
 .map(row=>({pay:+row[income],w:+row[weight],age:+row[age]}));
const expanded=rows=>rows.reduce((s,r)=>s+r.w,0),N=expanded(people);
const group=predicate=>people.filter(r=>predicate(r.pay)),pp=rows=>100*expanded(rows)/N;
const rate=predicate=>pp(group(predicate)),fmt=n=>new Intl.NumberFormat('es-CL').format(n);
const thousands=n=>Math.round(n/1000)*1000,shownMoney=s=>Number(s.replace(/[^0-9]/g,''));
const percent=n=>n.toFixed(1).replace('.',',')+'%';
const near=(actual,expected,tol,label)=>assert(Math.abs(actual-expected)<=tol,label+': '+actual+' ≠ '+expected);
const mean=people.reduce((s,r)=>s+r.w*r.pay,0)/N;
let accum=0;const median=[...people].sort((a,b)=>a.pay-b.pay).find(r=>(accum+=r.w)>=N/2).pay;
const minimum=refs.find(r=>r.paso==='minimo').neto_esi;
assert.equal(people.length,38729);assert.equal(Math.min(...people.map(r=>r.age)),15);
assert.equal(Math.round(mean),962945);assert.equal(median,680000);
const belowMean=rate(v=>v<mean),beforeMinimum=rate(v=>v<minimum),throughMedian=rate(v=>v<=median);
assert.equal(document.getElementById('cover-finding').textContent,Math.round(belowMean/10)+' de cada 10 ganan menos que el promedio.');
assert(document.querySelector('.cover-figure-detail > p').textContent.includes(percent(belowMean)));
assert.equal(document.querySelector('.income-row.mean strong').textContent,'≈ $'+fmt(thousands(mean)));
const universe=document.querySelector('.survey-universe').textContent;
for(const value of [fmt(people.length),fmt(thousands(N)),fmt(thousands(expanded(group(v=>v>0)))),fmt(thousands(expanded(group(v=>v===0))))])assert(universe.includes(value),value);
assert(document.querySelector('.cover-source').textContent.includes('15 años o más') && universe.includes('15 años o más'));
const foot=document.querySelector('#relato-minimo .story-foot').textContent;
assert(foot.includes('18 a 65 años') && foot.includes('infracción'));
assert(document.querySelector('#relato-minimo h3').textContent.includes('1 de cada '+Math.round(100/beforeMinimum)));
assert(document.querySelector('#relato-mediana h3').textContent.includes('$'+fmt(thousands(median))));
const millions=[1,2,3,4,6,8,10],upper=m=>group(v=>v>=m*1000000);
assert(document.querySelector('#relato-millones h3').textContent.includes(Math.round(pp(upper(1))/10)+' de cada 10'));
assert(document.querySelector('#relato-altos h3').textContent.includes('menos del 1%') && pp(upper(6))<1);
for(const m of [8,10])assert(document.querySelector('.story-precision').textContent.includes('$'+m+' millones o más hubo '+upper(m).length+' casos'));
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
  const bar=careerFigure.querySelector('a[href="'+expected+'"]').closest('li');
  const row=tableRows.find(tr=>tr.querySelector('th').textContent===ref.nombre);
  assert(row.cells[1].textContent.includes(fmt(ref.pesos)));
  const net=shownMoney(row.cells[1].querySelector('strong').textContent),reached=group(v=>v>=net);
  assert.equal(row.cells[2].querySelector('strong').textContent,percent(pp(reached)),ref.nombre);
  assert.equal(row.cells[2].querySelector('small').textContent,'≈ '+fmt(thousands(expanded(reached)))+' personas',ref.nombre);
  near(+bar.dataset.multiple,net/median,501/median,ref.nombre);
}
assert.equal(new Set(careers.map(ref=>ref.lixandria_id)).size,careers.length);
assert.equal(narrative.querySelector('a[href="https://lixandria.cl/preferences/63%7C%7C0"]').textContent,'Ingeniería Comercial');
assert(narrative.textContent.includes('$976.000') && narrative.textContent.includes('$1.396.000'));
const careerRate=name=>{const row=tableRows.find(tr=>tr.querySelector('th').textContent===name);
 const net=shownMoney(row.cells[1].querySelector('strong').textContent);return rate(v=>v>=net)};
const psychology=Math.round(careerRate('Psicología')),nursing=Math.round(careerRate('Enfermería'));
assert.deepEqual([...narrative.querySelectorAll('.career-count')].map(el=>el.textContent),[psychology+' de 100',nursing+' de 100']);
const next=narrative.querySelector('.career-next').textContent;
assert(next.includes('$1,6 millones') && next.includes(Math.round(rate(v=>v>=1600000))+' de cada 100'));
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
 const salary=shownMoney(row.cells[1].querySelector('strong').textContent),reached=group(v=>v>=thousands(salary));
 const cases=row.cells[2].textContent;
 assert(cases.includes(reached.length ? reached.length+' casos en la muestra' : 'Ningún caso en la muestra'),role.nombre);
 if(reached.length>=60)assert(cases.includes(fmt(thousands(expanded(reached)))+' personas en Chile'),role.nombre);
 near(+graphRow.dataset.multiple,salary/median,.000002,role.nombre);
}
for(const figure of [careerFigure,salaryFigure]){
 const bars=[...figure.querySelectorAll('li[data-multiple]')];
 const base=bars.find(el=>el.classList.contains('cargo-reference'));
 const width=el=>parseFloat(el.querySelector('.cargo-track i').style.width);
 assert.equal(Number(base.dataset.multiple),1);
 assert(Math.abs(Math.max(...bars.map(width))-100)<.0001);
 for(const el of bars)assert(Math.abs(width(el)/width(base)-Number(el.dataset.multiple))<.0003);
}
assert(salaries.textContent.includes('Ningún caso en la muestra'));
assert(Math.abs(+salaries.querySelector('.cargo-reference').dataset.multiple-1)<.0001);
const tvn=caseRows.find(row=>row.cells[0].textContent.includes('Directora ejecutiva de TVN'));
assert(salaries.querySelector('#public-salary-title').textContent.includes(Math.round(shownMoney(tvn.cells[1].querySelector('strong').textContent)/median)+' veces'));
const careerDots=narrative.querySelector('.career-people');
assert.equal(careerDots.querySelectorAll('circle').length,100);
assert.equal(careerDots.querySelectorAll('.career-dot-both').length,nursing);
assert.equal(careerDots.querySelectorAll('.career-dot-first-only').length,psychology-nursing);
const band=[...document.querySelectorAll('.income-band-key [data-share]')].map(b=>Number(b.dataset.share));
assert.equal(band.length,5);
assert(Math.abs(band.reduce((sum,x)=>sum+x,0)-100)<.00001);
const bands=[v=>v===0,v=>v>0 && v<minimum,v=>v>=minimum && v<1000000,v=>v>=1000000 && v<2000000,v=>v>=2000000];
bands.forEach((accept,i)=>near(band[i],rate(accept),.000001,'Tramo '+i));
assert(document.querySelector('#band-title').textContent.includes('Casi la mitad') && band[2]>=45 && band[2]<50);
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
 const survey=app.getDomain('all','all','all');assert.equal(survey.n,people.length);near(survey.N,N,.01,'N nacional');
 const expected=[beforeMinimum,throughMedian,...millions.map(m=>pp(upper(m)))];
 assert.equal(rates.length,expected.length);rates.forEach((r,i)=>near(r,expected[i],.000001,'Umbral '+i));
 assert.deepEqual(rates.slice(2),millions.map(n=>survey.curve.p[n*20]));
 assert.equal(steps[3].querySelectorAll('.rate-list li').length,3);
 for(const row of d.querySelectorAll('.rate-list li')){const scale=row.closest('#relato-altos')?100:1;assert.equal(row.querySelectorAll('circle').length,100);assert.equal(row.querySelectorAll('circle[fill="#22694f"]').length,Math.round(+row.dataset.rate*scale));}
 for(offset of [0,1,2,3,2,0]){w.dispatchEvent(new w.Event('scroll'));assert.equal(d.querySelector('.story-step.current'),steps[offset]);assert.equal(d.querySelector('.story-index a[aria-current]').hash,'#'+steps[offset].id);assert.deepEqual(app.getState(),before);}
 app.setState({age:'35_39',amount:2000000});assert.equal(app.getState().age,'35_39');assert(d.getElementById('survival-example').textContent.includes('35'));assert.equal(d.querySelector('.income-row.median strong').textContent,'≈ $'+fmt(thousands(median)));app.setState({occupation:'2',age:'35_39',sex:'2'});
 const scoped=app.getDomain('2','2','35_39');const occ=d.querySelector('[data-rank-occupation="2"]');
 const rankPercent=new Intl.NumberFormat('es-CL',{maximumFractionDigits:scoped.N/survey.N<.01?2:1}).format(scoped.N/survey.N*100);
 assert(occ.querySelector('.rank-n').textContent.includes(rankPercent+'% del total nacional'));
 const sexTable=d.getElementById('sex-comparison');assert(sexTable.textContent.includes(fmt(thousands(scoped.median))));
 const prior=sexTable.innerHTML;app.setState({sex:'1'});assert.equal(sexTable.innerHTML,prior);assert(d.getElementById('occupation-context').textContent.includes('Hombres'));
 dom.window.close();
}
raw.window.close();console.log('PASS: story forward/back, national estimates, filters independent and text readable without JS.');
