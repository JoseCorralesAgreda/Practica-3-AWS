# Evidencias

Esta carpeta contiene resultados locales y evidencia serie EP01 aportada por el usuario. Ver [analisis](ejecucion-prolongada.md), [81 muestras PIR](pir-muestras.csv) y [11 ciclos](ciclos.csv). No incluye capturas AWS/Alexa ni verificacion mecanica.

- `resultados.csv`: estado de cada prueba, valores y evidencia.
- `latencias.csv`: tiempos de cada comando, extremo a extremo.
- `pir.csv`: observación de movimiento y clasificación.

Agregar fotografías de montaje, vídeos, capturas de intents/slots, DynamoDB y Shadow, y logs sin secretos. Anonimizar userId y datos personales. Para cada evidencia indicar fecha, placa, versión de código y operador. Los resultados fallidos también se conservan.

Los tests unitarios y la compilación inicial se registran en `verificacion-local.txt`. No prueban conectividad real ni funcionamiento físico. No publicar firmware compilado con secretos embebidos.

EP01 se incorporo el 2026-11-09; fecha real de ejecucion, operador y binario no informados. Campos vacios significan datos no disponibles. `pir.csv` enumera los nueve HIGH en orden temporal (uno durante calentamiento): NO_EVALUABLE por falta de referencia fisica; no son los 40 ensayos N02. `latencias.csv` permanece vacio por falta de mediciones. N01 y otros casos quedan PARCIAL segun `resultados.csv`.
