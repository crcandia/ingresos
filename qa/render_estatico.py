"""Inspect a hydrated DOM using a PDF renderer, without a browser engine.

Form controls are replaced with noninteractive flow elements only in the QA
snapshot because WeasyPrint does not lay out native HTML controls like a browser.
This is not a substitute for a browser test. Native SVG plots are also exported
as a vector PDF with a white background.
"""
from pathlib import Path
import re
import sys
import tinycss2
import lxml.html
from weasyprint import HTML, CSS
from pypdf import PdfReader, PdfWriter
import cairosvg
import fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'qa/render_temporal'
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

for name,width,height in [('desktop',1400,2800),('mobile',390,5200),('desktop_log',1400,2800),('mobile_log',390,5200)]:
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

destination=ROOT/'figuras/curvas_vista_general.pdf'
destination.parent.mkdir(exist_ok=True)
writer=PdfWriter()
for name in ['distribution','survival','survival_log']:
    raw=(ROOT/f'qa/{name}.svg').read_bytes()
    path=OUT/f'{name}.pdf'
    cairosvg.svg2pdf(bytestring=raw,write_to=str(path),background_color='white')
    writer.add_page(PdfReader(path).pages[0])
writer.write(destination)
print(destination)
