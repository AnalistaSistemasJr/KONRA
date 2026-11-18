# CATÁLOGOS
 
El objetivo de los catálogos establecido es tener una estandarización de campos, evitando así variaciones de una misma referencia en la base de datos, facilitando la agrupación de datos.

A continuación, se detallan los catálogos creados:

## CATÁLOGO "ESTACIONES"

El catálogo contiene las estaciones a las cuales se les puede aplicar un movimiento.

Estructura de la base:

|numero_estacion|estacion|razon_social|estacion_activa|
|---------------|--------|------------|---------------|
|  num_estacion | nombre |razon_social|      true     |


**REGLAS DEL CATÁLOGO:**

1. Todos los campos son obligatorios
2. El campo _"NUMERO ESTACION"_ debe de ser un número entero.
3. _"NUMERO ESTACION"_ y _"ESTACION"_ son campos de validación, es decir, no se permiten duplicados.


**REGISTRO DE ESTACIONES:**

Existen dos formas de cargar estaciones dentro de la base:

1. **Por comando:** El comando `import_cuentas` escribe la información extraída de un csv, utilizando una transacción única, el comando es repetible. 
Por defecto, se realiza una simulación, la cual sirve como validación previa, para escribir en la base, agregar `--aplicar`. Ejemplo:
```ps
python manage.py import_estaciones "C:\Users\User1\Desktop\Repo\Catalogos\catalogo1.csv" --aplicar
```
El csv debe de contar con la estructura establecida previamente.

2. **Panel admin:** Desde el panel de administración de Django, en la sección de CATALOGOS, estará disponible "Estaciones", en el cual se podrá visualizar la información, así como realizar modificaciones de las estaciones ya registradas. Aquí el proceso consta del llenado de un formulario sencillo e intuitivo. 

**UBICACIÓN ARCHIVOS:**

- **Modelo:** apps/catalogos/models (Modelo Estacion).
- **Comando:** apps/catalogos/management/commands/import_estaciones.py


## CATÁLOGO "RUBROS"

El catálogo contiene las categorías que podrán ser aplicadas a una cuenta contable para su agrupación.

Estructura de la base:

| id |  rubro  |rubro_activo|   clave   |
|----|---------|------------|-----------|
|  1 | Rubro_1 |    true    |  rubro_1  |


**REGLAS DEL CATÁLOGO:**

1. Los campos _rubro_ y _rubro_activo_ son obligatorios.
2. El campo _**id**_ se genera de manera automática por el sistema, es decir, no puede ser ingresado por el usuario.
3. El campo _**clave**_, al igual que el id, se genera de manera automática,  éste se genera normalizando lo ingresado en el campo rubro.

**VALIDACIÓN DE RUBROS:**

Con el fin de evitar duplicados, al registrar un rubro, internamente se ejecuta el siguiente flujo:

1. **Petición de registro:**
    1. Generación de clave: Normalización de texto (Todo pasa a minúsculas, sin acentos, dobles espacios, caracteres de ancho cero o completo, conseva la "ñ".)

    2. Comparación de claves: Busqueda de duplicado entre claves existentes

2. **Resultado:** Aceptado / Rechazado (En caso de encontrar clave ya registrada)

**Ejemplo:** 

Se ingresa:

|      rubro      |rubro_activo|
|-----------------|------------|
| Inversión  Peña |    true    |

Se genera en db:

| id |      rubro     |rubro_activo|       clave      |
|----|----------------|------------|------------------|
|  1 | Inversión Peña |    true    |  inversion peña  |

**REGISTRO DE RUBROS:**

Existen dos formas de cargar rubros dentro de la base:

1. **Por comando:** El comando `import_rubros` escribe la información extraída de un csv, utilizando una transacción única, el comando es repetible. 
Por defecto, se realiza una simulación, la cual sirve como validación previa, para escribir en la base, agregar `--aplicar`. Ejemplo:
```ps
python manage.py import_rubros "C:\Users\User1\Desktop\Repo\Catalogos\catalogo_rubros.csv" --aplicar
```
El csv debe de contar con la estructura establecida previamente (Ver ejemplo).

2. **Panel admin:** Desde el panel de administración de Django, en la sección de CATALOGOS, estará disponible "Rubros", en el cual se podrá visualizar la información, así como realizar modificaciones de los rubros ya registrados. Aquí el proceso consta del llenado de un formulario sencillo e intuitivo.

**UBICACIÓN ARCHIVOS:**

- **Modelo:** apps/catalogos/models.py (Modelo Rubro).
- **Comando:** apps/catalogos/management/commands/import_rubros.py
- **Función normalizadora:** apps/catalogos/normalize.py (normalizar_texto)

## CATÁLOGO "CUENTAS"

El catálogo contiene las cuentas a las que se puede asociar el movimiento a registrar. Todas las cuentas están disponibles para todas las estaciones.
Este catálogo está asociado directamente con el catálogo de rubros, pues cada elemento está asociado a uno. 

Estructura de la base:

|numero_cuenta | nombre_cuenta | tipo_cuenta | rubro  |   especificacion    | cuenta_activa |
|--------------|---------------|-------------|--------|---------------------|---------------|
|nn-nn-nn-nn-nn|  nom cuenta 1 |    tipo 1   | rubro 1| Cuenta asociacidada |      true     |


**REGLAS DEL CATÁLOGO:**

1. Los campos *numero_cuenta, nombre_cuenta, tipo_cuenta, rubro, cuenta_activa* son obligatorios.
2. El número de cuenta debe tener el formato "nn-nn-nn-nn-nn", donde cada n es un número entre 0-9. El formato se verifica con una función de validación.
3. El rubro asignado a la cuenta, debe de existir en el catálogo "Rubros", de lo contrario, no procederá el registro.
4. El campo *tipo_cuenta* es obligatorio; sin embargo, cuenta con "No_definido" como valor por defecto.
5. El campo *numero_cuenta* es validador, es decir, no se pueden repetir números de cuenta en los registros.

**TIPOS DE CUENTAS**

El campo *tipo_cuenta*, tiene valores ya establecidos dentro del modelo, los cuales son:

- Activos
- Pasivos
- Capital
- Ingresos
- Gastos
- Costos
- Interno
- No_definido (Default)

Por lo que solo se puede elegir dentro de estas opciones al hacer un registro.

**REGISTRO DE CUENTAS**

Existen dos formas de cargar cuentas dentro de la base:

1. **Por comando:** El comando `import_cuentas` escribe la información extraída de un csv, utilizando una transacción única, el comando es repetible. 
Por defecto, se realiza una simulación, la cual sirve como validación previa, para escribir en la base, agregar `--aplicar`. Ejemplo:
```ps
python manage.py import_cuentas "C:\Users\User1\Desktop\Repo\Catalogos\catalogo_cuentas.csv" --aplicar
```
El csv debe de contar con la estructura establecida previamente (Ver ejemplo).

2. **Panel admin:** Desde el panel de administración de Django, en la sección de CATALOGOS, estará disponible "Rubros", en el cual se podrá visualizar la información, así como realizar modificaciones de los rubros ya registrados. Aquí el proceso consta del llenado de un formulario sencillo e intuitivo.

**UBICACIÓN ARCHIVOS:**

- **Modelo:** apps/catalogos/models.py (Modelo Cuenta).
- **Tipos cuenta:**  apps/catalogos/modelos.py (Class TipoCuenta) 
- **Comando:** apps/catalogos/management/commands/import_cuentas.py
- **Función validadora:** apps/catalogos/validation.py

## RECOMENDACIONES Y CONSIDERACIONES GENERALES

1. Si el proyecto está por ejecutarse, la forma más sencilla y rápida de cargar un catálogo de los antes mencionados, es por comando. Si el proyecto está desplegado, por el panel de administración resultará más cómodo.

2. Si un elemento (estación, rubro, cuenta) dejará de estar en operación, NO se debe de eliminar del catálogo, solo se establece como inactivo, como consecuencia, la opción deja de aparecer dentro de los formularios establecidos. 