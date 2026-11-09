# EP01 — Ejecución prolongada PIR y servo

Registro serie proporcionado por el usuario e incorporado el 2026-11-09. Fecha/hora de ejecución, operador, commit/binario cargado, ajustes del PIR, distancia, movimiento de referencia y condiciones de alimentación: no informados. Los tiempos son milisegundos desde el arranque, no UTC. No se conectó a AWS ni se repitió el ensayo para elaborar este análisis.

Se transcribieron todas las muestras `PIR` a [pir-muestras.csv](pir-muestras.csv) y todos los inicios de ciclo a [ciclos.csv](ciclos.csv). Son extractos estructurados del texto suministrado, no una captura serie original: no conservan el intercalado de mensajes sin timestamp. La fuente completa es el mensaje del usuario en esta conversación.

## Resultados observables

| Magnitud | Resultado |
|---|---|
| Primera / última muestra PIR | 148 / 1010079 ms |
| Ventana entre muestras extremas | 1009931 ms = 16 min 49,931 s |
| Tiempo desde arranque hasta última muestra | 16 min 50,079 s |
| Último `listo=0` / primer `listo=1` observado | 52083 / 67084 ms; no mide el instante exacto de transición |
| Ventana desde primera muestra lista | 942995 ms = 15 min 42,995 s |
| Ciclos iniciados / terminados declarados | 11 / 11; 3 iniciados antes de 60 s, 8 después |
| Flancos HIGH posteriores al calentamiento | 8: siete coinciden con inicio de ciclo y uno no inicia ciclo |
| Flanco sin ciclo | 431618 ms, 14727 ms después del inicio anterior (416891 ms) |
| Última muestra | LOW, listo=1, servo=idle, automatico=1 |

Los siete inicios coincidentes con HIGH son 155028, 233435, 329602, 416891, 570348, 689916 y 992624 ms. Cada uno está separado al menos 60 s del inicio anterior, incluido el ciclo de origen no identificado a 257780 ms. Es compatible con activación automática y enfriamiento; el log no etiqueta la causa de cada ciclo. El flanco de 431618 ms se descarta sin ciclo diferido visible mientras LOW, coherente con el código local.

Los ciclos a 18405, 34352, 51262 y 257780 ms no tienen un HIGH listo asociado. Los tres primeros suceden durante calentamiento. Son compatibles con órdenes externas/manuales, pero no prueban que Alexa las haya emitido: faltan activationId, desired/delta y petición de origen.

El texto incluye para cada ciclo orden de 180°, retorno a 0° y finalización con LED apagado. Confirma mensajes del controlador, no posición medida, giro efectivo, dosis ni observación óptica del LED. No hay timestamps en retorno/finalización; no se puede medir duración de ciclo con este registro. La diferencia HIGH→LOW mide el pulso muestreado del PIR, no el tiempo del servo.

Hay un mensaje de conexión MQTT y confirmaciones repetidas `Shadow: actualizacion de reported aceptada por AWS.`, incluso al final. No aparecen rechazos, desconexiones, nuevos arranques ni retrocesos de los tiempos en el texto suministrado. Esto respalda continuidad observada y aceptación de reported según el diagnóstico serie; no demuestra disponibilidad sin interrupciones, contenido JSON, convergencia desired/reported ni latencias de nube. Los accepted carecen de timestamp. Las muestras locales periódicas alrededor de 15 s no miden el intervalo entre aceptaciones en AWS.

## Trazabilidad del plan

| Caso | Estado con EP01 | Pendiente para aprobar |
|---|---|---|
| P01 / RF1 | PARCIAL: calentamiento y HIGH/LOW observados | Cruces a 1, 2 y 3 m, referencia física y modo desactivado |
| P02 / RF2 | PARCIAL: confirmaciones de reported | JSON sensor/actuador y tiempos de recepción |
| P03 / RF3, RF5 | PARCIAL: 11 secuencias de ciclo declaradas | Cinco órdenes Alexa trazadas con requestId, desired/delta y vídeo |
| P11 / automático | PARCIAL: siete coincidencias y un flanco sin ciclo en cooldown | Habilitar/deshabilitar por voz, HIGH sostenido controlado y comprobación física |
| P16 / restricciones | PENDIENTE: el log menciona LED | Inspección del circuito y función del LED; el plan exige sin LED funcional |
| N01 / estabilidad | PARCIAL: más de 15 min observados tras listo=1, sin reinicio visible | Diez ciclos tras calentamiento (hay ocho), consultas cada minuto, alternancia de modo, uptimeSeconds y verificación física |
| N02 / clasificación | PENDIENTE | 40 ensayos con referencia y distancias; HIGH/LOW no permiten TP/TN/FP/FN |
| N03 / latencia | PENDIENTE | Fin de solicitud y primer movimiento en referencia temporal común |
| N04 / reportes | PARCIAL: aceptación repetida | Timestamps de accepted y flancos eléctricos; umbrales no medidos |
| N05–N06 / recuperación | PENDIENTE | Cortes controlados de red y alimentación |

P04–P10, P12–P15 y P17–P20 no reciben validación adicional de este extracto.

## Diferencias y límites

El firmware local `firmware/src/Ambientador.cpp` no contiene los mensajes `Servo: angulo ordenado...` ni control de LED del registro. Por tanto, su lógica sirve como referencia de compatibilidad, pero no identifica el binario ensayado. Guardar el código exacto cargado antes de atribuirle esta ejecución. No se modificó firmware para hacerlo coincidir con la evidencia.

El diagnóstico anterior de HIGH sostenido se conserva como otro ensayo. EP01 sí contiene retornos a LOW; no prueba que el problema anterior esté resuelto bajo las mismas condiciones ni permite concluir sensor defectuoso, exactitud o ausencia de interferencia del servo. El módulo fue identificado previamente por el usuario como HW-416-B; este log no verifica su modelo.

Conservar después el archivo serie original, fecha de captura, versión cargada, montaje y vídeo. Completar los ensayos faltantes sin cambiar retrospectivamente sus criterios de aceptación.

## Pulsos muestreados

[pir-pulsos.csv](pir-pulsos.csv) contiene las nueve parejas HIGH/LOW. Tras calentamiento, las ocho duraciones observadas van de 1277 a 2729 ms. Son diferencias entre muestras del loop, no mediciones electricas precisas ni duraciones del servo. No permiten clasificar aciertos o errores sin movimiento de referencia.

## Cambio posterior para pruebas

Despues de EP01 se redujo AUTO_COOLDOWN_MS de 60000 a 5000 ms. Los resultados anteriores conservan su interpretacion con 60 s; no validan el nuevo intervalo. Repetir P11 con flancos antes y despues de 5 s desde el inicio del ultimo ciclo. El calentamiento inicial del PIR sigue en 60 s.

Actualizacion posterior: se integro test-led (e3e08a1) en main. El firmware local ahora incluye el LED de estado y los mensajes de angulo descritos en EP01. La diferencia de codigo indicada en el analisis corresponde al momento de incorporacion de la evidencia; la coincidencia de mensajes no identifica por si sola el binario original ensayado. Se reaplico el intervalo de pruebas de 5 s.
