# Revisión independiente: tramos de cinco años y perfil de ingresos

**Dictamen: PASS_WITH_RISKS.** No se encontraron defectos materiales pendientes que impidan completar y publicar este cambio. La granularidad, los cálculos y el nuevo gráfico satisfacen el pedido. Los riesgos residuales son la precisión limitada de varios cruces y la ausencia de una prueba independiente en navegador real.

Revisión realizada el 14 de octubre de 2026 sobre el checkout de `ingresos-chile-esi`, sus datos recalculados y `site/index.html`. No se modificó código, datos ni archivos publicados. El único archivo escrito por el revisor es este informe.

## Hallazgos y acciones

No hay correcciones obligatorias pendientes. Las condiciones relevantes están comunicadas en la interfaz:

- **Muestras pequeñas:** 63 de los 216 cruces específicos de ocupación, sexo y edad tienen menos de 60 observaciones. El mínimo es una observación. Los símbolos vacíos, las notas exploratorias y los intervalos no estimables aparecen en los casos comprobados. Conservar esas señales al publicar (`interfaz/dashboard.js:138–151`).
- **Tramo abierto:** hay once tramos de cinco años entre 20–24 y 70–74, más 75+. Este último reúne 564 observaciones; 80+ tendría 170 y produciría cruces vacíos. La agrupación evita esos vacíos, pero no garantiza precisión. La excepción queda explícita junto al gráfico (`codigo/analizar_dashboard.py:21–24`; `interfaz/dashboard.html:63`).
- **Interpretación:** P25–P75 representa dispersión, no un intervalo de confianza. Los máximos son descriptivos y la comparación entre edades es transversal. Las tres advertencias están presentes junto al gráfico (`interfaz/dashboard.html:62–63`).

## Comprobaciones independientes de los datos

Se leyó `datos/esi2025_columnas_necesarias.csv.gz` y se aplicó el universo `ocup_ref == 1` y edad de 20 años o más: 38.380 observaciones de las 93.458 del archivo. Las 38.729 personas ocupadas de referencia de todas las edades no se confundieron con ese universo.

Se contrastaron los **390 dominios** nuevos contra cálculos independientes de tamaño muestral, expansión, media y P25/P50/P75. Para los cuantiles se agregaron los pesos de ingresos idénticos y se buscó el primer valor cuya masa acumulada alcanzara cada probabilidad; no se importó el helper del pipeline. Las medias se calcularon como suma ponderada dividida por la expansión. Todos coincidieron dentro del redondeo de exportación a seis decimales; la diferencia absoluta máxima fue inferior a 0,0000005.

Las 30 particiones por ocupación y sexo cubren exactamente sus totales, sin edades omitidas ni solapadas. Los **30 dominios con edad `all` son idénticos a HEAD**, incluyendo histogramas y curvas. También se reconstruyeron desde el crudo los 150 dominios de los antiguos tramos etarios: sus tamaños, expansiones, medias y cuartiles coinciden con la versión anterior. Por tanto, la mayor granularidad conserva la comparabilidad de las referencias previas.

Se revisaron de forma independiente errores estándar de la media en diez dominios, incluyendo muestras de 1, 2, 5, 9, 10 y 20 casos y dominios nacionales. Se reconstruyeron las contribuciones por conglomerado y estrato conservando las 5.440 unidades primarias de muestreo del diseño completo. Los errores estándar y los intervalos t coincidieron. Los grados de libertad nulos producen intervalos de media nulos; los grados de libertad 1 producen intervalos amplios y quedan señalados como exploratorios. No se encontraron etiquetas de calidad alta con grados de libertad menores que 9. El conjunto nuevo contiene 13 dominios con grados de libertad 0 y 11 con grados de libertad 1.

## Comprobaciones del gráfico y la interacción

Se ejecutó `site/index.html` mediante jsdom sin cargar recursos remotos. En siete perfiles de ocupación y sexo se comprobaron **336 valores y coordenadas** de media, mediana, P25 y P75 contra los dominios correspondientes, calibrando las coordenadas con los ejes del SVG. Se verificaron los doce puntos por serie, las marcas exploratorias, los empates en los máximos, la tabla de doce filas y la ausencia de errores JavaScript.

Seleccionar 75+ resalta ese tramo sin recortar la comparación entre edades; cambiar el monto consultado no altera el perfil de ingresos. La consulta con teclado funciona hasta el último tramo. Los casos de una observación muestran la advertencia exploratoria y el intervalo no estimable. La descarga CSV contiene los doce tramos y sus cuartiles correctos, además de la selección y las comparaciones por ocupación.

En el perfil nacional, la mediana máxima puntual es $800.000 y está empatada entre 35–39 y 40–44; el promedio máximo puntual es aproximadamente $1.189.519 en 40–44. La interfaz conserva ese empate y la advertencia contra una interpretación de significación estadística.

Se inspeccionó visualmente `qa/render_temporal/edad5/perfil.png`: las edades, ejes, mediana, promedio y banda son legibles. Es una imagen estática y no demuestra el comportamiento en navegador. La comprobación independiente fue focalizada; no se atribuye al revisor la batería de 780 combinaciones ejecutada por el implementador.

## Límites del dictamen

La revisión cubre la consistencia del cambio local, los cálculos indicados y el comportamiento comprobable con jsdom. No certifica pruebas de diferencias entre edades, trayectorias salariales individuales ni precisión suficiente en cruces pequeños. Tampoco certifica la publicación remota o la apariencia en todos los navegadores y tamaños de pantalla. Estos límites no impiden completar el cambio con las advertencias presentes.
