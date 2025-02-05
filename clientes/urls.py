from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.ClienteListView.as_view(), name='clientes_lista'),
    path('<int:pk>/', views.ClienteDetailView.as_view(), name='cliente_detalle'),
    path('<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente_editar'),
    path('registrar/', views.RegistrarView.as_view(), name='registrar'),
    path('login/', auth_views.LoginView.as_view(template_name='clientes/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
