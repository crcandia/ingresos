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


def ejemplos_carreras(referencias, registros, total):
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
    industrial = por_nombre['Ingeniería Civil Industrial']
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

    filas = []
    for carrera in sorted(por_nombre.values(), key=lambda r: r['pesos']):
        cantidad = numero(round(carrera['personas'] / 1000) * 1000)
        filas.append(f'''<tr><th scope="row">{carrera["link"]}</th>
          <td><strong>{carrera["neto"]}</strong><small>Bruto: ${numero(carrera["pesos"])}</small></td>
          <td><strong>{porcentaje(carrera["tasa"])}</strong><small>≈ {cantidad} personas</small></td></tr>''')

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
        <figcaption>Cada punto representa a una de cada 100 personas ocupadas de 20 años o más en Chile (ESI 2025). Para cada carrera estimamos el líquido a partir del ingreso bruto promedio al tercer año de titulación (Mi Futuro).</figcaption>
      </figure>
      <p class="career-next">Más arriba, {comercial["link"]} y {derecho["link"]} rondan los $1,6 millones líquidos, con unos <strong>{diferencia}</strong> de diferencia. Cerca de {round(comercial["tasa"])} de cada 100 personas ocupadas alcanzaban esos montos.</p>
      <details class="salary-detail"><summary>Comparar las ocho carreras</summary>
        <p>Cerca de los dos millones aparece {industrial["link"]}, con un líquido estimado de <strong>{industrial["neto"]}</strong>. Puedes abrir el nombre de cada carrera para explorar sus alternativas en Lixandria.</p>
        <table class="career-table"><caption>Ingresos mensuales al tercer año y su lugar en la distribución nacional</caption>
        <thead><tr><th scope="col">Carrera universitaria</th><th scope="col">Líquido estimado</th><th scope="col">Ganan ese monto o más en Chile</th></tr></thead><tbody>{''.join(filas)}</tbody></table>
        <p class="salary-source">Psicología, Ingeniería Comercial, Derecho y Enfermería fueron las cuatro carreras con más estudiantes de primer año en las universidades chilenas en 2026. <a href="https://www.mifuturo.cl/wp-content/uploads/2026/07/Informe-de-Matr%C3%ADcula-2026.pdf#page=25">Informe de matrícula del SIES, p. 25</a>.</p>
      </details>
      <details class="salary-detail"><summary>De dónde salen los sueldos y cómo estimamos el líquido</summary>
        <p>Mi Futuro publica ingresos brutos. Para estimar qué recibiría una persona asalariada con ese ingreso medio, descontamos un 18,7% por cotizaciones y aplicamos el impuesto de septiembre de 2025. El monto efectivo depende de los descuentos personales. <a href="{fuente}">Estadísticas por carrera de Mi Futuro</a> · <a href="{sii}">Tabla de impuesto del SII</a>.</p>
        <p>Mi Futuro usa los ingresos anuales declarados al SII en 2022, 2023 y 2024, divididos por doce. Incluye a quienes alcanzaron el equivalente anual del sueldo mínimo. En Derecho ajusta un año por el tiempo entre la licenciatura y el título. <a href="https://www.mifuturo.cl/wp-content/uploads/2025/12/Metodologia-Estadisticas-por-Carrera_2025-2026.pdf#page=5">Metodología de Mi Futuro</a>.</p>
        <p>Las carreras están en pesos de septiembre de 2025. Para cada líquido estimado, redondeado a mil pesos, contamos cuántas personas ocupadas de 20 años o más alcanzaron ese monto en su trabajo principal en la ESI, expresada en pesos de octubre. Ese porcentaje se refiere a personas de todas las carreras y niveles educativos.</p>
      </details></section>'''


def ejemplos_cargos(referencias, registros, mediana_nacional):
    cargos = []
    for ref in referencias:
        if ref['paso'] != 10:
            continue
        if 'totales' in ref:
            monto = sum(ref['totales']) / ref['meses']
        elif 'liquidos_jueces' in ref:
            monto = median(ref['liquidos_jueces'])
        else:
            monto = ref['pesos']
        casos, personas = sobre_umbral(registros, monto)
        cargos.append(dict(ref, monto=monto, multiplo=monto / mediana_nacional, casos=casos, personas=personas))

    cargos.sort(key=lambda cargo: cargo['monto'])
    destacados = [cargo for cargo in cargos if 'etiqueta_grafico' in cargo]
    tvn = next(cargo for cargo in cargos if cargo['nombre'] == 'Directora ejecutiva de TVN')
    codelco = next(cargo for cargo in cargos if cargo['nombre'] == 'Presidente ejecutivo de Codelco')
    maximo = max(cargo['multiplo'] for cargo in destacados)

    def barra(nombre, monto, periodo, multiplo, es_referencia=False):
        ancho = 100 * multiplo / maximo
        veces = f'{multiplo:.1f}'.replace('.', ',').removesuffix(',0')
        clase = ' class="cargo-reference"' if es_referencia else ''
        return f'''<li{clase} data-multiple="{multiplo:.6f}">
          <div class="cargo-row-head"><span>{escape(nombre)}</span><b>{veces}×</b></div>
          <span class="cargo-track" aria-hidden="true"><i style="width:{ancho:.5f}%"></i></span>
          <small>≈ {pesos(monto)} · {escape(periodo)}</small></li>'''

    barras = [barra('Ingreso mediano en Chile', mediana_nacional, 'ESI 2025, personas ocupadas de 20 años o más', 1, True)]
    barras.extend(barra(c['etiqueta_grafico'], c['monto'], c['periodo'], c['multiplo']) for c in destacados)
    filas = []
    for cargo in cargos:
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
              <small>{escape(cargo['detalle'])}</small></td>
          <td>{encuesta}</td></tr>''')

    millones_codelco = f'{codelco["monto"] / 1_000_000:.1f}'.replace('.', ',')
    return f'''<section class="salary-story public-salaries" id="sueldos-de-altos-cargos" aria-labelledby="public-salary-title">
      <h4 id="public-salary-title"><em>{round(tvn["multiplo"])} veces</em> el ingreso mediano</h4>
      <p>En 2025, la directora ejecutiva de TVN recibió en promedio <strong>{pesos(tvn["monto"])} líquidos al mes</strong>. En la ESI, la mitad de las personas ocupadas ganaba hasta unos {pesos(mediana_nacional)} al mes.</p>
      <figure class="cargo-figure"><figcaption>Cuántos ingresos medianos caben en cada sueldo</figcaption>
        <ul class="cargo-bars">{''.join(barras)}</ul>
        <p>La primera barra equivale a un ingreso mediano. Para los jueces usamos la mediana de los seis titulares del tribunal. Para la rectora usamos el líquido legal que informa la universidad.</p></figure>
      <p class="cargo-tail"><strong>${millones_codelco} millones al mes</strong> promedió la presidencia ejecutiva de Codelco entre noviembre de 2025 y octubre de 2026, sumando lo pagado a sus dos titulares. Ninguna persona de la muestra de la ESI alcanzó ese monto.</p>
      <details class="salary-detail cargo-detail"><summary>Ver los {len(cargos)} cargos, sus fechas y fuentes</summary>
        <p>Cada cifra corresponde al cargo y período indicados. La última columna cuenta los casos de la ESI que alcanzaron el mismo monto neto mensual en su trabajo principal, redondeado a mil pesos. Las remuneraciones están en pesos de su período y la encuesta, en pesos de octubre de 2025.</p>
        <table class="cargo-table"><caption>Remuneraciones líquidas y referencias de la encuesta</caption>
        <thead><tr><th scope="col">Cargo y fuente</th><th scope="col">Monto mensual</th><th scope="col">Alcanzaron ese monto en la ESI</th></tr></thead>
        <tbody>{''.join(filas)}</tbody></table>
      </details></section>'''
