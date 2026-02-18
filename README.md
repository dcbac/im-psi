# Práctica 1

Ejecución de la aplicacion en entorno de prueba (con base de datos local):
```sh
DEBUG=1 TESTING=1 python manage.py migrate
DEBUG=1 TESTING=1 python manage.py createsuperuser
DEBUG=1 TESTING=1 python manage.py runserver 8001
```

Ejecución de la batería de tests (con base de datos local):
```sh
DEBUG=1 TESTING=1 python manage.py test catalog.tests --verbosity 2
```
