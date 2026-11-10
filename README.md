# Ambientador inteligente — Práctica 3

Ambientador controlado por una skill personalizada de Alexa, con ESP32, PIR HC-SR501 y servomotor SG90 de 180°. Alexa usa una Lambda Python que modifica el Shadow clásico; el ESP32 se conecta mediante MQTT/TLS. DynamoDB conserva la vinculación de cada usuario con su propio Thing.

## Archivos principales

- [Firmware PlatformIO](firmware/src/main.cpp): una clase `Ambientador`, sensor, servo, Shadow y reconexión.
- [Lambda Python](backend/lambda_function.py): una clase `AmbientadorSkill`, vinculación, consultas y comandos.
- [Modelo de Alexa es-ES](alexa/interaction-model.es-ES.json), importable desde JSON Editor.
- [Configuración y montaje](docs/configuracion.md): datos del despliegue, conexiones y configuración de AWS y Alexa.
- [Informe técnico](docs/informe.md): las ocho secciones exigidas, contrato Shadow, diagramas y resultados.
- [Plan de pruebas](docs/pruebas.md): criterios medibles, procedimientos y registro de evidencias.
- [Guía de defensa](docs/defensa.md): decisiones, límites y recorrido de demostración.
- [Configuraciones AWS](infra/): tabla, políticas y ejemplos de Shadow.

## Comportamiento

1. Abrir «ambientador inteligente» y decir «vincula mi ambientador con thing».
2. «Activa el ambientador»: solicita un ciclo 0° → 180° → 0° (700 ms por fase).
3. «Activa el modo automático»: permite un ciclo ante un nuevo flanco de movimiento del PIR, con separación mínima de 5 s (configuración de pruebas) desde el último ciclo. Requiere conexión y sincronización con el Shadow.
4. «Desactiva el modo automático»: impide nuevos ciclos por PIR; deja terminar el ciclo en curso.
5. «Hay movimiento», «cuál es el estado del motor» y «está activado el modo automático» consultan `reported`.
6. «Cambia mi ambientador a ambientador dos» reemplaza la vinculación, si ese Thing existe y está autorizado; «desvincula mi ambientador» la elimina.

El modo automático es una extensión solicitada por el usuario. Arranca desactivado y se recupera el valor deseado al conectar. La dosificación se calibra acoplando el mecanismo al pulsador.

## Verificación local

Desde la raíz, con Python y PlatformIO instalados:

```powershell
python -m pip install -r backend/requirements-dev.txt platformio
python -B -m unittest discover -s tests -v
Copy-Item firmware/include/secrets.example.h firmware/include/secrets.h
python -m platformio run -d firmware
```

No sobrescribir un `secrets.h` ya configurado. La plantilla permite compilar pero no conectarse. En esta carpeta se preparó también `.venv`; se puede sustituir `python` por `.\.venv\Scripts\python.exe`.

## Estado de entrega

Proyecto desplegado y en operación. Placa confirmada: DOIT ESP32 DEVKIT V1 (`esp32doit-devkit-v1`). Región `us-east-2`, cuenta, endpoint IoT ATS e ID de skill configurados. Lambda `Alexa`, ARN `arn:aws:lambda:us-east-2:679937333206:function:Alexa`, con permiso de logs y disparador Alexa Skills Kit. Infraestructura desplegada en AWS y vinculación Lambda–DynamoDB verificada. La skill responde en el simulador de Alexa Developer Console y el dispositivo intercambia estado por el Shadow.

Resultados registrados: 22/22 pruebas del backend, compilación correcta del firmware y ciclo de servo observado. [EP01](evidencias/ejecucion-prolongada.md) reúne 11 ciclos completos con `reported` aceptado por AWS en una ventana de 15 min 42,995 s, y [AL01](evidencias/pruebas-alexa-vivo.md) las capturas del simulador. El detalle de pruebas y resultados está en [docs/pruebas.md](docs/pruebas.md) y en el [informe](docs/informe.md).

Cada integrante aporta sus propios commits; la publicación en GitHub y el envío del enlace al LMS corresponden al grupo.
