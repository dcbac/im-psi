# Práctica 1

Requisitos:
```sh
python -mvenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Ejecución de la aplicacion en entorno de prueba (con base de datos local):
```sh
DEBUG=1 TESTING=1 python manage.py migrate
DEBUG=1 TESTING=1 python populate_catalog.py
DEBUG=1 TESTING=1 python manage.py createsu
DEBUG=1 TESTING=1 python manage.py runserver 8001
```

Ejecución de la batería de tests (con base de datos local):
```sh
DEBUG=1 TESTING=1 python manage.py test catalog.tests --verbosity 2
```

Pruebas de covertura:
```sh
DEBUG=1 TESTING=1 coverage erase
DEBUG=1 TESTING=1 coverage run --omit="*/test*" --source=catalog manage.py test catalog.tests
DEBUG=1 TESTING=1 coverage report -m -i | tee coverage.txt
```

**Observaciones.**
Sobre las credenciales de `neon.tech`:

Este repositorio se ha hecho público para poder darle acceso a `render`.
Por esta razón, las credenciales de la base de datos de producción y el token secreto de `django` se han configurado exclusivamente en `render` y no corresponen a los presentes en la historia de git de este repo.
Como consecuencia, a menos que se especifique `TESTING=1` como variable de entorno en la línea de comandos, las ejecuciones en local van a fallar.

La URL asignada por `render` para este proyecto es: [p1-15-2401-2026-1.onrender.com](https://p1-15-2401-2026-1.onrender.com/catalog/)
