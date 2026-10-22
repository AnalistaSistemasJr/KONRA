# ARCHIVO RECAPITULAR LAS REGLAS DE NEGOCIO APLICADAS

Escribir sobre:

## BASE DE DATOS
Se elige realizar el desarrollo en postgresql debido a las ventajas que este tiene sobre sqlite. El manejo de decimales, ASCII y seguridad.
Para comprobar la conexión, en terminal, correr lo siguiente:
python manage.py shell -c "from django.db import connection; print(connection.vendor)"    
git ls-files | findstr sqlite 

Salida:
9 objects imported automatically (use -v 2 for details).

postgresql

## CÁLCULO REGLA SALDO FINAL
El saldo final de cada cuenta, es cálculado de la siguiente manera
> Saldo Final = Saldo anterior + Entrada - Salida
<strong>NOTA:</strong> Siempre se sigue esta regla sin importar el signo del monto ingresado.


## MONTOS
### Condiciones de escritura
1. Decimales permitidos: 2
2. Dígitos permitidos: 12

### Límites de monto
El monto a ingresar en cada movimiento, hasta la fecha (Octubre 2026), está limitado a las siguientes condiciones:
1. Tiene que ser diferente de cero, se permiten montos negativos
2. El valor absoluto del monto tiene que ser menor o igual que 1,000,000.00


### RUBROS
### Modelo de datos
1. La tabla contiene 3 columnas:<br>

|clave|rubro|rubro_activo|
| --- | --- | --- |
nomina|Nómina|true

2. El campo "clave" sirve para evitar la duplicidad de rubros, normalizando las entradas, es decir, esto evita que se guarde:
> "Nómina " y "NÓMINA" (ambos rubros tienen por clave "nomina"); sin embargo, se conserva el caracter "ñ", la finalidad es evitar ambigüedades con nombres de rubro que lo requieran.

## CATALOGO CUENTAS
El número de cuenta se almacena como texto y no como entero, ya que representa una estructura jerárquica contable. Actualmente se adopta el formato NN-NN-NN-NN-NN, donde cada segmento consta de dos dígitos. Esta regla se basa en la convención utilizada habitualmente en catálogos contables mexicanos y permite preservar ceros a la izquierda.