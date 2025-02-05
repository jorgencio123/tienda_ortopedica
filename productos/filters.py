import django_filters
from .models import Producto

class ProductoFilter(django_filters.FilterSet):
    # Definir el filtro de precio con etiquetas personalizadas
    precio__gte = django_filters.NumberFilter(field_name='precio', lookup_expr='gte', label='Precio mínimo')
    precio__lte = django_filters.NumberFilter(field_name='precio', lookup_expr='lte', label='Precio máximo')
    
    # Filtro para categoría
    categoria = django_filters.CharFilter(field_name='categoria', lookup_expr='exact', label='Categoría')
    
    # Filtro de stock disponible
    stock__gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte', label='Stock mínimo')

    class Meta:
        model = Producto
        fields = ['precio__gte', 'precio__lte', 'categoria', 'stock__gte']
