from django.shortcuts import get_object_or_404, redirect, render
from .models import Carrito, ItemCarrito
from productos.models import Producto
import hmac
import hashlib
import requests
from django.conf import settings



def obtener_o_crear_carrito(request):
    """Obtiene el carrito del usuario o crea uno nuevo basado en la sesión si es un invitado."""
    if request.user.is_authenticated:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()  # Crea una nueva sesión si no existe
            session_key = request.session.session_key

        carrito, created = Carrito.objects.get_or_create(session_key=session_key, usuario=None)

    return carrito

def ver_carrito(request):
    """Muestra el carrito, ya sea de un usuario autenticado o un invitado."""
    carrito = obtener_o_crear_carrito(request)
    total = sum(item.subtotal() for item in carrito.items.all())
    return render(request, 'carrito/ver_carrito.html', {'carrito': carrito, 'total': total})

def agregar_al_carrito(request, producto_id):
    """Agrega un producto al carrito, asegurando que no se duplique en la primera adición."""
    carrito = obtener_o_crear_carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)
    
    item, created = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)

    if not created:  # Si el producto ya existía, sumamos 1
        item.cantidad += 1

    item.save()
    return redirect('ver_carrito')

def eliminar_del_carrito(request, item_id):
    """Elimina un item del carrito."""
    carrito = obtener_o_crear_carrito(request)
    item = get_object_or_404(ItemCarrito, id=item_id, carrito=carrito)
    item.delete()
    return redirect('ver_carrito')



def procesar_compra(request):
    # Obtener el carrito del usuario
    carrito = Carrito.objects.filter(usuario=request.user).first()
    
    if not carrito:
        return redirect('productos_lista')  # Redirige a la lista de productos si no hay carrito

    # Calcular el total
    total = sum(item.subtotal() for item in carrito.items.all())
    
    # Parámetros requeridos para la solicitud a Flow
    params = {
        "apiKey": "6CF5B5F9-38A4-4A8C-AA2A-354L8197C8E9",  # Cambiar por tu apiKey
        "commerceOrder": f"ORDENnumerorandom1",  # Usamos el ID del carrito para la orden
        "subject": f"Compra en el carrito de {request.user.username}",
        "currency": "CLP",
        "amount": total,  # Monto total de la compra
        "email": "jorgencio97@gmail.com",                   # Email del cliente
        "paymentMethod": 9,  # Medios de pago (9 = Todos)
        "urlConfirmation": "https://www.youtube.com/watch?v=-nvtT2h50sw&ab_channel=Weasperoconm%C3%BAsica-Topic",  # URL de confirmación
        "urlReturn": "https://www.youtube.com/watch?v=e2tyZw-07EM&ab_channel=Weasperoconm%C3%BAsica-Topic"  # URL de retorno
    }

    # SecretKey proporcionado (debes reemplazarlo con el real)
    secret_key = b"fe82ed8001f66e33d9922ce5f46762d6a6ad3493"

    # Ordenar los parámetros alfabéticamente por clave
    sorted_keys = sorted(params.keys())

    # Concatenar los parámetros en el formato clave+valor
    to_sign = "".join(f"{key}{params[key]}" for key in sorted_keys)

    # Generar la firma HMAC-SHA256
    signature = hmac.new(secret_key, to_sign.encode(), hashlib.sha256).hexdigest()

    # Agregar la firma a los parámetros
    params["s"] = signature

    # Realizar la solicitud POST al servicio de Flow
    base_url = "https://sandbox.flow.cl/api"
    service = "/payment/create"
    url = f"{base_url}{service}"
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=params, headers=headers)

    # Manejo de la respuesta
    if response.status_code == 200:
        data = response.json()
        redirect_url = f"{data['url']}?token={data['token']}"
        print("Orden creada exitosamente.")
        print("Redirigir al cliente a:", redirect_url)
        return redirect(redirect_url)  # Redirigir al usuario a la URL del pago
    else:
        print("Error al crear la orden. Código:", response.status_code)
        print("Detalle:", response.text)
        return render(request, 'carrito/error_pago.html', {'error': "Hubo un problema al procesar la compra. Intenta nuevamente."})