"""Bundle the dashboard into an offline HTML and a web version with Analytics."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
template = (ROOT / 'interfaz/dashboard.html').read_text()
data = json.loads((ROOT / 'datos/dashboard.json').read_text())
assert len(data['domains']) == 180
embedded = json.dumps(data, ensure_ascii=False, separators=(',', ':'), allow_nan=False).replace('</', '<\\/')
html = template.replace('/*__STYLES__*/', (ROOT / 'interfaz/dashboard.css').read_text())
html = html.replace('__DASHBOARD_DATA__', embedded)
html = html.replace('/*__SCRIPT__*/', (ROOT / 'interfaz/dashboard.js').read_text())
assert '__DASHBOARD_DATA__' not in html and '/*__SCRIPT__*/' not in html
out = ROOT / 'Ingresos_Chile_ESI2025.html'
out.write_text(html)
site = ROOT / 'site'
site.mkdir(exist_ok=True)
web_csp = "default-src 'none'; script-src 'unsafe-inline' https://www.googletagmanager.com; style-src 'unsafe-inline'; img-src data: blob: https://*.google-analytics.com https://www.googletagmanager.com; connect-src https://*.google-analytics.com https://*.google.com https://www.googletagmanager.com; base-uri 'none'; form-action 'none'"
offline_csp = "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data: blob:; connect-src 'none'; base-uri 'none'; form-action 'none'"
web = html.replace('content="' + offline_csp + '"', 'content="' + web_csp + '"', 1)
web = web.replace('</head>', (ROOT / 'interfaz/analytics.html').read_text() + '\n</head>', 1)
web = web.replace('<span id="privacy-note">Archivo autocontenido. Funciona sin conexión y no envía información.</span>', '<span id="privacy-note">Esta versión web usa Google Analytics para medir visitas. “Guardar copia” descarga una versión sin Analytics.</span>', 1)
(site / 'index.html').write_text(web)
print(f'Created {out.name}: {out.stat().st_size:,} bytes, 180 aggregate domains. Web version adds Google Analytics G-XSFF2F0XKK.')
