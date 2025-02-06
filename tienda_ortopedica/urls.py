from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView  # Importa RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('carrito/', include('carrito.urls')),
    path('productos/', include('productos.urls')),
    path('clientes/', include('clientes.urls')),
    path('', RedirectView.as_view(url='/clientes/login/', permanent=False)),


    # ... otras rutas
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
