# apps/servicios/forms.py
from django import forms
from .models import Servicio, CategoriaServicio
from django.core.exceptions import ValidationError


class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = [
            'nombre', 'descripcion', 'categoria', 'ciudad', 'precio',
            'tipo_precio', 'moneda', 'experiencia', 'disponible',
            'imagen_principal', 'imagen_1', 'imagen_2', 'imagen_3', 'imagen_4', 'imagen_5'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Plomería 24/7'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Reparo fugas, instalo tuberías...'
            }),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Nueva Guinea, Managua, Bluefields...'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '50.00'
            }),
            'tipo_precio': forms.Select(attrs={'class': 'form-select'}),
            'moneda': forms.Select(attrs={'class': 'form-select'}),
            'experiencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '5 años'
            }),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'imagen_principal': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'imagen_1': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'imagen_2': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'imagen_3': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'imagen_4': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'imagen_5': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
        labels = {
            'nombre': 'Nombre del Servicio',
            'descripcion': 'Descripción',
            'categoria': 'Categoría',
            'ciudad': 'Ciudad',
            'precio': 'Precio',
            'tipo_precio': 'Tipo de Precio',
            'moneda': 'Moneda',
            'experiencia': 'Experiencia',
            'disponible': 'Disponible ahora',
            'imagen_principal': 'Foto Principal',
            'imagen_1': 'Foto 2',
            'imagen_2': 'Foto 3',
            'imagen_3': 'Foto 4',
            'imagen_4': 'Foto 5',
            'imagen_5': 'Foto 6',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'autofocus': 'autofocus'})

        # Hacer todas las imágenes opcionales
        for field in ['imagen_principal', 'imagen_1', 'imagen_2', 'imagen_3', 'imagen_4', 'imagen_5']:
            self.fields[field].required = False

    def clean(self):
        cleaned_data = super().clean()

        # VALIDAR WHATSAPP EN PERFIL
        if not self.user or not self.user.perfil.whatsapp:
            raise ValidationError(
                "¡Necesitas agregar tu WhatsApp en tu perfil para publicar servicios! "
                "Ve a tu perfil y complétalo."
            )

        return cleaned_data