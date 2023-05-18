# ¿Como ejecutar el backend?

1. Use el comando `pip` para instalar las dependencias necesarias:

Para ello, abra una instancia de la línea de comandos en su sistema, ubíquese en la carpeta `requirements` y ejecute el comando:
	 `pip install -r requirements.txt`

En caso de presentar errores con la librería `mysqlclient` por favor siga los pasos descritos en el archivo README.txt de la carpeta `requirements ` mencionada anteriormente.

2. Tras instalar las dependencias necesarias, use el formato de `.env.example` para escribir un archivo `.env` con la información requerida, dicho archivo debe ubicarse en la carpeta raíz del repositorio
3. Puede usar el archivo `docker-compose.yml` para crear un contenedor por defecto que ejecutará el servicio MySQL 8.0 de ser necesario
4. Para agregar datos aleatorios a la base de datos (testing) diríjase a la carpeta `src` y ejecute el comando:
`python manage.py seed --number n`
donde `n` representa la cantidad de registros en cada tabla a agregar
5. Para ejecutar el servidor diríjase a la previamente mencionada carpeta `src` y ejecute el comando:
`python manage.py runserver`

NOTA: Se recomienda usar la versión 3.7.x de Python

Si estás teniendo problemas al intentar usar pip install mysqlclient
Puedes descargarlo de: https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient
y usar:
	pip install <filename>.whl
para instalarlo
(Escoge la versión ...-cpxx-cpxx-... donde xx representa la versión de Python,
por ejemplo, 37 para 3.7)