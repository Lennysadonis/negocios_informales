# apps/negocios/forms.py
from django import forms
from .models import Negocio
from django.core.exceptions import ValidationError


class NegocioForm(forms.ModelForm):

    class Meta:
        model = Negocio
        fields = [
            'nombre', 'descripcion', 'categoria', 'ciudad', 'direccion',
            'horario', 'instagram', 'facebook',
            'imagen_principal', 'imagen_1', 'imagen_2', 'imagen_3', 'imagen_4', 'imagen_5'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Ferretería El Progreso'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe tu negocio...'
            }),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Nueva Guinea, Managua, Bluefields...'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Barrio Central, frente al parque'
            }),
            'horario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lun-Vie 9AM-5PM'
            }),
            'instagram': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://instagram.com/tu_negocio'
            }),
            'facebook': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/tu_negocio'
            }),
            'imagen_principal': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'imagen_1': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'imagen_2': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'imagen_3': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'imagen_4': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'imagen_5': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'nombre': 'Nombre del negocio',
            'descripcion': 'Descripción',
            'categoria': 'Categoría',
            'ciudad': 'Ciudad',
            'direccion': 'Dirección (opcional)',
            'horario': 'Horario (opcional)',
            'instagram': 'Instagram (opcional)',
            'facebook': 'Facebook (opcional)',
            'imagen_principal': 'Foto Principal (recomendada)',
            'imagen_1': 'Foto Adicional 1',
            'imagen_2': 'Foto Adicional 2',
            'imagen_3': 'Foto Adicional 3',
            'imagen_4': 'Foto Adicional 4',
            'imagen_5': 'Foto Adicional 5',
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
                "¡Necesitas agregar tu número de WhatsApp en tu perfil para publicar un negocio! "
                "Ve a tu perfil y complétalo."
            )

        return cleaned_data