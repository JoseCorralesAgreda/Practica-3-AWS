# Evidencias

Esta carpeta contiene plantillas de registro; no contiene aún mediciones físicas ni capturas de AWS/Alexa.

- `resultados.csv`: estado de cada prueba, valores y evidencia.
- `latencias.csv`: tiempos de cada comando, extremo a extremo.
- `pir.csv`: observación de movimiento y clasificación.

Agregar fotografías de montaje, vídeos, capturas de intents/slots, DynamoDB y Shadow, y logs sin secretos. Anonimizar userId y datos personales. Para cada evidencia indicar fecha, placa, versión de código y operador. Los resultados fallidos también se conservan.

Los tests unitarios y la compilación inicial se registran en `verificacion-local.txt`. No prueban conectividad real ni funcionamiento físico. No publicar firmware compilado con secretos embebidos.
