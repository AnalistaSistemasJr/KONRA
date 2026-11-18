# ROLES

El objetivo del siguiente archivo es explicar el proceso para dar de alta los roles.

De igual manera, se describirán los roles y la función de cada uno de ellos dentro del sistema, siendo una guía para saber que rol designar al dar de alta un nuevo usuario.

## CONFIGURACIÓN DE ROLES

### Archivo roles.py
El archivo roles.py ubicado en `apps\users\roles.py`, concentra todos los grupos y acciones permitidas que tiene sobre un modelo.

Por defecto Django crea `delete`, `change`, `add`, `view` al migrar un modelo.

### Comando setup_roles

El comando sincroniza los permisos con la base de datos, es decir, crea o actualiza los grupos, cada que se realice un cambio en el archivo se debe correr en terminal lo siguiente: 

```
python manage.py setup_roles
```

## TIPOS DE ROLES

A continuación se detallan los tipos de roles y los permisos del grupo.

### Capturista

El rol está diseñado para las personas que solo tendrán funciones de captura de movimientos, por lo que solo tienen los siguientes permisos:

- `add_registro_movimientos`: Agregar nuevos registros.
- `view_registro_movimientos`: Visualizar los movimientos registrados, solo los registros propios.

### Auditor

El rol está diseñado para las personas que necesitan consultar la información consolidada, pero no de captura, por lo que solo tienen los siguientes permisos:+

- `view_registro_movimientos`: Visualiza la información consolidada, una bitácora.

### Soporte

El rol, como su nombre lo indica, está para dar mantenimiento a catálogos, sus funciones no están relacionada a lo que se registra por parte de los usuarios. Teniendo los siguiente permisos.

- `view_`: Ver información guardada en el catálogo.
- `add_`: Agregar un nuevo elemento al catálogo.
- `change_`: Editar un elemento existente del catálogo.

Estos permisos aplican para todos los catálogos: Estaciones, Cuentas y Rubros.