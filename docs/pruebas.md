# Plan de pruebas obligatorio y registro de validación

## Alcance y preparación

Verificar RF1–RF9, extensión automática, requisitos no funcionales y restricciones del montaje. Las pruebas locales no reemplazan las de integración. Estado inicial de todos los ensayos físicos: **PENDIENTE**.

Material: ESP32 y circuito revisado, regla/cinta para marcar 1–3 m, fuente y multímetro, cámara que registre simulador y servo en una misma toma, PC con Alexa Developer Console, IoT MQTT Test Client y logs Lambda. Para medir el flanco eléctrico del PIR usar analizador lógico u osciloscopio con referencia temporal alineada al registro de recepción; si no se dispone, declarar la limitación y no afirmar que la latencia eléctrica fue medida con precisión.

Preparar `thing` y un segundo Thing de prueba permitido por IAM. El segundo puede usar otro dispositivo para la demo completa o un Shadow de prueba para validar exclusivamente aislamiento de usuarios; indicar cuál. Usar dos usuarios Alexa reales para integración; dos userId artificiales en tests solo comprueban el backend. Inicializar Shadows antes de pruebas concurrentes. Configurar 5 V, masa común, placa correcta y sin acoplar aerosol en ensayos repetitivos.

Guardar por ensayo: fecha UTC, operador, versión/commit, placa, ajustes PIR, WiFi, intención reconocida, Thing, valor esperado, valor observado, resultado y ruta de evidencia. No almacenar userId completo ni certificados en capturas públicas. Repetir pruebas afectadas después de corregir fallos y conservar ambos resultados.

## Casos funcionales y de interacción

| ID / requisitos | Procedimiento y frase exacta dentro de la skill | Criterio de aceptación | Evidencia |
|---|---|---|---|
| P01 / RF1 | Reiniciar; esperar 60 s; cruzar a 1, 2 y 3 m; dejar volver OUT a LOW | pirReady pasa a true; presence sigue HIGH/LOW; no ciclos con automático desactivado | Vídeo, reportes |
| P02 / RF2 | Sin movimiento 2 min; luego provocar 5 cambios OUT | Reportes contienen sensor/actuador; respaldo ≤16 s y eventos ≤1 s en conexión estable | Tiempos de update/accepted |
| P03 / RF3, RF5 | «activa el ambientador», 5 veces separadas por finalización | Cada requestId nuevo produce un ciclo; desired cambia, delta llega y reported converge | JSON Alexa, Shadow, vídeo |
| P04 / RF4 | «hay movimiento», «hay presencia», «qué detecta el sensor» con HIGH y LOW; repetir durante calentamiento | Intent correcto; lectura de reported en español o aviso de calentamiento | JSON y respuesta |
| P05 / RF6 | «cuál es el estado del motor» y «el motor está activo» | Respuesta concuerda con fase reportada reciente y no afirma posición medida | Captura y Shadow |
| P06 / RF7 | «vincula mi ambientador con thing»; salir y volver a abrir skill | Registro DynamoDB persistente; nueva sesión controla thing | Tabla y sesiones |
| P07 / RF8 | Usuario A vincula thing; B otro Thing; A/B consultan y activan; usuario C sin vínculo intenta activar | Cada solicitud usa su Thing; C recibe guía y no modifica Shadow | Capturas anonimizadas, dos Shadows |
| P08 / RF9 | Intentar vínculo a nombre inexistente y a nombre no permitido | No reemplaza el vínculo válido; mensaje comprensible; no hay escritura DynamoDB | Tabla antes/después |
| P09 / RF9 | «cambia mi ambientador a ambientador dos» con Thing válido | Mismo userId queda asociado al nuevo Thing; comandos siguientes van al nuevo | Tabla y Shadow |
| P10 / RF9 | «desvincula mi ambientador», repetir, luego pedir activación | DeleteItem idempotente; pide vincular; automático físico no se altera por desvincular | Tabla y respuesta |
| P11 / extensión | «activa el modo automático»; esperar convergencia; provocar LOW→HIGH; mantener HIGH; provocar otro flanco antes y después de 60 s; «desactiva el modo automático» | Un ciclo por flanco elegible; HIGH continuo y flancos en enfriamiento no actúan; tras desactivar no inicia nuevos ciclos; manual sigue disponible | Vídeo, reportes y tiempos |
| P12 / frescura | Desconectar placa, esperar >45 s; preguntar sensor/motor/modo | Informa que no hay datos recientes, sin presentar lectura antigua como actual | Respuesta y sampledAt |
| P13 / reconexión | Desconectar WiFi/Internet; solicitar ciclo y cambio de modo por Alexa; reconectar | Recupera conexión y desired; ciclo pendiente una vez; convergencia; automático no inicia offline | Serie temporal y vídeo |
| P14 / duplicados | Reenviar mismo evento Alexa/requestId y mismo desired; reiniciar tras ciclo | No repite el ciclo por el mismo identificador; luego acepta uno distinto | NVS preservada, vídeo y Shadow |
| P15 / concurrencia | Dos comandos próximos con Shadow inicializado y usuarios vinculados al mismo Thing | Uno pendiente; el otro espera o reintenta por conflicto sin borrar la orden pendiente | Logs y versiones |
| P16 / restricciones | Inspección de circuito y secretos | Actuador SG90, sin LED funcional; alimentación ≤12 V DC; secretos ignorados; no access keys en fuentes | Foto y revisión |
| P17 / controles Alexa | Abrir skill; «ayuda»; frase ajena; «cancelar»; «salir» | Ayuda/fallback comprensibles, stop/cancel terminan sesión | JSON simulador |
| P18 / frases automáticas | «enciende el modo automático», «apaga el modo automático», «está activado el modo automático», «cuál es el modo actual» | Intents correctos; consulta reported, no desired pendiente | Capturas |
| P19 / seguridad | Evento con otro applicationId; certificado no autorizado; rol sin acceso a Thing de prueba | No accede a datos para otra skill; AWS rechaza MQTT/Thing ajeno; sin cambio físico | Tests/logs sin secretos |
| P20 / recuperación de errores | Probar Shadow inexistente y acceso denegado; corregir permisos; recuperar conexión | Mensaje de servicio ante error; creación inicial/reportes y recuperación tras corrección | Logs y Shadow |

Probar también todas las frases exportadas en `alexa/interaction-model.es-ES.json` con Utterance Profiler o el simulador, anotando intent y slot esperados/obtenidos. No basta con ejecutar cada intent directamente en Lambda. Verificar «Alexa, abre ambientador inteligente» fuera de sesión; las frases cortas se prueban dentro de la sesión. La invocación global sin nombre de skill no es un criterio prometido por una Custom skill.

## Ensayos cuantitativos no funcionales

### N01 — Estabilidad (15 minutos)

Tras calentamiento y conexión, registrar `uptimeSeconds` y hora inicial. Operar 15 min, consultar cada minuto, ejecutar al menos 10 ciclos, alternar modo y movimiento. Registrar cada reporte y monitor serie. Éxito: cero reinicios/bloqueos, uptime monotónico, ciclos completos, comunicación disponible. Un reinicio por alimentación se considera fallo, no se descarta del análisis. Separar este ensayo de la desconexión intencional de N05.

### N02 — Exactitud de clasificación PIR

Marcar 1, 2 y 3 m y usar recorrido transversal dentro del campo observado. Estabilizar 60 s y fijar sensibilidad/retardo/jumper. Hacer 20 ensayos con una persona caminando (7 a 1 m, 7 a 2 m y 6 a 3 m) y 20 sin movimiento durante ventanas de 5 s. Alternar el orden y esperar LOW estable más 5 s antes de cada ensayo; con el retardo corto del módulo, ampliar la espera si fuera necesario. HIGH durante la ventana positiva es TP; ausencia es FN. En ventana negativa, HIGH es FP y LOW es TN. Mantener condiciones de referencia anotadas.

Éxito: `(FP+FN)/40 ≤ 0,10`, es decir, como máximo 4 errores. Informar sensibilidad `TP/(TP+FN)` y especificidad `TN/(TN+FP)` además del error global. Personas inmóviles no son positivos de movimiento. La cifra aplica al rango y condiciones ensayados, no al alcance comercial del módulo. Si falla, revisar entorno/ajuste y registrar nueva serie sin ocultar la anterior.

### N03 — Tiempo de respuesta extremo a extremo

Registrar en una misma toma de vídeo la finalización de la frase y el primer movimiento del servo. Veinte activaciones manuales con placa lista, conexión estable y separación suficiente. Registrar al menos una invocación fría de Lambda por separado; no usar solo Duration de CloudWatch como tiempo total. Para simulador por texto, medir desde envío y etiquetar como latencia de texto, sin confundirla con voz.

Calcular cada `t_movimiento - t_fin_frase`, media y máximo; éxito máximo ≤3 s. Anotar resolución de vídeo (a 30 fps, cada cuadro dura aproximadamente 33 ms). Separar tiempo hasta movimiento y duración completa del ciclo (~1,4 s ordenados, por verificar). Si no cumple, reportar distribución, condición de red, cold start y segmentos medibles; no cambiar retrospectivamente el objetivo para declararlo aprobado.

### N04 — Frecuencia de reporte

Durante 5 min quieto, registrar recepción de `/update/accepted` y obtener todos los intervalos: máximo ≤16 s, temporizador nominal 15 s. Luego medir 10 cambios eléctricos OUT contra recepción en nube: máximo ≤1 s. Una grabación de persona y pantalla mide detección humana + sensor + red, una métrica distinta de OUT→nube: identificar cuál se obtuvo.

Contar reportes periódicos y por evento. Comparar con 4/min nominales, explicar extras por movimiento, servo y reconexión; no usar ese conteo como factura total AWS.

### N05 — Reconexión y aplicación pendiente

Realizar 3 cortes de al menos 30 s (WiFi o salida a Internet), con alimentación de placa sostenida. Mientras está offline, mandar activación y cambio de modo por Alexa. Después restablecer conectividad y medir hasta comienzo del ciclo y convergencia. Objetivo ≤30 s, una ejecución del comando, sin reinicio manual. Verificar suspensión automática offline. Si se reinicia el ESP32 como ensayo adicional, considerar el calentamiento de 60 s del PIR por separado; el comando manual no necesita esperar calentamiento.

### N06 — Corte de energía y límites de deduplicación

Completar un ciclo, cortar/restaurar alimentación sin borrar NVS: no repetir el identificador. Repetir con corte durante ciclo; documentar que el servo vuelve al reposo al iniciar y no se garantiza completar el ciclo interrumpido. El intervalo entre guardar identificador y comenzar movimiento puede causar omisión: se acepta como límite documentado del prototipo, no como entrega exactly-once. Nunca ejecutar esta prueba con aerosol acoplado.

## Resultados locales ya ejecutados

2026-11-08, Windows, Python 3.14 local, boto3 1.43.126, PlatformIO 6.2.0:

- `python -B -m unittest discover -s tests -v`: **22 pruebas, OK**. Dobles de los clientes AWS, sin red ni acceso real a cuentas.
- `python -m platformio run -d firmware`: **SUCCESS**, ESP32 `esp32dev`, plataforma 6.9.0, PubSubClient 2.8, ArduinoJson 6.21.5, ESP32Servo 1.1.1. Compilación con plantilla ficticia, sin cargar firmware.
- Aviso de herramienta externa: esptool 4.5.1 emitió SyntaxWarning de Python 3.14 por `return` en `finally`; no impidió compilar. Para despliegue Python Lambda se propone 3.12/3.13; la ejecución real en ese runtime queda pendiente.

Estos resultados no aprueban por sí solos P01–P20/N01–N06. El backend cubre validaciones y ramas de contrato; los protocolos, hardware y lenguaje hablado requieren integración.

## Registro y criterio de cierre

Usar [resultados.csv](../evidencias/resultados.csv), [latencias.csv](../evidencias/latencias.csv) y [pir.csv](../evidencias/pir.csv). Las plantillas no contienen mediciones inventadas. Añadir evidencias con nombre `ID-fecha-descripcion` y actualizar las secciones 4–7 del informe.

El proyecto integrado estará validado cuando RF1–RF9, restricciones y umbrales declarados tengan resultado aprobado con evidencia; los fallos abiertos deben explicarse. Confirmar la excepción académica del automático. La demo debe incluir cambios de vínculo y no limitarse a un Thing fijo. Fotografías y aportes reales por integrante forman parte de la entrega.

Actualización con placa confirmada: compilación **SUCCESS** para `esp32doit-devkit-v1`, 30,50 s, RAM 46 556 bytes y flash 929 425 bytes. Región, cuenta, endpoint e ID de skill incorporados; las pruebas de integración continúan pendientes. Ver [registro local](../evidencias/verificacion-local.txt).
