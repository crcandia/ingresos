"""Render the national reading guide from the same survey estimates as the explorer."""
def relato(data):
    d = data['domains']['all|all|all']
    def clp(x): return '$' + f'{round(x / 1000) * 1000:,}'.replace(',', '.')
    def dec(x): return f'{x:.1f}'.replace('.', ',')
    def row(label, key):
        width = d[key] / max(d['mean'], d['median']) * 100
        return f'<div class="income-row {key}"><div><span>{label}</span><strong>≈ {clp(d[key])}</strong></div><i aria-hidden="true" style="width:{width:.2f}%"></i></div>'
    hero = f'''<section class="cover" aria-labelledby="title">
      <div class="cover-copy"><p class="kicker">CHILE &nbsp; / &nbsp; ENCUESTA SUPLEMENTARIA DE INGRESOS 2025</p>
      <h1 id="title">Ingresos netos<br><em>en Chile</em></h1>
      <p class="cover-lead">¿Cuánto se gana al mes por el trabajo principal?</p>
      <p class="cover-definition"><strong>Neto significa después de los descuentos.</strong> Para quienes reciben un sueldo, se descuentan cotizaciones e impuestos. Para quienes trabajan por cuenta propia, se restan los costos de su actividad. La encuesta también cuenta beneficios que se reciben en especie.</p>
      <div class="cover-actions"><a class="cover-primary" href="#relato">Recorrer las cifras ↓</a><a href="#explorar">Ir a los filtros</a></div></div>
      <aside class="cover-figure"><p class="kicker">EL PUNTO MEDIO</p><h2>La mitad gana hasta <br><strong>≈ {clp(d['median'])}</strong> al mes.</h2>
      {row('Mediana', 'median')}{row('Promedio', 'mean')}
      <p>Si ordenamos a las personas de menor a mayor ingreso, la mediana marca el punto medio. Los ingresos más altos empujan el promedio hacia arriba.</p></aside>
      <p class="cover-source">Fuente: INE · ESI 2025. Personas ocupadas de 20 años o más en Chile. Montos por persona, en pesos de octubre de 2025.</p>
    </section>'''
    from pathlib import Path
    import json
    from html import escape
    refs=json.loads((Path(__file__).resolve().parents[1]/'fuentes/referencias_salariales.json').read_text())
    def referencias(n):
        items=[]
        for a in refs:
            if a['paso']!=n: continue
            x=a['pesos'] if 'pesos' in a else sum(a['totales'])/a['meses']
            cifra=clp(x)
            signo='' if x==round(x/1000)*1000 else '≈ '
            items.append(f"""<div><h4>{escape(a['nombre'])}</h4><b>{signo}{cifra} <small>· {a['tipo'].lower()} al mes</small></b><p>{escape(a['detalle'])} <a href="{escape(a['url'])}" target="_blank" rel="noopener noreferrer">{escape(a['fuente'])}</a></p></div>""")
        if not items: return ''
        return '<aside class="salary-refs"><span class="kicker">REFERENCIAS FUERA DE LA ENCUESTA</span>'+''.join(items)+'</aside>'
    steps=[]
    grid=data['meta']['grid']
    for i,(n,question,reading) in enumerate([
        (1,'¿Cuántas personas llegan al millón?','Contamos tanto a quien gana exactamente un millón como a quien gana más.'),
        (2,'Al subir a dos millones, ¿cuántas quedan?','Este grupo está dentro del anterior: quien gana dos millones también supera el millón.'),
        (4,'Cuatro millones: dos de cada cien','El grupo se achica. Por cada persona que llega a este monto, unas 49 ganan menos.'),
        (6,'Seis millones: menos de una de cada cien','Para ver un grupo tan pequeño, ampliamos el 1% superior. Ahora cada punto representa a una persona de cada 10.000 del total.'),
        (8,'Ocho millones: ¿qué tan frecuente es?',''),
        (10,'Diez millones: ¿cuántas personas llegan tan alto?','')]):
        j=(n*1000000-grid['start'])//grid['step']
        p=d['curve']['p'][j]; persons=round(d['N']*p/100/1000)*1000
        zoom=p<1
        pct=lambda v: f'{v:.{2 if zoom else 1}f}'.replace('.',',')
        units=round(p*(100 if zoom else 1)); base='10.000' if zoom else '100'
        title=f'${n} millón' if n==1 else f'${n} millones'
        if d['curve']['q'][j]==1:
            reading=f"Estimación exploratoria: {d['curve']['n'][j]} personas encuestadas declararon ese monto o más. El intervalo de confianza del 95% va de {pct(d['curve']['lo'][j])}% a {pct(d['curve']['hi'][j])}% del total."
        count=f'{persons:,}'.replace(',','.')
        steps.append(f"""<article class="story-step" data-units="{units}" data-base="{base}" data-monto="{title}" data-percent="{pct(p)}%">
          <p class="kicker">0{i+1} / 06 · {title.upper()} O MÁS</p><h3>{question}</h3>
          <p>De cada {base} personas ocupadas de 20 años o más, unas <strong>{units}</strong> ganan {title} netos o más al mes. Son cerca de <strong>{count} personas</strong> en Chile (≈ {pct(p)}%).</p><p>{reading}</p>{referencias(n)}</article>""")
    first=d['curve']['p'][(1000000-grid['start'])//grid['step']]
    dots=''.join('<i class="on"></i>' if i<round(first) else '<i></i>' for i in range(100))
    story=f"""<section class="read-story" id="relato" aria-labelledby="story-title"><p class="kicker">01 &nbsp; / &nbsp; PANORAMA NACIONAL</p>
    <h2 id="story-title">Del millón a los diez millones: ¿cuántas personas llegan?</h2><p class="story-intro">Los puntos verdes cuentan a quienes ganan al menos el monto indicado en su trabajo principal. Las cifras de la encuesta son netas. Al lado encontrarás referencias conocidas: cuando dicen «bruto», todavía faltan los descuentos, así que no les corresponde directamente el porcentaje de la encuesta.</p>
    <div class="story-layout"><div class="dot-panel" aria-hidden="true"><span class="kicker" id="dot-key">CADA PUNTO: 1 DE CADA 100</span><strong id="dot-label">$1 millón o más</strong>
    <div class="dots">{dots}</div><span id="dot-count">≈ {dec(first)}% del total</span></div><div class="story-steps">{''.join(steps)}</div></div></section>"""
    return hero, story
