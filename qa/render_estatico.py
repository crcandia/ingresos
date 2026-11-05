"""Inspect a hydrated DOM using a PDF renderer, without a browser engine.

Form controls are replaced with noninteractive flow elements only in the QA
snapshot because WeasyPrint does not lay out native HTML controls like a browser.
This is not a substitute for a browser test. Native SVG plots are also exported
as a vector PDF with a white background.

After running run_dom_checks.cjs, use --solo-figuras to export just the
two public PDFs without writing temporary layout images or PDFs.
"""
import argparse
import io
import json
import math
from pathlib import Path
import re
import tinycss2
from lxml import etree
import lxml.html
from weasyprint import HTML, CSS
from pypdf import PdfReader, PdfWriter
import cairosvg
import fitz

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('out', nargs='?', type=Path, default=ROOT/'qa/render_temporal')
parser.add_argument('--solo-figuras', action='store_true')
args = parser.parse_args()
OUT = args.out

def validate_figures(svgs):
    """Reject old QA snapshots before exporting their graphics as current data."""
    dashboard=json.loads((ROOT/'datos/dashboard.json').read_text())
    national=dashboard['domains']['all|all|all']
    ages=[a['id'] for a in dashboard['meta']['age'] if a['id']!='all']
    profile=etree.fromstring(svgs['age-profile'])
    for field in ['median', 'mean']:
        marks=profile.xpath('//*[@class=$cls]',cls='age-'+field+'-point')
        observed={m.get('data-age-id'):float(m.get('data-value')) for m in marks}
        expected={age:dashboard['domains']['all|all|'+age][field] for age in ages}
        expected={age:value for age,value in expected.items() if value is not None}
        if len(marks)!=len(expected) or observed!=expected:
            raise ValueError('El perfil de edad no coincide con los datos: '+field)

    dist=etree.fromstring(svgs['distribution'])
    x0=float(dist.xpath('//*[local-name()="text" and text()="$0M"]/@x')[0])
    x1=float(dist.xpath('//*[local-name()="text" and text()="$1M"]/@x')[0])
    for field,dash in [('median','5 4'),('mean','2 3')]:
        x=float(dist.xpath('//*[@stroke-dasharray=$dash]/@x1',dash=dash)[0])
        if not math.isclose((x-x0)/(x1-x0)*1_000_000,national[field],abs_tol=0.01):
            raise ValueError('La distribución no coincide con los datos: '+field)

    # Two labelled gridlines recover each vertical scale directly from the SVG.
    grid=dashboard['meta']['grid']
    p=national['curve']['p'][round((1_000_000-grid['start'])/grid['step'])]
    for name in ['survival','survival_log']:
        root=etree.fromstring(svgs[name]); selected=root.xpath('//*[@class="survival-selected"]')[0]
        ticks=root.xpath('//*[@data-log-tick]')
        lines=root.xpath('//*[local-name()="line" and @y1=@y2]')
        values=[float(t.text.rstrip('%').replace('.','').replace(',','.')) for t in ticks]
        positions=[float(line.get('y1')) for line in lines[:len(ticks)]]
        if name.endswith('_log'):
            project=math.log10
        else:
            project=lambda v:v
        y0,y1=positions[0],positions[-1]; v0,v1=project(values[0]),project(values[-1])
        expected_y=y0+(y1-y0)*(project(p)-v0)/(v1-v0)
        if not math.isclose(float(selected.get('cy')),expected_y,abs_tol=1e-6):
            raise ValueError('La curva a $1 millón no coincide con los datos: '+name)

svgs={name:(ROOT/f'qa/{name}.svg').read_bytes() for name in ['distribution','survival','survival_log','age-profile']}
validate_figures(svgs)
screen_sizes=[] if args.solo_figuras else [('desktop',1400,4400),('mobile',390,9200)]
if screen_sizes:
    OUT.mkdir(parents=True, exist_ok=True)

def flatten_screen_css(css,width):
    out=[]
    for rule in tinycss2.parse_stylesheet(css,skip_whitespace=False):
        if rule.type=='at-rule' and rule.lower_at_keyword=='media':
            query=tinycss2.serialize(rule.prelude).strip()
            ok=True
            if 'print' in query or 'prefers-' in query:ok=False
            for mode,value in re.findall(r'(max|min)-width:\s*(\d+)px',query):
                ok &= width<=int(value) if mode=='max' else width>=int(value)
            if ok:out.append(tinycss2.serialize(rule.content))
        else:out.append(tinycss2.serialize([rule]))
    return ''.join(out)

for name,width,height in screen_sizes:
    doc=lxml.html.fromstring((ROOT/f'qa/snapshot_{name}.html').read_text())
    styles=doc.xpath('//style')[0]
    css=flatten_screen_css(styles.text,width)
    css=css.replace('font-size:clamp(32px,3.6vw,52px)','font-size:50px')
    css=css.replace('font-size:clamp(25px,2.7vw,38px)','font-size:36px')
    for tag in ['button','select','input','fieldset','legend']:
        css=re.sub(r'(?<![\w.-])'+tag+r'(?![\w-])','.qa-'+tag,css)
        for el in doc.xpath('//'+tag):
            if tag=='select':
                options=el.xpath('option[@selected]') or el.xpath('option')[:1]
                text=options[0].text_content() if options else ''
                for child in list(el):el.remove(child)
                el.text=text+' ▾'
            elif tag=='input':
                if el.get('type')=='range':
                    el.text=''
                    el.set('style','display:block;height:4px;background:#afc6b4;border-radius:5px;margin:25px 0 20px')
                else:el.text=el.get('value','')
            el.tag='div'
            el.set('class',(el.get('class','')+' qa-'+tag).strip())
    for details in doc.xpath('//details'):
        if 'open' not in details.attrib:
            for el in details.xpath('*[not(self::summary)]'):el.set('style','display:none')
    styles.text='.qa-button{display:inline-block;text-align:center;line-height:1.5}.qa-fieldset{min-width:0}'+css
    # Explicit dimensions make the non-browser viewport assumption inspectable.
    override=f'@page{{size:{width}px {height}px;margin:0}} body{{width:{width}px}} .plot svg{{max-width:100%}}'
    output=OUT/f'{name}.pdf'
    HTML(string=lxml.html.tostring(doc,encoding='unicode'),media_type='screen').write_pdf(output,stylesheets=[CSS(string=override)])
    pdf=fitz.open(output)
    for i,page in enumerate(pdf):
        page.get_pixmap(matrix=fitz.Matrix(1.2 if name.startswith('mobile') else 1,1.2 if name.startswith('mobile') else 1)).save(OUT/f'{name}-{i+1}.png')
    print(name,'pages',len(pdf))

for filename,names in [('curvas_vista_general.pdf',['distribution','survival','survival_log']),
                       ('perfil_ingresos_por_edad.pdf',['age-profile'])]:
    destination=ROOT/'figuras'/filename
    destination.parent.mkdir(exist_ok=True)
    writer=PdfWriter()
    for name in names:
        vector=cairosvg.svg2pdf(bytestring=svgs[name],background_color='white')
        writer.add_page(PdfReader(io.BytesIO(vector)).pages[0])
    writer.write(destination)
    print(destination)
