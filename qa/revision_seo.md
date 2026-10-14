# Revisión independiente de miniatura y SEO técnico

Adversarial verdict: PASS_WITH_RISKS

Completion claim challenged: Los archivos del dashboard incorporan una miniatura social, metadatos y recursos SEO coherentes, una vista inicial legible sin ejecutar JavaScript y copias offline funcionales; están preparados para empaquetar y subir al repositorio autorizado.

Findings: No quedan defectos materiales pendientes en los fuentes y archivos públicos revisados. Se corrigieron dos hallazgos durante la revisión.

Required fixes before final: Ninguno en el código revisado. El ZIP generado después de incorporar este informe debe pasar la comprobación final de miembros y hashes antes de su entrega. La publicación en Netlify, la indexación y las vistas previas reales requieren verificación externa separada.

## Hallazgos corregidos

1. **Dataset anidado incompleto.** La referencia a la fuente original se declaraba como otro objeto `Dataset`, pero carecía de descripción. La versión revisada usa la URL original directamente en `isBasedOn` (`codigo/seo_web.py:87`). El grafo final contiene un único Dataset completo, referido al resumen agregado que realmente se ofrece como CSV.
2. **Controles estáticos incoherentes al guardar.** Una copia del grupo de técnicos, hombres de 50–59 años, consultando $3 millones, conservaba las cifras y el JSON de estado, pero sin JavaScript mostraba la ocupación inicial y $1 millón en los controles. Se serializan ahora los valores de inputs y las opciones seleccionadas antes de generar el archivo (`interfaz/dashboard.js:182`). Se verificaron la primera copia y una segunda copia guardada después de cambiar de nuevo el monto, la ocupación y la métrica.

## Evidencia funcional y de contenido

Se inspeccionaron el código generador, los HTML distribuidos, el JSON-LD, la configuración y los recursos publicados. Las pruebas independientes utilizaron Node.js con jsdom, sin habilitar recursos externos ni realizar solicitudes de medición.

- Se reprodujo el HTML offline desde la plantilla, estilos, JavaScript y JSON, ejecutando el prerender por entrada y salida estándar, sin escribir archivos. Coincidió exactamente con el artefacto examinado. Ambos HTML incorporan la aplicación vigente y los mismos datos.
- Antes de ejecutar JavaScript ya están presentes las cifras principales, ambos gráficos, cinco tarjetas de edad, nueve ocupaciones y la definición del universo. Los valores iniciales coinciden tras la hidratación. Tres llamadas adicionales a `render()` no duplicaron identificadores, controles, SVG ni tooltips.
- La copia guardada conserva ocupación, sexo, edad, monto, rango, orden y escala. Sus controles y cifras también coinciden al abrirla sin JavaScript. Se eliminan Analytics, canonical, JSON-LD, metadatos sociales e iconos remotos, y se restaura la CSP offline. Una segunda copia mantuvo esas propiedades.
- El título, la descripción, canonical, `og:url`, sitemap y enlaces de recursos usan `https://ingresos.criss-lab.com/` de manera coherente. Se comprobaron la existencia de los archivos locales referenciados y los tamaños reales declarados en Open Graph.
- El CSV publicado es idéntico byte a byte a `tablas/resumen_dominios.csv`. Sus 180 claves son únicas. Tamaños muestrales, poblaciones, medias, errores estándar, intervalos, medianas, cuantiles y grados de libertad coinciden con los agregados JSON, dentro de su redondeo. Los IC no estimables permanecen como celdas vacías. Los datos JSON no cambiaron respecto del estado anterior en Git.
- El Dataset describe correctamente los 180 cruces y el universo de ocupados de referencia de 20 años o más. La descarga visible apunta al mismo CSV que `distribution.contentUrl`. Se declara elaboración independiente y procedencia INE, sin atribuir al INE la autoría del dashboard ni inventar una licencia.
- Se contrastó la afiliación de Cristian Candia a CRiSS-LAB con su página de autor en el sitio del laboratorio. El marcado no incluye reseñas, calificaciones ni una promesa de resultado enriquecido FAQ.
- Las reglas locales de Netlify no asignan más de un `Cache-Control` a las rutas públicas examinadas. La regla global añade otras cabeceras. Existe una redirección explícita de `/index.html` a `/`, un documento 404 con `noindex`, robots.txt y sitemap XML válido. Estas comprobaciones describen la configuración, no una respuesta HTTP ya desplegada.
- Las reglas de `crear_paquete.py` incluyen los PNG públicos, además de SVG, CSV y recursos SEO. No se excluyen ya las imágenes necesarias para la miniatura y los iconos.

## Inspección de la miniatura

Se abrió y examinó el PNG real: **1737 × 905 píxeles, 1.675.823 bytes**. Su tamaño coincide con Open Graph y está por debajo del límite de 5 MB utilizado por la validación local. El título tiene buena jerarquía y contraste; el subtítulo explica cómo explorar el dashboard. La composición mantiene márgenes alrededor de los textos. Las formas son decorativas y no se presentan como una distribución estadística. No contiene un logotipo institucional que implique patrocinio del INE.

Los iconos PNG miden 32 × 32 y 180 × 180 píxeles. El SVG mantiene el símbolo de barras de la interfaz.

SHA-256 de la miniatura: `bde18f855533e1a2c7c22587d66024b340004fe9b5ec4170d25801f305f2f7a3`.

## Límites del dictamen

La revisión permite considerar los archivos preparados para su subida a GitHub. No certifica por sí misma que se haya realizado esa subida, un despliegue en Netlify o una actualización de DNS. La entrega final debe comprobar esos estados mediante la evidencia del proceso correspondiente.

No se utilizó un navegador real ni un validador remoto de resultados enriquecidos. No se verificaron respuestas HTTPS del dominio, indexación en Google, recepción de eventos en Analytics ni la miniatura que finalmente muestran las plataformas sociales y sus cachés. La inspección del PNG y las pruebas DOM no sustituyen esas verificaciones. El SEO configurado no garantiza rastreo, indexación ni posición en resultados.

## Referencias consultadas

- [Google: SEO de aplicaciones JavaScript](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics).
- [Google: datos estructurados Dataset](https://developers.google.com/search/docs/appearance/structured-data/dataset).
- [Netlify: cabeceras y combinación de valores](https://docs.netlify.com/manage/routing/headers/).
- [Cristian Candia en CRiSS-LAB](https://criss-lab.com/author/cristian-candia/).

Consulta y revisión realizadas el 14 de octubre de 2026.
