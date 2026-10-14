# Revisión independiente de Google Analytics

Adversarial verdict: PASS_WITH_RISKS

Completion claim challenged: La integración local añade la etiqueta `G-XSFF2F0XKK` a la versión web, mantiene los datos e interfaz del dashboard y permite descargar copias sin Analytics con sus filtros conservados.

Findings: No quedan defectos funcionales pendientes en este alcance. Se corrigió un defecto del constructor antes del cierre: una sustitución global del texto del pie alteraba también el literal JavaScript que debía restaurar el mensaje offline. La versión revisada sustituye únicamente el elemento `#privacy-note` y restaura su texto directamente al guardar (`construir_dashboard.py:22`, `interfaz/dashboard.html:68`, `interfaz/dashboard.js:182`).

Required fixes before final: Ninguno para la integración local revisada. Este dictamen no certifica publicación, DNS ni recepción de eventos en Google Analytics.

## Evidencia

Se revisaron los fuentes y ambos HTML generados. Los archivos construidos coinciden exactamente con la plantilla, CSS, JavaScript, JSON y fragmento de Analytics vigentes.

La versión web incluye una única carga asíncrona de `https://www.googletagmanager.com/gtag/js?id=G-XSFF2F0XKK` y una única orden `config` con ese identificador. Se verificaron las dos órdenes iniciales de `dataLayer`: `js` y `config`. El pie de la versión web informa de Analytics.

Las directivas CSP configuradas cubren la carga de la etiqueta y los destinos indicados en la [guía oficial para Analytics sin funciones de Ads](https://developers.google.com/tag-platform/security/guides/csp?hl=en): `www.googletagmanager.com`, `*.google-analytics.com` y, para conexiones, `*.google.com`. El fragmento también coincide con la estructura de [instalación oficial de gtag.js](https://developers.google.com/tag-platform/gtagjs). Ambas referencias se consultaron el 14 de octubre de 2026. Esta comparación del código no sustituye la comprobación de tráfico en el sitio publicado.

Se ejecutaron pruebas independientes con Node.js y jsdom, sin habilitar carga de recursos externos ni enviar solicitudes a Google:

- La aplicación inicia en la versión web aunque la biblioteca externa no se ejecute durante la prueba.
- Al guardar desde la web se eliminan los dos fragmentos de Analytics y dos scripts adicionales simulados de sus dominios, como los que podría insertar una biblioteca durante su ejecución.
- La copia no contiene el identificador de medición, scripts externos ni fragmentos `data-web-analytics`. Al reabrirla no existen `dataLayer` ni `gtag`.
- Se restaura exactamente la CSP offline, con `connect-src 'none'` y sin dominios remotos permitidos. El pie vuelve a indicar que es un archivo autocontenido.
- Ocupación, sexo, edad, monto, rango, criterio de comparación y escala logarítmica se conservan al guardar y reabrir.
- Se modificaron filtros en esa primera copia y se guardó una segunda copia. Conservó los nuevos filtros y siguió sin Analytics, con el pie y la CSP offline correctos.
- El HTML offline original tampoco incluye Analytics y conserva los 38.380 casos del universo inicial.
- Los JSON incrustados son idénticos en las versiones web y offline y en la copia guardada. `datos/dashboard.json` coincide byte a byte con la versión en `HEAD` anterior a la integración.
- No se observaron errores de JavaScript.

## Archivos examinados

| Archivo | SHA-256 |
| --- | --- |
| `Ingresos_Chile_ESI2025.html` | `4156d9005e0c56d808e7e0813c979faf125d616d7a8f533cdace414a7aeb842d` |
| `site/index.html` | `094fd96267eea79e9f2775a3d841a3b977fad7371f0a64df1a21d1db291b9177` |
| `datos/dashboard.json` | `4d65eb30103c3c8457740c5608b3ed14d0d433463cbce4816caf7586cea272e2` |

## Límites

Las comprobaciones funcionales se realizaron con jsdom. No se ejecutó la biblioteca remota de Google ni se verificó la aplicación de CSP en un navegador real. Se comprobó su configuración y la eliminación de las etiquetas en las copias, no un envío ni la recepción de eventos en producción.

`PUBLICACION.md` distingue correctamente los archivos preparados del despliegue y la existencia del DNS. El sitio todavía requiere completar y verificar la publicación; este informe no afirma que esté en línea. La prueba final de Analytics debe realizarse sobre el dominio publicado, comprobando las solicitudes y su recepción en la propiedad correspondiente.
