# Sistema auxiliar de caja "Grupo NR"

## ¿QUÉ ES?
KONRA (Nombre no oficial, solo repositorio) es un sistema auxiliar de caja interno para el empresa "Grupo NR",
en el cual se lleva el registro de flujo de dinero de las diferentes estaciones.
**NO** es un sistema de gestión contable.

## ENTORNO DE DESARROLLO Y REQUISITOS

Para trabajar en este proyecto necesitarás tener instalado el siguiente software en tu equipo:

1. **Editor de código:** [Visual Studio Code](https://code.visualstudio.com)
2. **Control de versiones:** [Git](https://git-scm.com) / [GitHub](https://github.com)
3. **Contenedores:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) (incluye Docker Compose)

## TECNOLOGÍAS Y ENTORNO DE EJECUCIÓN

- [Python](https://docs.python.org/3/) 3.14 sobre Windows (PowerShell) 
- [Django](https://docs.djangoproject.com/en/6.1/) 5.2
- [PostgreSQL](https://www.postgresql.org/docs/) 16 ejecutándose en Docker
- Conexión a PostgreSQL restringida a `127.0.0.1`
- django-environ para la gestión de variables de entorno
- coverage para la medición de cobertura de pruebas

## INSTALACIÓN LOCAL DE PROJECTO

### **1. Clonar el repositorio**

```bash
git clone https://github.com/AnalistaSistemasJr/KONRA
```

### **2. Configuración de variables de entorno**
Crear y activar el entorno virtual e instalar dependencias.
Crear un archivo llamado `.env` en la raíz del proyecto para definir las credenciales locales de la base de datos, no tienen valore por defecto (verificar que este archivo se encuentre en `.gitignore`):

```env
SECRET_KEY=colocar-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=django_db
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=postgres_password
DATABASE_URL=postgresql://usuario:contraseña@servidor:puerto/nombre_base_datos
```

### **3. Construcción de contenedores**
Este comando descargará las imágenes necesarias, creará el contenedor de la base de datos PostgreSQL y el contenedor de la aplicación Django:
```bash
docker compose up --build
```
*Para apagar los servicios usa `docker compose down`

### **4. Migraciones, superusuario y configuración de roles**
Ejecutar los siguientes comandos dentro de la terminal de VS Code:
```ps
python manage.py migrate
python manage.py setup_roles
python manage.py createsuperuser
```

### **5. Importación de catálogos**
Los comandos `import_cuentas`, `import_estaciones` e `import_rubros`, escriben la información extraída desde un archivo CSV, usan una transacción única y son repetibles. Por defecto, solo realizan una simulación, para escribir, utilzar `--aplicar`. Ejemplo de uso:

```ps
python manage.py import_cuentas "C:\Users\User1\Desktop\Repo\Catalogos\catalogo1.csv" --aplicar
```

**Estructura requerida en los catálogos**

Es obligatorio que los archivos CSV cuenten con la siguiente estructura, de lo contrario, no podrán ser cargados.

1. **Catálogo de rubros**

<center>

|  rubro  | rubro_activo |
|---------|--------------|
| rubro_1 |     true     |  

</center>

2. **Catálogo de estaciones**

<center>

| numero_estacion | estacion | razon_social	| estacion_activa |
|-----------------|----------|--------------|-----------------|
|       1         |estacion_1|  razon_soc_1 |      true       |

</center>

3. **Catálo de cuentas**

*Especificaciones:* 
- El campo "rubro" solo puede contener uno de los rubros previamente cargado.
- El  número de cuenta debe tener el formato "nn-nn-nn-nn-nn", donde "n" es un dígito del 0-9.
- "tipo_cuenta" puede ir en blanco; sin embargo, si decide establecerse un tipo, solo pueden ser de los ya definidos.
- "especificacion" puede ir en blanco.

| numero_cuenta | nombre_cuenta | tipo_cuenta |  rubro  | especificacion | cuenta_activa |
|---------------|---------------|-------------|---------|---------------|---------------|
00-00-00-00-00 |  cuenta num 1 |   Activos    | rubro_1 |  cuenta de act  |      true     |


### **6. Ejecución de pruebas**

Para correr las pruebas del entorno, ejecuta:

```powershell
python manage.py test
coverage run --source=apps manage.py test
coverage report -m
```
**Criterio:** 100% de covertura

## ESTRUCTURA PRINCIPAL DEL PROYECTO

```
KONRA/
├─apps/
│  ├──catalogos/
│  │    ├──management/
│  │    ├──migrations/
│  │    ├──test/
│  │    ├──admin.py
│  │    ├──apps.py
│  │    ├──models.py
│  │    └──views.py
│  ├──docs/
│  ├──movs/
│  └──users/
├─config/
├─templates/
│  ├──movs/
│  └──users/
├─.env
├─.gitignore
├─docker-compose.yaml
├─manage.py
├─README.py
└─requirements.txt
```