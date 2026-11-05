// Exercise scroll-driven storytelling separately from survey filtering.
const {JSDOM}=require('jsdom'),fs=require('fs'),path=require('path'),assert=require('assert/strict');
const html=fs.readFileSync(path.join(__dirname,'../Ingresos_Chile_ESI2025.html'),'utf8');
const raw=new JSDOM(html);assert.equal(raw.window.document.querySelectorAll('.story-step').length,6);
assert(raw.window.document.querySelector('.cover-definition').textContent.includes('cotizaciones e impuestos'));
assert.equal(raw.window.document.querySelectorAll('.salary-refs h4').length,5);
for(const width of [390,1280]){
 let fn;const dom=new JSDOM(html,{runScripts:'dangerously',pretendToBeVisual:true,beforeParse(w){
 Object.defineProperty(w,'innerWidth',{value:width});w.IntersectionObserver=class{constructor(cb){fn=cb}observe(){}};
 w.requestAnimationFrame=cb=>{cb();return 1};
 }});
 const w=dom.window,d=w.document,app=w.ESI_DASHBOARD,steps=[...d.querySelectorAll('.story-step')];
 let offset=0;steps.forEach((el,i)=>el.getBoundingClientRect=()=>({top:(i-offset)*800}));
 const before=app.getState();fn([{isIntersecting:true}]);
 for(offset of [0,1,2,3,4,5,3,2,0]){w.dispatchEvent(new w.Event('scroll'));
 const milestone=[1,2,4,6,8,10][offset];const probs=app.getDomain('all','all','all').curve.p[milestone*20];
 assert.equal(d.querySelectorAll('.dots .on').length,Math.round(probs*(probs<1?100:1)));assert.equal(d.querySelector('.story-step.current'),steps[offset]);assert(d.getElementById('dot-label').textContent.startsWith('$'+milestone));assert(d.getElementById('dot-key').textContent.includes(probs<1?'10.000':'1 DE CADA 100'));assert.deepEqual(app.getState(),before);}
 app.setState({age:'35_39',amount:2000000});assert.equal(app.getState().age,'35_39');assert(d.getElementById('survival-example').textContent.includes('35'));assert.equal(d.querySelector('.income-row.median strong').textContent,'≈ $688.000');dom.window.close();
}
raw.window.close();console.log('PASS: story forward/back, national estimates, filters independent and text readable without JS.');
