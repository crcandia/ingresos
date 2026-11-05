# Ingresos en Chile · ESI 2025

¿Qué gana la persona que queda al medio si se ordenan los ingresos del trabajo de menor a mayor? En Chile, la mediana fue de **$680.000 mensuales** y el promedio fue de **$962.945**. El **68,7%** de las personas ocupadas de referencia ganó menos que ese promedio. Son estimaciones de la Encuesta Suplementaria de Ingresos (ESI) 2025 del INE, en pesos de octubre de 2025. [Abrir el sitio](https://ingresos.criss-lab.com/) · [Repositorio](https://github.com/crcandia/ingresos)

Para explorar sin conexión, abre `Ingresos_Chile_ESI2025.html` en un navegador. El archivo incluye los datos agregados, las imágenes, los gráficos y los controles.

## A quiénes representan las cifras

El INE identifica con `ocup_ref == 1` a las personas que llevan al menos un mes en su ocupación actual. La ESI 2025 contiene **38.729** personas en ese grupo. Sus factores de expansión representan a **9.022.697 personas**. La muestra incluye desde los 15 hasta los 95 años. El análisis conserva a todos los ocupados de referencia, incluso a quienes declaran un ingreso de $0.

El ingreso corresponde al trabajo principal. Para las personas asalariadas se descuentan cotizaciones e impuestos. Para quienes trabajan de manera independiente se consideran los ingresos después de los costos de la actividad. La portada y el recorrido usan la población nacional completa. Los filtros del explorador calculan los resultados dentro del grupo elegido.

## Cómo leer el sitio

- **De menor a mayor.** El recorrido reparte a toda la población en cinco tramos. Comienza en $0 y el último tramo reúne a quienes ganan $2 millones o más. Luego amplía distintos puntos de la distribución, incluidos los ingresos superiores a $10 millones. Los pictogramas indican cuántas personas alcanzan un monto y explicitan su denominador.
- **Carreras y cargos.** La comparación parte de las cuatro carreras universitarias con más matrícula de primer año según SIES 2026. Para las 20 carreras, Mi Futuro entrega un promedio bruto al tercer año. El sitio estima cuánto recibiría una persona asalariada con ese bruto y lo sitúa en la distribución de la ESI. Cada carrera tiene su propia ficha en Lixandria. Los 14 cargos públicos incluyen la fecha, la fuente y el tipo de pago utilizado.
- **Edad, sexo y ocupación.** El explorador compara trece tramos de edad, desde 15–19 hasta 70–74 y un último grupo de 75 años o más. El total de edades corresponde a la ocupación y al sexo elegidos. Las trece tarjetas muestran cada tramo por separado. En el perfil de edad, la banda entre los percentiles 25 y 75 contiene la mitad central de los ingresos. Las comparaciones por sexo y por ocupación mantienen los demás filtros.
- **Consulta de un monto.** La proporción incluye a quienes ganan exactamente el monto consultado. La escala logarítmica de la curva ayuda a distinguir porcentajes pequeños. Los intervalos y avisos indican cuánto respaldo ofrece la muestra. Un cruce vacío muestra que la encuesta carece de observaciones para ese grupo. Las diferencias entre edades describen grupos de personas observadas en 2025.

Las nueve ocupaciones con nombre en el explorador reúnen 38.573 encuestados. El total de ocupaciones también incluye los 156 casos de los códigos residuales del INE. Los denominadores, las fórmulas y los cruces vacíos están documentados en [Datos y método](README_DATOS.md).

## Guardar y exportar

**Guardar copia** descarga un HTML con la selección y la escala actuales. **Descargar datos de esta vista** exporta las cifras con su precisión de cálculo en un CSV con separador de punto y coma, punto decimal y codificación UTF-8 con BOM. **Imprimir / PDF** abre el diálogo del navegador. Los enlaces del sitio abren una pestaña nueva. La medición de Google Analytics corresponde a la versión web. Las copias descargables funcionan sin conexión.

## Reproducir el análisis

Desde la raíz del repositorio, con Python y una versión de Node.js compatible con jsdom 30, ejecuta estos comandos.

```bash
python3 -m pip install -r requirements.txt
npm install --prefix qa
python3 -B codigo/analizar_dashboard.py
python3 -B construir_dashboard.py
```

El primer script valida el hash del extracto incluido, calcula los 420 cruces y exporta las tablas. El constructor combina los agregados y las fuentes de la interfaz para generar `Ingresos_Chile_ESI2025.html` y `site/index.html`. Ambos incluyen una vista inicial legible sin JavaScript. En el HTML se distribuyen agregados de la encuesta.

El conteo de asalariados públicos y privados requiere la variable `categoria_ocupacion` del CSV completo del INE. El resultado ya está en `fuentes/universo_asalariados.json`. Para regenerarlo, ejecuta este paso entre el análisis y la construcción del HTML. La URL y la huella del original están en `fuentes/procedencia.json`.

```bash
python3 -B codigo/contar_asalariados.py /ruta/esi_2025_personas.csv
```

## Comprobar la reproducción

```bash
node qa/run_dom_checks.cjs
node qa/check_relato.cjs
node qa/check_analytics.cjs
node qa/check_seo.cjs
```

Las pruebas de DOM recorren las combinaciones de filtros y ambas escalas de la curva, el guardado y reapertura, el CSV, la geometría de los gráficos, el relato nacional y los metadatos. Los resultados que registra cada ejecución están en `datos/validacion.json` y `qa/validacion_*.json`. El contraste independiente con el CSV del INE se documenta en [Verificación del universo](qa/revision_universo.md).

Después de ejecutar las pruebas de DOM se pueden generar los PDF vectoriales desde los mismos SVG que usa la interfaz.

```bash
python3 -m pip install -r qa/requirements.txt
python3 -B qa/render_estatico.py
```

`figuras/curvas_vista_general.pdf` incluye la distribución y la curva acumulada en escalas lineal y logarítmica. `figuras/perfil_ingresos_por_edad.pdf` reúne las medianas, los promedios y la banda de percentiles de los trece tramos. Las figuras corresponden a la vista nacional inicial. `python3 -B crear_paquete.py` prepara el ZIP y comprueba los archivos contra `MANIFEST_SHA256.json`.

## Fuentes de las comparaciones y publicación

Las carreras proceden de Mi Futuro. Los brutos universitarios están expresados en pesos de septiembre de 2025. Para reproducir una consulta, envía por POST el `action` y el `id` de la carrera al servicio de Mi Futuro y lee `tercer_ano`. La metodología del sitio explica el tratamiento particular de Derecho, la conversión ilustrativa a líquido y el redondeo del monto a mil pesos para situarlo en la ESI. El identificador `lixandria_id` corresponde al catálogo de Lixandria. [Servicio de Mi Futuro](https://www.mifuturo.cl/wp-admin/admin-ajax.php) · [Referencias y cifras originales](fuentes/referencias_salariales.json)

Los cargos distinguen pagos de un mes, medianas de una nómina y promedios de pagos durante un año. Para el Senado se toma la mediana del saldo pagado a 50 integrantes. En la Cámara, la dieta bruta del registro y el líquido declarado por José Carlos Meza se identifican por separado. Para las alcaldías se indican el mes del pago, sus incentivos y la población en el Censo 2024. La fila de la nómina utilizada para Valparaíso se conserva en el paquete. [Extracto de la nómina](fuentes/autoridades_planta_2025.csv) · [Archivo original del CPLT](https://consejotransparencia.cl/transparencia_activa/datoabierto/archivos/TA_PersonalPlanta.csv)

La carpeta `site/` contiene la versión para publicación. [Configuración de publicación](PUBLICACION.md) · [Metadatos y vistas previas](SEO.md)

El análisis de la distribución y de los cruces por edad, sexo y ocupación fue elaborado por Cristian Candia, CRiSS-LAB, con datos de la ESI 2025 del Instituto Nacional de Estadísticas de Chile.
