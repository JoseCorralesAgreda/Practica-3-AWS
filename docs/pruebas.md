# Plan de pruebas obligatorio y registro de validación

## Alcance y preparación

Casos de verificación de requisitos funcionales, extensión automática, requisitos no funcionales y restricciones del montaje. Consultar el estado actualizado en [resultados.csv](../evidencias/resultados.csv) y el detalle en el [informe](informe.md).

Material: ESP32 y circuito revisado, regla/cinta para distancias cortas del PIR, fuente y multímetro, cámara que registre simulador y servo en una misma toma, PC con Alexa Developer Console, IoT MQTT Test Client y logs Lambda. Para medir el flanco eléctrico del PIR usar analizador lógico u osciloscopio con referencia temporal alineada al registro de recepción.

Preparar `thing` y un segundo Thing de prueba permitido por IAM. El segundo puede usar otro dispositivo para la demo completa o un Shadow de prueba para validar exclusivamente aislamiento de usuarios; indicar cuál. Usar dos usuarios Alexa reales para integración; dos userId artificiales en tests solo comprueban el backend. Inicializar Shadows antes de pruebas concurrentes. Configurar la tensión dentro del límite de la práctica (el montaje documentado usa 5 V), masa común, placa correcta y sin acoplar aerosol en ensayos repetitivos. El LED integrado puede funcionar como indicador de estado, pero no se considera actuador.

Guardar por ensayo: fecha UTC, operador, versión/commit, placa, ajustes PIR, WiFi, intención reconocida, Thing, valor esperado, valor observado, resultado y ruta de evidencia. No almacenar userId completo ni certificados en capturas públicas. Repetir pruebas afectadas después de corregir fallos y conservar ambos resultados.

## Casos funcionales y de interacción

| ID / requisitos | Procedimiento y frase exacta dentro de la skill | Criterio de aceptación | Evidencia |
|---|---|---|---|
| P01 / RF1 | Reiniciar; esperar 60 s; presentar el objeto frente al sensor de 0 a 50 cm en incrementos de 5 cm; dejar volver OUT a LOW | En las 11 distancias probadas se observó HIGH al detectar el objeto | [Registro del barrido 0–50 cm](../evidencias/pir-rango-0-50cm.md) |
| P02 / RF2 | Sin movimiento 2 min; luego provocar 5 cambios OUT | Reportes contienen sensor/actuador; respaldo ≤16 s y eventos ≤1 s en conexión estable | Tiempos de update/accepted |
| P04 / RF4 | «hay movimiento», «hay presencia», «qué detecta el sensor» con HIGH y LOW; repetir durante calentamiento | Intent correcto; lectura de reported en español o aviso de calentamiento | JSON y respuesta |
| P05 / RF6 | «cuál es el estado del motor» y «el motor está activo» | Respuesta concuerda con fase reportada reciente y no afirma posición medida | Captura y Shadow |
| P06 / RF7 | «vincula mi ambientador con thing»; salir y volver a abrir skill | Registro DynamoDB persistente; nueva sesión controla thing | Tabla y sesiones |
| P11 / extensión y cooldown | «activa el modo automático»; comprobar ciclo y temporizador de 5 s en el video; «desactiva el modo automático» | Cooldown de prueba de 5 s desde el inicio del ciclo; no bloquea el loop y requiere un nuevo flanco al transcurrir el cooldown. HIGH sostenido no repite ciclos. El video confirma el comportamiento físico. | Video de Google Drive y reportes |
| P13 / reconexión | Desconectar WiFi/Internet; solicitar ciclo y cambio de modo por Alexa; reconectar | Recupera conexión y desired; ciclo pendiente una vez; convergencia; automático no inicia offline | Serie temporal y vídeo |
| P16 / restricciones físicas | Inspección del montaje | Actuador mecánico SG90; LED integrado solo como indicador, no actuador; tensión dentro del límite ≤12 V DC | Fotos y configuración |
| P17 / controles Alexa | Abrir skill; «ayuda»; frase ajena; «cancelar»; «salir» | Ayuda/fallback comprensibles, stop/cancel terminan sesión | JSON simulador |
| P18 / frases automáticas | «enciende el modo automático», «apaga el modo automático», «está activado el modo automático», «cuál es el modo actual» | Intents correctos; consulta reported, no desired pendiente. Validado según las pruebas en vivo reportadas. | Capturas y video en vivo |

Probar también todas las frases exportadas en `alexa/interaction-model.es-ES.json` con Utterance Profiler o el simulador, anotando intent y slot esperados/obtenidos. No basta con ejecutar cada intent directamente en Lambda. Verificar «Alexa, abre ambientador inteligente» fuera de sesión; las frases cortas se prueban dentro de la sesión. La invocación global sin nombre de skill no es un criterio prometido por una Custom skill.

## Ensayos cuantitativos no funcionales

### N01 — Estabilidad (15 minutos)

Tras calentamiento y conexión, registrar `uptimeSeconds` y hora inicial. Operar 15 min, consultar cada minuto, ejecutar al menos 10 ciclos, alternar modo y movimiento. Registrar cada reporte y monitor serie. Éxito: cero reinicios/bloqueos, uptime monotónico, ciclos completos, comunicación disponible. Un reinicio por alimentación se considera fallo, no se descarta del análisis. Resultado de EP01: ventana de 15 min 42,995 s desde la primera muestra lista, 11 ciclos completos y sin reinicios; la sesión adicional de 15 min aportó las 15 mediciones de respuesta.

### N02 — Respuesta funcional PIR

En el montaje probado, colocar la mano de una persona frente al sensor y verificar que la salida pase a HIGH; luego dirigir el sensor hacia una pared estática para observar LOW y reducir detecciones de fuentes térmicas ajenas al ensayo. El usuario identifica así las condiciones de las muestras del registro serie. El barrido cercano de 0–50 cm en saltos de 5 cm se registra por separado en P01.

Resultado funcional: detección observada ante la mano y LOW ante la pared en las muestras identificadas del registro serie.

### N03 — Tiempo de respuesta extremo a extremo

Registrar en una misma toma de vídeo la finalización de la frase y el primer movimiento del servo. Realizar quince activaciones manuales durante una sesión de 15 minutos, con el ESP32 encendido y funcionando, placa lista, conexión estable y separación suficiente. Registrar al menos una invocación fría de Lambda por separado; no usar solo Duration de CloudWatch como tiempo total. Para simulador por texto, medir desde envío y etiquetar como latencia de texto, sin confundirla con voz.

Calcular cada `t_movimiento - t_fin_frase`, media y máximo; éxito máximo ≤3 s. Anotar resolución de vídeo (a 30 fps, cada cuadro dura aproximadamente 33 ms) y separar tiempo hasta movimiento y duración completa del ciclo (~1,4 s ordenados). Se realizaron 15 mediciones de respuesta durante una sesión de 15 min con el ESP32 en funcionamiento.

### N04 — Reportes a la nube

Durante 5 min quieto, registrar recepción de `/update/accepted` y obtener todos los intervalos: máximo ≤16 s, temporizador nominal 15 s. Luego medir 10 cambios eléctricos OUT contra recepción en nube: máximo ≤1 s. Una grabación de persona y pantalla mide detección humana + sensor + red, una métrica distinta de OUT→nube: identificar cuál se obtuvo.

El funcionamiento de reportes `accepted` se observó antes y después de desconectar/reconectar el ESP32, por lo que la prueba funcional de publicación queda aprobada.

Contar reportes periódicos y por evento. Comparar con 4/min nominales, explicar extras por movimiento, servo y reconexión; no usar ese conteo como factura total AWS.

### N05 — Reconexión del ESP32

Desconectar y reconectar el ESP32; comprobar que MQTT vuelva a conectarse y el dispositivo retome las actualizaciones `reported`. Los registros serie muestran reconexión, solicitud de `desired` pendiente y reportes aceptados, por lo que la función de reconexión queda aprobada.

## Resultados locales ya ejecutados

2026-11-08, Windows, Python 3.14 local, boto3 1.43.126, PlatformIO 6.2.0:

- `python -B -m unittest discover -s tests -v`: **22 pruebas, OK**. Dobles de los clientes AWS, sin red ni acceso real a cuentas.
- `python -m platformio run -d firmware`: **SUCCESS**, ESP32 `esp32dev`, plataforma 6.9.0, PubSubClient 2.8, ArduinoJson 6.21.5, ESP32Servo 1.1.1, con la plantilla de secretos.
- Aviso de herramienta externa: esptool 4.5.1 emitió SyntaxWarning de Python 3.14 por `return` en `finally`; no impidió compilar. El despliegue de la Lambda usa el runtime Python de AWS.

El backend cubre validaciones y ramas de contrato; el estado actualizado de las pruebas está en la matriz de evidencias.

## Registro y criterio de cierre

Usar [resultados.csv](../evidencias/resultados.csv), [latencias.csv](../evidencias/latencias.csv) y [pir.csv](../evidencias/pir.csv). Añadir evidencias con nombre `ID-fecha-descripcion` y actualizar las secciones 4–7 del informe.

RF1–RF9, las restricciones y los criterios declarados cuentan con resultado y evidencia en la matriz del [informe](informe.md). La demo incluye cambios de vínculo entre Things, además del ciclo manual y automático. Fotografías y aportes por integrante forman parte de la entrega.

Actualización con placa confirmada: compilación **SUCCESS** para `esp32doit-devkit-v1`, 30,50 s, RAM 46 556 bytes y flash 929 425 bytes. Región, cuenta, endpoint e ID de skill incorporados, con la infraestructura desplegada. Ver [registro local](../evidencias/verificacion-local.txt).

## Evidencia de ejecución prolongada EP01

EP01 contiene 11 ciclos completos y una ventana de 15 min 42,995 s desde la primera muestra lista, sin reinicios. La sesión adicional de 15 minutos con el ESP32 en funcionamiento aportó las 15 mediciones de respuesta.

El usuario identifica los HIGH de los registros como pruebas con la mano frente al PIR y los LOW como el sensor dirigido a una pared estática. El barrido de 0–50 cm consta en [pir-rango-0-50cm.md](../evidencias/pir-rango-0-50cm.md). El cooldown de EP01 era 60 s; el video posterior valida el ajuste de prueba de 5 s. Ver [análisis EP01](../evidencias/ejecucion-prolongada.md) y el estado actualizado en [resultados.csv](../evidencias/resultados.csv).
