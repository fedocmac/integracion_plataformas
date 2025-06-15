from django import forms
from .models import Categoria


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']  # Campos del modelo a incluir
        labels = {
            'nombre': 'Nombre de la categoría',
            'descripcion': 'Descripción de la categoría'
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemeplo: Sonido'
            }),
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemeplo: Accesorios de audio como parlantes y audifonos.'
            })
        }
        error_messages = {
            'nombre': {
                'required': 'Este campo es obligatorio',
                'max_length': 'El nombre no puede tener más de %(limit_value)d caracteres.',
            },
            'descripcion': {
                'required': 'Este campo es obligatorio',
                'max_length': 'La descripción no puede tener más de %(limit_value)d caracteres.',
            }
        }