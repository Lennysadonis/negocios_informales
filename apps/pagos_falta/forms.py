from django import forms
from .models import Promocion

class PromocionForm(forms.ModelForm):
    class Meta:
        model = Promocion
        fields = ['plan']
        widgets = {
            'plan': forms.RadioSelect(choices=PLANES_PROMOCION)
        }