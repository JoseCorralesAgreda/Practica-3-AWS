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

**¿Qué sucede si se corta WiFi?** Se suspende el automático y el ciclo ya iniciado termina. Se reintenta conexión cada 5 s y, tras TLS, se consulta el Shadow antes de operar. Las órdenes manuales pendientes se aplican al recuperar conexión. Los timeouts hacen que 5 s sea un intervalo de reintento, no una garantía de recuperación completa.

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

**¿Por qué no siempre funciona «Alexa, activa el ambientador» desde fuera?** Es una skill Custom; requiere abrirla o incluir su invocación. La integración Smart Home tiene otro modelo y no se implementa aquí. Mostrar el flujo que realmente reconoce el simulador.

**¿Cumple la consigna el automático?** Es una extensión pedida por el usuario que difiere de la frase de control únicamente por voz. Debe explicarse y acordarse, no ocultarse. Los RF básicos se pueden demostrar con modo desactivado.

## Qué no afirmar sin evidencia

No afirmar 3 s de latencia por haber fijado timers, 90 % de exactitud sin ensayos, posición real por `servo.write`, ausencia de personas por PIR LOW, operación completa por un test unitario, ni despliegue exitoso porque existen plantillas. Mostrar qué se midió, cómo y bajo qué condiciones.

Cada integrante debe poder seguir `handle → GetItem → command → UpdateThingShadow` y `onMessage → applyDesired → startCycle → report`, explicar el circuito y aportar commits propios. No inventar historial ni repartir respuestas memorizadas sin conocer el sistema completo.

## Evidencia de ejecucion prolongada EP01 (incorporada 2026-11-09)

El registro serie aportado por el usuario abarca 16 min 50,079 s desde arranque: 11 ciclos iniciados y terminados declarados, ocho tras calentamiento. Desde la primera muestra lista hasta la ultima hay 15 min 42,995 s sin reinicios visibles. N01 queda PARCIAL: faltan diez ciclos tras calentamiento, consultas por minuto, alternancia de modo y uptimeSeconds.

Siete HIGH listos coinciden con inicio de ciclo; otro HIGH a 431618 ms no activa, solo 14,727 s despues del ciclo anterior, compatible con cooldown. Hay conexion MQTT y confirmaciones repetidas de reported aceptado. P01/P02/P03/P11/N04 reciben evidencia parcial. No hay referencia fisica para exactitud, tiempos de solicitud/movimiento para latencia ni timestamps de accepted para frecuencia de nube. No se valida Alexa, recuperacion o posicion mecanica.

La fecha de ejecucion y el binario no fueron informados. Los mensajes de angulo/LED no existen en el firmware local: identificar la version cargada y revisar la restriccion P16 sobre LED funcional. Ver [analisis, cobertura y limites](../evidencias/ejecucion-prolongada.md) y sus CSV. No se cambiaron los criterios originales ni el firmware.
