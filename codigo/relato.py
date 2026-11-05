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
    salaried=json.loads((Path(__file__).resolve().parents[1]/'fuentes/universo_asalariados.json').read_text())
    def referencias(n):
        items=[]; extras=[]
        for a in refs:
            if a['paso']!=n: continue
            x=a['pesos'] if 'pesos' in a else sum(a['totales'])/a['meses']
            tipo=a['tipo'].lower()
            if 'supuesto_cotizacion' in a:
                imponible=x*(1-a['supuesto_cotizacion'])
                assert 0 < imponible <= 3463250
                tasa,rebaja=(.04,37403.10) if imponible<=2077950 else (.08,120521.10)
                x=imponible-max(0,imponible*tasa-rebaja)
                tipo='líquido estimado'
            cifra=clp(x)
            signo='' if x==round(x/1000)*1000 else '≈ '
            shown=round(x/1000)*1000
            hits=[w for y,w in records if y>=shown]
            if len(hits)>=60:
                count=fmt(round(sum(hits)/1000)*1000)
                comparison=f'En la ESI 2025, ≈ {count} personas ganaban ese monto o más al mes.'
            elif hits:
                count=fmt(round(sum(hits)/100)*100)
                comparison=f'En la ESI 2025, ≈ {count} personas ganaban ese monto o más. Estimación exploratoria: solo {len(hits)} casos en la muestra.'
            else:
                comparison='Nadie en la muestra declaró un ingreso tan alto; eso no permite estimar cuántas personas lo recibían en Chile.'
            explore=' · <a href="https://lixandria.cl/preferences/" target="_blank" rel="noopener noreferrer">Explorar carreras en Lixandria</a>' if 'consulta' in a else ''
            (extras if a.get('extra') else items).append(f"""<div><h4>{escape(a['nombre'])}</h4><b>{signo}{cifra} <small>· {tipo} al mes</small></b><p>{escape(a['detalle'])} <a href="{escape(a['url'])}" target="_blank" rel="noopener noreferrer">{escape(a['fuente'])}</a>{explore}</p><p class="anchor-count">{comparison}</p></div>""")
        if not items: return ''
        if extras:
            more='otras carreras' if n==2 else 'otros cargos'
            items.append(f'<details class="extra-refs"><summary>Comparar {more} ({len(extras)})</summary>'+''.join(extras)+'</details>')
        if n==2:
            items.append(f'<details class="story-precision"><summary>Cómo estimamos el líquido de las carreras</summary><p>Mi Futuro publica promedios brutos. Simulamos el sueldo de una persona asalariada que ganara ese promedio: descontamos 18,7% por cotizaciones y luego el impuesto mensual según la <a href="{refs[1]["tabla_sii"]}">tabla del SII de septiembre de 2025</a>. El resultado es orientativo: no es un promedio observado de sueldos líquidos y puede diferir para quienes emiten boletas.</p></details>')
        return '<aside class="salary-refs"><span class="kicker">SUELDOS PARA COMPARAR</span>'+''.join(items)+'</aside>'
    # These two cutoffs do not fall on the explorer's $50,000 grid.
    import csv, gzip, math
    minimum=next(a for a in refs if a['paso']=='minimo')
    cutoffs=[minimum['neto_esi'], d['median']]
    weights=[0.,0.]
    total=0.;records=[]
    with gzip.open(Path(__file__).resolve().parents[1]/'datos/esi2025_columnas_necesarias.csv.gz','rt') as f:
        for r in csv.DictReader(f):
            if r['ocup_ref'] not in ('1','1.0') or int(r['edad'])<20: continue
            y,w=float(r['ing_t_p']),float(r['fact_cal_esi'])
            total+=w;records.append((y,w))
            for i,v in enumerate(cutoffs):
                if y>=v: weights[i]+=w
    assert math.isclose(total,d['N'],abs_tol=.01)
    fmt=lambda x:f'{round(x):,}'.replace(',','.')
    def result(amount,p,zoom=False):
        base=10000 if zoom else 100
        rate=p*base/100
        percent=(f'{p:.2f}' if zoom else f'{p:.1f}').replace('.',',')
        persons=fmt(round(total*p/100/1000)*1000)
        dots=''.join(f'<circle cx="{(i%10)*8+4}" cy="{(i//10)*8+4}" r="3" fill="{("#22694f" if i<round(rate) else "#d5dfd5")}"/>' for i in range(100))
        return f'<li data-rate="{p:.8f}"><span class="r-label">{amount}</span><svg class="proportion-dots" viewBox="0 0 80 80" aria-hidden="true">{dots}</svg><b>≈ {round(rate)} de {fmt(base)}</b><small><strong>≈ {persons} personas</strong> en Chile ganan este monto o más (≈ {percent}%).</small></li>'
    def rows(ns,zoom=False):
        return ''.join(result(('$1 millón' if n==1 else f'${n} millones'),d['curve']['p'][n*20],zoom) for n in ns)
    def caution(n):
        j=n*20;c=d['curve'];lo,hi=[f'{c[k][j]:.2f}'.replace('.',',') for k in ('lo','hi')]
        return f'${n} millones: {c["n"][j]} casos, intervalo del 95% entre {lo}% y {hi}%.'
    m=fmt(cutoffs[0])
    parts=[
        ('minimo','Sueldo mínimo','El sueldo mínimo de referencia',f'La ESI 2025 usa <strong>${m} netos al mes</strong> como sueldo mínimo de referencia. ¿Cuántas personas ganaban al menos esa cantidad en su trabajo principal?',result(f'${m} netos',100*weights[0]/total),f'<p class="story-foot">El INE calcula este mínimo descontando un 18,7% al mínimo legal de octubre de 2025. La encuesta también incluye independientes y personas con jornada parcial. <a href="{minimum["manual"]}">Manual ESI 2025, p. 12</a> · <a href="{minimum["url"]}">Mínimo legal</a></p>'),
        ('mediana','Mediana','¿Dónde está la mitad?',f'La mediana fue de <strong>≈ {clp(d["median"])} netos al mes</strong>. Si ordenas a las personas por ingreso, ese es el monto que encuentras al llegar a la mitad de la fila.',result(f'Mediana (≈ {clp(d["median"])})',100*weights[1]/total),''),
        ('millones','$1–4 millones','¿Cuántas personas llegan al millón?','Casi tres de cada diez. Al subir el monto a dos millones, queda cerca de una de cada diez. Cada fila incluye a quienes alcanzan ese monto y a quienes lo superan. Por eso, una persona que gana cuatro millones también cuenta en las filas anteriores.',rows([1,2,3,4]),referencias(2)),
        ('altos','$6–10 millones','Seis, ocho y diez millones, lado a lado','Aquí conviene pensar en <strong>10.000 personas ocupadas</strong>: menos de cien ganan seis millones netos o más. Ampliamos el 1% superior: cada punto verde es 1 persona de cada 10.000 del total. Los cien puntos juntos representan solo a las cien personas con más ingresos de esas 10.000.',rows([6,8,10],True),'<details class="story-precision"><summary>¿Qué tan precisas son las cifras de $8 y $10 millones?</summary><p>Son estimaciones exploratorias por el bajo número de casos en la encuesta. '+caution(8)+' '+caution(10)+'</p></details>'+referencias(10))]
    nav=''.join(f'<a href="#relato-{k}"><small>0{i}</small> {label}</a>' for i,(k,label,*_) in enumerate(parts,1))
    steps=''.join(f'<article class="story-step" id="relato-{k}"><p class="kicker">0{i} / 04</p><h3>{title}</h3><p>{intro}</p><p class="story-caption">Ingreso neto mensual igual o mayor a · {"1 punto = 1 de cada 10.000" if k=="altos" else "1 punto = 1 de cada 100"}</p><ul class="rate-list">{graphics}</ul>{notes}</article>' for i,(k,label,title,intro,graphics,notes) in enumerate(parts,1))
    story=f"""<section class="read-story" id="relato" aria-labelledby="story-title"><p class="kicker">01 &nbsp; / &nbsp; PANORAMA NACIONAL</p>
    <h2 id="story-title">Del sueldo mínimo a los diez millones</h2><p class="story-intro">¿Cuántas personas en Chile llegan a cada monto? Seguimos el ingreso neto mensual de quienes trabajan y tienen 20 años o más. Todos los montos que comparamos son netos. Cuando el líquido es una estimación, lo indicamos junto al monto.</p>
    <div class="survey-universe"><strong>¿A cuántas personas representa esta encuesta?</strong><p>Las {fmt(d["n"])} personas encuestadas incluidas en este recorrido representan a <b>≈ {fmt(round(total/1000)*1000)} personas ocupadas</b> de 20 años o más, con al menos un mes en su empleo. De ellas, <b>≈ {fmt(round((total-d["zeroN"])/1000)*1000)} tenían ingreso positivo</b> en su trabajo principal. Los porcentajes del recorrido usan el total de ocupados, incluidos quienes declararon cero. Se excluye a las personas desocupadas.</p><details><summary>¿Cuántas eran asalariadas?</summary><p>De ese total, ≈ {fmt(round(salaried["asalariados"]/1000)*1000)} eran asalariadas del sector público o privado, y ≈ {fmt(round(salaried["asalariados_con_ingreso"]/1000)*1000)} de ellas tenían ingreso positivo. El resto del universo incluye, entre otros, a quienes trabajan por cuenta propia.</p></details></div>
    <div class="story-layout"><nav class="story-index" aria-label="Etapas del recorrido">{nav}</nav><div class="story-steps">{steps}</div></div></section>"""
    return hero, story
