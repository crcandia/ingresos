# Verificación de la población y los agregados · ESI 2025

El 5 de noviembre de 2026 se contrastaron los agregados del paquete con una lectura independiente del archivo de personas del INE. El cálculo usó únicamente `ocup_ref == 1` para definir la población nacional. No se importaron las funciones del análisis ni de la interfaz.

| Medida | Resultado del contraste |
|---|---:|
| Registros en el original | 93.458 |
| Personas ocupadas de referencia encuestadas | 38.729 |
| Personas representadas, suma de `fact_cal_esi` | 9.022.697,147158 |
| Media ponderada mensual | $962.944,699310 |
| Mediana ponderada mensual | $680.000 |
| Ingreso estrictamente inferior a la media | 68,708376% |
| Ingreso de $1.000.000 o más | 29,394181% |
| Asalariados de los sectores público y privado, ponderados | 6.655.923,151355 |
| Asalariados con ingreso positivo, ponderados | 6.650.326,131579 |

El 68,7% bajo la media se obtuvo comparando cada ingreso con la media sin redondear. Ninguna observación coincidía con ella. El comunicado del INE informa $962.945 de promedio, $680.000 de mediana y 68,7% con ingreso menor o igual al promedio. [Resultados publicados por el INE](https://www.ine.gob.cl/sala-de-prensa/prensa/general/noticia/2026/07/14/la-mitad-de-las-personas-ocupadas-en-chile-percibieron-ingresos-menores-o-iguales-a-%24680.000-en-2025)

## Comprobaciones contra los archivos del paquete

El CSV completo tiene el SHA-256 `4ff7b8682622c81e2c950544d387e4e8168c3706d2bd7f147b047143a201998f`, idéntico al registrado en [Procedencia](../fuentes/procedencia.json). Con la biblioteca estándar de Python se agruparon los pares de ingreso y ponderador por edad, sexo y ocupación. Se ordenaron los ingresos y se localizó el primer valor cuya ponderación acumulada alcanzaba cada cuantil.

- **Claves y totales.** Se verificó la presencia de las 420 combinaciones esperadas en `datos/dashboard.json` y `tablas/resumen_dominios.csv`. En cada una coincidieron el número de encuestados y la suma de ponderadores. Para los 416 dominios observados también coincidieron la media y los percentiles 25, 50 y 75.
- **Distribuciones.** Se recalcularon por separado las 210 barras de cada histograma observado y los casos y porcentajes que alcanzaban diez umbrales en cada dominio. Se probaron $0, $50.000, $550.000, $1.000.000, $1.950.000, $2.000.000, $5.000.000, $10.000.000, $20.000.000 y $21.000.000. Todos los conteos coincidieron exactamente. La mayor diferencia absoluta entre los valores calculados y los del JSON fue inferior a 0,0000005, compatible con los seis decimales de exportación.
- **Grupos sin muestra.** Las cuatro claves vacías fueron `1|all|15_19`, `1|1|15_19`, `1|2|15_19` y `8|2|15_19`. El JSON conserva cero en los recuentos y la suma de ponderadores. Se verificaron valores nulos en medias, cuantiles, porcentaje imputado, histogramas y proporciones. En el CSV quedaron en blanco las correspondientes estimaciones de resumen.
- **Población asalariada.** Al sumar los ponderadores de las categorías 3 y 4 de `categoria_ocupacion` se reprodujo `fuentes/universo_asalariados.json`, tanto para el total como para quienes tenían `ing_t_p > 0`.

Los resultados por edad incluyen **349 encuestados de 15 a 19 años** (70.436 personas expandidas) y **564 de 75 años o más**. Los códigos de ocupación 10 y 999 suman 156 registros que entran en el total de ocupaciones. Los 234 cruces que especifican tanto edad como sexo y ocupación tienen de cero a 620 observaciones. En 78 de ellos hay menos de 60 observaciones, incluidos los tres vacíos de este subconjunto.

Esta revisión comprobó los cálculos puntuales y las exportaciones contra el original. Las verificaciones de las varianzas y los intervalos están en [Validación del análisis](../datos/validacion.json). Los informes anteriores de esta carpeta están identificados como históricos. Para las pruebas del sitio se usan los comandos y archivos de validación descritos en [Reproducción](../README.md#comprobar-la-reproducción).
