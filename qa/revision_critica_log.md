# Revisión crítica independiente: escala logarítmica y universo de edad

Adversarial verdict: PASS_WITH_RISKS

Completion claim challenged: El HTML permite alternar la curva de altos ingresos entre escala lineal y logarítmica del porcentaje, conserva esa elección al guardar, y explica qué población reúne «Total (20+)».

Findings: No quedan defectos materiales pendientes en el alcance de interfaz, agregados y definición del universo revisados. La publicación externa no forma parte de este dictamen.

Required fixes before final: Ninguno en este alcance. Una comprobación de interacción y composición en un navegador real sigue sin estar disponible y debe declararse como límite.

## Hallazgos iniciales y resolución

1. **Prioridad alta, representación del intervalo.** La versión anterior unía los límites del IC mediante diagonales, mientras que la estimación central era escalonada. Se encontraron 208 transiciones con `p[i-1] > hi[i]`: en esos tramos la curva podía parecer fuera de su propia banda. En el total nacional, entre $1.000.000 y $1.050.000, los valores eran 29,612969%, 26,365833% y límite superior siguiente 27,248218%. La versión revisada usa pasos coherentes en ambos bordes y separa intervalos faltantes (`interfaz/dashboard.js:74–80`). Se comprobaron 762 puntos medios de segmentos en la curva nacional, sumando ambas escalas, y todos quedaron dentro de su banda.

2. **Prioridad media, universo ambiguo.** «20+» no significaba toda la muestra ESI. El filtro reúne a ocupados de referencia de al menos 20 años, para la ocupación y el sexo seleccionados. La nueva etiqueta «Total (20+)», la nota visible junto a los filtros y la explicación de los conteos aclaran esta distinción (`interfaz/dashboard.html:27`; `interfaz/dashboard.js:14,167`).

3. **Prioridad menor, precisión de las etiquetas.** Se corrigieron la división exacta «50% / 50%» de la mediana, la ambigüedad de «sobre umbral» en los encabezados CSV y la nota del histograma cuando un umbral de $50.000 cae dentro de un intervalo de $100.000. La versión revisada también declara los tooltips como región de estado accesible; esto se comprobó en DOM, sin afirmar una prueba con lector de pantalla.

## Contraste con el CSV original

Se leyó directamente `esi_raw_source/distribucion_ingresos_chile_ESI2025/datos_originales/esi_2025_personas.csv`, sin importar el código de agregación. Su SHA-256 coincide con `meta.provenance.sha256Original`.

| Cobertura | Registros |
| --- | ---: |
| CSV completo | 93.458 |
| Ocupados de referencia, `ocup_ref == 1`, todas las edades | 38.729 |
| Ocupados de referencia menores de 20 años, excluidos | 349 |
| Universo inicial del dashboard, `ocup_ref == 1` y `edad >= 20` | 38.380 |

El universo inicial representa 8.952.261,090340 personas mediante los factores de expansión. Incluye 154 casos con códigos de ocupación residuales: 128 del código 10 y 26 del 999. Las cinco edades particionan el universo de 20 años o más; aplicar ocupación o sexo reduce el denominador.

Las proporciones y los conteos nacionales coinciden directamente con el CSV para los umbrales $0, $1.000.000, $2.000.000, $5.000.000 y $20.000.000, dentro del redondeo de seis decimales. La comparación es inclusiva: conserva 490 observaciones exactamente en $1 millón y 157 exactamente en $2 millones. En $20 millones quedan dos casos y 0,009118% ponderado.

## Validación funcional independiente

Se ejecutó Node.js con jsdom disponible en `tmp/dashboard_qa/node_modules`, sobre el HTML distribuido. Las pruebas interceptaron la descarga como un Blob y reabrieron su contenido en una nueva instancia de DOM.

- El control alterna `survivalScale` y sus estados `aria-pressed`; el cambio deja intactos los resultados numéricos de la consulta.
- Las marcas logarítmicas son 0,0001%, 0,001%, 0,01%, 0,1%, 1%, 10% y 100%, separadas por distancias verticales iguales. Se verificó la posición de los marcadores mediante interpolación en el logaritmo de las marcas SVG, independiente de la función de coordenadas de la aplicación.
- Se probaron seis dominios reales: `all|all|all`, `6|2|20_29`, `1|2|20_29`, `8|2|60_mas`, `2|2|30_39` y `all|all|60_mas`. Conservan el mismo eje logarítmico; las consultas con cero observaciones no tienen marcador positivo. El dominio de ocho mujeres en ocupaciones agropecuarias de 20–29 años muestra explícitamente la ausencia de casos desde $1 millón y no dibuja curva ni banda.
- No hay observaciones positivas redondeadas a cero en los agregados. La proporción positiva mínima es 0,003506% y el límite inferior positivo mínimo es 0,000494%, por encima del piso del eje. El código interrumpe las curvas cuando no hay casos, sin sustituir los ceros por un valor positivo (`interfaz/dashboard.js:64–94`).
- Se probó además una copia sintética en memoria: un IC faltante y un límite inferior igual a cero en la curva nacional. En log se obtuvieron tres bandas separadas y una nota sobre el cero no representable; en lineal, dos bandas. No se conectaron los huecos ni aparecieron coordenadas NaN o infinitas. Este caso sintético no altera los archivos de datos; los datos actuales no contienen límites inferiores iguales a cero.
- Una copia guardada y reabierta conservó ocupación, sexo, edad, monto, rango, orden y escala logarítmica. «Restablecer» recupera la escala lineal. La consulta por teclado sigue mostrando «Sin casos observados» al llegar al último umbral.
- Los encabezados CSV explicitan `mayor_o_igual_umbral`. Una instancia con ancho simulado de 270 píxeles conservó geometría SVG finita. No se observaron errores de JavaScript.

El HTML examinado coincidió exactamente con la sustitución de la plantilla, CSS, JavaScript y JSON realizada por `construir_dashboard.py`, sin ejecutar una nueva construcción durante esta comprobación.

SHA-256 del HTML revisado: `3c8f77d99f2045ba3fdadd83269b235203f9ccc9f93c706c83247e2128f04cc4`.

## Riesgos y límites

La validación funcional fue de DOM con jsdom. No se utilizó Chrome, Safari ni Firefox, y el ancho simulado no constituye una inspección visual real ni una prueba de descarga, impresión o lector de pantalla en esos navegadores. Una representación estática tampoco sustituye esa comprobación.

Las cifras siguen describiendo dominios de una encuesta: los grupos pequeños y las colas escasas conservan incertidumbre muestral. La escala logarítmica mejora la lectura de proporciones pequeñas, pero no aumenta su precisión. Los intervalos son puntuales y la curva se consulta en una malla de $50.000; los segmentos escalonados no reconstruyen los saltos exactos entre todos los ingresos individuales.
