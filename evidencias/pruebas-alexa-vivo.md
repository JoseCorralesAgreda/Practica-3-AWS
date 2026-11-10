# Pruebas en vivo de Alexa — AL01

Capturas del simulador Alexa Developer Console compartidas por el usuario el 2026-11-10, junto con extractos serie del ESP32. Los archivos de imagen se guardan en esta carpeta. En tres capturas se ocultó el panel de entrada JSON para no divulgar el identificador de cuenta mostrado allí; se conservaron el diálogo del simulador y su respuesta.

## Resultados observados

| Evidencia | Entrada o acción | Resultado visible |
|---|---|---|
| [AL01 — abrir la skill](alexa-01-inicio-skill.png) | «abre ambientador inteligente» | La skill responde con las funciones disponibles. |
| [AL02 — activar motor](alexa-02-activar-motor.png) | «mueve el motor» | Alexa confirma que envió la activación y que la aplicará al reconectarse si el dispositivo está desconectado. El registro serie adicional muestra un ciclo del servo. |
| [AL03 — desactivar automático](alexa-03-desactivar-automatico.png) | «desactiva modo automático» | Alexa confirma la solicitud de desactivación. El registro serie adicional posteriormente muestra `automatico=0`. |
| [AL04 — consultar presencia con movimiento](alexa-04-consultar-presencia-movimiento.png) | «hay presencia» | Responde que la última lectura detectó movimiento y aclara que el PIR no confirma una persona inmóvil. |
| [AL05 — consultar presencia sin movimiento](alexa-05-consultar-presencia-sin-movimiento.png) | «hay presencia» | Responde que la última lectura no detectó movimiento y aclara el límite del PIR. |
| [AL06 — consultar motor](alexa-06-consultar-estado-motor.png) | «cuál es el estado del motor» | Informa motor en reposo y aclara que el servo no tiene realimentación de posición. |
| [AL07 — consultar modo automático](alexa-07-consultar-modo-automatico.png) | «está activado el modo automático» | Informa que el modo reportado está desactivado. |
| [AL08 — activar automático](alexa-08-activar-automatico.png) | «activa el modo automático» | Alexa confirma la solicitud y advierte que se aplicará al reconectarse si está desconectado. El registro serie adicional muestra `automatico=1` antes y después del tramo desactivado. |

**VincularIntent** se probó con un Thing y se registra como completado; la persistencia en DynamoDB se verificó en la infraestructura desplegada. La frase de vinculación que aparece en AL03 forma parte de la ayuda contextual.

## Registro serie relacionado

Fragmento adicional del registro serie proporcionado por el usuario:

```text
PIR t=303634 ms GPIO27=LOW listo=1 servo=idle automatico=1
Shadow: actualizacion de reported aceptada por AWS.
Servo: angulo ordenado=180 grados (presion); LED encendido
Inicio ciclo: 313945 ms
Shadow: actualizacion de reported aceptada por AWS.
Servo: angulo ordenado=0 grados (retorno); LED encendido
Shadow: actualizacion de reported aceptada por AWS.
Servo: ciclo terminado, angulo ordenado=0 grados; LED apagado
PIR t=363646 ms GPIO27=LOW listo=1 servo=idle automatico=1
Shadow: actualizacion de reported aceptada por AWS.
PIR t=378648 ms GPIO27=LOW listo=1 servo=idle automatico=1
Shadow: actualizacion de reported aceptada por AWS.
PIR t=393652 ms GPIO27=LOW listo=1 servo=idle automatico=0
Shadow: actualizacion de reported aceptada por AWS.
PIR t=446472 ms GPIO27=LOW listo=1 servo=idle automatico=0
Shadow: actualizacion de reported aceptada por AWS.
PIR t=452836 ms GPIO27=HIGH listo=1 servo=idle automatico=0
Shadow: actualizacion de reported aceptada por AWS.
PIR t=455426 ms GPIO27=LOW listo=1 servo=idle automatico=0
PIR t=470430 ms GPIO27=LOW listo=1 servo=idle automatico=0
Shadow: actualizacion de reported aceptada por AWS.
PIR t=485434 ms GPIO27=LOW listo=1 servo=idle automatico=0
Shadow: actualizacion de reported aceptada por AWS.
PIR t=545444 ms GPIO27=LOW listo=1 servo=idle automatico=0
Shadow: actualizacion de reported aceptada por AWS.
PIR t=560448 ms GPIO27=LOW listo=1 servo=idle automatico=0
Shadow: actualizacion de reported aceptada por AWS.
Shadow: actualizacion de reported aceptada por AWS.
PIR t=575451 ms GPIO27=LOW listo=1 servo=idle automatico=1
```

El extracto registra un ciclo de servo, reportes aceptados y cambios observados de `automatico=1` a `0` y luego `1`. Mientras el modo aparece desactivado se observa un HIGH del PIR, sin ciclo asociado en el fragmento, lo que respalda el efecto del modo sobre la activación automática.

## Estado de cobertura

- **Completado con capturas:** abrir la skill, activar motor (una ejecución observada), consultar sensor con ambas respuestas, consultar estado del motor y activar/desactivar/consultar el modo automático.
- **Vinculación:** completada con un Thing; la persistencia se verificó en DynamoDB.
- Las frases del modo automático se probaron y el [video compartido](https://drive.google.com/drive/folders/1d_Hg945M0cD-lJ1bk0L4BZTwfwMi8PAt?usp=sharing) valida físicamente el cooldown de 5 s. Para producción se propone un cooldown de 60 s para reducir el desperdicio de fragancia. Las 15 mediciones de respuesta se realizaron durante una sesión de 15 min.
