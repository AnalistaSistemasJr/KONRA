from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.catalogos.models import Estacion, Cuenta
from apps.movs.inmutable import InmutableModel

class Tipo_movimiento(models.TextChoices):
    ENTRADA = "E", "Entrada"
    SALIDA = "S", "Salida"
    
class Registro_Movimientos(InmutableModel):   
    fecha_caja = models.DateField("Fecha de caja")
    estacion = models.ForeignKey(Estacion, on_delete=models.PROTECT, related_name="movimientos")
    cuenta = models.ForeignKey(Cuenta, on_delete=models.PROTECT, related_name="movimientos")
    tipo_movimiento = models.CharField(max_length = 1, choices=Tipo_movimiento.choices)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    descripcion = models.CharField(max_length=100)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, on_delete = models.PROTECT)
    creado_en = models.DateTimeField(auto_now_add=True, editable=False)
    
    class Meta(InmutableModel.Meta):
        constraints = [
            models.CheckConstraint(
                condition=(
                        ~models.Q(monto=0)),
                name = "monto_registro_diferente_de_cero", 
                violation_error_message = "El monto debe de ser diferente de cero"
                ),
            models.CheckConstraint(
                condition=(
                        models.Q(monto__gte=-1000000)
                        & models.Q(monto__lte=1000000)),
                name = "monto_dentro_del_limite", 
                violation_error_message = "El monto supera el límite establecido"
                ),
            models.CheckConstraint(
                condition = models.Q(
                    tipo_movimiento__in = Tipo_movimiento.values
                ),
                name = "tipo_movimiento_valido"
            ),
        ]

        permissions = (
            ("ver_saldos", "Puede visualizar los saldos"),
        )



class SaldoInicial(InmutableModel):
    monto = models.DecimalField(max_digits=14, decimal_places=2)
    fecha_referencia = models.DateField()
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    creado_en = models.DateField(auto_now_add=True, editable=False)
    unico = models.BooleanField(default = True, editable = False, unique=True)

    class Meta(InmutableModel.Meta):
        constraints = [
            models.CheckConstraint(
                condition = (models.Q(monto__gte = 0)),
                name = "saldo_inicial_mayor_igual_a_cero",
                violation_error_message = "El saldo inicial debe de ser mayor o igual a cero"
            ),
            models.CheckConstraint(
                condition = (models.Q(unico=True)),
                name = "saldo_inicial_unico",
                violation_error_message = "El saldo inicial deber de ser único"
            )
        ]