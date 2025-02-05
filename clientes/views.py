from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Cliente

class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'clientes/cliente_lista.html'
    context_object_name = 'clientes'

class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = 'clientes/cliente_detalle.html'
    context_object_name = 'cliente'

class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    template_name = 'clientes/cliente_form.html'
    fields = ['direccion', 'telefono']
    success_url = reverse_lazy('clientes_lista')

class RegistrarView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'clientes/registrar.html'

    def form_valid(self, form):
        user = form.save()
        Cliente.objects.create(usuario=user, direccion='', telefono='')
        return redirect('login')
