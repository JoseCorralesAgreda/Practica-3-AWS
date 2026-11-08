# Configuración y montaje

## 1. Datos y decisiones pendientes

Datos confirmados por el usuario:

| Dato | Valor |
|---|---|
| Placa PlatformIO | `esp32doit-devkit-v1` (DOIT ESP32 DEVKIT V1) |
| Región indicada | `us-east-2` |
| Cuenta AWS | `443972183454` |
| Thing ARN | `arn:aws:iot:us-east-2:443972183454:thing/thing` |
| Endpoint IoT ATS | `a2krhgw96q3m1o-ats.iot.us-east-2.amazonaws.com` |
| ID de skill | `amzn1.ask.skill.8f29b895-fb91-4340-9bad-077860e12778` |
| Tabla propuesta | `AmbientadorVinculaciones` |
| Función Lambda | `Alexa` |
| ARN de Lambda | `arn:aws:lambda:us-east-2:443972183454:function:Alexa` |

El ARN confirma que Lambda e IoT están en `us-east-2`, cuenta `443972183454`. Crear la tabla DynamoDB en esa misma región. La política del rol ya incluye el grupo de logs `/aws/lambda/Alexa`. Calibrar los ángulos del SG90 y confirmar aceptación académica del automático. WiFi, certificado y clave privada se completan localmente en `secrets.h`; no enviarlos por chat.

IoT y Lambda pueden tener regiones diferentes: `IOT_REGION` selecciona IoT; DynamoDB está en la región de Lambda. La documentación actual de Alexa admite US East (Ohio), `us-east-2`, para Lambda de skills Custom: no es necesario trasladar la función únicamente por esa región. Ver [regiones admitidas por Alexa](https://developer.amazon.com/en-US/docs/alexa/custom-skills/host-a-custom-skill-as-an-aws-lambda-function.html).

## 2. Conexiones

| Componente | Pin | Conexión |
|---|---|---|
| ESP32 | USB | Alimentación y programación desde PC |
| PIR HC-SR501 | VCC | Fuente regulada de 5 V, según la ficha del módulo concreto |
| PIR HC-SR501 | OUT | GPIO 27; confirmar nivel alto compatible con 3,3 V |
| PIR HC-SR501 | GND | Tierra común |
| SG90 | Señal, normalmente naranja | GPIO 18 |
| SG90 | Positivo, normalmente rojo | Fuente externa regulada de 5 V compatible con el ejemplar |
| SG90 | GND, normalmente marrón | Tierra común con ESP32 y PIR |

Verificar las etiquetas: el orden de pines del PIR varía entre módulos. No alimentar el servo desde 3V3 ni desde un GPIO. Utilizar una fuente con margen suficiente para el pico de arranque/bloqueo (como punto inicial, 5 V / 1 A para un SG90; verificar el consumo del ejemplar). Un condensador de 470 µF entre 5 V y GND cerca del servo ayuda ante transitorios, respetando polaridad. No unir el positivo de la fuente externa con el USB/5V del ESP32 en este montaje; unir únicamente las tierras y las señales. Todo funciona a baja tensión, sin conmutar red eléctrica.

Calibrar primero sin brazo acoplado al pulsador. `REST_ANGLE`, `PRESS_ANGLE` y `SERVO_PHASE_MS` están al inicio de `main.cpp`. El intervalo PWM de 500–2400 µs es configurable y no garantiza que todos los clones SG90 admitan los extremos sin forzarse. El requisito de servo de 180° describe su capacidad; el mecanismo real puede necesitar menos recorrido.

Ajustar PIR a retardo corto y anotar posición del jumper H/L y sensibilidad. Esperar 60 s desde el arranque; exigir retorno a LOW antes de una nueva prueba. Un nivel HIGH mantenido no produce ciclos sucesivos; un flanco durante el enfriamiento se descarta, no se encola.

## 3. AWS IoT Core (Thing existente: thing)

1. En la región del Thing, obtener el endpoint **iot:Data-ATS**. El firmware usa solo el hostname; Lambda usa `https://` seguido del mismo hostname.
2. Verificar certificado X.509 activo, asociado al Thing y a una política IoT. Descargar o ubicar certificado y clave privada de forma local. La clave privada no se puede recuperar desde IoT si se perdió; en ese caso crear un certificado nuevo.
3. La región y cuenta ya están incorporadas en [iot-policy.template.json](../infra/iot-policy.template.json). La plantilla limita cliente y tópicos a `thing`. Crear o actualizar la política y asociarla al certificado. Para otro dispositivo, generar política y certificado propios con su nombre; no compartir certificado entre placas.
4. Copiar [secrets.example.h](../firmware/include/secrets.example.h) a `secrets.h`; completar WiFi 2,4 GHz, hostname ATS, nombre del Thing, Amazon Root CA 1, certificado y clave privada completos. Mantener las cabeceras PEM reales. No usar `setInsecure()`.
5. Crear el Shadow **clásico/sin nombre** con el contenido de [shadow-initial.json](../infra/shadow-initial.json), o dejar que lo cree el primer reporte. No cargar `shadow.example.json` como inicial: contiene telemetría ilustrativa y un comando de ejemplo.
6. Permitir salida a MQTT TLS 8883 y NTP UDP 123. Un reloj sin sincronizar impide iniciar TLS. En redes institucionales pueden estar bloqueados.
7. Compilar, cargar por USB y abrir monitor a 115200:

```powershell
python -m platformio run -d firmware
python -m platformio run -d firmware -t upload
python -m platformio device monitor -d firmware
```

El perfil ya corresponde a la placa confirmada: DOIT ESP32 DEVKIT V1. En IoT MQTT Test Client observar `$aws/things/thing/shadow/#`; la consola usa permisos del operador, distintos a la política del dispositivo. No editar manualmente `reported` para simular que actuó el hardware.

## 4. Tabla DynamoDB

Crear `AmbientadorVinculaciones` en la región de Lambda. Clave de partición `userId` tipo String; **sin clave de ordenación**. No crear `thingName` ni `fechaVinculacion` como claves o índices. Usar capacidad bajo demanda según la plantilla; no implica costo cero.

Definición lista para AWS CLI, si se dispone de una sesión AWS autorizada:

```powershell
aws dynamodb create-table --cli-input-json file://infra/dynamodb-table.json --region us-east-2
```

Esperar estado ACTIVE. Un registro será `{userId, thingName, fechaVinculacion}`. `PutItem` reemplaza la vinculación del mismo usuario, `GetItem` la lee de forma consistente y `DeleteItem` la elimina. No hace falta Scan, Query, GSI ni almacenar sensor/historial en la tabla.

No se impone exclusividad de propietario: dos usuarios pueden vincular el mismo Thing si conocen su nombre y está autorizado en IAM. Es una simplificación académica explícita, no una prueba de propiedad. Una versión de producción necesitaría vinculación con código secreto temporal o account linking.

## 5. Lambda existente

1. Usar runtime Python 3.12 o 3.13 y handler `lambda_function.lambda_handler`. El archivo [lambda_function.py](../backend/lambda_function.py) va en la raíz del editor o ZIP. Boto3 está disponible en el runtime; las dependencias locales sirven para las pruebas.
2. Configurar 128 MB y timeout 8 s como punto inicial; medir latencia y ajustar si hiciera falta. No incorporar la Lambda a una VPC sin salida a los servicios AWS.
3. Aplicar las cuatro variables ya completadas de [environment.example.json](../backend/environment.example.json). `IOT_REGION` puede diferir de la región de Lambda; la tabla permanece en esta última.
4. Adjuntar al rol la política [lambda-role-policy.template.json](../infra/lambda-role-policy.template.json) ya completada para la cuenta `443972183454`, región `us-east-2` y función `Alexa`. El trust policy está en [lambda-trust-policy.json](../infra/lambda-trust-policy.json). La lista de recursos IoT autoriza `thing` y `ambientador-dos` para la demostración; agregar explícitamente los Things admitidos. El código no tiene un Thing fijo.
5. Configurar el disparador **Alexa Skills Kit**, habilitando verificación del ID exacto de skill. Ese ID debe coincidir con `ALEXA_SKILL_ID`. El código valida además `context.System.application.applicationId` antes de acceder a datos.
6. Guardar y desplegar el código. Revisar CloudWatch ante fallos; no registrar eventos completos de Alexa ni secretos.

Un ZIP puede prepararse con:

```powershell
Compress-Archive -LiteralPath backend/lambda_function.py -DestinationPath backend/lambda.zip -Force
```

La función solo necesita DescribeThing, GetThingShadow, UpdateThingShadow, GetItem, PutItem, DeleteItem y logs. No requiere Publish MQTT, Scan de DynamoDB, crear Things ni eliminar Shadows. Los permisos de creación/configuración corresponden al operador, no al rol de ejecución.

## 6. Alexa Developer Console

1. Crear skill **Custom**, idioma **Español (ES)** y backend propio. Importar [interaction-model.es-ES.json](../alexa/interaction-model.es-ES.json) en JSON Editor. Guardar y Build Model.
2. Configurar Endpoint → AWS Lambda ARN → Default Region con `arn:aws:lambda:us-east-2:443972183454:function:Alexa`. En la función `Alexa`, comprobar el disparador Alexa Skills Kit con verificación habilitada para `amzn1.ask.skill.8f29b895-fb91-4340-9bad-077860e12778`. Si existen endpoints geográficos adicionales, revisar que no dirijan las pruebas a otra función.
3. Poner Test en Development y usar el simulador es-ES. No hace falta publicar la skill para la práctica.
4. «Alexa, abre ambientador inteligente». Dentro de la sesión: «vincula mi ambientador con thing», «activa el ambientador», «activa el modo automático» y «desactiva el modo automático».
5. Fuera de sesión, usar una invocación completa como «Alexa, dile a ambientador inteligente que active el ambientador» y comprobar cómo la reconoce el simulador. La frase global «Alexa, activa el ambientador» no está garantizada por una skill Custom sin invocación; no es una skill Smart Home.
6. Para otros nombres, agregar valores/sinónimos al slot `THING_NAME` y reconstruir el modelo. El tipo personalizado no sustituye la validación en AWS. Evitar normalizar nombres arbitrarios a minúsculas: IoT distingue mayúsculas y minúsculas.
7. Verificar los intents y slots reconocidos en el JSON del simulador; los tests Python no prueban reconocimiento de lenguaje natural.

## 7. Diagnóstico

| Síntoma | Revisar |
|---|---|
| No conecta WiFi | SSID 2,4 GHz, contraseña y alcance |
| No inicia MQTT | NTP, endpoint ATS, certificados completos, puerto 8883, cliente igual a Thing |
| MQTT conecta pero no hay Shadow | Permisos topic/topicfilter, suscripciones, Shadow clásico |
| Alexa informa error de servicio | Región, tabla ACTIVE, políticas y logs de Lambda |
| Alexa no entiende thing | Ver slot reconocido, usar sinónimo o añadir uno adecuado |
| Servo reinicia ESP32 | Fuente, masa común, caída de tensión y bloqueo mecánico |
| PIR no vuelve a activar | Retardo del módulo, LOW previo, 60 s de enfriamiento y conexión |
| Consulta indica datos viejos | `sampledAt`, NTP, reportes, más de 45 s sin datos |

Al desconectar Internet, no se inician ciclos automáticos; el ciclo ya iniciado termina. Un comando manual pendiente permanece en desired y se aplica al reconectar. Desvincular al usuario no borra el Shadow ni desactiva el modo automático del dispositivo. Antes de desarmar, desactivar el modo y comprobar `reported.automatic=false`.

## Fuentes de configuración

- [Tópicos reservados del Shadow](https://docs.aws.amazon.com/iot/latest/developerguide/device-shadow-mqtt.html).
- [Versiones y sincronización](https://docs.aws.amazon.com/iot/latest/developerguide/device-shadow-data-flow.html).
- [Invocación de skills personalizadas](https://developer.amazon.com/en-US/docs/alexa/custom-skills/understanding-how-users-invoke-custom-skills.html).
- [Validación de solicitudes Alexa](https://developer.amazon.com/en-US/docs/alexa/custom-skills/handle-requests-sent-by-alexa.html).
- [CreateTable de DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_CreateTable.html).
- [Guía PIR de Adafruit](https://learn.adafruit.com/pir-passive-infrared-proximity-motion-sensor?view=all): orientativa; confirmar ficha del módulo HC-SR501 comprado.
