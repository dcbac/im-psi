# RESUMEN

## 📋 ÍNDICE
1. [Comandos](#1-comandos)
2. [Modelos](#2-modelos-modelspy)
3. [Consultas](#3-consultas-filter)
4. [URLs y Vistas](#4-urls-y-vistas)
5. [Templates y Archivos Estáticos](#5-templates-y-archivos-estáticos)
6. [Class-Based Views (CBV)](#6-class-based-views-cbv)
7. [Formularios](#7-formularios)
8. [Autenticación y Permisos](#8-autenticación-y-permisos)
9. [Sesiones](#9-sesiones)
10. [Tests](#10-tests-testspy)
11. [Variables de Entorno (.env)](#11-variables-de-entorno-env)

---

## 1. Comandos

### Entorno Virtual
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Inicio Proyecto
```bash
django-admin startproject locallibrary
cd locallibrary
python3 manage.py startapp catalog
```

### Añadir app a settings
En `settings.py`, añadir a `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ...
    'catalog.apps.CatalogConfig',  # O simplemente 'catalog'
]
```

### Postgres

#### Iniciar
```bash
sudo systemctl restart postgresql
createdb -U alumnodb -h localhost psi
```

### Mange
```bash
python3 manage.py makemigrations  # Detecta cambios en models.py
python3 manage.py migrate         # Aplica cambios a la BD

python3 manage.py runserver 8001  # Puerto personalizado

python3 manage.py createsuperuser
```
---

## 2. MODELOS (models.py)

### Argumentos Comunes de Campos

| Argumento | Descripción |
|-----------|-------------|
| `max_length` | Longitud máxima (obligatorio en CharField) |
| `blank=True` | Permite vacío en **formularios** |
| `null=True` | Permite NULL en **base de datos** |
| `default` | Valor por defecto (puede ser función) |
| `unique=True` | Valor único en toda la tabla |
| `choices` | Lista de opciones (tuplas) |
| `help_text` | Texto de ayuda en formularios |
| `verbose_name` | Nombre legible del campo |
| `primary_key=True` | Define como clave primaria |
| `db_index=True` | Crea índice en BD (búsquedas rápidas) |
| `editable=False` | No editable en formularios |

### Tipos de Campos Comunes

| Campo | Uso |
|-------|-----|
| `CharField(max_length)` | Texto corto (hasta max_length caracteres) |
| `TextField()` | Texto largo sin límite |
| `IntegerField()` | Números enteros |
| `DecimalField(max_digits, decimal_places)` | Decimales precisos (precios) |
| `FloatField()` | Números decimales (menos preciso) |
| `BooleanField()` | True/False |
| `DateField()` | Fecha (YYYY-MM-DD) |
| `DateTimeField()` | Fecha y hora |
| `EmailField()` | Email con validación automática |
| `URLField()` | URL con validación |
| `FileField(upload_to)` | Subir archivos |
| `ImageField(upload_to)` | Subir imágenes (requiere Pillow) |
| `SlugField()` | Slug (letras, números, guiones) |
| `AutoField()` | Entero auto-incremental (PK por defecto) |
| `UUIDField()` | UUID (identificador único universal) |

### Relaciones

#### ForeignKey (1 a N)
```python
# Un libro tiene UN autor, un autor tiene MUCHOS libros
autor = models.ForeignKey('Autor', on_delete=models.CASCADE)
```

#### ManyToManyField (N a N)
```python
# Un libro tiene MUCHOS géneros, un género tiene MUCHOS libros
generos = models.ManyToManyField('Genero')
```

### Lookups Esenciales

| Lookup | Descripción |
|--------|-------------|
| `exact` | Igualdad exacta (case-sensitive) |
| `iexact` | Igualdad (case-insensitive) |
| `contains` | Contiene texto (case-sensitive) |
| `icontains` | Contiene texto (case-insensitive) |
| `startswith` | Empieza con |
| `endswith` | Termina con |
| `gt` | Mayor que (>) |
| `gte` | Mayor o igual (>=) |
| `lt` | Menor que (<) |
| `lte` | Menor o igual (<=) |
| `range` | Rango inclusivo [a, b] |
| `in` | Valor en lista |
| `isnull` | Es NULL (True/False) |

### Filtrar por Relaciones
```python
# Libros del género "Ciencia Ficción"
Libro.objects.filter(generos__nombre="Ciencia Ficción")
```
---

## 4. URLS

**Tipos de Path Converters:**
- `<int:var>` → Enteros
- `<str:var>` → Strings (sin /)
- `<slug:var>` → Slugs (letras, números, guiones, underscores)
- `<uuid:var>` → UUIDs
- `<path:var>` → Cualquier string (incluye /)
---

## 5. CSS

**En `settings.py`:**
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```
---

## 6. Vistas creadas por Djando

ListView --> Lista (pones model = Modelo ; Template con un for modelo in lista_modelo)
DetailView --> Detalles

## 7. FORMULARIOS

Cambiar forms.py y views.py

---

## 8. AUTENTICACIÓN Y PERMISOS

### Restringir Acceso a Vista (@)

```python
from django.contrib.auth.decorators import login_required

@login_required
def mi_vista(request):
    # Solo usuarios autenticados pueden acceder
    return render(request, 'template.html')
```

### Restringir Acceso a Vista (Clase)

```python
from django.contrib.auth.mixins import LoginRequiredMixin

class MiVista(LoginRequiredMixin, generic.ListView):
    model = Libro
    # Solo usuarios autenticados pueden acceder
```

### Comprobar Permisos en View (Decorador)

```python
from django.contrib.auth.decorators import permission_required

@permission_required('catalog.can_mark_returned')
@permission_required('catalog.can_edit')
def mi_vista(request):
    # Solo usuarios con ese permiso pueden acceder
    pass
```

### Comprobar Permisos en View (Clase)

```python
from django.contrib.auth.mixins import PermissionRequiredMixin

class MiVista(PermissionRequiredMixin, generic.View):
    permission_required = 'catalog.can_mark_returned'
    # O múltiples permisos:
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
    # Nota: 'catalog.change_book' se crea automáticamente para el modelo Book
    # junto con add_book, delete_book
```

### Comprobar Permisos en Template

```django
{% if perms.catalog.can_mark_returned %}
    <!-- Solo se muestra si el usuario tiene el permiso -->
    <p>Usuario puede marcar libros como devueltos</p>
    <a href="{% url 'libro-return' libro.id %}">Devolver libro</a>
{% endif %}
```

**Verificar si usuario está autenticado:**
```django
{% if user.is_authenticated %}
    <p>Bienvenido, {{ user.username }}!</p>
    <a href="{% url 'logout' %}">Cerrar sesión</a>
{% else %}
    <a href="{% url 'login' %}">Iniciar sesión</a>
{% endif %}
```

---

## 9. SESIONES

### Trabajar con Sesiones

```python
# --- OBTENER VALOR DE SESIÓN ---
# Devuelve KeyError si no existe
mi_coche = request.session['mi_coche']

# Devuelve None si no existe
mi_coche = request.session.get('mi_coche')

# Con valor por defecto si no existe
mi_coche = request.session.get('mi_coche', 'mini')

# --- ESTABLECER VALOR ---
request.session['mi_coche'] = 'mini'

# --- ELIMINAR VALOR ---
del request.session['mi_coche']

# --- FORZAR ACTUALIZACIÓN (si modificas objetos mutables) ---
request.session.modified = True
```

### Ejemplo: Contador de Visitas
```python
def mi_vista(request):
    num_visitas = request.session.get('num_visitas', 0)
    request.session['num_visitas'] = num_visitas + 1
    
    return render(request, 'template.html', {
        'num_visitas': num_visitas
    })
```

---

## 10. TESTS

### Estructura Básica

```python
from django.test import TestCase
from .models import Autor

class AutorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Se ejecuta UNA vez al inicio de la clase de tests"""
        Autor.objects.create(nombre='Juan', apellido='García')
    
    def setUp(self):
        """Se ejecuta ANTES de cada test individual"""
        pass
    
    def test_nombre_label(self):
        """Verificar etiqueta del campo"""
        autor = Autor.objects.get(id=1)
        field_label = autor._meta.get_field('nombre').verbose_name
        self.assertEqual(field_label, 'nombre')
    
    def test_nombre_max_length(self):
        """Verificar longitud máxima"""
        autor = Autor.objects.get(id=1)
        max_length = autor._meta.get_field('nombre').max_length
        self.assertEqual(max_length, 100)
```

### Tests de Vistas

```python
from django.test import TestCase
from django.urls import reverse

class LibroListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Igual
    
    def test_view_url_exists(self):
        """La URL existe"""
        response = self.client.get('/catalog/libros/')
        self.assertEqual(response.status_code, 200)
    
    def test_view_url_accesible_por_nombre(self):
        """Se accede por nombre de URL"""
        response = self.client.get(reverse('libros'))
        self.assertEqual(response.status_code, 200)
    
    def test_view_usa_template_correcto(self):
        """Usa el template correcto"""
        response = self.client.get(reverse('libros'))
        self.assertTemplateUsed(response, 'catalog/libro_list.html')
    
    def test_paginacion_es_diez(self):
        """La paginación es de 10 items"""
        response = self.client.get(reverse('libros'))
        self.assertEqual(len(response.context['lista_libros']), 10)
```

### Tests con Autenticación

```python
from django.contrib.auth.models import User

class VistaProtegidaTest(TestCase):
    def setUp(self):
        # Crear usuario de prueba
        test_user = User.objects.create_user(
            username='testuser',
            password='12345'
        )
        test_user.save()
    
    def test_redirect_si_no_autenticado(self):
        """Redirige a login si no está autenticado"""
        response = self.client.get(reverse('mi-vista-protegida'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/mi-vista/')
    
    def test_accede_si_autenticado(self):
        """Permite acceso si está autenticado"""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('mi-vista-protegida'))
        self.assertEqual(response.status_code, 200)
```

---

## 11. VARIABLES DE ENTORNO (.env)

### Configuración de PostgreSQL

Crea un archivo `.env` en la raíz del proyecto:

```env
POSTGRESQL_URL='postgres://alumnodb:alumnodb@localhost:5432/psi'
DEBUG=True
ALLOWED_HOSTS='*'
SECRET_KEY=''
```

**En `settings.py`:**
```python
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Leer variables de entorno
SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-por-defecto-insegura')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Configurar PostgreSQL
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('POSTGRESQL_URL'),
        conn_max_age=600
    )
}
```