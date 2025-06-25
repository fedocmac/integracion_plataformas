from django import forms
from .models import Categoria
from django.core.exceptions import ValidationError



class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['name', 'description']  # <-- Usa los nombres reales
        labels = {
            'name': 'Nombre de la categoría',
            'description': 'Descripción de la categoría'
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Sonido'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Accesorios de audio como parlantes y audífonos.'
            })
        }
        error_messages = {
            'name': {
                'required': 'Este campo es obligatorio',
                'max_length': 'El nombre no puede tener más de %(limit_value)d caracteres.',
            },
            'description': {
                'required': 'Este campo es obligatorio',
                'max_length': 'La descripción no puede tener más de %(limit_value)d caracteres.',
            }
        }
    def clean_name(self):
        name = self.cleaned_data['name']
        qs = Categoria.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe una categoría con este nombre.")
        return name