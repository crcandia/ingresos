"""Place documented salary examples on the national ESI income distribution."""
from html import escape
from statistics import median


def numero(value):
    return f'{round(value):,}'.replace(',', '.')


def pesos(value):
    return '$' + numero(round(value / 1000) * 1000)


def porcentaje(value):
    return f'{value:.1f}'.replace('.', ',') + '%'


def liquido_estimado(referencia):
    """Simulate a wage earner at Mi Futuro's gross mean using September 2025 tax."""
    imponible = referencia['pesos'] * (1 - referencia['supuesto_cotizacion'])
    if not 0 < imponible <= 3_463_250:
        raise ValueError('La referencia requiere revisar los tramos de impuesto de septiembre de 2025.')
    tasa, rebaja = (.04, 37_403.10) if imponible <= 2_077_950 else (.08, 120_521.10)
    return imponible - max(0, imponible * tasa - rebaja)


def sobre_umbral(registros, monto):
    # Compare the exact threshold readers see on the page, including equal incomes.
    pesos_mostrados = round(monto / 1000) * 1000
    factores = [factor for ingreso, factor in registros if ingreso >= pesos_mostrados]
    return len(factores), sum(factores)


TITULO_CARRERAS = 'El millón queda entre Psicología y Enfermería'


def grafico_sueldos(titulo, grupos, mediana_nacional, nota):
    """One linear scale for every row in this figure, including the national median."""
    maximo = max([mediana_nacional] + [monto for _, filas in grupos for _, monto, _ in filas])

    def barra(nombre_html, monto, contexto, referencia=False):
        multiplo = monto / mediana_nacional
        veces = f'{multiplo:.1f}'.replace('.', ',').removesuffix(',0')
        clase = ' class="cargo-reference"' if referencia else ''
        return f'''<li{clase} data-multiple="{multiplo:.6f}">
          <div class="cargo-row-head"><span>{nombre_html}</span><b>{veces}×</b></div>
          <span class="cargo-track" aria-hidden="true"><i style="width:{100 * monto / maximo:.5f}%"></i></span>
          <small><strong>≈ {pesos(monto)}</strong> · {escape(contexto)}</small></li>'''

    base = barra('Ingreso mediano en Chile', mediana_nacional, 'ESI 2025, personas ocupadas de 15 años o más', True)
    listas = [f'<ul class="cargo-bars base-nacional">{base}</ul>']
    for grupo, filas in grupos:
        if grupo:
            listas.append(f'<h5 class="salary-group">{escape(grupo)}</h5>')
        listas.append('<ul class="cargo-bars">' + ''.join(barra(*fila) for fila in filas) + '</ul>')
    return f'''<figure class="cargo-figure comparison-figure" style="--median-position:{100 * mediana_nacional / maximo:.5f}%">
        <figcaption>{escape(titulo)}</figcaption>{''.join(listas)}<p>{escape(nota)}</p></figure>'''


def ejemplos_carreras(referencias, registros, total, mediana_nacional):
    por_nombre = {}
    for ref in referencias:
        if ref['paso'] != 2:
            continue
        if ref['consulta']['campo'] != 'tercer_ano':
            raise ValueError(f"La comparación requiere ingresos al tercer año para {ref['nombre']}.")
        monto = liquido_estimado(ref)
        casos, personas = sobre_umbral(registros, monto)
        if casos < 60:
            raise ValueError(f"Revisar la precisión del umbral de {ref['nombre']} antes de publicarlo.")
        url = f"https://lixandria.cl/preferences/{int(ref['lixandria_id'])}%7C%7C0"
        link = f'<a href="{url}">{escape(ref["nombre"])}</a>'
        por_nombre[ref['nombre']] = dict(ref, link=link, monto=monto, neto=pesos(monto), personas=personas, tasa=100 * personas / total)

    psico = por_nombre['Psicología']
    enfermeria = por_nombre['Enfermería']
    comercial = por_nombre['Ingeniería Comercial']
    derecho = por_nombre['Derecho']
    fuente = escape(psico['url'], quote=True)
    sii = escape(psico['tabla_sii'], quote=True)

    alcanzan_psico = round(psico['tasa'])
    alcanzan_enfermeria = round(enfermeria['tasa'])
    # Both counts refer to the same hundred people. The higher threshold is nested.
    grupos = (['both'] * alcanzan_enfermeria
              + ['first-only'] * (alcanzan_psico - alcanzan_enfermeria)
              + ['rest'] * (100 - alcanzan_psico))
    puntos = ''.join(f'<circle class="career-dot-{grupo}" cx="{i % 10 * 8 + 4}" cy="{i // 10 * 8 + 4}" r="3"/>'
                     for i, grupo in enumerate(grupos))
    diferencia = pesos(abs(comercial['monto'] - derecho['monto']))
    # Compare the common rounded landmark with all earners. Individual rates stay in the table.
    umbral_comun = round((comercial['monto'] + derecho['monto']) / 2 / 100_000) * 100_000
    millones = f'{umbral_comun / 1_000_000:.1f}'.replace('.', ',')
    _, personas = sobre_umbral(registros, umbral_comun)
    alcanzan_umbral = round(100 * personas / total)

    filas = []
    barras = []
    for carrera in sorted(por_nombre.values(), key=lambda r: r['pesos']):
        cantidad = numero(round(carrera['personas'] / 1000) * 1000)
        barras.append((carrera['link'], carrera['monto'],
                       f'{porcentaje(carrera["tasa"])} gana ese monto o más en Chile'))
        filas.append(f'''<tr><th scope="row">{carrera["link"]}</th>
          <td><strong>{carrera["neto"]}</strong><small>Bruto: ${numero(carrera["pesos"])}</small></td>
          <td><strong>{porcentaje(carrera["tasa"])}</strong><small>≈ {cantidad} personas</small></td></tr>''')

    grafico = grafico_sueldos('Cuántos ingresos medianos representa cada carrera', [(None, barras)], mediana_nacional,
        'Las barras muestran el líquido estimado al tercer año de titulación. El porcentaje cuenta a las personas ocupadas de 15 años o más en Chile que ganan ese monto o más, cualquiera sea su formación.')
    return f'''<section class="salary-story career-story" id="sueldos-por-carrera" aria-labelledby="career-title">
      <h4 id="career-title">{TITULO_CARRERAS}</h4>
      <figure class="career-hundred">
        <svg class="career-people" viewBox="0 0 80 80" width="144" height="144" aria-hidden="true">{puntos}</svg>
        <div class="career-outcomes">
          <div class="career-outcome"><span class="career-key" aria-hidden="true"><i></i><i class="career-key-ring"></i></span>
            <div><strong class="career-count">{alcanzan_psico} <small>de 100</small></strong>
            <span>personas ocupadas en Chile ganaban al menos <b>{psico["neto"]}</b> al mes, el líquido estimado en {psico["link"]}.</span></div></div>
          <div class="career-outcome"><span class="career-key" aria-hidden="true"><i></i></span>
            <div><strong class="career-count">{alcanzan_enfermeria} <small>de 100</small></strong>
            <span>llegaban también a <b>{enfermeria["neto"]}</b>, el líquido estimado en {enfermeria["link"]}.</span></div></div>
        </div>
        <figcaption>Cada punto representa a una de cada 100 personas ocupadas de 15 años o más en Chile (ESI 2025). Para cada carrera estimamos el líquido a partir del ingreso bruto promedio al tercer año de titulación (Mi Futuro).</figcaption>
      </figure>
      <p class="career-next">Unos <strong>{diferencia}</strong> separan a {comercial["link"]} de {derecho["link"]}. Ambas rondan los ${millones} millones líquidos. En Chile, <strong>{alcanzan_umbral} de cada 100</strong> personas ocupadas ganaban esa suma o más.</p>
      <details class="salary-detail salary-comparator"><summary>Comparar las {len(por_nombre)} carreras</summary>
        <div id="comparador-carreras"><p>Desde educación de párvulos hasta medicina, las barras ordenan el líquido estimado al tercer año de titulación. El nombre de cada carrera lleva a sus opciones de estudio en Lixandria.</p>
        {grafico}</div>
        <details class="salary-detail salary-values"><summary>Ver sueldos brutos y cuántas personas alcanzan cada monto</summary>
        <table class="career-table"><caption>Ingresos mensuales al tercer año y su lugar en la distribución nacional</caption>
        <thead><tr><th scope="col">Carrera universitaria</th><th scope="col">Líquido estimado</th><th scope="col">Ganan ese monto o más en Chile</th></tr></thead><tbody>{''.join(filas)}</tbody></table>
        </details>
        <p class="salary-source">La selección incluye las cuatro carreras con más estudiantes de primer año en 2026 y otras de áreas como computación, minería, salud, educación y diseño. <a href="https://www.mifuturo.cl/wp-content/uploads/2026/07/Informe-de-Matr%C3%ADcula-2026.pdf#page=25">Matrícula universitaria del SIES, p. 25</a>.</p>
      </details>
      <details class="salary-detail"><summary>De dónde salen los sueldos y cómo estimamos el líquido</summary>
        <p>Mi Futuro publica ingresos brutos. Para estimar qué recibiría una persona asalariada con ese ingreso medio, descontamos un 18,7% por cotizaciones y aplicamos el impuesto de septiembre de 2025. El monto efectivo depende de los descuentos personales. <a href="{fuente}">Estadísticas por carrera de Mi Futuro</a> · <a href="{sii}">Tabla de impuesto del SII</a>.</p>
        <p>Mi Futuro usa los ingresos anuales declarados al SII en 2022, 2023 y 2024, divididos por doce. Incluye a quienes alcanzaron el equivalente anual del sueldo mínimo. En Derecho ajusta un año por el tiempo entre la licenciatura y el título. <a href="https://www.mifuturo.cl/wp-content/uploads/2025/12/Metodologia-Estadisticas-por-Carrera_2025-2026.pdf#page=5">Metodología de Mi Futuro</a>.</p>
        <p>Las carreras están en pesos de septiembre de 2025. Para cada líquido estimado, redondeado a mil pesos, contamos cuántas personas ocupadas de 15 años o más alcanzaron ese monto en su trabajo principal en la ESI, expresada en pesos de octubre. Ese porcentaje se refiere a personas de todas las carreras y niveles educativos.</p>
      </details></section>'''


def ejemplos_cargos(referencias, registros, mediana_nacional):
    cargos = []
    for ref in referencias:
        if ref['paso'] != 10:
            continue
        if 'totales' in ref:
            monto = sum(ref['totales']) / ref['meses']
        elif 'liquidos_individuales' in ref:
            monto = median(ref['liquidos_individuales'])
        elif 'liquidos_jueces' in ref:
            monto = median(ref['liquidos_jueces'])
        else:
            monto = ref['pesos']
        casos, personas = sobre_umbral(registros, monto)
        cargos.append(dict(ref, monto=monto, multiplo=monto / mediana_nacional, casos=casos, personas=personas))

    cargos.sort(key=lambda cargo: cargo['monto'])
    tvn = next(cargo for cargo in cargos if cargo['nombre'] == 'Directora ejecutiva de TVN')
    codelco = next(cargo for cargo in cargos if cargo['nombre'] == 'Presidente ejecutivo de Codelco')
    diputado = next(cargo for cargo in cargos if cargo['nombre'] == 'Diputado José Carlos Meza')
    electos, otros = [], []
    filas = []
    for cargo in cargos:
        contexto = [cargo['periodo']]
        if 'contexto_grafico' in cargo:
            contexto.append(cargo['contexto_grafico'])
        fuentes_adicionales = []
        if 'habitantes_censo2024' in cargo:
            habitantes = f'{numero(cargo["habitantes_censo2024"])} habitantes'
            contexto.append(habitantes)
            fuentes_adicionales.append(f'<small>{habitantes} según el <a href="{escape(cargo["url_censo"], quote=True)}">Censo 2024</a>.</small>')
        if 'url_bruto' in cargo:
            fuentes_adicionales.append(f'<small>Bruto del mes: ${numero(cargo["pesos_brutos"])} según el <a href="{escape(cargo["url_bruto"], quote=True)}">Registro de Remuneraciones</a>.</small>')
        if 'id_pagina_cplt' in cargo:
            fuentes_adicionales.append(f'<small>Nómina {escape(cargo["id_pagina_cplt"])} del <a href="https://consejotransparencia.cl/datosabiertos/">Consejo para la Transparencia</a>.</small>')
        grupo = electos if cargo.get('eleccion_popular') else otros
        grupo.append((escape(cargo.get('etiqueta_grafico', cargo['nombre'])), cargo['monto'], ' · '.join(contexto)))
        casos = cargo['casos']
        if casos >= 60:
            poblacion = numero(round(cargo['personas'] / 1000) * 1000)
            encuesta = f'≈ {poblacion} personas en Chile ({casos} casos en la muestra).'
        elif casos:
            encuesta = f'{casos} casos en la muestra. Poca precisión para estimar el total nacional.'
        else:
            encuesta = 'Ningún caso en la muestra. La encuesta no permite estimar el total nacional.'
        filas.append(f'''<tr><th scope="row">{escape(cargo['nombre'])}
            <a href="{escape(cargo['url'], quote=True)}">{escape(cargo['fuente'])}</a></th>
          <td><strong>${numero(cargo['monto'])}</strong><small>{escape(cargo['periodo'])}</small>
              <small>{escape(cargo['detalle'])}</small>{''.join(fuentes_adicionales)}</td>
          <td>{encuesta}</td></tr>''')

    grafico = grafico_sueldos('Cuántos ingresos medianos caben en cada sueldo',
        [('Autoridades de elección popular', electos), ('Tribunales, universidad y empresas públicas', otros)],
        mediana_nacional, 'Todas las barras usan la misma escala. Las cifras son líquidas y corresponden al período indicado. En las alcaldías, los habitantes corresponden al Censo 2024.')
    curepto = next(c for c in cargos if c['nombre'] == 'Alcalde de Curepto')
    valparaiso = next(c for c in cargos if c['nombre'] == 'Alcaldesa de Valparaíso')
    if curepto['periodo'] != valparaiso['periodo']:
        raise ValueError('La comparación de alcaldías requiere liquidaciones del mismo mes.')
    razon_habitantes = round(valparaiso['habitantes_censo2024'] / curepto['habitantes_censo2024'])
    diferencia_alcaldias = pesos(valparaiso['monto'] - curepto['monto'])
    millones_codelco = f'{codelco["monto"] / 1_000_000:.1f}'.replace('.', ',')
    return f'''<section class="salary-story public-salaries" id="sueldos-de-altos-cargos" aria-labelledby="public-salary-title">
      <h4 id="public-salary-title"><em>{round(tvn["multiplo"])} veces</em> el ingreso mediano</h4>
      <p>En 2025, la directora ejecutiva de TVN recibió en promedio <strong>{pesos(tvn["monto"])} líquidos al mes</strong>. En la ESI, la mitad de las personas ocupadas ganaba hasta unos {pesos(mediana_nacional)} al mes.</p>
      {grafico}
      <p>En octubre de 2025, las {diputado['personas_registro_bruto']} personas que figuran en el <a href="{escape(diputado['url_bruto'], quote=True)}">registro de diputadas y diputados</a> tuvieron la misma dieta bruta de <strong>${numero(diputado['pesos_brutos'])}</strong>. Los descuentos personales cambian el líquido. La barra muestra el que publicó José Carlos Meza para ese mes.</p>
      <p class="municipal-comparison">Valparaíso tenía unas <strong>{razon_habitantes} veces</strong> la población de Curepto. En {valparaiso['periodo'].lower()}, su alcaldesa recibió unos <strong>{diferencia_alcaldias} líquidos más</strong> que el alcalde de Curepto. Ambas liquidaciones incluyen incentivos.</p>
      <p class="cargo-tail"><strong>${millones_codelco} millones al mes</strong> promedió la presidencia ejecutiva de Codelco entre noviembre de 2025 y octubre de 2026, sumando lo pagado a sus dos titulares. Ninguna persona de la muestra de la ESI alcanzó ese monto.</p>
      <details class="salary-detail cargo-detail"><summary>Ver los {len(cargos)} cargos, sus fechas y fuentes</summary>
        <p>Cada cifra corresponde al cargo y período indicados. La última columna cuenta los casos de la ESI que alcanzaron el mismo monto neto mensual en su trabajo principal, redondeado a mil pesos. Las remuneraciones están en pesos de su período y la encuesta, en pesos de octubre de 2025.</p>
        <table class="cargo-table"><caption>Remuneraciones líquidas y referencias de la encuesta</caption>
        <thead><tr><th scope="col">Cargo y fuente</th><th scope="col">Monto mensual</th><th scope="col">Alcanzaron ese monto en la ESI</th></tr></thead>
        <tbody>{''.join(filas)}</tbody></table>
      </details></section>'''
