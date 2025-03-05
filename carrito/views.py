from django.shortcuts import get_object_or_404, redirect, render
from .models import Carrito, ItemCarrito
from productos.models import Producto
import hmac
import hashlib
import requests
from django.conf import settings
import uuid
import random
import string
from django.db import IntegrityError
from transacciones.models import Transaccion
from django.views.decorators.csrf import csrf_exempt
import os
import json


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import FileResponse
from io import BytesIO



def generate_pdf(carrito, buyer, address):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y_position = height - 50
    
    c.setFont("Helvetica", 12)
    total = 0
    
    # Agregar los items y calcular total
    for item in carrito.items.all():
        line = f"{item.producto.nombre} x{item.cantidad} = {item.subtotal()}"
        c.drawString(50, y_position, line)
        y_position -= 20
        total += item.subtotal()
    
    # Espaciado entre secciones
    y_position -= 20
    
    # Agregar información del comprador
    c.drawString(50, y_position, f"Comprador: {buyer}")
    y_position -= 20
    c.drawString(50, y_position, f"Dirección: {address}")
    y_position -= 20
    
    # Agregar total
    c.drawString(50, y_position, f"Total = {total}")
    
    c.save()
    buffer.seek(0)
    return buffer

def generar_pdf_carrito(request):
    carrito = get_object_or_404(Carrito, usuario=request.user)
    buyer = request.user.username
    address = request.user.direccion # Dirección temporal
    pdf_buffer = generate_pdf(carrito, buyer, address)
    return FileResponse(pdf_buffer, as_attachment=True, filename="compra.pdf")




@csrf_exempt
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

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def confirmacion_pago(request):
    if request.method == "POST":
        # Aquí procesas la respuesta de Flow
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def ver_carrito(request):
    """Muestra el carrito, ya sea de un usuario autenticado o un invitado."""
    carrito = obtener_o_crear_carrito(request)
    total = carrito.total()  # Llamar al método total() del modelo
    return render(request, 'carrito/ver_carrito.html', {'carrito': carrito, 'total': total})


@csrf_exempt
def agregar_al_carrito(request, producto_id):
    """Agrega un producto al carrito, asegurando que no se duplique en la primera adición."""
    carrito = obtener_o_crear_carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Verificar si hay stock disponible
    if producto.stock <= 0:
        # Aquí puedes manejar la situación, como redirigir con un mensaje de error
        return redirect('ver_carrito')  # o retornar un mensaje de error

    item, created = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)

    if not created:  # Si el producto ya existía, sumamos 1
        if item.cantidad < producto.stock:  # Verifica si hay suficiente stock
            item.cantidad += 1
        else:
            # Aquí también puedes manejar el caso de falta de stock
            return redirect('ver_carrito')

    item.save()

    # Restar stock del producto
    producto.stock -= item.cantidad  # Resta la cantidad agregada al carrito
    producto.save()  # Guarda el producto con el nuevo stock

    return redirect('ver_carrito')


@csrf_exempt
def eliminar_del_carrito(request, item_id):
    """Elimina un item del carrito."""
    carrito = obtener_o_crear_carrito(request)
    item = get_object_or_404(ItemCarrito, id=item_id, carrito=carrito)
    item.delete()
    return redirect('ver_carrito')







@csrf_exempt
def procesar_compra(request):
    # Obtener el carrito del usuario
    carrito = Carrito.objects.filter(usuario=request.user).first()

    if not carrito:
        return redirect('productos_lista')  # Redirige a la lista de productos si no hay carrito

    # Calcular el total
    total = sum(item.subtotal() for item in carrito.items.all())

    # Generar un ID aleatorio único para la orden
    orden_id = str(uuid.uuid4())  # Generamos un ID único con UUID

    # Verificar si el ID ya existe en Transaccion
    if Transaccion.objects.filter(nombre=orden_id).exists():
        orden_id = str(uuid.uuid4())  # Generar un nuevo ID si ya existe

    # Guardar el ID de la transacción en el modelo Transaccion
    transaccion = Transaccion(nombre=orden_id)
    transaccion.save()

    # Datos de entrada para la solicitud de pago
    api_key = "1FA90364-F729-4167-A3D2-50FB1LD779C9"  # Reemplaza con tu apiKey
    secret_key = "4726f7297cffd829d7d366621e13bc25c5e816c9"  # Reemplaza con tu secretKey
    commerce_order = f"ORDEN{orden_id}"  # Número de orden del comercio
    subject = f"Compra en el carrito de {request.user.username}"
    currency = "CLP"
    amount = total  # Monto de la orden
    email = "ortopediaelloa@hotmail.com"  # Correo del cliente
    payment_method = 9  # Todos los medios
    url_confirmation = "https://tusitio.com/confirmacion"  # URL de confirmación
    url_return = "https://www.instagram.com/ortopedia_el_loa/"  # URL de retorno
    timeout = 3600  # Tiempo de expiración en segundos (opcional)

    # Parámetros de la solicitud
    params = {
        'apiKey': api_key,
        'commerceOrder': commerce_order,
        'subject': subject,
        'currency': currency,
        'amount': amount,
        'email': email,
        'paymentMethod': payment_method,
        'urlConfirmation': url_confirmation,
        'urlReturn': url_return,
        'timeout': timeout,
    }

    # Ordenar los parámetros por nombre de forma alfabética
    sorted_params = ''.join([f"{key}{params[key]}" for key in sorted(params)])

    # Firmar el string con el SecretKey usando HMAC SHA-256
    signature = hmac.new(secret_key.encode(), sorted_params.encode(), hashlib.sha256).hexdigest()

    # Añadir la firma al parámetro 's'
    params['s'] = signature

    # Enviar la solicitud POST a la API de Flow
    url = "https://sandbox.flow.cl/api/payment/create"
    response = requests.post(url, data=params)

    # Verificar la respuesta
    if response.status_code == 200:
        data = response.json()
        # Si la respuesta es exitosa, redirigir al cliente al URL del pago
        redirect_url = f"{data['url']}?token={data['token']}"
        print("Orden creada exitosamente. Redirigir al cliente a:", redirect_url)
        buyer = request.user.username
        address = request.user.cliente.direccion         
        pdf_buffer = generate_pdf(carrito, buyer, address)

        # Ruta correcta donde se guardarán los PDFs (por ejemplo, /media/pedidos)
        pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pedidos')
        os.makedirs(pdf_dir, exist_ok=True)  # Crea la carpeta si no existe

        # Guardar el archivo PDF en la ubicación correcta
        pdf_path = os.path.join(pdf_dir, f"compra_{orden_id}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_buffer.getvalue())
        return redirect(redirect_url)  # Redirigir al usuario a la URL del pago
    else:
        print("Error al generar la orden de pago:", response.status_code, response.text)
        # Si hubo un error, mostrar un mensaje de error
        return render(request, 'carrito/error_pago.html', {'error': "Hubo un problema al procesar la compra. Intenta nuevamente."})

    # Si llegamos aquí, significa que la redirección fue exitosa
    # Procesamiento adicional (como la generación de PDF) se puede hacer aquí si es necesario
    


    








def ver_productos(request):
    """Muestra la lista de productos junto con la cantidad total del carrito."""
    productos = Producto.objects.all()
    carrito = obtener_o_crear_carrito(request)
    return render(request, 'productos.html', {
        'productos': productos,
        'carrito': carrito,
    })






import os
from django.conf import settings
from datetime import datetime
from django.shortcuts import render

class PDFFile:
    def __init__(self, name, file_path, url):
        self.name = name
        self.file_path = file_path  # Ruta local
        self.url = url              # URL accesible desde el navegador
        self.date_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).date()

def ver_ventas(request):
    # Directorio de PDFs en la carpeta media
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pedidos')
    pdf_files = []

    if os.path.exists(pdf_dir):
        all_files = os.listdir(pdf_dir)
        pdf_files = [
            PDFFile(
                f,
                os.path.join(pdf_dir, f),
                os.path.join(settings.MEDIA_URL, 'pedidos', f)  # URL pública del archivo
            )
            for f in all_files if f.endswith('.pdf')
        ]

    # Filtrar por fecha si se proporciona en el formulario
    filter_date = request.GET.get("date")
    if filter_date:
        try:
            filter_date = datetime.strptime(filter_date, "%Y-%m-%d").date()
            pdf_files = [pdf for pdf in pdf_files if pdf.date_modified == filter_date]
        except ValueError:
            pass  # Fecha inválida, no se aplica el filtro

    return render(request, 'carrito/ventas.html', {'pdf_files': pdf_files})
