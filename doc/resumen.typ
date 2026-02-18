#import "@preview/showybox:2.0.4": showybox

#let box(title, content) = {
  showybox(
    title: title,
    frame: (
      border-color: green,
      title-color: green.lighten(15%),
      body-color: green.lighten(90%),
      footer-color: green.lighten(90%),
    ),
    breakable: true,
    content,
  )
}

#title("Comandos Interesantes")

Extractos de la práctica.

#box(
  "Iniciar postgresql en laboratorios EPS",
  [
    ```bash
    sudo systemctl restart postgresql
    # CREATE USER alumnodb WITH PASSWORD 'alumnodb' CREATEDB;
    ```
  ],
)

#box(
  "Entorno virtual Python",
  [
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
  ],
)

#box(
  "Reiniciar base de datos",
  [
    ```bash
    dropdb -U alumnodb psi
    createdb -U alumnodb psi
    python3 populate_catalog.py
    ```
  ],
)

#box(
  "Crear el proyecto",
  [
    ```bash
    django-admin startproject <project-name>
    ```
  ],
)

#box(
  "Crear aplicación",
  [
    ```bash
    python3 manage.py startapp <name>
    ```
  ],
)

#box(
  "Registrar aplicación",
  [
    Añadir a `settings.py` en la lista `INSTALLED_APPS`: `'name.apps.NameConfig'`
  ],
)

#box(
  "Definir urls (ejemplo catalog)",
  [
    ```python
    urlpatterns = [
        path('admin/', admin.site.urls),
        path('catalog/', include('catalog.urls')),
        path('', RedirectView.as_view(url='catalog/')),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    ```
  ],
)

#box(
  "Actualizar base de datos",
  [
    ```bash
    python3 manage.py makemigrations
    python3 manage.py migrate
    ```
  ],
)

#box(
  "Arrancar la web",
  [
    ```bash
    python3 manage.py runserver 8001
    ```
  ],
)

#pagebreak()

#box(
  "Crear superusuario",
  [
    ```bash
    python3 manage.py createsuperuser
    ```
  ],
)

#box(
  "Añadir CSS estático",
  [
    ```html
    <!-- Add additional CSS in static file -->
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/styles.css' %}" />
    ```
  ],
)

#box(
  "O una imagen",
  [
    ```html
    {% load static %}
    <img
      src="{% static 'images/local_library_model_uml.png' %}"
      alt="UML diagram"
      style="width:555px;height:540px;" />
    ```
  ],
)

#box(
  [Usar una clase para `view` (Con muchas opciones extra)],
  [
    ```python
    class BookListView(generic.ListView):
      model = Book
      context_object_name = 'book_list'   # your own name for the list as a template variable
      queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
      template_name = 'books/my_arbitrary_template_name_list.html'  # Specify your own template name/location

      def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context
    ```
  ],
)

#box(
  "Ejemplo sin usar clase",
  [
    ```python
    def book_detail_view(request, primary_key):
      try:
          book = Book.objects.get(pk=primary_key)
      except Book.DoesNotExist:
          raise Http404('Book does not exist')

      return render(request, 'catalog/book_detail.html', context={'book': book})
    ```
  ],
)

#box(
  "Alternativa",
  [
    ```python
    from django.shortcuts import get_object_or_404

    def book_detail_view(request, primary_key):
        book = get_object_or_404(Book, pk=primary_key)
        return render(request, 'catalog/book_detail.html', context={'book': book})
    ```
  ],
)

#pagebreak()

#box(
  "Sesiones",
  [
    ```python
    # Get a session value by its key (e.g. 'my_car'), raising a KeyError if the key is not present
    my_car = request.session['my_car']

    # Get a session value, setting a default if it is not present ('mini')
    my_car = request.session.get('my_car', 'mini')

    # Set a session value
    request.session['my_car'] = 'mini'

    # Delete a session value
    del request.session['my_car']

    # Set session as modified to force data updates/cookie to be saved.
    request.session.modified = True
    ```
  ],
)

#box(
  "Restringir acceso a una vista",
  [
    ```python
    from django.contrib.auth.decorators import login_required

    @login_required
    def my_view(request):
        # …
    ```
  ],
)

#box(
  "Comprobar permisos en template",
  [
    ```html
    {% if perms.catalog.can_mark_returned %}
        <!-- We can mark a BookInstance as returned. -->
        <!-- Perhaps add code to link to a "book return" view here. -->
    {% endif %}
    ```
  ],
)

#box(
  "Comprobar permisos en view",
  [
    ```python
    from django.contrib.auth.decorators import permission_required

    @permission_required('catalog.can_mark_returned')
    @permission_required('catalog.can_edit')
    def my_view(request):
      # …
    ```
  ],
)

#box(
  "Comprobar permisos en view (alternativa con Mixin)",
  [
    ```python
    from django.contrib.auth.mixins import PermissionRequiredMixin

    class MyView(PermissionRequiredMixin, View):
        permission_required = 'catalog.can_mark_returned'
        # Or multiple permissions
        permission_required = ('catalog.can_mark_returned', 'catalog.change_book')
        # Note that 'catalog.change_book' is permission
        # Is created automatically for the book model, along with add_book, and delete_book
          # …
    ```
  ],
)

#box(
  "ModelForm",
  [
    ```python
    class RenewBookModelForm(ModelForm):
        def clean_due_back(self):
            data = self.cleaned_data["due_back"]

            if not data:
                raise ValidationError(_("Invalid date - none provided"))

            # Check if a date is not in the past.
            if data < datetime.date.today():
                raise ValidationError(_("Invalid date - renewal in past"))

            # Check if a date is in the allowed range (+4 weeks from today).
            if data > datetime.date.today() + datetime.timedelta(weeks=4):
                raise ValidationError(_("Invalid date - renewal more than 4 weeks ahead"))

            # Remember to always return the cleaned data.
            return data

        class Meta:
            model = BookInstance
            fields = ["due_back"]
            labels = {"due_back": _("Renewal date")}
            help_texts = {
                "due_back": _("Enter a date between now and 4 weeks (default 3).")
            }
    ```
  ],
)

#box(
  "Ejemplo de .env",
  [
    ```bash
    POSTGRESQL_URL="postgres://alumnodb:alumnodb@localhost:5432/psi"
    DEBUG=true
    TESTING=true
    ALLOWED_HOSTS='*'
    SECRET_KEY='4fa236d892eeeb1cbce626e8eecf097e'
    ```
  ],
)

#box(
  "Vistas CRUD partir de modelos",
  [
    ```python
    class BookCreate(PermissionRequiredMixin, CreateView):
        model = Book
        fields = "__all__"
        permission_required = "catalog.add_book"


    class BookUpdate(PermissionRequiredMixin, UpdateView):
        model = Book
        # Not recommended (potential security issue if more fields added)
        fields = "__all__"
        permission_required = "catalog.change_book"


    class BookDelete(PermissionRequiredMixin, DeleteView):
        model = Book
        success_url = reverse_lazy("books")
        permission_required = "catalog.delete_book"

        def form_valid(self, form):
            try:
                self.object.delete()
                return HttpResponseRedirect(self.success_url)
            except Exception as e:
                return HttpResponseRedirect(
                    reverse("book-delete", kwargs={"pk": self.object.pk})
                )
    ```
  ]
)
