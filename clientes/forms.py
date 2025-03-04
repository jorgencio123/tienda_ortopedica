from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Cliente

class RegistroForm(UserCreationForm):
    direccion = forms.CharField(
        max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    telefono = forms.CharField(
        max_length=15, required=True, widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'direccion', 'telefono']
