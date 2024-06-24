# TFG

Para ejecutar el proyecto se debe ejecutar los siguientes comandos en una terminal 
situada en el mismo directorio en el que se encuentra el resto de directorios como
flaskr, dump, etc:

  mongod //para iniciar la conexión de la base de datos

  . venv/bin/activate
  
  export FLASK_ENV=development
  
  export FLASK_APP=flaskr
  
  flask run

Una vez que ejecutemos el comando "flask run" nos mostrará la dirección donde está corriendo la aplicación.


Si quieremos generar audios, primero deberemos ejecutar el módulo de generación, para ello debemos acceder a este otro respositorio:

  - https://github.com/fraan-pedregosa/AudioLDMTFG.git

Depués debemos ejecutar esa aplicación con el siguiente comando:

  python3 app.py

Esperamos a que se carguen los componentes necesarios y ya podemos ir a la aplicación y generar los audios que queramos. (Destacar que en local un audio de unos 10 segundos puede llegar a tardar 12 o 15 minutos, pero si miramos la terminal del módulo de generación, veremos una barra de progreso).
