from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Producto
from .filters import ProductoFilter
from django_filters.views import FilterView



class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'productos/producto_detalle.html'
    context_object_name = 'producto'



class ProductoGestionView(DetailView):
    model = Producto
    template_name = 'productos/producto_gestion.html'  # Nuevo nombre de plantilla
    context_object_name = 'producto'


class ProductoListViewJefe(FilterView):
    model = Producto
    template_name = 'productos/producto_lista_jefe.html'  # Nuevo nombre de plantilla
    context_object_name = 'productos'
    filterset_class = ProductoFilter

class ProductoListView(FilterView):
    model = Producto
    template_name = 'productos/producto_lista.html'
    context_object_name = 'productos'
    filterset_class = ProductoFilter

class ProductoCreateView(CreateView):
    model = Producto
    template_name = 'productos/producto_form.html'
    fields = ['nombre', 'descripcion', 'precio', 'stock', 'categoria', 'imagen']
    success_url = reverse_lazy('productos_lista')

class ProductoUpdateView(UpdateView):
    model = Producto
    template_name = 'productos/producto_form.html'
    fields = ['nombre', 'descripcion', 'precio', 'stock', 'categoria', 'imagen']
    success_url = reverse_lazy('productos_lista')

class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = 'productos/producto_confirmar_eliminar.html'
    success_url = reverse_lazy('productos_lista')


