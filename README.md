# Ambientador inteligente — Práctica 3

Base de un ambientador controlado por una skill personalizada de Alexa, con ESP32, PIR HC-SR501 y servomotor SG90 de 180°. Alexa usa una Lambda Python que modifica el Shadow clásico; el ESP32 se conecta mediante MQTT/TLS. DynamoDB conserva la vinculación de cada usuario con su propio Thing.

## Archivos principales

- [Firmware PlatformIO](firmware/src/main.cpp): una clase `Ambientador`, sensor, servo, Shadow y reconexión.
- [Lambda Python](backend/lambda_function.py): una clase `AmbientadorSkill`, vinculación, consultas y comandos.
- [Modelo de Alexa es-ES](alexa/interaction-model.es-ES.json), importable desde JSON Editor.
- [Configuración y montaje](docs/configuracion.md): instrucciones para las instancias existentes y la nueva tabla.
- [Diseño y base del informe](docs/informe.md): las ocho secciones exigidas, contrato Shadow y diagramas.
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

El modo automático es una extensión solicitada por el usuario: la consigna indica control exclusivamente por voz. Debe explicitarse esa diferencia al docente. Arranca desactivado y se recupera el valor deseado al conectar. El prototipo no demuestra dosificación real, posición mecánica medida ni detección de ocupación estática.

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

Implementación local y pruebas del backend disponibles. Placa confirmada: DOIT ESP32 DEVKIT V1 (`esp32doit-devkit-v1`). Región `us-east-2`, cuenta, endpoint IoT ATS e ID de skill configurados con los datos proporcionados. Lambda confirmada: `Alexa`, ARN `arn:aws:lambda:us-east-2:679937333206:function:Alexa`; permiso de logs completado para esta función. Infraestructura desplegada en AWS y vinculación Lambda–DynamoDB verificada. Registro serie del circuito disponible en [EP01](evidencias/ejecucion-prolongada.md), con 11 ciclos declarados y reported aceptado; Alexa y validacion fisica completa pendientes; consultar [estado y pasos de conexión](docs/despliegue-aws.md). Consultar [pruebas](docs/pruebas.md) para separar resultados locales de validaciones pendientes.

El informe contiene campos pendientes de evidencia real, integrantes, fotografías y resultados. No debe entregarse como si las pruebas de hardware y nube ya hubieran sido realizadas. Cada integrante debe hacer sus propios commits; la publicación en GitHub y el envío del enlace al LMS corresponden al grupo.
