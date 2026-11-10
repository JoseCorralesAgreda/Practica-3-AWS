# Evidencias

Esta carpeta contiene resultados locales, pruebas en vivo de Alexa, evidencia serie EP01, reconexión MQTT y fotos del montaje. Ver [pruebas Alexa AL01 y capturas](pruebas-alexa-vivo.md), [análisis EP01](ejecucion-prolongada.md), [reconexión MQTT R01](reconexion-mqtt.md), [81 muestras PIR](pir-muestras.csv), [11 ciclos](ciclos.csv), [foto 1](montaje-esp32-servo-01.jpeg) y [foto 2](montaje-esp32-servo-02.jpeg).

- `resultados.csv`: estado de cada prueba, valores y evidencia.
- `latencias.csv`: tiempos de cada comando, extremo a extremo.
- `pir.csv`: observación de movimiento y clasificación.

Las [grabaciones en vivo](https://drive.google.com/drive/folders/1d_Hg945M0cD-lJ1bk0L4BZTwfwMi8PAt?usp=sharing) están en Google Drive; revisar cada una y vincularla al caso correspondiente antes de usarla como evidencia adicional. Las capturas de comandos Alexa están en AL01; todavía faltan capturas de DynamoDB y Shadow, y logs sin secretos. Anonimizar userId y datos personales. Para cada evidencia indicar fecha, placa, versión de código y operador. Los resultados fallidos también se conservan.

Los tests unitarios y la compilación inicial se registran en `verificacion-local.txt`. No prueban conectividad real ni funcionamiento físico. No publicar firmware compilado con secretos embebidos.

EP01 se incorporó el 2026-11-09; fecha real de ejecución, operador y binario no informados. `pir.csv` enumera las nueve muestras HIGH del registro serie; el usuario identifica los HIGH con la mano frente al PIR y los LOW con el sensor apuntando a una pared estática. Ver el [registro de barrido 0–50 cm y contexto N02](pir-rango-0-50cm.md). El usuario informa que realizó 15 mediciones de respuesta; `latencias.csv` aún necesita los valores individuales para calcular el máximo. Los resultados actualizados están en `resultados.csv`.
