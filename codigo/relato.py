"""Build the national reading guide from the same survey records as the explorer."""
import csv
import gzip
import json
import math
from pathlib import Path

from .referencias_salariales import ejemplos_cargos, ejemplos_carreras, numero, pesos


ROOT = Path(__file__).resolve().parents[1]


def porcentaje(valor, decimales=1):
    return f'{valor:.{decimales}f}'.replace('.', ',') + '%'


def miles(personas):
    return numero(round(personas / 1000) * 1000)


def portada(nacional, bajo_promedio):
    def barra(etiqueta, clave):
        monto = nacional[clave]
        ancho = 100 * monto / max(nacional['mean'], nacional['median'])
        return f'''<div class="income-row {clave}"><div><span>{etiqueta}</span><strong>≈ {pesos(monto)}</strong></div>
          <i aria-hidden="true" style="width:{ancho:.2f}%"></i></div>'''

    return f'''<section class="cover" aria-labelledby="title">
      <div class="cover-copy">
        <p class="kicker">ENCUESTA SUPLEMENTARIA DE INGRESOS 2025</p>
        <h1 id="title">Ingresos netos<br><em>en Chile</em></h1>
        <p class="cover-lead">¿Cuántas personas ganan lo mismo que tú o más?</p>
        <p class="cover-definition">Para asalariados, el ingreso neto es lo que queda tras cotizaciones e impuestos. Para quienes trabajan por cuenta propia, se descuentan los costos de la actividad.</p>
      </div>
      <aside class="cover-figure" aria-labelledby="cover-finding">
        <img class="cover-illustration" src="__PORTADA_IMAGEN__" alt="" width="1152" height="480">
        <div class="cover-figure-detail"><h2 id="cover-finding"><strong>{round(bajo_promedio / 10)} de cada 10</strong> ganan menos que el promedio.</h2>
          {barra('Mediana', 'median')}{barra('Promedio', 'mean')}
          <p>Los ingresos más altos elevan el promedio. En 2025, el {porcentaje(bajo_promedio)} de las personas ocupadas de 20 años o más ganó menos que esa cifra.</p></div>
      </aside>
      <nav class="cover-actions" aria-label="Explorar los ingresos"><a class="cover-primary" href="#relato">Recorrer las cifras ↓</a><a href="#explorar">Comparar mi ingreso</a><a href="#sueldos-por-carrera">Ver sueldos por carrera</a></nav>
      <p class="cover-source">Fuente: INE, ESI 2025. Ingreso mensual del trabajo principal de personas ocupadas de 20 años o más, en pesos de octubre de 2025.</p>
    </section>'''


def distribucion_completa(registros, total, minimo):
    # Incomes in the ESI extract are non-negative. The last band has no upper limit.
    tramos = [
        ('Sin ingreso ($0)', '#bdc7bb'),
        ('Sobre $0 y bajo el mínimo', '#cb9d64'),
        ('Del mínimo a menos de $1 millón', '#246752'),
        ('De $1 millón a menos de $2 millones', '#80ad95'),
        ('$2 millones o más', '#344e44'),
    ]
    pesos_tramo = [0.0] * len(tramos)
    for ingreso, factor in registros:
        if ingreso < 0:
            raise ValueError('La distribución por tramos requiere revisar los ingresos negativos.')
        if ingreso == 0:
            indice = 0
        elif ingreso < minimo:
            indice = 1
        elif ingreso < 1_000_000:
            indice = 2
        elif ingreso < 2_000_000:
            indice = 3
        else:
            indice = 4
        pesos_tramo[indice] += factor
    assert math.isclose(sum(pesos_tramo), total, abs_tol=.01)

    segmentos = []
    claves = []
    for (etiqueta, color), peso in zip(tramos, pesos_tramo):
        proporcion = 100 * peso / total
        segmentos.append(f'<i style="width:{proporcion:.8f}%;background:{color}"></i>')
        claves.append(f'''<li data-share="{proporcion:.8f}" style="--band-color:{color}">
          <strong>{porcentaje(proporcion)}</strong><span>{etiqueta}</span></li>''')
    return f'''<figure class="income-band" id="distribucion-completa" aria-labelledby="band-title">
      <figcaption id="band-title">Casi la mitad gana entre el mínimo y un millón.</figcaption>
      <div class="income-band-strip" aria-hidden="true">{''.join(segmentos)}</div>
      <ul class="income-band-key">{''.join(claves)}</ul>
      <p>Cada persona ocupa un solo tramo. El mínimo de referencia es de ${numero(minimo)} netos al mes.</p>
    </figure>'''


def pictograma(etiqueta, proporcion, total, comparacion, ampliado=False):
    base = 10_000 if ampliado else 100
    puntos = round(proporcion * base / 100)
    circulos = []
    for i in range(100):
        color = '#22694f' if i < puntos else '#d5dfd5'
        circulos.append(f'<circle cx="{(i % 10) * 8 + 4}" cy="{(i // 10) * 8 + 4}" r="3" fill="{color}"/>')
    personas = miles(total * proporcion / 100)
    return f'''<li data-rate="{proporcion:.8f}" data-comparison="{comparacion}"><span class="r-label">{etiqueta}</span>
      <svg class="proportion-dots" viewBox="0 0 80 80" aria-hidden="true">{''.join(circulos)}</svg>
      <b>≈ {puntos} de {numero(base)}</b><small><strong>≈ {personas} personas</strong> ({porcentaje(proporcion, 2 if ampliado else 1)})</small></li>'''


def relato(data):
    nacional = data['domains']['all|all|all']
    referencias = json.loads((ROOT / 'fuentes/referencias_salariales.json').read_text())
    asalariados = json.loads((ROOT / 'fuentes/universo_asalariados.json').read_text())
    minimo = next(ref for ref in referencias if ref['paso'] == 'minimo')
    monto_minimo = minimo['neto_esi']

    registros = []
    with gzip.open(ROOT / 'datos/esi2025_columnas_necesarias.csv.gz', 'rt') as archivo:
        for fila in csv.DictReader(archivo):
            if fila['ocup_ref'] in ('1', '1.0') and int(fila['edad']) >= 20:
                registros.append((float(fila['ing_t_p']), float(fila['fact_cal_esi'])))
    total = sum(factor for ingreso, factor in registros)
    assert math.isclose(total, nacional['N'], abs_tol=.01)
    bajo_minimo = 100 * sum(factor for ingreso, factor in registros if ingreso < monto_minimo) / total
    bajo_promedio = 100 * sum(factor for ingreso, factor in registros if ingreso < nacional['mean']) / total
    # dashboard.json stores monetary values to six decimal places. Compare both
    # sides at that precision so observations exactly at the median remain included.
    mediana = nacional['median']
    hasta_mediana = 100 * sum(factor for ingreso, factor in registros if round(ingreso, 6) <= mediana) / total
    curva = nacional['curve']

    def cuadros_millones(montos, ampliado=False):
        partes = []
        for millones in montos:
            cantidad = '$1 millón' if millones == 1 else f'${millones} millones'
            partes.append(pictograma(cantidad + ' o más', curva['p'][millones * 20], total, 'ge', ampliado))
        return ''.join(partes)

    def precision(millones):
        indice = millones * 20
        inferior = porcentaje(curva['lo'][indice], 2)
        superior = porcentaje(curva['hi'][indice], 2)
        return f'Para ${millones} millones o más hubo {curva["n"][indice]} casos. El intervalo del 95% va de {inferior} a {superior}.'

    nota_minimo = f'''<p class="story-foot">El INE calcula el mínimo neto con un descuento de 18,7% sobre el mínimo legal de octubre de 2025. La encuesta incluye a independientes y a quienes trabajan a jornada parcial. <a href="{minimo["manual"]}">Manual del INE, p. 12</a> · <a href="{minimo["url"]}">Mínimo legal</a>.</p>'''
    nota_altos = f'''<details class="story-precision"><summary>¿Qué precisión tienen las cifras más altas?</summary>
      <p>{precision(8)} {precision(10)} Son estimaciones exploratorias porque hay pocos casos observados.</p></details>'''
    partes = [
        ('minimo', 'El mínimo', '<em>1 de cada 5</em> gana menos que el mínimo.',
         pictograma(f'Menos de ${numero(monto_minimo)}', bajo_minimo, total, 'lt'),
         'Cada punto representa a una de 100 personas ocupadas. En verde aparecen quienes quedaron bajo el mínimo de referencia.',
         nota_minimo),
        ('mediana', 'La mitad', f'La mitad gana hasta <em>unos {pesos(mediana)}.</em>',
         pictograma('Hasta la mediana', hasta_mediana, total, 'le'),
         f'Si ordenas a las personas por ingreso, la del centro recibe unos {pesos(mediana)} al mes. Los puntos verdes llegan hasta ese lugar de la fila.',
         ''),
        ('millones', 'Desde un millón', '<em>3 de cada 10</em> llegan al millón.',
         cuadros_millones([1, 2, 3, 4]),
         'Cada cuadro vuelve a mirar a las mismas 100 personas. Quien gana $4 millones o más aparece en verde en los cuatro.',
         ejemplos_carreras(referencias, registros, total, mediana)),
        ('altos', 'Los ingresos más altos', 'A <em>$6 millones</em> llega menos del 1%.',
         cuadros_millones([6, 8, 10], ampliado=True),
         'Aquí ampliamos el 1% superior. Los cien puntos muestran a las cien personas con más ingresos de un grupo de 10.000. En verde están quienes alcanzan cada monto, incluidos los que ganan más de $10 millones.',
         nota_altos + ejemplos_cargos(referencias, registros, mediana)),
    ]
    nav = []
    historias = []
    for indice, (clave, etiqueta, titulo, cuadros, explicacion, contexto) in enumerate(partes, 1):
        nav.append(f'<a href="#relato-{clave}"><small>0{indice}</small> {etiqueta}</a>')
        escala = '1 punto = 1 de cada 10.000 personas · se muestra el 1% superior' if clave == 'altos' else '1 punto = 1 de cada 100 personas'
        historias.append(f'''<article class="story-step" id="relato-{clave}">
          <p class="kicker">{etiqueta.upper()}</p><h3>{titulo}</h3>
          <figure class="threshold-figure"><p class="story-scale">{escala}</p>
            <ul class="rate-list">{cuadros}</ul><figcaption class="story-caption">{explicacion}</figcaption></figure>
          {contexto}</article>''')

    historia = f'''<section class="read-story" id="relato" aria-labelledby="story-title">
      <p class="kicker">PANORAMA NACIONAL</p><h2 id="story-title">Los ingresos de Chile, de menor a mayor</h2>
      {distribucion_completa(registros, total, monto_minimo)}
      <details class="survey-universe"><summary>¿A quiénes representa la encuesta?</summary>
        <p>Las {numero(nacional["n"])} personas encuestadas representan a unas {miles(total)} personas ocupadas de 20 años o más, con al menos un mes en su empleo. Unas {miles(total - nacional["zeroN"])} recibieron ingresos por su trabajo principal y unas {miles(nacional["zeroN"])} declararon cero. La distribución incluye a ambos grupos.</p>
        <p>De ese total, unas {miles(asalariados["asalariados"])} personas trabajaban como asalariadas del sector público o privado y unas {miles(asalariados["asalariados_con_ingreso"])} de ellas recibieron ingresos. También se cuentan beneficios en especie, como alimentos que se reciben como parte del pago.</p>
      </details>
      <div class="story-layout"><nav class="story-index" aria-label="Etapas del recorrido">{''.join(nav)}</nav>
        <div class="story-steps">{''.join(historias)}</div></div></section>'''
    return portada(nacional, bajo_promedio), historia
