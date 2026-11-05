"""Place documented salary examples on the national ESI income distribution."""
from html import escape


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
        por_nombre[ref['nombre']] = dict(ref, link=link, neto=pesos(monto), personas=personas, tasa=100 * personas / total)

    psico = por_nombre['Psicología']
    enfermeria = por_nombre['Enfermería']
    comercial = por_nombre['Ingeniería Comercial']
    derecho = por_nombre['Derecho']
    industrial = por_nombre['Ingeniería Civil Industrial']
    fuente = escape(psico['url'], quote=True)
    sii = escape(psico['tabla_sii'], quote=True)

    barras = []
    for carrera in [psico, enfermeria]:
        barras.append(f'''<div class="career-mark">
          <span class="career-mark-label">Al menos {carrera["neto"]}</span>
          <span class="career-track" aria-hidden="true"><i style="width:{carrera["tasa"]:.4f}%"></i></span>
          <strong>{round(carrera["tasa"])} de 100</strong></div>''')

    filas = []
    for carrera in sorted(por_nombre.values(), key=lambda r: r['pesos']):
        cantidad = numero(round(carrera['personas'] / 1000) * 1000)
        filas.append(f'''<tr><th scope="row">{carrera["link"]}</th>
          <td><strong>{carrera["neto"]}</strong><small>Bruto: ${numero(carrera["pesos"])}</small></td>
          <td><strong>{porcentaje(carrera["tasa"])}</strong><small>≈ {cantidad} personas</small></td></tr>''')

    return f'''<section class="salary-story" id="sueldos-por-carrera" aria-labelledby="career-title">
      <p class="kicker">SUELDOS POR CARRERA</p><h4 id="career-title">¿Cuánto se gana al tercer año de titularse?</h4>
      <p>El millón de pesos queda entre dos de las carreras que más estudiantes reciben en Chile. Al tercer año de titulación, el ingreso bruto promedio de {psico["link"]} equivale a unos <strong>{psico["neto"]} líquidos al mes</strong> para una persona asalariada. En {enfermeria["link"]}, el mismo cálculo da <strong>{enfermeria["neto"]}</strong>.</p>
      <figure class="career-figure"><figcaption>De cada 100 personas que trabajan en Chile, ¿cuántas alcanzan esos montos?</figcaption>
        {''.join(barras)}<small>Personas ocupadas de 20 años o más · ESI 2025</small></figure>
      <p>En {comercial["link"]} y {derecho["link"]}, los montos quedan mucho más cerca. El líquido estimado al tercer año es de <strong>{comercial["neto"]}</strong> en la primera y <strong>{derecho["neto"]}</strong> en la segunda. En ambos casos, alrededor de {round(comercial["tasa"])} de cada 100 personas ocupadas en Chile ganaban esa cantidad o más.</p>
      <p class="salary-source">Estas cuatro carreras registraron la mayor matrícula universitaria de primer año en Chile en 2026. <a href="https://www.mifuturo.cl/wp-content/uploads/2026/07/Informe-de-Matr%C3%ADcula-2026.pdf#page=25">Informe de matrícula del SIES, p. 25</a>.</p>
      <details class="salary-detail"><summary>Comparar las ocho carreras</summary>
        <p>Cerca de los dos millones aparece {industrial["link"]}, con un líquido estimado de <strong>{industrial["neto"]}</strong>. Puedes abrir el nombre de cada carrera para explorar sus alternativas en Lixandria.</p>
        <table class="career-table"><caption>Ingresos mensuales al tercer año y su lugar en la distribución nacional</caption>
        <thead><tr><th scope="col">Carrera universitaria</th><th scope="col">Líquido estimado</th><th scope="col">Ganan ese monto o más en Chile</th></tr></thead><tbody>{''.join(filas)}</tbody></table>
      </details>
      <details class="salary-detail"><summary>De dónde salen los sueldos y cómo estimamos el líquido</summary>
        <p>Mi Futuro publica ingresos brutos. Para estimar qué recibiría una persona asalariada con ese ingreso medio, descontamos un 18,7% por cotizaciones y aplicamos el impuesto de septiembre de 2025. El monto efectivo depende de los descuentos personales. <a href="{fuente}">Estadísticas por carrera de Mi Futuro</a> · <a href="{sii}">Tabla de impuesto del SII</a>.</p>
        <p>Mi Futuro usa los ingresos anuales declarados al SII en 2022, 2023 y 2024, divididos por doce. Incluye a quienes alcanzaron el equivalente anual del sueldo mínimo. En Derecho ajusta un año por el tiempo entre la licenciatura y el título. <a href="https://www.mifuturo.cl/wp-content/uploads/2025/12/Metodologia-Estadisticas-por-Carrera_2025-2026.pdf#page=5">Metodología de Mi Futuro</a>.</p>
        <p>Las carreras están en pesos de septiembre de 2025. Para cada líquido estimado, redondeado a mil pesos, contamos cuántas personas ocupadas de 20 años o más alcanzaron ese monto en su trabajo principal en la ESI, expresada en pesos de octubre. Ese porcentaje se refiere a personas de todas las carreras y niveles educativos.</p>
      </details></section>'''


def ejemplos_cargos(referencias, registros):
    cargos = {}
    for ref in referencias:
        if ref['paso'] != 10:
            continue
        monto = ref['pesos'] if 'pesos' in ref else sum(ref['totales']) / ref['meses']
        casos, personas = sobre_umbral(registros, monto)
        unidad = 100 if casos < 60 else 1000
        cargos[ref['nombre']] = dict(neto=pesos(monto), casos=casos, personas=numero(round(personas / unidad) * unidad),
                                      fuente=f'<a href="{escape(ref["url"], quote=True)}">{escape(ref["fuente"])}</a>')

    presidente = cargos['Presidente de la República en 2025']
    codelco = cargos['Presidente ejecutivo de Codelco']
    directora = cargos['Directora laboral del Consejo Directivo de BancoEstado']
    banco = cargos['Presidente del Consejo Directivo de BancoEstado']
    return f'''<section class="salary-story public-salaries" aria-labelledby="public-salary-title">
      <h4 id="public-salary-title">¿Dónde queda el sueldo de un presidente?</h4>
      <p>En noviembre de 2025, Gabriel Boric recibió unos <strong>{presidente["neto"]} líquidos</strong> como presidente de la República, justo por debajo del primer umbral del gráfico. Unas <strong>{presidente["personas"]} personas</strong> en Chile alcanzaban ese monto en su trabajo principal, según la ESI. {presidente["fuente"]}.</p>
      <p>La presidencia ejecutiva de Codelco queda fuera del gráfico. Entre noviembre de 2025 y octubre de 2026, la empresa pagó por ese cargo un promedio de <strong>{codelco["neto"]} líquidos al mes</strong>, sumando lo recibido por sus dos titulares en ese período. Ninguna persona de la muestra alcanzó ese monto. La encuesta no permite estimar cuántas lo recibían en Chile. {codelco["fuente"]}.</p>
      <details class="salary-detail"><summary>¿Y en el Consejo Directivo de BancoEstado?</summary>
        <p>En 2025, la directora laboral recibió en promedio <strong>{directora["neto"]} líquidos al mes</strong> y el presidente del consejo, <strong>{banco["neto"]}</strong>. Unas {directora["personas"]} personas en Chile alcanzaban el primer monto en la ESI. Para el segundo, la estimación es de unas {banco["personas"]} personas y se basa en apenas {banco["casos"]} casos de la muestra. {banco["fuente"]}.</p>
      </details></section>'''
