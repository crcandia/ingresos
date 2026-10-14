# Ingresos en Chile · ESI 2025

Repositorio: [crcandia/ingresos](https://github.com/crcandia/ingresos).

Abrir `Ingresos_Chile_ESI2025.html` en un navegador moderno. El archivo contiene los datos agregados, gráficos, estilos y controles. Funciona sin conexión y puede compartirse como un único archivo. No requiere instalación, cuenta ni servidor.

## Uso

Elegir ocupación, sexo y edad. La vista principal muestra mediana, promedio, población representada, distribución y proporción que gana un monto o más. El monto puede cambiarse escribiendo una cantidad, moviendo el control o usando las referencias de $1–5 millones.

El gráfico de altos ingresos permite elegir escala lineal o logarítmica para el porcentaje. En logarítmica, las marcas verticales avanzan por factores de diez y el eje es el mismo para todos los grupos. La curva y su banda de confianza tienen la misma geometría escalonada. La curva se interrumpe cuando no hay casos observados, sin sustituir ceros por valores positivos. El mensaje debajo del gráfico indica el primer umbral sin casos. La escala solo cambia la representación.

Las cinco tarjetas comparan edades dentro de la ocupación y sexo elegidos. Seleccionar una tarjeta cambia el grupo principal. La comparación inferior conserva edad y sexo y muestra las nueve ocupaciones. Puede ordenarse por mediana, promedio o porcentaje sobre el monto consultado.

“Guardar copia” descarga un HTML que conserva los filtros y la escala elegidos. “Descargar datos de esta vista” exporta un CSV con las cifras sin el redondeo visual. El CSV tiene delimitador punto y coma, punto decimal y codificación UTF-8 con BOM. Las columnas `mayor_o_igual_umbral` incluyen ingresos exactamente iguales al monto. “Imprimir / PDF” utiliza el diálogo de impresión del navegador.

## Universo y precisión

Personas ocupadas de referencia ESI de 20 años o más. “Total (20+)” agrupa los cinco tramos para la ocupación y sexo elegidos. No significa toda la muestra de la ESI. El archivo original contiene 93.458 registros. De ellos, 38.729 son ocupados de referencia. El dashboard incluye los 38.380 de 20 años o más y excluye 349 menores de 20 años. Esta restricción explica las diferencias con las cifras nacionales de todas las edades. La vista inicial representa aproximadamente 8,95 millones de personas. Todas las ocupaciones incluye 154 casos en códigos residuales, además de los nueve grupos disponibles.

Cada porcentaje es condicional a su grupo. La curva cuenta ingresos iguales o superiores al monto. Una consulta sin casos observados no se presenta como ausencia de personas en la población. Las referencias con poco respaldo se señalan como exploratorias. Los intervalos corresponden a la proporción o a la media, según la etiqueta. No hay intervalos de la mediana ni de las cantidades de personas en la interfaz.

Los ingresos se redondean a miles y las cantidades de personas a centenas, o decenas para cifras inferiores a mil. Los porcentajes muestran más decimales cuando son pequeños. El símbolo ≈ identifica ese redondeo. Los cálculos conservan mayor precisión.

Ver `README_DATOS.md` para las variables, el diseño muestral, el criterio conservador de precisión y las validaciones estadísticas.

## Reproducir

Para recalcular los agregados desde el extracto público incluido:

```bash
python -m pip install -r requirements.txt
npm install --prefix qa
python -B codigo/analizar_dashboard.py
python -B construir_dashboard.py
```

El análisis valida el hash del extracto, los universos y las sumas. La construcción usa Python y Node.js con jsdom para incluir la vista inicial en el HTML. Se genera desde `interfaz/` y `datos/dashboard.json`, sin descargar recursos durante la construcción. Los microdatos individuales no se incrustan en el dashboard.

Para verificar la lógica de la interfaz:

```bash
npm install --prefix qa
node qa/run_dom_checks.cjs
node qa/check_analytics.cjs
node qa/check_seo.cjs
```

Se prueban los 180 dominios en ambas escalas y los controles, las consultas sin casos, la geometría de los SVG, las descargas y la reapertura de una copia con estado guardado. También se comprueba la distancia logarítmica de las marcas y la alineación escalonada de la banda. Estas son pruebas de DOM con jsdom, no una sesión real de Chrome, Safari o Firefox.

Para la inspección estática y la exportación vectorial de los gráficos iniciales:

```bash
python -m pip install -r qa/requirements.txt
python -B qa/render_estatico.py
```

La inspección usa WeasyPrint. Los controles se sustituyen por elementos estáticos solo en las copias de inspección. El archivo final conserva controles HTML nativos. `figuras/curvas_vista_general.pdf` contiene tres páginas con la distribución y la curva acumulada en escala lineal y logarítmica, exportadas directamente desde los SVG generados por la interfaz.

En la primera página del PDF, la línea verde discontinua marca la mediana y la ocre punteada marca el promedio. Las barras oscuras empiezan en el umbral consultado, $1 millón en la vista inicial. En la segunda y tercera páginas, la banda es el IC puntual del 95% y el trazo discontinuo identifica precisión limitada. Las tres páginas corresponden a todas las ocupaciones, ambos sexos y edades de 20 años o más.

El proyecto también incluye la configuración de Netlify y la copia web en `site/index.html`. `construir_dashboard.py` actualiza ambas versiones del HTML. La versión web incorpora Google Analytics con el identificador `G-XSFF2F0XKK` suministrado por el autor. Su política de contenido permite los dominios de Google necesarios para cargar la etiqueta y enviar mediciones. El pie de página informa de Analytics. El archivo descargable y las copias generadas con “Guardar copia” omiten Analytics y bloquean conexiones externas. Ver `PUBLICACION.md` para el destino solicitado y la configuración de dominio.

## Comprobaciones incluidas

La versión web incluye miniatura social, Open Graph, Twitter Card, URL canónica, sitemap, robots.txt, iconos y metadatos estructurados de autor, página y datos. La vista inicial se puede leer sin JavaScript. Ver `SEO.md` para la configuración, construcción y comprobaciones pendientes sobre el dominio publicado.

`datos/validacion.json` contiene las comprobaciones del cálculo. `qa/validacion_interfaz.json` registra las pruebas funcionales. `qa/revision_independiente.md` documenta la primera revisión, que contrastó los 180 dominios con el CSV original. `qa/revision_critica_log.md` documenta la revisión de esta actualización. `qa/verificacion_universo.json` conserva la comprobación de cobertura y la identidad de los agregados. `MANIFEST_SHA256.json` permite verificar la integridad del paquete.

Limitación de verificación: no se ejecutó una inspección interactiva en un navegador real desde este entorno. La lógica se probó con jsdom y el diseño se inspeccionó mediante una representación estática en tamaños de escritorio y teléfono.

Fuente: Instituto Nacional de Estadísticas de Chile, Encuesta Suplementaria de Ingresos 2025. Elaboración: Dr. Cristian Candia.
