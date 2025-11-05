# apps/usuarios/forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import Perfil, Calificacion


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


class PerfilUpdateForm(forms.ModelForm):
    # VALIDACIÓN: + seguido de 1-15 dígitos
    phone_validator = RegexValidator(
        regex=r'^\+\d{1,15}$',
        message="Formato inválido. Ej: +50557277494, +50212345678"
    )

    whatsapp = forms.CharField(
        max_length=16,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={
            'class': 'form-control whatsapp-field',
            'placeholder': 'Pon tu número aquí',
            'style': 'border: 3px solid #25D366; font-weight: bold; text-align: center; letter-spacing: 1.5px; font-size: 1.1rem;',
            'autocomplete': 'off'
        }),
        required=True,
        help_text='¡OBLIGATORIO! Ej: +50557277494, +50212345678, +1 5551234567'
    )

    class Meta:
        model = Perfil
        fields = ['foto', 'bio', 'telefono', 'whatsapp']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Cuéntanos sobre ti...'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opcional: 2222-3333'
            }),
            'foto': forms.ClearableFileInput(attrs={
                'class': 'd-none',
                'id': 'id_foto',
                'accept': 'image/*'
            })
        }

    def clean_whatsapp(self):
        wa = self.cleaned_data['whatsapp']
        wa = wa.replace(' ', '').replace('-', '')
        if not wa.startswith('+'):
            raise forms.ValidationError("Debe comenzar con +")
        if not wa[1:].isdigit():
            raise forms.ValidationError("Solo números después del +")
        if len(wa) < 6 or len(wa) > 16:
            raise forms.ValidationError("Número muy corto o largo (6-16 caracteres)")
        return wa


# FORMULARIO DE CALIFICACIÓN UNIFICADO
class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['puntuacion', 'comentario']
        widgets = {
            'puntuacion': forms.RadioSelect(attrs={'class': 'd-inline'}),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Escribe tu opinión...',
                'style': 'resize: none;'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [
            (5, '5 Estrellas - Excelente'),
            (4, '4 Estrellas - Muy bueno'),
            (3, '3 Estrellas - Bueno'),
            (2, '2 Estrellas - Regular'),
            (1, '1 Estrella - Malo'),
        ]
        self.fields['puntuacion'].widget.choices = choices
        self.fields['puntuacion'].required = True