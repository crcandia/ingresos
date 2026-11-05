# SEO y vistas previas

La página tiene como dirección canónica [ingresos.criss-lab.com](https://ingresos.criss-lab.com/). El título, la descripción, la fecha de modificación, los datos de autoría y la ruta de la miniatura se configuran en `interfaz/seo.json`. El generador es `codigo/seo_web.py`.

## Qué puede leer un buscador

La portada, el recorrido, la fuente, las referencias salariales y los gráficos iniciales están en el HTML antes de ejecutar JavaScript. Las respuestas sobre el promedio, la mediana y quién alcanza un millón al mes usan `all|all|all` en `datos/dashboard.json`. Las 38.729 personas ocupadas de referencia de la ESI representan a unas 9,02 millones de personas. Las preguntas por edad aclaran que el primer tramo abarca de 15 a 19 años. Los resultados nacionales siguen siendo la referencia al usar los filtros del explorador.

La versión web incluye título y descripción, Open Graph, Twitter Card, URL canónica, iconos y un grafo JSON-LD para `WebSite`, `WebPage`, `Person` y `Dataset`. La ficha del conjunto de datos enlaza el CSV agregado de los 420 cruces. La sección sobre las 20 carreras tiene su propio identificador, `#sueldos-por-carrera`, y explica sus fuentes de Mi Futuro y Lixandria. Las estimaciones por carrera y las referencias de autoridades proceden de fuentes distintas de la encuesta. Los enlaces a edad, sexo, ocupación y metodología llevan a los encabezados de esas secciones.

Las fechas cumplen funciones distintas. Los datos de ingreso de la ESI corresponden a 2025. El campo `modified` se actualiza cuando cambia el contenido publicado. El sitemap usa esa fecha y la misma dirección canónica.

## Vista previa al compartir

La miniatura social, `site/assets/ingresos-chile-esi2025-social.png`, mide 1737 × 905 píxeles. La portada editorial dice «Ingresos en Chile» y «Explora por edad, sexo y ocupación». Su geometría es decorativa. Se generó el 14 de octubre de 2026 para acompañar los enlaces compartidos.

La imagen que ve quien entra al sitio es distinta. `site/assets/ingresos-chile-trabajo.webp` es la ilustración de una feria chilena que también se incrusta en el HTML descargable. Los iconos se regeneran desde `interfaz/favicon.svg` con `python3 -B codigo/generar_iconos.py` y CairoSVG.

## Construcción y comprobaciones locales

```bash
npm install --prefix qa
python3 -B construir_dashboard.py
node qa/check_relato.cjs
node qa/check_analytics.cjs
node qa/check_seo.cjs
```

El constructor utiliza Node.js con jsdom para prerenderizar los datos y las comparaciones. Si cambió la definición de población o un agregado de la encuesta, primero se recalculan los datos como indica el [README](README.md#reproducir-el-análisis).

El resumen público `site/datos/resumen-ingresos-esi2025.csv` se copia de `tablas/resumen_dominios.csv`. Los controles locales verifican la coherencia entre el CSV, el HTML y el contenido estructurado. Revisan la ruta y las dimensiones de la miniatura, el contenido de la vista inicial, la conservación de los filtros y los recursos de publicación. La copia generada con «Guardar copia» restaura la política de conexión del HTML descargable y elimina los metadatos web y Analytics. La carpeta `site/` incluye además `robots.txt`, `sitemap.xml`, `_headers`, `_redirects` y `404.html`.

El contenido principal precede al bloque JSON del explorador. El control de SEO comprueba que quepa en los primeros 1,9 MB sin comprimir. [Documentación de Google Search Central sobre rastreo](https://developers.google.com/search/blog/2026/03/crawler-blog-post)

## Verificación tras publicar

Comprobar sobre el dominio HTTPS la portada, el CSV, la miniatura, `robots.txt`, el sitemap, la redirección de `/index.html` y una ruta inexistente. La carpeta y la configuración de despliegue se describen en [Publicación](PUBLICACION.md).

Para conocer el estado de indexación, seleccionar la propiedad del dominio en Search Console, enviar el sitemap e inspeccionar la URL canónica. El estado de rastreo y las vistas previas de terceros se verifican en los respectivos servicios. [Search Console](https://search.google.com/search-console) · [Sitemap del sitio](https://ingresos.criss-lab.com/sitemap.xml)

[SEO de aplicaciones JavaScript](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics) · [Marcado Dataset](https://developers.google.com/search/docs/appearance/structured-data/dataset) · [Open Graph](https://ogp.me/)
