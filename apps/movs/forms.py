from django.forms import ModelForm, ValidationError, forms
from apps.movs.models import RegistrarCargo
from django.utils import timezone

class RegistrarForm(ModelForm):
    class Meta:
        model = RegistrarCargo
        fields = ['estacion', 'concepto', 'monto', 'fecha']

    def clean_fecha(self):
        fecha = self.cleaned_data["fecha"]
        if fecha > timezone.localdate():
            raise forms.ValidationError("La fecha no puede ser futura.")
        return fecha