# Reconexión MQTT — evidencia R01

Extracto de registro serie compartido por el usuario el 2026-11-10.

```text
QTT no conectado: -2
MQTT conectado; solicitando desired pendiente.
Shadow: actualizacion de reported aceptada por AWS.
Shadow: actualizacion de reported aceptada por AWS.
PIR t=15894 ms GPIO27=LOW listo=0 servo=idle automatico=1
```

## Qué demuestra el extracto

- El cliente registró un estado de desconexión (`-2`) y luego informó que MQTT se conectó de nuevo.
- Tras reconectar, el firmware indicó que solicitaba el `desired` pendiente.
- Se registraron dos aceptaciones de actualizaciones `reported` por AWS.
- La última línea muestra el estado local en `t=15894 ms`: PIR LOW y todavía no listo, servo idle y modo automático activo.

## Alcance

Esto respalda la reconexión MQTT y la reanudación funcional de reportes; junto con la desconexión y reconexión del ESP32, la prueba funcional de reconexión queda **completada**. El extracto registra además la solicitud del `desired` pendiente al recuperar la sesión, que el firmware aplica tras el `get` al Shadow.
