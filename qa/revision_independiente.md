# Revisión adversarial independiente

Adversarial verdict: PASS_WITH_RISKS

Completion claim challenged: El archivo HTML permite explorar ingresos de la ESI 2025 por grandes grupos ocupacionales, cinco edades y sexo, funciona con datos incrustados y conserva denominadores y advertencias de precisión coherentes.

Findings: Sin defectos estadísticos o funcionales pendientes dentro del alcance revisado. Se encontraron y corrigieron dos defectos antes del cierre.

1. El tooltip del histograma asignaba intervalos usando redondeo sobre el índice de barra, lo que mostraba el intervalo vecino dentro de parte de una barra. `interfaz/dashboard.js`, función `makeTooltip`, ahora usa límites de intervalos para histogramas y conserva selección por proximidad para la curva. La corrección pasó 720 posiciones simuladas, cubriendo ambos rangos y tres posiciones dentro de cada barra.
2. La nota del histograma mostraba 0% poblacional cuando no se habían observado ingresos de $3 millones o más. `renderDistribution` ahora indica explícitamente que no se observaron casos. Se verificó esta rama en el HTML construido para mujeres agropecuarias, forestales y pesqueras calificadas de 20–29 años.

Required fixes before final: Ninguno para los datos, denominadores y funciones revisados. La revisión visual estática y el guardado final corresponden al proceso principal.

## Evidencia independiente

Se leyó directamente el CSV original y se compararon sus diez columnas utilizadas con el extracto reproducible. Coinciden celda por celda, incluidas las filas fuera de los dominios.

Se recalcularon los 180 dominios sin importar la implementación del análisis. Coinciden tamaños muestrales, poblaciones expandidas, medias, medianas ponderadas, los 210 intervalos del histograma y 13 umbrales por dominio, incluidos $0, $50.000, $550.000, $1.000.000, $1.050.000, $1.950.000, $2.000.000, $3.650.000, $5.000.000, $9.950.000, $15.150.000, $20.000.000 y $21.000.000. Las diferencias respecto de los agregados JSON se encuentran dentro del redondeo a seis decimales.

Se recalcularon independientemente las varianzas por estratos y UPM, conservando las UPM sin observaciones del dominio, en seis selecciones: all|all|all, 1|2|20_29, 6|2|20_29, 8|2|60_mas, 3|1|40_49 y 5|2|50_59. Coinciden los grados de libertad, errores estándar de las medias y los intervalos logit de las proporciones en cuatro umbrales por dominio cuando el intervalo es identificable.

Los 38.380 encuestados de 20 años o más incluyen 154 personas con códigos de ocupación fuera de 1–9. Estos casos están en los agregados de todas las ocupaciones y no se reasignan. El total original de ocupados es 38.729. Los menores de 20 años se excluyen explícitamente del dashboard. La consulta inclusiva conserva los 490 empates exactamente en $1 millón y 157 en $2 millones.

Con jsdom se verificaron independientemente las 720 posiciones de tooltip, la advertencia del dominio de 8 encuestadas, el tratamiento de cero casos observados, el umbral inclusivo $0 y la consulta de $1.050.000. No aparecieron errores de JavaScript. El documento no tiene scripts, estilos ni imágenes remotos. El JavaScript no contiene fetch, XMLHttpRequest, WebSocket, sendBeacon ni importaciones de red. Las consultas operan sobre agregados incrustados. El vínculo de la fuente oficial es navegación voluntaria.

Se revisaron además `qa/validacion_interfaz.json` y su código de prueba, que registran controles, 180 dominios renderizados, geometría SVG finita, exportación de 15 filas CSV y reapertura de una copia con los filtros conservados.

## Riesgos y límites

La interacción se validó en DOM con jsdom, no en un navegador real. El entorno no ofrecía el navegador autorizado. Por tanto, no corresponde afirmar compatibilidad probada en Chrome, Safari o Firefox, ni descarga e impresión verificadas en esos navegadores. El proceso principal revisa la composición estática por separado.

Las celdas pequeñas y las colas escasas siguen teniendo incertidumbre muestral real. El dashboard conserva los conteos y las marcas exploratorias, y no convierte ausencia de casos en ausencia poblacional. Los intervalos son de proporciones y medias, no de los totales expandidos ni de la mediana. Las comparaciones son descriptivas y las diferencias entre edades no son trayectorias individuales.
