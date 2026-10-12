from django.test import TestCase
from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.contrib.auth.models import Group
from django.core.management import call_command
from apps.movs.models import Registro_Movimientos
from apps.catalogos.models import Estacion, Cuenta

class ModeloRegistroTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles")
        cls.usuario = get_user_model().objects.create_user(
            username="user1", 
            password = "prueba-123-xyz"
            )
        cls.usuario.groups.add(Group.objects.get(name="Auditor"))

        cls.estacion = Estacion.objects.create(
            numero_estacion=1,
            estacion="PUEBLITO",
            estacion_activa=True
        )

        cls.cuenta = Cuenta.objects.create(
            numero_cuenta = "40-00-00-00-00",
            nombre_cuenta = "Ingresos",
            cuenta_activa = True
        )
    
    def datos(self, **cambios):
        base = dict(
            fecha_caja=date.today(),
            estacion=self.estacion,
            cuenta=self.cuenta,
            tipo_movimiento=Registro_Movimientos.Tipo.ENTRADA,
            monto=Decimal("20.00"),
            descripcion="GASTO DE PRUEBA",
            creado_por=self.usuario,
        )
        base.update(cambios)
        return base    

    def test_Mov_Cargo_Cero(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Registro_Movimientos.objects.create(**self.datos(monto = Decimal("0.00")))

    def test_no_permite_borrar_estacion_con_movimientos(self):
        Registro_Movimientos.objects.create(
            fecha_caja=date.today(),
            estacion=self.estacion,
            cuenta=self.cuenta,
            tipo_movimiento=Registro_Movimientos.Tipo.ENTRADA,
            monto=100,
            descripcion="Prueba",
            creado_por=self.usuario,
        )

        with self.assertRaises(ProtectedError):
            self.estacion.delete()

        self.assertTrue(
            Estacion.objects.filter(pk=self.estacion.pk).exists()
        )     

    def test_confirmacion_llenada_campos_automaticos(self):
        registros_iniciales = Registro_Movimientos.objects.count()
        Registro_Movimientos.objects.create(
            fecha_caja = date.today(),
            estacion = self.estacion,
            cuenta = self.cuenta,
            tipo_movimiento = Registro_Movimientos.Tipo.SALIDA,
            monto = "-2335.28",
            descripcion = "Prueba llenado automatico", 
        ) 
        registros_finales = Registro_Movimientos.objects.count()
        self.assertEqual(registros_iniciales + 1, registros_finales)
