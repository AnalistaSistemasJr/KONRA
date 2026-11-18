# REGLAS DE NEGOCIO

El objetivo del siguiente documento, es presentar las reglas que sea han establecido durante el desarrollo del sistema con apoyo del área de contabilidad. 

## SALDO DE CAJA

El sistema solo maneja una caja contable, cada movimientos, tanto entradas como salidas que realicen los usuarios, afectan solo a dicha caja.

Aunque dentro del sistema se manejan varias cuentas contables (Ver "01 catalogos" para más información); no presentan una caja contable en su individualidad, en otras palabras, son solo un medio de agrupación de movimientos. 


## CÁLCULO SALDO FINAL

El saldo final sigue la siguiente fórmula:

$$
Sf_{actual} = Sf_{anterior} + \sum Entradas - \sum Salidas 
$$

Donde $Sf$ = *Saldo final*. Además, cualquier movimiento puede ser tanto positivo como negativo, es decir, $\pm$ entrada y $\pm$ salida. 

Los símbolos de la fórmula son estrictos, sin importar el signo del movimiento, estos se conservan.

**Ejemplo:**

Saldo final anterior $= \$421$<br>
$\sum$ Movimiento (Entrada) $= \$900$<br>
$\sum$ Movimientos (Salida) $= -\$200$<br>
Saldo final actual $= \$421 + \$900 - (-\$200) = \$1,521$

Igualmente, este proceso ocurre en cada nuevo registro agregado.


## REGISTRO (FECHA DE CAJA)

La fecha de caja es la fecha en la que los saldos de la caja se verán afectados.

En el formulario de registro de un movimiento, hay un campo para ingresar dicha fecha, este campo es libre, es decir, se puede agregar cualquier fecha mientras no sea mayor al día en que se realiza el registro.

Sin embargo, para llevar un mejor control de los registros, también existe la fecha de referencia (nombre en modelo: *creado_en*), la cual se guarda de manera automática (no ingresada por el usuario), para saber con exactitud el momento en que fue registrado dicho movimiento, por ende, estas fechas pueden diferenciar.