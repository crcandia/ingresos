// Generate the initial HTML from the same application that runs in the browser.
// Resources stay disabled: this build never fetches Analytics or external pages.
const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const {JSDOM, VirtualConsole} = require(require.resolve('jsdom', {paths: [path.join(root, 'qa')]}));
const errors = [];
const dom = new JSDOM(fs.readFileSync(0, 'utf8'), {
  url: 'https://ingresos.criss-lab.com/',
  runScripts: 'dangerously',
  virtualConsole: new VirtualConsole().on('jsdomError', error => errors.push(error.message))
});
const document = dom.window.document;
if (errors.length || !dom.window.ESI_DASHBOARD || !document.querySelector('#median').textContent) {
  throw new Error('Could not prerender dashboard: ' + errors.join('\n'));
}
document.querySelectorAll('.tooltip').forEach(node => node.remove());
document.documentElement.dataset.prerendered = 'true';
process.stdout.write(dom.serialize());
dom.window.close();
