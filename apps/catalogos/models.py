from django.db import models
from django.db.models.functions import Upper
from django.contrib.auth.decorators import login_required, permission_required

class Rubro(models.Model):
    rubro = models.CharField(max_length = 100)
    rubro_activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "rubro"
        verbose_name_plural = "rubros"

    def __str__(self):
        return self.rubro

class Estacion(models.Model):
    numero_estacion = models.IntegerField()
    estacion = models.CharField(max_length = 100)
    razon_social = models.CharField(max_length = 100)
    estacion_activa = models.BooleanField(default = True)

    class Meta:
        ordering = ['numero_estacion']
        verbose_name = "estación"
        verbose_name_plural = "estaciones"

        constraints = [
            models.UniqueConstraint(
                Upper('estacion'),
                name = "estacion_nombre_unico",
                violation_error_message = "Ya existe una estación identificada con este nombre"
            ),
            models.UniqueConstraint(
                'numero_estacion',
                name = "numero_de_estacion_unico",
                violation_error_message = "Ya existe una estación identificada con este número"
            ),
            models.CheckConstraint(condition = models.Q(numero_estacion__gt = 0),
                                   name = "estacion_numero_positivo",
                                   violation_error_message = "El número de estación debe de ser positivo")
        ]

    def __str__(self):
        return f"{self.numero_estacion} - {self.estacion}"

class TipoCuenta(models.TextChoices):
    ACTIVOS  = "Activos", "Activos"
    PASIVOS  = "Pasivos", "Pasivos"
    CAPITAL  = "Capital", "Capital"
    INGRESOS = "Ingresos", "Ingresos"
    GASTOS   = "Gastos", "Gastos"
    COSTOS   = "Costos", "Costos"
    DEFAULT  = "No_definido", "No_definido"

class Cuenta(models.Model):

    numero_cuenta = models.CharField(max_length = 20)
    nombre_cuenta = models.CharField(max_length = 100)
    tipo_cuenta = models.CharField(max_length = 50, choices = TipoCuenta.choices, default=TipoCuenta.DEFAULT)
    rubro = models.ForeignKey(Rubro, on_delete = models.PROTECT)
    especificacion = models.CharField(max_length = 100, blank = True)
    cuenta_activa = models.BooleanField(default = True)

    class Meta:
        verbose_name = "cuenta"
        verbose_name_plural = "cuentas"

        constraints = [
            models.UniqueConstraint(
                'numero_cuenta',
                name = "numero_cuenta_unico",
                violation_error_message = "Ya existe una cuenta registrada con dicho número"
            ),
            models.CheckConstraint(
                condition=models.Q(
                    tipo_cuenta__in=TipoCuenta.values
                ),
                name="tipo_cuenta_valido",
            )
        ]

    def __str__(self):
        return f"{self.numero_cuenta} - {self.nombre_cuenta}"

