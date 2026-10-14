# Datos del dashboard ESI 2025

Este proyecto reproduce distribuciones de ingresos por grandes grupos ocupacionales, sexo registrado en la encuesta y edad. El dashboard recibe únicamente agregados. El extracto que permite reproducirlos conserva las filas del marco muestral completo.

## Fuente y población

Fuente: INE, ESI 2025, archivo de personas. Su URL, fecha de descarga, tamaño y SHA-256 están en `fuentes/procedencia.json`. El SHA-256 del original fue comprobado antes de extraer columnas.

Se usa `ocup_ref == 1`, que identifica a los ocupados de referencia con al menos un mes de antigüedad en el empleo actual, y edad de 20 años o más. El archivo original contiene 93.458 registros, de los cuales 38.729 son ocupados de referencia. El dashboard incluye 38.380 de 20 años o más. Los 349 ocupados menores de 20 años no forman parte del dashboard. Los resultados anteriores nacionales incluyen esos menores y, por ello, no tienen exactamente el mismo denominador. No faltan edades entre los ocupados de referencia. El botón “Total (20+)” combina los doce tramos de edad dentro de la ocupación y sexo seleccionados, no la totalidad de registros de la ESI.

Los doce tramos no se superponen: intervalos de cinco años desde 20–24 hasta 70–74, más 75 años o más. Este último grupo contiene 564 encuestados y se mantiene abierto porque 80+ tendría solo 170 y cruces de ocupación y sexo vacíos. El agregado de edad `all` corresponde a 20 años o más. Los nombres de ocupación son versiones abreviadas de los grandes grupos, códigos `b1` del 1 al 9. El agregado `all` también conserva 154 casos de los códigos 10 y 999, que no tienen un panel individual. Los nueve grupos identificados suman 38.226 encuestados. `sexo` usa las categorías registradas por la encuesta, 1 hombres y 2 mujeres.

El ingreso analizado es `ing_t_p`, ingreso neto mensual de la ocupación principal en pesos chilenos. Para asalariados se consideran los descuentos legales e impuestos. Para independientes se resta el costo de la actividad. El ingreso puede incluir componentes en especie de acuerdo con la ESI. No es ingreso del hogar ni suma de todas las ocupaciones. Se conservan los ingresos cero y los montos imputados de la fuente. Los documentos oficiales utilizados están en `fuentes/`.

## Reproducción

Desde la raíz del proyecto:

```bash
python3 -m pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B codigo/analizar_dashboard.py > datos/ejecucion.log 2>&1
```

El script verifica el hash del extracto, calcula los 390 dominios y escribe `datos/dashboard.json`, `datos/validacion.json` y tablas CSV y LaTeX. No necesita conexión a internet ni el archivo original completo. El JSON final puede variar en su marca de tiempo aunque los cálculos sean iguales.

## Diseño e incertidumbre

La ponderación usa `fact_cal_esi`. Las varianzas usan 5.440 unidades primarias de muestreo y 232 estratos, sin estratos de una sola UPM. Las selecciones son dominios del diseño completo. No se filtran físicamente las filas antes de calcular las varianzas. La implementación vectorizada expande la varianza de Taylor de la razón y se contrasta con la clase `Design` utilizada en el análisis nacional.

La media tiene error estándar e intervalo bilateral del 95%, usando t con los grados de libertad del dominio. Los percentiles 25, 50 y 75 son cuantiles de la distribución empírica ponderada. No se calculan errores estándar ni intervalos de esos cuantiles.

La curva contiene P(ingreso ≥ umbral) cada $50.000 entre $0 y $21 millones, inclusive. Sus intervalos del 95% se calculan en escala logit y corresponden a la proporción. No son intervalos del total expandido. Las estimaciones puntuales de personas sobre un umbral se obtienen multiplicando la proporción por la población ponderada del dominio. Los intervalos `lo` y `hi` son `null` cuando la muestra presenta una proporción de cero o uno. Una muestra sin casos sobre el umbral no demuestra ausencia de personas en la población.

La visualización de altos ingresos usa escala lineal o logarítmica de base diez en el eje del porcentaje, conservando el monto en escala lineal. Los valores numéricos son los mismos en ambas vistas. El rango logarítmico es común a todos los grupos y abarca todos los porcentajes e intervalos positivos. La curva y los límites de la banda se dibujan con escalones en la malla de $50.000. Los tramos sin casos se interrumpen, no se sustituyen por constantes positivas. Los límites de confianza no positivos se omiten en log y se explicitan si aparecen. Las estimaciones no se recalculan al alternar la escala.

La clasificación de cada punto combina la regla de precisión de la proporción y la del total. Es la regla conservadora que se utilizó en los paneles anteriores:

- `q = 2`: dominio con n ≥ 60 y grados de libertad ≥ 9, error estándar de la proporción ≤ min(p, 1−p)^(2/3)/9, y evento con n ≥ 60, grados de libertad ≥ 9 y CV del total ≤ 15%.
- `q = 1`: hay casos observados, pero no se cumple ese criterio conjunto. Se muestra como exploratorio o de precisión limitada.
- `q = 0`: no hay casos observados. No se interpreta como un cero poblacional.

Tener 60 casos en el grupo no garantiza precisión suficiente de sus ingresos extremos. Estos indicadores describen precisión muestral, no eliminan posibles errores de medición o no respuesta. Las diferencias por sexo, edad u ocupación son descriptivas y no identifican efectos causales.

## Contrato del JSON

`domains` tiene 390 entradas. La clave es `ocupación|sexo|edad`. Las opciones son 10 ocupaciones incluyendo `all`, tres sexos incluyendo `all`, y trece edades incluyendo `all`.

| Campo | Contenido |
|---|---|
| `n` | Número de encuestados del dominio |
| `N` | Población expandida del dominio |
| `mean`, `meanSE`, `meanLo`, `meanHi` | Media, error estándar y límites de IC95, en pesos |
| `meanCV`, `meanQ` | CV de la media y precisión: 2 si n ≥ 60, gdl ≥ 9 y CV ≤ 15%, en otro caso 1 |
| `median`, `p25`, `p75` | Cuantiles ponderados en pesos |
| `df` | Grados de libertad del dominio |
| `zeroN`, `zero_n` | Población expandida y casos muestrales con ingreso cero |
| `imputedPct` | Porcentaje ponderado con `imp_d1_monto == 1` o `imp_d5_monto == 1` |
| `hist` | 210 porcentajes por intervalos de $100.000, desde [0, 100.000) hasta [20.900.000, 21.000.000). Suman aproximadamente 100% |
| `curve.p`, `curve.n` | 421 porcentajes y números de casos con ingreso mayor o igual al umbral |
| `curve.lo`, `curve.hi` | Límites del IC95 de la proporción, en porcentaje 0–100 |
| `curve.q` | Indicador de precisión 0, 1 o 2 para cada umbral |

Las matrices se ordenan por umbral ascendente. Los números continuos se guardan con seis decimales, los conteos son enteros y los valores no identificables son `null`. El histograma expresa porcentaje por intervalo y no densidad. El máximo observado de ingresos es inferior a $21 millones, por lo que no hay una cola excluida del histograma.

## Controles ejecutados

`datos/validacion.json` registra la comprobación de 130 pares dominio–umbral contra la implementación original, las particiones por sexo y edad, los cinco resultados anteriores por edad, las sumas de histogramas, la monotonicidad de las curvas y el contrato de exportación. Las referencias nacionales verificadas incluyen población ponderada, media y error estándar.

Entre los 216 cruces específicos de ocupación, sexo y tramo de edad, los tamaños van de 1 a 620 encuestados y 63 grupos tienen menos de 60 casos. El gráfico de edad marca con símbolos vacíos los grupos de muestra o precisión limitada. La banda P25–P75 representa la mitad central de la distribución y no un intervalo de confianza. Las cifras máximas entre edades no constituyen pruebas de diferencias estadísticamente significativas. Las tablas de resumen permiten identificar cada grupo sin interpretar ese umbral como garantía de precisión.
