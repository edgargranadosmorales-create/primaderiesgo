# Dashboard EY menos Treasury 10Y
Paquete listo para ejecutar, NO desplegado. El HTML con datos se genera al ejecutar por primera vez. Se comprobó la sintaxis Python, pero no las descargas en vivo en este entorno.

## Inicio local
Instala Python 3.12. Extrae el ZIP y abre una terminal en la carpeta.
    python -m pip install -r requirements.txt
    python actualizar.py
Abre index.html. Las consultas requieren internet. El gráfico generado incorpora Plotly y puede verse offline.

## Automatización con GitHub
1. Crea un repositorio y sube todo el contenido extraído, incluyendo la carpeta oculta .github y su workflow.
2. En Actions habilita los workflows y abre Actualizar diferencial diario > Run workflow.
3. Comprueba que finalice en verde y aparezcan index.html y data/.
4. En Settings > Pages elige Deploy from a branch, rama main (o tu rama predeterminada), carpeta /(root).
5. Guarda como favorito la URL que te muestre GitHub.

Consulta programada a las 01:30 UTC, equivalente a 19:30 del día anterior en UTC-6. GitHub puede retrasar tareas; revisa su estado en Actions. En repositorios públicos inactivos puede deshabilitar la programación. Comprueba costos y políticas vigentes de tu cuenta. No requiere API keys.
El workflow guarda y publica nuevos datos al cambiar el HTML. El refresco del navegador no descarga fuentes: vuelve a leer el HTML publicado.

## Método y límites
Histórico MENSUAL desde enero de 1997: EY TTM de Multpl menos promedio de observaciones DGS10 del mismo mes. Excluye el mes del EY más reciente de esa curva. No son cierres diarios ni datos forward.
DIARIO desde instalación: captura las observaciones con la fecha publicada del EY y conserva el último Treasury anterior o de esa fecha. Muestra ambas fechas. No inventa fechas cuando la fuente no publica. Marca estimaciones en CSV.
Si el Treasury se retrasa más de 7 días o falla una fuente, conserva el HTML anterior y el workflow falla. Revisa las fechas de datos y consulta: un sitio visible no garantiza una actualización exitosa.
Si Multpl cambia su formato habrá que adaptar el parser. No existe garantía de disponibilidad de fuentes públicas.
El diferencial NO es la prima de riesgo esperada completa. Los datos históricos pueden estar revisados, no son point-in-time para backtesting.
Fuentes: Multpl S&P 500 Earnings Yield by Month y FRED DGS10.
