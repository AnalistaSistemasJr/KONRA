from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class RegistrarCargo(models.Model):
    ESTACIONES = [("PUEBLITO", "PUEBLITO"), ("ESNIRU","ESNIRU"),
                ("MACIAS", "MACIAS"), ("PRO M3", "PRO M3"),
                ("TORRES", "TORRES"), ("PIRULES", "PIRULES"),
                ("JUAN PABLO", "JUAN PABLO"), ("PRADERA", "PRADERA"),
                ("PASTEUR", "PASTEUR"), ("CIRCUNVALACIÓN", "CIRCUNVALACIÓN"),
                ("ARCOS", "ARCOS"), ("BERNARDO QUINTANA", "BERNARDO QUINTANA"),
                ("SERVIMAX", "SERVIMAX"), ("ESNILOS", "ESNILOS"),
                ("HELOCAPE","HELOCAPE"), ("HIDRO", "HIDRO"), ("OSO", "OSO"),
                ("TUXPAN",  "TUXPAN"), ("SENIRI", "SENIRI")]
    estacion = models.CharField(max_length=200, choices=ESTACIONES)
    concepto = models.CharField(max_length = 100)
    monto = models.DecimalField(max_digits = 12, decimal_places = 2)
    fecha = models.DateField("Fecha de caja")
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, on_delete = models.PROTECT)
    
    class Meta:
        constraints = [
            models.CheckConstraint(condition = models.Q(monto__gt = 0) | models.Q(monto__lt = 0), 
                                   name = "monto_registro_diferente_de_cero", 
                                   violation_error_message = "El mondo debe de ser diferente de cero")
        ]
