# SEO y vistas previas

La versión web usa `https://ingresos.criss-lab.com/` como URL canónica. La configuración común está en `interfaz/seo.json` y la generación en `codigo/seo_web.py`.

Incluye título y descripción, Open Graph, Twitter Card grande, autor, iconos, datos estructurados de WebSite, WebPage, Person y Dataset, sitemap y robots.txt. No se añaden reseñas, calificaciones, licencias, cuentas sociales, traducciones ni servicios de búsqueda inexistentes. Las preguntas frecuentes son contenido visible y no se marcan como un resultado enriquecido de FAQ.

`codigo/prerenderizar_dashboard.cjs` ejecuta el mismo JavaScript de la aplicación con jsdom y sin recursos externos. La vista inicial contiene cifras, gráficos y comparaciones antes de ejecutar JavaScript en el navegador. Al abrir la página, los filtros funcionan con los mismos datos. El archivo descargable también contiene esa vista inicial. Al guardar desde la web se eliminan Analytics, los metadatos web y los iconos remotos, y se restablece la política offline.

## Miniatura

`site/assets/ingresos-chile-esi2025-social.png`, 1737 × 905 píxeles, es la imagen de enlaces compartidos. Se generó con imagegen el 14 de octubre de 2026. El archivo elegido se conserva sin edición de píxeles. La geometría es decorativa y no representa una distribución estadística.

Brief de generación: portada editorial horizontal, fondo marfil, tipografía verde oscuro, formas geométricas verdes y un acento ocre. Título «Ingresos en Chile», subtítulo «Explora por edad, sexo y ocupación», fuente «ESI 2025 · Microdatos INE», autor «Dr. Cristian Candia · CRISS-LAB» y dominio `ingresos.criss-lab.com`. Sin cifras estadísticas, ejes, logos institucionales ni promesas de resultados.

Los iconos conservan el símbolo de barras de la interfaz. Se regeneran desde `interfaz/favicon.svg` con `python3 -B codigo/generar_iconos.py` y CairoSVG.

## Construcción y validación

Requiere Node.js compatible con jsdom 30, además de Python. Las dependencias de JavaScript se instalan con `npm install --prefix qa`. Netlify no necesita compilar: publica los archivos ya construidos.

```bash
npm install --prefix qa
python3 -B construir_dashboard.py
node qa/check_analytics.cjs
node qa/check_seo.cjs
```

El resumen CSV publicado se copia directamente de `tablas/resumen_dominios.csv`. No contiene microdatos. Los archivos `_headers`, `_redirects` y `404.html` están dentro del directorio publicado. No hay una regla que convierta cualquier ruta inexistente en la página principal.

`modified` debe cambiarse solo cuando se actualice contenido relevante. No se cambia automáticamente en cada compilación. Al cambiar la miniatura conviene usar otro nombre de archivo y actualizar la configuración, porque las redes pueden conservar la imagen anterior en caché.

## Comprobaciones sobre el dominio

Una vez desplegado, comprobar HTTPS, la respuesta de la portada, la imagen, el CSV, robots.txt y sitemap.xml, la redirección de `/index.html` y el estado 404 de una ruta inexistente. Añadir `ingresos.criss-lab.com` como dominio principal en Netlify. Verificar propiedad en Google Search Console, enviar el sitemap e inspeccionar la URL. La verificación requiere acceso a la cuenta o al DNS y no se sustituye por una etiqueta inventada.

Configurar el SEO no prueba que Google haya indexado el sitio ni garantiza posiciones. El resultado depende también del despliegue, el rastreo y la relevancia del contenido.

## Referencias consultadas

- https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics
- https://developers.google.com/search/docs/appearance/structured-data/dataset
- https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
- https://ogp.me/

## Actualización para búsquedas · 16 de octubre de 2026

Título y descripción orientados a ingresos en Chile, sueldo promedio y mediano. Enlaces HTML a los temas principales y preguntas con respuestas numéricas visibles sin JavaScript. Las cifras se generan desde el agregado `all|all|all` en `datos/dashboard.json`, nunca se mantienen a mano. El universo 20+ se explica junto a las respuestas y se distingue de un promedio exclusivo de asalariados. Estas respuestas generales permanecen fijas cuando se aplican filtros.

La edición de los datos continúa siendo ESI 2025. La fecha de modificación describe el cambio editorial, no una actualización de ingresos a 2026. No se crearon páginas repetidas por palabras clave.

Para confirmar la presencia en Google, abrir https://search.google.com/search-console y seleccionar la propiedad del dominio. Enviar `https://ingresos.criss-lab.com/sitemap.xml`. Inspeccionar `https://ingresos.criss-lab.com/`, probar la URL publicada y solicitar indexación. La etiqueta de Analytics no prueba que la propiedad esté verificada en Search Console. No hay confirmación de estas operaciones desde este proyecto.

Referencias adicionales:
- https://developers.google.com/search/docs/fundamentals/seo-starter-guide
- https://developers.google.com/search/docs/monitor-debug/search-console-start
