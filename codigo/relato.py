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
    steps=[]
    for i, (n, question, explanation) in enumerate([
        (1, 'Un millón de pesos al mes', 'Aquí cuentan tanto quienes ganan exactamente un millón como quienes lo superan.'),
        (2, '¿Y si subimos a dos millones?', 'Quienes alcanzan este monto también estaban en el grupo anterior. Ahora contamos solo a quienes llegan al umbral más alto.'),
        (4, '¿Quiénes llegan a cuatro millones?', 'Son pocas personas de cada cien. En la encuesta representan a miles de trabajadores a lo largo del país.')]):
        grid=data['meta']['grid']
        idx=(n*1000000-grid['start'])//grid['step']
        p=d['curve']['p'][idx]; persons=round(d['N']*p/100/1000)*1000
        units=round(p)
        title=f'${n} millón' if n==1 else f'${n} millones'
        steps.append(f'''<article class="story-step" data-units="{units}" data-monto="{title}" data-percent="{dec(p)}%">
          <p class="kicker">0{i+1} / 03</p><h3>{question}</h3>
          <p>De cada 100 personas ocupadas de 20 años o más, unas <strong>{units}</strong> alcanzan un ingreso neto mensual de {title} o más. Eso equivale a cerca de <strong>{persons:,} personas</strong> en Chile ({dec(p)}%).</p><p>{explanation}</p></article>'''.replace(f'{persons:,}',f'{persons:,}'.replace(',','.')))
    first=d['curve']['p'][(1000000-data['meta']['grid']['start'])//data['meta']['grid']['step']]
    dots=''.join('<i class="on"></i>' if i<round(first) else '<i></i>' for i in range(100))
    story=f'''<section class="read-story" id="relato" aria-labelledby="story-title"><p class="kicker">01 &nbsp; / &nbsp; PANORAMA NACIONAL</p>
    <h2 id="story-title">De cada 100 personas, ¿cuántas llegan al millón?</h2><p class="story-intro">Cada punto representa a una de cada cien personas ocupadas de 20 años o más. Los puntos verdes muestran cuántas alcanzan cada ingreso neto mensual, en números redondos.</p>
    <div class="story-layout"><div class="dot-panel" aria-hidden="true"><span class="kicker">INGRESO NETO MENSUAL</span><strong id="dot-label">$1 millón o más</strong>
    <div class="dots">{dots}</div><span id="dot-count">≈ {dec(first)}% del total</span></div><div class="story-steps">{''.join(steps)}</div></div></section>'''
    return hero, story
