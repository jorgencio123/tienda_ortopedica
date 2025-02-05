from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductoListView.as_view(), name='productos_lista'),
    path('nuevo/', views.ProductoCreateView.as_view(), name='producto_crear'),
    path('producto-lista-jefe/', views.ProductoListViewJefe.as_view(), name='ProductoListViewjefe'),
    path('<int:pk>/', views.ProductoDetailView.as_view(), name='producto_detalle'),
    path('<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='producto_editar'),
    path('<int:pk>/eliminar/', views.ProductoDeleteView.as_view(), name='producto_eliminar'),
    path('gestion/<int:pk>/', views.ProductoGestionView.as_view(), name='producto_gestion'),

]
