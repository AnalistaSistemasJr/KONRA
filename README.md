# Documentación Técnica del Proyecto Web (Django + Docker)

Este repositorio contiene la arquitectura base de un proyecto web desarrollado en Django, utilizando PostgreSQL como base de datos y Docker para la contenedorización del entorno de desarrollo.

## 🚀 Entorno de Desarrollo y Requisitos

Para trabajar en este proyecto necesitarás tener instalado el siguiente software en tu equipo:
* **Editor de Código:** [Visual Studio Code](https://code.visualstudio.com/ "Visual Studio Code download")
* **Control de Versiones:** [Git](https://git-scm.com/ "Git download") / Cuenta de [GitHub](https://github.com/ "GitHub login")
* **Contenedores:** [Docker Desktop](https://www.docker.com/products/docker-desktop/ "Docker Desktop download") (incluye Docker Compose)

## 🛠️ Tecnologías Utilizadas

* **Backend:** [Django](https://docs.djangoproject.com/ "Django Documentation") (Python)
* **Base de Datos:** [PostgreSQL](https://www.postgresql.org/ "PostgreSQL Documentation")
* **Frontend:** HTML5 básico, CSS y formularios nativos de Django.
* **Orquestación:** Docker & Docker Compose.

---

## 💻 Instrucciones de Instalación Local

Sigue estos pasos para clonar el proyecto y levantar el entorno local:

### 1. Clonar el repositorio
```bash
git clone <URL_DE_TU_REPOSITORIO_EN_GITHUB>
cd <NOMBRE_DE_LA_CARPETA_DEL_PROYECTO>
```

### 2. Configurar variables de entorno
Crea un archivo llamado `.env` en la raíz del proyecto para definir las credenciales locales de la base de datos (asegúrate de que este archivo esté en tu `.gitignore`):
```env
DEBUG=True
SECRET_KEY=tu_secret_key_de_desarrollo
DB_NAME=django_db
DB_USER=postgres
DB_PASSWORD=postgres_password
DB_HOST=db
DB_PORT=5432
```

### 3. Construir e iniciar los contenedores Docker
Este comando descargará las imágenes necesarias, creará el contenedor de la base de datos PostgreSQL y el contenedor de la aplicación Django:
```bash
docker compose up --build
```
*Para apagar los servicios usa `docker compose down` o `Ctrl + C`.*

### 4. Aplicar migraciones y crear superusuario
Abre una nueva terminal en VS Code y ejecuta los comandos dentro del contenedor de Django:
```bash
# Aplicar las migraciones a la base de datos PostgreSQL
docker compose exec web python manage.py migrate

# Crear el administrador para el panel de Django
docker compose exec web python manage.py createsuperuser
```

### 5. Acceder a la aplicación
Una vez corriendo, abre tu navegador e ingresa a:
* **Sitio Web (Vista de Ejemplo/Formulario):** `http://localhost:8000`
* **Panel de Administración:** `http://localhost:8000/admin`

---

## 🏗️ Estado Actual del Proyecto y Arquitectura

Hasta el momento, el proyecto se encuentra en su fase inicial con los siguientes componentes configurados:

* **Arquitectura de Modelos:** Modelos base diseñados en `models.py`.
* **Catálogos:** Tablas de referencia iniciales integradas en la base de datos.
* **Vistas y Formularios:** Se ha implementado un `forms.py` y una vista básica en Django para procesar y desplegar un formulario de ejemplo en el HTML.
* **Pruebas Unitarias:** Pruebas automatizadas iniciales creadas en `tests.py` para validar la lógica de los modelos y los catálogos.

### Ejecución de Pruebas Unitarias
Para correr la suite de pruebas dentro del entorno Docker, ejecuta:
```bash
docker compose exec web python manage.py test
```

---

## 📁 Estructura Principal de Carpetas (Resumen)

```text
├── .github/               # Flujos de trabajo o configuraciones de GitHub
├── core_project/          # Configuración principal de Django (settings.py, urls.py)
├── apps/                  # Aplicaciones internas de Django (Modelos, Vistas, Formularios)
│   ├── templates/         # Archivos HTML de la aplicación
│   ├── models.py          # Arquitectura de datos y catálogos
│   ├── forms.py           # Formularios básicos de Django
│   ├── views.py           # Lógica de las vistas de ejemplo
│   └── tests.py           # Pruebas automatizadas de modelos y catálogos
├── Dockerfile             # Configuración del contenedor de la aplicación web
├── docker-compose.yml     # Orquestación de servicios (web + db)
├── requirements.txt       # Dependencias de Python/Django
└── README.md              # Este archivo de documentación
```
