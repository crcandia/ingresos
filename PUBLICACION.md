# Publicación de Ingresos en Chile

Destino solicitado: `ingresos.criss-lab.com`.

Repositorio: [crcandia/ingresos](https://github.com/crcandia/ingresos), rama `main`.

El proyecto incluye `netlify.toml` y `site/index.html`. Netlify debe usar la carpeta base `site`, publicar `.` y no ejecutar compilación. El sitio es HTML estático con datos agregados incrustados. El extracto de microdatos y las herramientas de análisis quedan fuera de la carpeta publicada.

Para actualizar el sitio desde el código fuente:

```bash
python3 -B construir_dashboard.py
```

Este comando genera el HTML descargable y `site/index.html` con los mismos datos e interfaz. La versión web añade la etiqueta Google Analytics `G-XSFF2F0XKK`, ajusta la política de contenido para permitir sus conexiones y muestra una nota en el pie. “Guardar copia” elimina la etiqueta y restablece el bloqueo de red para uso sin conexión. Después se confirma el cambio en GitHub y Netlify puede desplegarlo desde la rama configurada.

## Dominio

Primero se debe añadir `ingresos.criss-lab.com` como dominio del proyecto en Netlify. Luego se crea en la zona `criss-lab.com` de Cloudflare un registro CNAME llamado `ingresos`, cuyo destino sea el hostname real asignado por Netlify. No se debe inventar ese destino. Antes de crear o reemplazar un registro se revisa si ya existe.

El estado de publicación debe verificarse en Netlify y con una respuesta HTTPS del dominio. Tener estos archivos preparados no prueba que el sitio esté desplegado o que el DNS exista.

## Referencias

- [Configuración de Netlify](https://docs.netlify.com/build/configure-builds/file-based-configuration/)
- [Subdominio con DNS externo](https://docs.netlify.com/manage/domains/configure-domains/configure-external-dns/)
- [Registros DNS en Cloudflare](https://developers.cloudflare.com/dns/manage-dns-records/how-to/create-dns-records/)
