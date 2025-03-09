from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Producto
from .filters import ProductoFilter
from django_filters.views import FilterView
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render


class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'productos/producto_detalle.html'
    context_object_name = 'producto'



class ProductoGestionView(DetailView):
    model = Producto
    template_name = 'productos/producto_gestion.html'  # Nuevo nombre de plantilla
    context_object_name = 'producto'





class ProductoListView(FilterView):
    model = Producto
    template_name = 'productos/producto_lista.html'
    context_object_name = 'productos'
    filterset_class = ProductoFilter
    paginate_by = 16  # Número de productos por página

    def get_queryset(self):
        qs = super().get_queryset().order_by('nombre')
        return qs

class ProductoListViewJefe(FilterView):
    model = Producto
    template_name = 'productos/producto_lista_jefe.html'
    context_object_name = 'productos'
    filterset_class = ProductoFilter
    paginate_by = 16  # Ya está configurado para mostrar 16 elementos por página

    def get_queryset(self):
        return Producto.objects.all().order_by('nombre')  # Orden explícito



class ProductoCreateView(CreateView):
    model = Producto
    template_name = 'productos/producto_form.html'
    fields = ['nombre', 'descripcion', 'precio', 'stock', 'categoria', 'imagen']
    success_url = reverse_lazy('ProductoListViewjefe')

class ProductoUpdateView(UpdateView):
    model = Producto
    template_name = 'productos/producto_form.html'
    fields = ['nombre', 'descripcion', 'precio', 'stock', 'categoria', 'imagen']
    success_url = reverse_lazy('ProductoListViewjefe')

class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = 'productos/producto_confirmar_eliminar.html'
    success_url = reverse_lazy('ProductoListViewjefe')


