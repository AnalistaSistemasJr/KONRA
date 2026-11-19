# MONTOS

En este archivo, se registrarán las decisiones que se han tomado referente a los montos.
Cada que se agregue una, escribir la fecha para tener registro de la más actualizada.

### [Octubre 2026] - Uso de Decimal() en lugar de float()

La principal diferencia entre `Decimal()` y `float()` es como guardan cada uno los datos en memoria, `float` utiliza una aproximación binaria, mientras que `Decimal` utiliza la representación exacta.

Aunque `float` procesa las operaciones con más rápidez, por la naturaleza del auxiliar de caja, la precisión es clave.

Ejemplo:

Con `float`:
$0.1 + 0.2 = 0.30000000000000004 \neq 0.3$

Con `Decimal`:
$Decimal(0.1) + Decimal(0.2) = 0.3$


### [Noviembre 2026] - Límite del monto ingresado

El monto ingresado dentro del formulario, tiene las siguientes condiciones para que pueda ser aceptado:

1. Dígitos permitidos: 12.
2. Total de decimales: 2
3. El monto debe de ser diferente de cero, se permiten valores negativos.
4. El valor absoluto del monto dede de ser menor o mayor que $1,000,000.00

>[!NOTE]
>El punto 4 es un estado provisional, si se requiere cambiar, hacerlo desde el modelo.