# Datos y método · ESI 2025

## Fuente y población

El universo nacional se define exclusivamente por `ocup_ref == 1` en el archivo de personas de la ESI 2025. El INE identifica así a quienes llevan al menos un mes en su ocupación actual. Se conservan las 93.458 filas del archivo original para estimar las varianzas del diseño. Los resultados nacionales se calculan sobre las 38.729 personas ocupadas de referencia, que representan a 9.022.697 personas. Sus edades observadas van de 15 a 95 años. La URL del original, la fecha de descarga, el número de bytes, el SHA-256 y las diez columnas conservadas en el extracto figuran en [Procedencia](fuentes/procedencia.json).

El ingreso mensual de la ocupación principal se lee de `ing_t_p` y se expresa en pesos de octubre de 2025. En el trabajo asalariado se consideran los descuentos legales e impuestos y en el independiente, los costos de la actividad. Según la definición de la encuesta, el ingreso puede incluir componentes en especie. Se conservan los ingresos cero y las imputaciones del INE. El manual y la metodología de la ESI están en `fuentes/`.

| Medida nacional | Cálculo sobre la muestra ponderada |
|---|---:|
| Promedio mensual | $962.945 |
| Mediana mensual | $680.000 |
| Personas con ingreso estrictamente inferior al promedio | 68,7% |
| Personas con un ingreso de $1.000.000 o más | 29,4% |
| Población estimada con un ingreso de $1.000.000 o más | 2.652.148 |

Para reproducir el porcentaje bajo el promedio se compara cada ingreso con la **media sin redondear** y se suman los ponderadores de quienes quedan por debajo. La mediana es el primer ingreso cuya ponderación acumulada alcanza el 50%. El umbral de un millón incluye los ingresos exactamente iguales a ese monto. El [contraste con el CSV original](qa/revision_universo.md) conserva los resultados con mayor precisión.

## Edades, ocupaciones y cruces con pocos casos

- **Edad.** Hay doce intervalos consecutivos de cinco años, de 15–19 a 70–74, más el tramo abierto de 75 años o más. Los extremos reúnen 349 y 564 encuestados, respectivamente. El total `all` incluye las trece edades para el sexo y la ocupación elegidos.
- **Ocupación.** Las nueve categorías del explorador corresponden a los códigos `b1` del 1 al 9 y suman 38.573 personas encuestadas. Otras 129 tienen el código 10 y 27, el 999. Las 156 están en «Todas las ocupaciones».
- **Sexo.** Se conservan las categorías del archivo, `1` hombres y `2` mujeres. El agregado `all` incluye ambas.

La combinación de diez opciones de ocupación, tres de sexo y catorce de edad da **420 dominios**, contando los totales. Hay 416 con al menos una observación. Cuatro combinaciones de 15–19 años están vacías. En directivos y gerentes falta muestra tanto para mujeres como para hombres y, por tanto, para el total de ambos. También falta muestra para las mujeres operadoras de máquinas y ensambladoras en esa edad.

De los **234 cruces específicos** (nueve ocupaciones por dos sexos por trece edades), 78 tienen menos de 60 observaciones, incluidos los tres cruces específicos vacíos. El cuarto dominio vacío es el subtotal de ambos sexos. El mayor cruce específico reúne 620 encuestados.

## Diseño e incertidumbre

Los cálculos ponderan cada registro por `fact_cal_esi`. Para las varianzas se conservan las 5.440 unidades primarias de muestreo (UPM) y los 232 estratos del diseño completo. Cada selección se trata como un dominio. También permanecen en el cálculo las UPM que no aportan observaciones a esa selección.

El error estándar de la media se estima por linealización de Taylor. El intervalo bilateral del 95% usa la distribución t y los grados de libertad del dominio. Los percentiles 25, 50 y 75 se calculan sobre la distribución empírica ponderada. La banda P25–P75 describe la dispersión de ingresos dentro del grupo.

Para un dominio con al menos una observación, la curva estima la proporción que gana un ingreso **mayor o igual al umbral**, cada $50.000 entre $0 y $21 millones. Los intervalos puntuales del 95% se calculan en escala logit para proporciones entre cero y uno. La población que alcanza el umbral se estima multiplicando esa proporción por la suma de ponderadores del dominio. La escala lineal y la logarítmica presentan la misma estimación y el mismo intervalo.

La clasificación `curve.q` del umbral sigue estas reglas. Aquí, `p` y su error estándar se expresan entre 0 y 1.

| Código | Condición |
|---|---|
| `2` | El dominio tiene al menos 60 observaciones y 9 grados de libertad. El error estándar de la proporción es como máximo min(p, 1−p)^(2/3)/9. Además, el evento tiene al menos 60 observaciones, 9 grados de libertad y un CV del total ≤ 15%. |
| `1` | Hay observaciones que alcanzan el umbral y al menos uno de los criterios de precisión queda sin cumplir. |
| `0` | La encuesta carece de casos observados que alcancen el umbral. |

Si un grupo sí tiene muestra y ningún caso llega al monto consultado, la proporción **observada** es cero. Si falta muestra para todo el grupo, la proporción queda **sin estimar**. En ambos casos la población real sigue siendo desconocida en ese punto. La interfaz conserva esta distinción. Las diferencias entre ocupaciones, sexos y edades describen a los grupos encuestados en 2025.

## Contrato de datos

`datos/dashboard.json` contiene un objeto `domains` con claves `ocupación|sexo|edad`. Por ejemplo, `all|all|all` corresponde al total nacional y `all|all|15_19` a todas las personas ocupadas de referencia de 15 a 19 años.

| Campo | Contenido |
|---|---|
| `n`, `N`, `df` | Número de encuestados, suma de ponderadores y grados de libertad del dominio. |
| `mean`, `meanSE`, `meanLo`, `meanHi`, `meanCV` | Media, error estándar, límites del IC95% en pesos y coeficiente de variación en porcentaje. |
| `meanQ` | 0 para un dominio vacío, 2 si n ≥ 60, gdl ≥ 9 y CV ≤ 15%, y 1 para los demás dominios observados. |
| `p25`, `median`, `p75` | Cuantiles ponderados en pesos. |
| `zero_n`, `zeroN` | Encuestados con ingreso cero y suma de sus ponderadores. |
| `imputedPct` | Porcentaje ponderado con `imp_d1_monto == 1` o `imp_d5_monto == 1`. |
| `hist` | 210 porcentajes por intervalos de $100.000, entre $0 y $21 millones. En un dominio con muestra suman 100%, salvo redondeo. |
| `curve.p`, `curve.n`, `curve.q` | Porcentajes, número de casos y código de precisión para los 421 umbrales, en orden ascendente. |
| `curve.lo`, `curve.hi` | Límites del IC95% de la proporción, expresados entre 0 y 100. |

En un dominio vacío, los conteos y la suma de ponderadores son cero. Las medias, los cuantiles, el porcentaje imputado, las barras del histograma, las proporciones y sus intervalos son `null`. El CSV deja en blanco las estimaciones faltantes. En dominios observados también pueden faltar intervalos, por ejemplo si los grados de libertad son insuficientes. Los valores continuos del JSON se redondean a seis decimales. El máximo observado en la muestra fue $20.056.701, por lo que el histograma incluye todos los ingresos observados.

## Reproducción y controles

```bash
python3 -m pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B codigo/analizar_dashboard.py > datos/ejecucion.log 2>&1
```

El programa contrasta la estimación nacional y su error estándar, compara pares dominio–umbral con la implementación independiente del diseño en `codigo/diseno_encuesta.py`, comprueba las particiones por edad y sexo y verifica los resultados frente a `fuentes/referencia_edades.csv`. También comprueba la geometría numérica de las distribuciones, el orden de los cuantiles, la monotonicidad de las curvas y el contrato de valores faltantes. Exporta los resultados en `datos/dashboard.json`, las comprobaciones en `datos/validacion.json` y las tablas CSV y LaTeX en `tablas/`.

El extracto comprimido del paquete permite reproducir esos cálculos sin conexión. La distribución por carreras usa referencias de Mi Futuro y los cargos, registros de remuneraciones. Los umbrales de esas comparaciones se calculan sobre los montos individuales ponderados en el extracto ESI. [Construcción de la interfaz y fuentes salariales](README.md)
