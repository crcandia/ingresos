"""Bundle the dashboard into an offline HTML and a web version with Analytics."""
from pathlib import Path
from base64 import b64encode
import json
import subprocess
from html import escape
from codigo.relato import relato
from codigo.seo_web import preparar_web, respuestas_ingresos

ROOT = Path(__file__).resolve().parent
template = (ROOT / 'interfaz/dashboard.html').read_text()
data = json.loads((ROOT / 'datos/dashboard.json').read_text())
seo = json.loads((ROOT / 'interfaz/seo.json').read_text())
portada, historia = relato(data)
# Inline the small artwork so every saved copy keeps it, even when saved offline.
ilustracion = (ROOT / 'site/assets/ingresos-chile-trabajo.webp').read_bytes()
portada = portada.replace('__PORTADA_IMAGEN__', 'data:image/webp;base64,' + b64encode(ilustracion).decode('ascii'))
template = template.replace('<!--__COVER__-->', portada).replace('<!--__STORY__-->', historia)
template = template.replace('__PAGE_TITLE__', escape(seo['title']))
template = template.replace('__PAGE_DESCRIPTION__', escape(seo['description'], quote=True))
template = template.replace('<!--__INCOME_ANSWERS__-->', respuestas_ingresos(data))
assert len(data['domains']) == len(data['meta']['age']) * len(data['meta']['sex']) * len(data['meta']['occupation'])
embedded = json.dumps(data, ensure_ascii=False, separators=(',', ':'), allow_nan=False).replace('</', '<\\/')
styles = '\n'.join((ROOT / 'interfaz' / name).read_text()
                   for name in ('dashboard.css', 'seo.css', 'relato.css', 'carreras.css'))
html = template.replace('/*__STYLES__*/', styles)
html = html.replace('__DASHBOARD_DATA__', embedded)
html = html.replace('/*__SCRIPT__*/', (ROOT / 'interfaz/dashboard.js').read_text())
assert '__DASHBOARD_DATA__' not in html and '/*__SCRIPT__*/' not in html
try:
    html = subprocess.run(['node', str(ROOT / 'codigo/prerenderizar_dashboard.cjs')], input=html,
                          text=True, capture_output=True, check=True).stdout
except (FileNotFoundError, subprocess.CalledProcessError) as error:
    raise RuntimeError('La construcción requiere Node.js y jsdom. Ejecuta npm install --prefix qa. ' + getattr(error, 'stderr', str(error))) from error
out = ROOT / 'Ingresos_Chile_ESI2025.html'
out.write_text(html.replace('<!--__WEB_RESOURCES__-->', ''))
site = ROOT / 'site'
site.mkdir(exist_ok=True)
web_csp = "default-src 'none'; script-src 'unsafe-inline' https://www.googletagmanager.com; style-src 'unsafe-inline'; img-src 'self' data: blob: https://*.google-analytics.com https://www.googletagmanager.com; connect-src https://*.google-analytics.com https://*.google.com https://www.googletagmanager.com; base-uri 'none'; form-action 'none'"
offline_csp = "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data: blob:; connect-src 'none'; base-uri 'none'; form-action 'none'"
web = html.replace('content="' + offline_csp + '"', 'content="' + web_csp + '"', 1)
web = web.replace('</head>', (ROOT / 'interfaz/analytics.html').read_text() + '\n</head>', 1)
web = web.replace('<span id="privacy-note">Archivo autocontenido. Funciona sin conexión y no envía información.</span>', '<span id="privacy-note">Montos de la encuesta en pesos de octubre de 2025.</span>', 1)
web = preparar_web(ROOT, web, data)
(site / 'index.html').write_text(web)
print(f"Created {out.name}: {out.stat().st_size:,} bytes, {len(data['domains'])} aggregate domains. Web version adds Google Analytics G-XSFF2F0XKK.")
