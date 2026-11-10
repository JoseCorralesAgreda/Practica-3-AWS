# P01 — Barrido PIR de 0 a 50 cm

Registro de la prueba reportada por el usuario el 2026-11-10. El sensor se probó desde 0 hasta 50 cm en incrementos de 5 cm; en cada posición reportada, el PIR detectó el objeto y puso la salida en HIGH.

| Ensayo | Distancia | Salida PIR observada | Detección |
|---:|---:|---|---|
| 1 | 0 cm | HIGH | ✅ Detectado |
| 2 | 5 cm | HIGH | ✅ Detectado |
| 3 | 10 cm | HIGH | ✅ Detectado |
| 4 | 15 cm | HIGH | ✅ Detectado |
| 5 | 20 cm | HIGH | ✅ Detectado |
| 6 | 25 cm | HIGH | ✅ Detectado |
| 7 | 30 cm | HIGH | ✅ Detectado |
| 8 | 35 cm | HIGH | ✅ Detectado |
| 9 | 40 cm | HIGH | ✅ Detectado |
| 10 | 45 cm | HIGH | ✅ Detectado |
| 11 | 50 cm | HIGH | ✅ Detectado |

**Resultado P01:** detección observada en las 11 distancias probadas del rango 0–50 cm. La distancia se midió desde el sensor según el procedimiento reportado. Este resultado documenta el rango ensayado; no implica que 50 cm sea el alcance máximo del PIR.

## Ajustes físicos informados

El usuario informa que el alcance máximo del módulo se regula manualmente con los potenciómetros y que el límite mínimo configurable para ese alcance es 300 cm. También informa que el retardo del módulo se puede ajustar entre 5 y 7 s. El retardo físico del PIR es distinto del `AUTO_COOLDOWN_MS` de 5 s del firmware y del calentamiento de 60 s al encender.

## Contexto de N02

En los [registros serie EP01](ejecucion-prolongada.md) y [muestras PIR](pir-muestras.csv), el usuario identifica las muestras HIGH como ensayos en los que se colocó la mano de un estudiante frente al sensor para comprobar el cambio de radiación infrarroja. Identifica las muestras LOW como el sensor apuntando a una pared, evitando fuentes de movimiento térmico que generen lecturas ajenas al ensayo. Con esta interpretación de las condiciones de prueba, la respuesta HIGH ante el objeto y LOW ante la pared se considera verificación funcional cualitativa de N02.

El barrido documenta el rango ensayado y la respuesta funcional del sensor en las condiciones del montaje.
