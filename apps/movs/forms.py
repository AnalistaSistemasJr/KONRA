from django.forms import ModelForm, ValidationError, forms
from apps.movs.models import RegistrarMovimiento
from django.utils import timezone
from apps.catalogos.models import Cuenta, Estacion

class RegistrarForm(ModelForm):
    class Meta:
        model = RegistrarMovimiento
        fields = ['fecha_caja', 'estacion', 'cuenta', 'tipo_movimiento', 'monto', 'descripcion' ]

    def clean_fecha(self):
        fecha = self.cleaned_data["fecha_caja"]
        if fecha > timezone.localdate():
            raise forms.ValidationError("La fecha no puede ser futura.")
        return fecha

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["estacion"].queryset = Estacion.objects.filter(estacion_activa=True)
        self.fields["cuenta"].queryset = Cuenta.objects.filter(cuenta_activa=True)