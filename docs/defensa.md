# Referencia para la defensa y demostración

## Recorrido de demostración

1. Mostrar circuito, fuente de 5 V, tierras comunes y separación de alimentación del servo. Identificar PIR y SG90; explicar que el firmware representa fase y ángulo ordenado.
2. Mostrar `reported` reciente y la estabilización del PIR. Abrir la skill y demostrar usuario sin vínculo.
3. Vincular `thing`, salir y volver a entrar; enseñar persistencia en DynamoDB.
4. Preguntar movimiento, accionar manualmente y seguir `desired → delta → reported`.
5. Habilitar automático por voz, provocar flanco y explicar los 5 s de enfriamiento para pruebas; deshabilitar y verificar que movimiento ya no activa el servo.
6. Cambiar vínculo a otro Thing autorizado, mostrar aislamiento de usuarios, rechazar nombre inexistente y desvincular.
7. Cortar red con alimentación mantenida, solicitar comando, recuperar conexión y comprobar aplicación pendiente.
8. Presentar mediciones reales de estabilidad, clasificación, latencia y frecuencia. Terminar mostrando límites y mejoras.

## Preguntas y respuestas técnicas

**¿Por qué un Shadow?** Conserva estado deseado y reportado aunque la placa se desconecte. Al reconectar consulta desired pendiente. Alexa no necesita conocer la IP de la placa.

**¿Quién escribe cada parte?** Lambda escribe desired y consulta reported. ESP32 escribe reported. AWS calcula delta y asigna version. El ejemplo JSON no reemplaza los reportes reales.

**¿Por qué no basta `activar=true`?** Una segunda activación con el mismo valor no produce una diferencia. `activationId` cambia por solicitud y permite distinguir ciclos. `automatic` sí es booleano porque representa un modo duradero.

**¿Qué confirma el requestId reportado?** Que el controlador aceptó el comando y comenzó a tramitarlo; no una dosis medida. La fase y el contador informan progreso, pero el SG90 no tiene sensor de posición conectado al ESP32.

**¿Se garantiza exactamente una vez?** No. Se guarda el último identificador en NVS antes del movimiento para evitar repetición tras reinicio, pero un corte entre ambas acciones puede perder la pulsación. Es una decisión de evitar duplicaciones, con límite explícito. Tampoco se conserva un historial ilimitado de solicitudes.

**¿Puede el Shadow guardar diez órdenes pendientes?** El contrato actual admite una. Shadow representa estado, no cola; el backend avisa cuando hay una activación pendiente. Concurrencia se controla con version y relectura ante conflicto.

**¿Qué sucede si se corta WiFi?** Se suspende el automático y el ciclo ya iniciado termina. Se reintenta conexión cada 5 s y, tras TLS, se consulta el Shadow antes de operar. Las órdenes manuales pendientes se aplican al recuperar conexión. El reintento de conexión se ejecuta cada 5 s.

**¿Por qué NTP?** La validación temporal de certificados necesita reloj correcto, y `sampledAt` permite saber si la telemetría es reciente. No se deshabilita la verificación TLS.

**¿El PIR detecta presencia?** Detecta variaciones de radiación infrarroja asociadas a movimiento. Una persona quieta puede no activar la salida. El atributo se llama presence por el caso de uso, pero la respuesta de Alexa y la exactitud se interpretan como movimiento.

**¿Qué es exactitud en un sensor digital?** Error de clasificación contra ensayos físicos observados: falsos positivos y negativos. No se informa un error de distancia porque el PIR no mide distancia.

**¿Qué evita activaciones continuas?** Solo un flanco LOW→HIGH nuevo, servo libre, modo habilitado, conexión sincronizada y al menos 5 s desde el último ciclo. Mantener HIGH no genera eventos adicionales. Un flanco descartado durante enfriamiento no queda en cola.

**¿Desactivar el automático detiene el servo a mitad?** No; impide nuevos ciclos automáticos y deja volver al reposo al ciclo en curso. La activación manual sigue disponible.

**¿Cómo hay varios usuarios?** El userId viene de `context.System.user.userId`. Cada solicitud consulta la fila correspondiente y usa su thingName. No se obtiene de un slot arbitrario para actuar ni se fija `thing` en Lambda.

**¿Qué contiene DynamoDB?** Una fila por usuario con Thing y fecha. No es base de telemetría, no necesita índices secundarios ni Scan. Cambiar vínculo reemplaza la fila; eliminarla no altera el estado del dispositivo.

**¿Conocer el nombre acredita propiedad?** No. Es la simplificación mínima de la práctica. IAM restringe Things admitidos pero varios usuarios pueden compartir uno; producción necesita prueba de propiedad/código seguro.

**¿Qué diferencia existe entre política IoT y rol Lambda?** La primera autoriza el certificado y cliente MQTT a tópicos concretos; el segundo autoriza llamadas AWS desde Lambda a los Things/tabla permitidos. El disparador Alexa controla quién puede invocar la función y el código valida además el applicationId.

**¿Por qué reportar por evento y cada 15 s?** El evento ofrece rapidez en movimiento; el respaldo permite saber que la muestra es reciente y reparar pérdidas de publicaciones QoS 0. Tiene un costo: 240 reportes/hora en reposo, más operaciones y tráfico asociado.

**¿Por qué clases si se pide sencillez?** La consigna exige POO. Una clase propia por ejecutable agrupa estado y operaciones sin jerarquías, fábricas ni archivos innecesarios.

**¿Cómo ampliar?** Añadir atributos a reported para otro sensor y desired/reported para otro control, más intents y lectura GPIO. Conservar transporte, vínculo y políticas por Thing; revisar permisos y tamaño del documento al ampliar.

**¿Cómo se invoca la skill?** Es una skill Custom, así que se abre con «Alexa, abre ambientador inteligente» o se incluye su invocación en la frase. El flujo demostrado usa ese modelo en el simulador.

**¿Qué aporta el modo automático?** Es una extensión pedida por el usuario: además del control por voz, un flanco del PIR dispara un ciclo cuando el modo está habilitado. Se documenta junto con el control por voz y se puede demostrar activándolo y desactivándolo desde la skill.

## Cómo exponer los resultados

Presentar cada afirmación junto con su evidencia: el barrido PIR de 0–50 cm, las capturas AL01 del simulador, el registro EP01 con los ciclos y los reportes aceptados, y la reconexión documentada en R01. Al describir el servo, explicar que `servoAngle` corresponde al ángulo ordenado y que la ejecución se comprueba con la fase reportada y la observación del montaje.

Cada integrante debe poder seguir `handle → GetItem → command → UpdateThingShadow` y `onMessage → applyDesired → startCycle → report`, explicar el circuito y aportar commits propios. No inventar historial ni repartir respuestas memorizadas sin conocer el sistema completo.

## Evidencia de ejecución y pruebas actualizadas

EP01 contiene 11 ciclos completos y una ventana de 15 min 42,995 s desde la primera muestra lista, sin reinicios. Se realizó además una sesión de 15 minutos con el ESP32 en funcionamiento y 15 mediciones de respuesta; consultar los resultados en [informe.md](informe.md) y [resultados.csv](../evidencias/resultados.csv).

La respuesta del PIR se documenta con el barrido de 0–50 cm y el contexto del registro HIGH ante la mano y LOW frente a una pared estática en [pir-rango-0-50cm.md](../evidencias/pir-rango-0-50cm.md). El video confirma el cooldown físico de prueba de 5 s; para producción se propone 60 s para reducir desperdicio. Ver [análisis EP01](../evidencias/ejecucion-prolongada.md) y [pruebas en vivo de Alexa](../evidencias/pruebas-alexa-vivo.md).
