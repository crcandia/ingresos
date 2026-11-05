// Exercise scroll-driven storytelling separately from survey filtering.
const {JSDOM}=require('jsdom'),fs=require('fs'),path=require('path'),assert=require('assert/strict');
const html=fs.readFileSync(path.join(__dirname,'../Ingresos_Chile_ESI2025.html'),'utf8');
const raw=new JSDOM(html);assert.equal(raw.window.document.querySelectorAll('.story-step').length,4);
assert(raw.window.document.querySelector('.cover-definition').textContent.includes('cotizaciones e impuestos'));
assert.equal(raw.window.document.querySelectorAll('.salary-refs h4').length,4);
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
 assert.deepEqual(rates.slice(2),[1,2,4,6,8,10].map(n=>survey.curve.p[n*20]));
 assert.equal(steps[3].querySelectorAll('.rate-list li').length,3);
 for(const x of d.querySelectorAll('.salary-refs b'))assert(x.textContent.includes('líquido'));
 for(offset of [0,1,2,3,2,0]){w.dispatchEvent(new w.Event('scroll'));assert.equal(d.querySelector('.story-step.current'),steps[offset]);assert.equal(d.querySelector('.story-index a[aria-current]').hash,'#'+steps[offset].id);assert.deepEqual(app.getState(),before);}
 app.setState({age:'35_39',amount:2000000});assert.equal(app.getState().age,'35_39');assert(d.getElementById('survival-example').textContent.includes('35'));assert.equal(d.querySelector('.income-row.median strong').textContent,'≈ $688.000');dom.window.close();
}
raw.window.close();console.log('PASS: story forward/back, national estimates, filters independent and text readable without JS.');
