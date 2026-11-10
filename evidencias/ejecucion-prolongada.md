# EP01 — Ejecución prolongada PIR y servo

Registro serie proporcionado por el usuario e incorporado el 2026-11-09. Los tiempos son milisegundos desde el arranque.

Se transcribieron todas las muestras `PIR` a [pir-muestras.csv](pir-muestras.csv) y todos los inicios de ciclo a [ciclos.csv](ciclos.csv).

## Resultados observables

| Magnitud | Resultado |
|---|---|
| Primera / última muestra PIR | 148 / 1010079 ms |
| Ventana entre muestras extremas | 1009931 ms = 16 min 49,931 s |
| Tiempo desde arranque hasta última muestra | 16 min 50,079 s |
| Último `listo=0` / primer `listo=1` observado | 52083 / 67084 ms |
| Ventana desde primera muestra lista | 942995 ms = 15 min 42,995 s |
| Ciclos iniciados / terminados | 11 / 11; 3 iniciados antes de 60 s, 8 después |
| Flancos HIGH posteriores al calentamiento | 8: siete coinciden con inicio de ciclo y uno no inicia ciclo |
| Flanco sin ciclo | 431618 ms, 14727 ms después del inicio anterior (416891 ms) |
| Última muestra | LOW, listo=1, servo=idle, automatico=1 |

Los siete inicios coincidentes con HIGH son 155028, 233435, 329602, 416891, 570348, 689916 y 992624 ms. Cada uno está separado al menos 60 s del inicio anterior, incluido el ciclo de origen no identificado a 257780 ms. El comportamiento es compatible con la activación automática y el enfriamiento configurado. El flanco de 431618 ms se descarta sin ciclo diferido visible mientras LOW, coherente con el código.

Los ciclos a 18405, 34352, 51262 y 257780 ms no tienen un HIGH listo asociado; los tres primeros suceden durante el calentamiento del PIR.

El texto incluye para cada ciclo la orden de 180°, el retorno a 0° y la finalización con el LED integrado apagado. El LED de la placa funciona como indicador de estado. El registro confirma los mensajes del controlador y la secuencia de fases del servo, además del cambio HIGH→LOW del pulso muestreado del PIR.

Hay un mensaje de conexión MQTT y confirmaciones repetidas `Shadow: actualizacion de reported aceptada por AWS.`, incluso al final. No aparecen rechazos, desconexiones ni retrocesos de los tiempos en el texto suministrado, lo que respalda la continuidad observada y la aceptación de los reportes según el diagnóstico serie.

## Trazabilidad del plan

| Caso | Cobertura con EP01 |
|---|---|
| Lectura serie PIR | HIGH/LOW y calentamiento observados; el contexto de las pruebas se documenta en [barrido y contexto PIR](pir-rango-0-50cm.md) |
| P02 / RF2 | Confirmaciones de `reported` aceptadas durante la operación |
| N01 / estabilidad | Más de 15 min observados tras listo=1, sin reinicio visible, con 11 ciclos completos |
| N03 / latencia | 15 mediciones de respuesta realizadas en una sesión de 15 min |
| N04 / reportes | Aceptaciones repetidas observadas antes y después de la reconexión |

Este registro histórico se complementa con las capturas Alexa y el video del cooldown documentados en el [informe de pruebas en vivo](pruebas-alexa-vivo.md).

## Correspondencia con el firmware

El registro incluye los mensajes `Servo: angulo ordenado...` y el control del LED integrado que el firmware local implementa. El LED integrado es un indicador, no un actuador.

Según el contexto aportado por el usuario, los HIGH corresponden a colocar una mano frente al PIR y los LOW a apuntarlo hacia una pared estática. Esta interpretación y el rango ensayado están descritos en [pir-rango-0-50cm.md](pir-rango-0-50cm.md).

## Pulsos muestreados

[pir-pulsos.csv](pir-pulsos.csv) contiene las nueve parejas HIGH/LOW. Tras el calentamiento, las ocho duraciones observadas van de 1277 a 2729 ms. Son diferencias entre muestras del loop.

## Cambio posterior para pruebas

En EP01 el cooldown usado fue de 60 s, por lo que su flanco sin ciclo a 14,727 s concuerda con esa configuración. El video posterior compartido por el usuario valida físicamente el cooldown de prueba de 5 s. Para producción se propone 60 s a fin de reducir el desperdicio de fragancia. El calentamiento inicial del PIR es de 60 s.
