# ARCHIVO RECAPITULACIÓN REGLAS DE NEGOCIO APLICADAS


## BASE DE DATOS
Se elige realizar el desarrollo en postgresql debido a las ventajas que este tiene sobre sqlite. El manejo de decimales, ASCII y seguridad.
Para comprobar la conexión, en terminal, correr lo siguiente:
python manage.py shell -c "from django.db import connection; print(connection.vendor)"    
git ls-files | findstr sqlite 

Salida:
9 objects imported automatically (use -v 2 for details).

postgresql

## SALDO INCIAL
Este saldo inicial tendrá que ser ejecutado por el comando 
```ps
python manage.py config_si monto --fecha --usuario --aplicar --confirmar-monto
```
**A CONSIDERAR:**
- Si no se usa `--aplicar`, NO se escribe nada, solo se ejecutan pruebas de validación.
- Una vez aplicado, es innamovible, es decir, ya no se pueden realizar cambios.
- El saldo incial no tiene límite, incluso puede ser cero; sin embargo, es obligatorio que esté configurado, de lo contrario, lanzará error en el guardado de los movimientos.

Ejemplo de ejecución:
```ps
python manage.py config_si 100.00 --fecha=2026-10-10 --usuario=user --aplicar --confirmar-monto=100.00
```

## CÁLCULO REGLA SALDO FINAL
El saldo final de cada cuenta, es cálculado de la siguiente manera
> Saldo Final = Saldo anterior + Entrada - Salida</br>
<strong>NOTA:</strong> Siempre se sigue esta regla sin importar el signo del monto ingresado.

Todo cálculo de saldo pasa por `apps/movs/saldos.py`, es decir, ningún cálculo se ejecuta desde una vista o reporte.

## MONTOS
### Condiciones de escritura
1. Decimales permitidos: 2
2. Dígitos permitidos: 12 

### Límites de monto
El monto a ingresar en cada movimiento, hasta la fecha (Octubre 2026), está limitado a las siguientes condiciones:
1. Tiene que ser diferente de cero, se permiten montos negativos
2. El valor absoluto del monto tiene que ser menor o igual que 1,000,000.00

## REGISTRO DE MOVIMIENTOS
En la base de datos, se guardarán 2 fechas al ingresar cada uno de los movimientos; sin embargo, solo una es ingresada por el usuario, la otra es creada automáticamente:

- **Fecha de caja:** Es la fecha en la que movimiento afectará a los saldos.
- **Fecha de referencia:** Es la fecha creada por el sistema, esta servirá para identificar el tiempo en que se están registrando los movimientos cada uno de los capturistas, de esta manera, ayudará a clasificar si los movimientos se registran en tiempo y forma.

## CONSULTA DE DATOS
El filtrado de información puede realizarse a través de los campos `estacion` y `cuenta`, admitiendo filtros de fecha (fecha de caja) para la extracción de la información.
Cualquier otro campo arrojará error.

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

## Historial de movimientos inmutable

**Regla movimiento registrado:** Un movimiento no se edita ni se borra. Un error se corrige con un movimiento inverso que lo anule, más un movimiento nuevo con el dato correcto. Duplicar un movimiento no corrige nada: lo repite.

### Capas de defensa
1. **Permisos de rol.** Capturista: ver y agregar movimientos. Auditor: solo ver. Soporte: sin acceso a movimientos. Ningún rol tiene `change_` ni `delete_`. Una prueba compara los permisos exactos de cada rol, así que cualquier permiso de más o de menos la hace fallar. `Registro_Movimientos` no está registrado en el admin y una prueba lo afirma.
2. **Modelo (`InmutableModel`, `apps/movs/inmutable.py`).**
   - `save()` sobre un objeto ya guardado lanza `PermissionDenied`.
   - `delete()` lanza `PermissionDenied`.
   - `QuerySet.update()` y `QuerySet.delete()` lanzan `PermissionDenied`, y con ellos `bulk_update()`.
   - `bulk_create(update_conflicts=True)` (upsert) lanza `PermissionDenied`. `ignore_conflicts=True` se permite porque no modifica filas existentes.
3. **Base de datos (pendiente de despliegue).** El usuario de PostgreSQL con el que corre la aplicación no debe tener `UPDATE` ni `DELETE` sobre la tabla de movimientos. Hay que verificarlo con una prueba manual contra la base de despliegue antes de cargar datos reales.

### Por qué cada pieza
- **`force_insert=True` en `save()` (mutación I2).** Sin él, un objeto con `pk` existente y `creado_en` informado se guarda como `UPDATE` y sobrescribe el movimiento. La prueba original pasaba aunque la línea faltara, porque el `UPDATE` fallaba por otra causa que no verificamos (probablemente `creado_en` nulo). La prueba corregida pasa `creado_en` y sí vigila la línea.
- **Firma explícita de `bulk_create` (mutación I6).** La primera versión recibía `**kwargs` y no reenviaba `update_conflicts`, así que el upsert estaba bloqueado por accidente y la guarda nunca se ejercitaba. Ahora la firma es explícita y una opción inesperada falla con `TypeError` en vez de ignorarse.

### Lo que esto no cubre
- SQL crudo y acceso directo a PostgreSQL. Esa defensa es la capa 3.
- Un superusuario con acceso a la base o al servidor.
- Borrados en cascada, que se saltan `delete()`. Hoy todas las claves foráneas hacia movimientos son `PROTECT`. Si se agrega una `CASCADE`, hay que revisarlo.

### Evidencia (mutaciones, 2026-10-28)
| Id | Mutación | Prueba que falló |
|----|---|---|
| I1 | quitar la guarda de `_state.adding` | `test_permiso_denegado_cambio_de_monto` (`IntegrityError`) |
| I2 | quitar `force_insert` | `test_save_directo_con_pk_existente_no_sobrescribe` |
| I3 | quitar `delete()` del modelo | `test_permiso_denegado_delete_mov` |
| I4 | quitar `update()` del queryset | `test_permiso_denegado_update_monto`, `test_permiso_denegado_bulk_update` |
| I5 | quitar `delete()` del queryset | `test_permiso_denegado_delete_all_movs` |
| I6 | quitar la guarda de `update_conflicts` | `test_bulk_create_upsert_no_sobrescribe` |
| I7 | `bulk_create` devuelve `[]` | `test_bulk_create_normal_crea_e_ignore_conflicts_no_modifica` |


