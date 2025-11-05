# apps/productos/forms.py
from django import forms
from .models import Producto, CategoriaProducto
from apps.negocios.models import Negocio
from django.core.exceptions import ValidationError


MONEDAS = [
    ('C$', 'Córdoba (C$)'),
    ('USD', 'Dólar (USD)'),
    ('EUR', 'Euro (€)'),
]


class ProductoForm(forms.ModelForm):
    moneda = forms.ChoiceField(
        choices=MONEDAS,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='C$',
        label='Moneda'
    )

    class Meta:
        model = Producto
        fields = [
            'nombre', 'descripcion', 'precio', 'categoria', 'stock', 'negocio',
            'tipo_precio', 'moneda',
            'imagen_principal', 'imagen_1', 'imagen_2', 'imagen_3', 'imagen_4', 'imagen_5'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Camiseta negra talla M'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Nueva, original, envío gratis...'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'placeholder': '15.99'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'value': '1'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'negocio': forms.Select(attrs={'class': 'form-select'}),
            'tipo_precio': forms.Select(attrs={'class': 'form-select'}),
            'imagen_principal': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'imagen_1': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'imagen_2': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'imagen_3': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'imagen_4': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'imagen_5': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Auto-focus
        self.fields['nombre'].widget.attrs.update({'autofocus': 'autofocus'})

        # Categorias
        self.fields['categoria'].queryset = CategoriaProducto.objects.all()

        # Negocios del usuario
        if self.user:
            self.fields['negocio'].queryset = Negocio.objects.filter(propietario=self.user, aprobado=True)
        else:
            self.fields['negocio'].queryset = Negocio.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        if not self.user or not self.user.perfil.whatsapp:
            raise ValidationError(
                "¡Necesitas agregar tu WhatsApp en tu perfil para publicar productos! "
                "Ve a tu perfil y complétalo."
            )
        return cleaned_data