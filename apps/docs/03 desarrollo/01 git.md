# BRANCH GIT

Git es utilizado para el control de versiones de código. Dentro de este proyecto, hasta el momento, se manejan tres ramas, cada una con diferentes objetivos.

### Branch `main`

Como su nombre lo indica, `main` es la rama principal, es decir, es el ambiente de producción. 
Por lo que, como es sabido, no se deben de realizar cambios directamente aquí hasta que éstos estén probados y autorizados.

### Branch `staging`

La rama `staging` es un amibiente de pruebas, es decir, aquí los usuarios finales pueden probar las nuevas funcionalidades, hacer movimientos sin afectar las bases de producción y sin afectar el funcionamiento del entorno de producción.

### Branch `piloto`

La rama `piloto` es el entorno de desarrollo, es decir, donde los desarrolladores pueden realizar cambios de todo tipo, una vez que se haga terminado de ejecutar el cambio, este pasaría al entorno de pruebas para que sea probado por los usuarios.


```
Flujo recomendado dentro de Git:

piloto ⇒ staging ⇒ main 
```