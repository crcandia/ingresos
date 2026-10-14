"""Build public metadata and crawler resources from one explicit site configuration."""
from pathlib import Path
from html import escape
import json
import shutil
import struct
from urllib.parse import urlparse


def preparar_web(root: Path, html: str, data: dict) -> str:
    config = json.loads((root / 'interfaz/seo.json').read_text())
    site = root / 'site'
    canonical = config['canonical']
    parsed = urlparse(canonical)
    assert parsed.scheme == 'https' and parsed.path == '/' and not parsed.query and not parsed.fragment
    image = site / config['image']
    signature = image.read_bytes()[:24]
    assert signature[:8] == b'\x89PNG\r\n\x1a\n', 'Social image must be a PNG'
    width, height = struct.unpack('>II', signature[16:24])
    assert width >= 1200 and 1.8 < width / height < 2.0
    assert image.stat().st_size < 5_000_000

    tags = []
    def meta(key, value, attribute='name'):
        tags.append(f'<meta data-web-meta {attribute}="{escape(key)}" content="{escape(str(value), quote=True)}">')
    def link(rel, href, extra=''):
        tags.append(f'<link data-web-meta rel="{rel}" href="{escape(href, quote=True)}"{extra}>')

    link('canonical', canonical)
    meta('robots', 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1')
    meta('author', config['author'])
    meta('theme-color', '#193d3b')
    meta('color-scheme', 'light')
    for key, value in {
        'og:type': 'website', 'og:site_name': 'Ingresos en Chile', 'og:locale': 'es_CL',
        'og:title': config['socialTitle'], 'og:description': config['socialDescription'],
        'og:url': canonical, 'og:image': canonical + config['image'],
        'og:image:secure_url': canonical + config['image'], 'og:image:type': 'image/png',
        'og:image:width': width, 'og:image:height': height, 'og:image:alt': config['imageAlt'],
    }.items():
        meta(key, value, 'property')
    for key, value in {
        'twitter:card': 'summary_large_image', 'twitter:title': config['socialTitle'],
        'twitter:description': config['socialDescription'],
        'twitter:image': canonical + config['image'], 'twitter:image:alt': config['imageAlt'],
    }.items():
        meta(key, value)
    link('icon', canonical + 'favicon.svg', ' type="image/svg+xml" sizes="any"')
    link('icon', canonical + 'favicon-32.png', ' type="image/png" sizes="32x32"')
    link('apple-touch-icon', canonical + 'apple-touch-icon.png', ' sizes="180x180"')

    person_id, site_id = canonical + '#autor', canonical + '#sitio'
    page_id, dataset_id = canonical + '#pagina', canonical + '#datos'
    dataset_description = (
        'Estadísticas agregadas de ingreso neto mensual de la ocupación principal en Chile, '
        'calculadas a partir de los microdatos públicos ESI 2025 del INE. Incluye 180 combinaciones '
        'de ocupación, sexo y edad, para personas ocupadas de referencia de 20 años o más. '
        'El CSV contiene mediana, promedio, intervalos del promedio, cuantiles, tamaño muestral '
        'y población expandida. Son estimaciones ponderadas, expresadas en pesos de octubre de 2025. '
        'Elaboración independiente de Cristian Candia. No representa toda la muestra de la ESI.'
    )
    graph = [
        {'@type': 'Person', '@id': person_id, 'name': config['author'],
         'sameAs': ['https://github.com/crcandia'],
         'affiliation': {'@type': 'Organization', 'name': 'CRISS-LAB', 'url': 'https://criss-lab.com/'}},
        {'@type': 'WebSite', '@id': site_id, 'url': canonical, 'name': 'Ingresos en Chile',
         'inLanguage': 'es-CL', 'publisher': {'@id': person_id}},
        {'@type': 'WebPage', '@id': page_id, 'url': canonical, 'name': config['title'],
         'description': config['description'], 'inLanguage': 'es-CL',
         'dateModified': config['modified'], 'isPartOf': {'@id': site_id},
         'author': {'@id': person_id}, 'mainEntity': {'@id': dataset_id},
         'primaryImageOfPage': {'@type': 'ImageObject', 'url': canonical + config['image'],
                                'width': width, 'height': height, 'caption': config['imageAlt']}},
        {'@type': 'Dataset', '@id': dataset_id,
         'name': 'Ingresos netos en Chile por ocupación, sexo y edad, personas de 20 años o más, ESI 2025',
         'description': dataset_description, 'url': canonical + '#datos',
         'creator': {'@id': person_id}, 'inLanguage': 'es-CL', 'isAccessibleForFree': True,
         'dateModified': data['meta']['generatedUTC'][:10], 'temporalCoverage': '2025',
         'spatialCoverage': {'@type': 'Place', 'name': 'Chile'},
         'keywords': ['ingresos laborales', 'Chile', 'ESI 2025', 'edad', 'sexo', 'ocupación'],
         'measurementTechnique': 'Factores de expansión de la ESI. Errores estándar del promedio por linealización de Taylor con estratos y conglomerados.',
         'variableMeasured': [
             {'@type': 'PropertyValue', 'name': 'Mediana del ingreso neto mensual', 'unitText': 'CLP'},
             {'@type': 'PropertyValue', 'name': 'Promedio del ingreso neto mensual', 'unitText': 'CLP'},
             {'@type': 'PropertyValue', 'name': 'Población expandida', 'unitText': 'personas'},
             {'@type': 'PropertyValue', 'name': 'Tamaño muestral', 'unitText': 'observaciones'}],
         'isBasedOn': data['meta']['provenance']['sourceURL'],
         'distribution': {'@type': 'DataDownload', 'encodingFormat': 'text/csv',
                          'contentUrl': canonical + config['dataset']},
         'mainEntityOfPage': {'@id': page_id}},
    ]
    structured = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    tags.append(f'<script data-web-meta id="structured-data" type="application/ld+json">{structured}</script>')
    html = html.replace('</head>', '\n'.join(tags) + '\n</head>', 1)
    resources = f'''<section class="public-data surface" id="datos" aria-labelledby="datos-title">
 <p class="eyebrow">FUENTES Y DESCARGAS</p><h2 id="datos-title">Datos para explorar y reproducir</h2>
 <p>Descarga el resumen de las 180 combinaciones de ocupación, sexo y edad. Incluye personas ocupadas de 20 años o más, con ingresos expresados en pesos de octubre de 2025. El CSV contiene mediana, promedio, intervalos del promedio, cuantiles, tamaño muestral y población expandida.</p>
 <p>Elaboración independiente de <strong>Cristian Candia</strong>, <a href="https://criss-lab.com/">CRISS-LAB</a>, a partir de microdatos públicos del INE. Las categorías y reglas de cálculo están documentadas en el repositorio.</p>
 <div class="public-data-links"><a href="{canonical + config['dataset']}" download>Descargar resumen completo · CSV</a><a href="{config['repository']}" target="_blank" rel="noopener noreferrer">Código y metodología · GitHub</a></div>
</section>'''
    html = html.replace('<!--__WEB_RESOURCES__-->', resources, 1)
    (site / 'datos').mkdir(exist_ok=True)
    shutil.copyfile(root / 'tablas/resumen_dominios.csv', site / config['dataset'])
    (site / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {canonical}sitemap.xml\n')
    (site / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'  <url><loc>{canonical}</loc><lastmod>{config["modified"]}</lastmod></url>\n</urlset>\n')
    (site / '_redirects').write_text('/index.html / 301!\n')
    (site / '_headers').write_text(
        '/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n'
        '/\n  Cache-Control: public, max-age=0, must-revalidate\n'
        '/index.html\n  Cache-Control: public, max-age=0, must-revalidate\n'
        '/assets/*\n  Cache-Control: public, max-age=86400\n'
        '/favicon*\n  Cache-Control: public, max-age=86400\n'
        '/apple-touch-icon.png\n  Cache-Control: public, max-age=86400\n')
    (site / '404.html').write_text('''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, follow"><title>Página no encontrada | Ingresos en Chile</title>
<style>body{margin:0;background:#f5f4ed;color:#193d3b;font:18px/1.6 system-ui,sans-serif}main{max-width:640px;margin:15vh auto;padding:24px}h1{font:48px/1.1 Georgia,serif}a{color:#216c63}small{letter-spacing:.15em}</style></head>
<body><main><small>INGRESOS EN CHILE · ESI 2025</small><h1>Esta página no existe.</h1><p>Puedes volver al dashboard para explorar los ingresos por ocupación, edad y sexo.</p><a href="/">Volver al dashboard</a></main></body></html>\n''')
    return html
