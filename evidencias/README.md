# Evidencias

Esta carpeta contiene resultados locales, pruebas en vivo de Alexa, evidencia serie EP01, reconexión MQTT y fotos del montaje. Ver [pruebas Alexa AL01 y capturas](pruebas-alexa-vivo.md), [análisis EP01](ejecucion-prolongada.md), [reconexión MQTT R01](reconexion-mqtt.md), [81 muestras PIR](pir-muestras.csv), [11 ciclos](ciclos.csv), [foto 1](montaje-esp32-servo-01.jpeg) y [foto 2](montaje-esp32-servo-02.jpeg).

- `resultados.csv`: estado de cada prueba, valores y evidencia.
- `latencias.csv`: tiempos de cada comando, extremo a extremo.
- `pir.csv`: observación de movimiento y clasificación.

Las [grabaciones en vivo](https://drive.google.com/drive/folders/1d_Hg945M0cD-lJ1bk0L4BZTwfwMi8PAt?usp=sharing) están en Google Drive y corresponden a los casos del plan de pruebas. Las capturas de comandos Alexa están en AL01. Anonimizar userId y datos personales en material nuevo. Para cada evidencia indicar fecha, placa, versión de código y operador.

Los tests unitarios y la compilación se registran en `verificacion-local.txt`; las pruebas de integración se documentan en AL01, EP01 y R01.

EP01 se incorporó el 2026-11-09. `pir.csv` enumera las nueve muestras HIGH del registro serie; el usuario identifica los HIGH con la mano frente al PIR y los LOW con el sensor apuntando a una pared estática. Ver el [registro de barrido 0–50 cm y contexto N02](pir-rango-0-50cm.md). Se realizaron 15 mediciones de respuesta durante una sesión de 15 minutos. Los resultados están en `resultados.csv`.
