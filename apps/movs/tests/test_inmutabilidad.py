from django.test import TestCase
from django.urls import reverse
from datetime import datetime, date
from decimal import Decimal
from io import StringIO
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from apps.catalogos.models import Estacion, Rubro, Cuenta
from apps.movs.models import Registro_Movimientos, Tipo_movimiento


class ImutabilidadTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", stdout=StringIO())
        cls.usuario = get_user_model().objects.create_user(
            username="user1", 
            password = "prueba-123-xyz"
            )
        cls.usuario.groups.add(Group.objects.get(name="Capturista"))

        cls.estacion = Estacion.objects.create(
            numero_estacion=1,
            estacion="PUEBLITO",
            estacion_activa=True
        )
        cls.rubro = Rubro.objects.create(rubro="Sueldos")

        cls.cuenta = Cuenta.objects.create(
            numero_cuenta = "40-00-00-00-00",
            nombre_cuenta = "Ingresos",
            tipo_cuenta = "Activos",
            rubro = cls.rubro,
            cuenta_activa = True
        )

    def test_crear_movimiento_exitoso(self):
        registros_iniciales = Registro_Movimientos.objects.count()
        movimiento = Registro_Movimientos.objects.create(
            fecha_caja = date.today(),
            estacion = self.estacion,
            cuenta = self.cuenta,
            tipo_movimiento = Tipo_movimiento.SALIDA,
            monto = Decimal("-5633.70"),
            descripcion = "Prueba movimientos exitoso", 
            creado_por = self.usuario
        )
        self.assertIsNotNone(movimiento.pk)
        self.assertEqual(Registro_Movimientos.objects.count(), registros_iniciales + 1)     

    def test_permiso_denegado_cambio_de_monto(self):
        movimiento = Registro_Movimientos.objects.create(
            fecha_caja = date.today(),
            estacion = self.estacion,
            cuenta = self.cuenta,
            tipo_movimiento = Tipo_movimiento.SALIDA,
            monto = Decimal("-5633.70"),
            descripcion = "Prueba permiso denegado", 
            creado_por = self.usuario
        )        

        monto_original = movimiento.monto
        movimiento = Registro_Movimientos.objects.get(pk = movimiento.pk)
        movimiento.monto = Decimal("100.34")

        with self.assertRaises(PermissionDenied):
            movimiento.save()

        movimiento.refresh_from_db()
        self.assertEqual(movimiento.monto, monto_original)

    def test_permiso_denegado_delete_mov(self):
        movimiento = Registro_Movimientos.objects.create(
            fecha_caja = date.today(),
            estacion = self.estacion,
            cuenta = self.cuenta,
            tipo_movimiento = Tipo_movimiento.SALIDA,
            monto = Decimal("-5633.70"),
            descripcion = "Prueba permiso denegado delete", 
            creado_por = self.usuario
        )          

        registros_iniciales = Registro_Movimientos.objects.count()

        with self.assertRaises(PermissionDenied):
            movimiento.delete()

        self.assertEqual(
            registros_iniciales,
            Registro_Movimientos.objects.count()
        )

    def test_permiso_denegado_update_monto(self):
        movimiento = Registro_Movimientos.objects.create(
            fecha_caja = date.today(),
            estacion = self.estacion,
            cuenta = self.cuenta,
            tipo_movimiento = Tipo_movimiento.SALIDA,
            monto = Decimal("-5633.70"),
            descripcion = "Prueba permiso denegado", 
            creado_por = self.usuario
        )

        monto_original = movimiento.monto

        with self.assertRaises(PermissionDenied):
            Registro_Movimientos.objects.filter(
                pk = movimiento.pk
            ).update(monto = Decimal("1003.45"))

        movimiento.refresh_from_db()

        self.assertEqual(movimiento.monto, monto_original)

    def test_permiso_denegado_delete_all_movs(self):
        movimiento = Registro_Movimientos.objects.create(
            fecha_caja = date.today(),
            estacion = self.estacion,
            cuenta = self.cuenta,
            tipo_movimiento = Tipo_movimiento.SALIDA,
            monto = Decimal("-5633.70"),
            descripcion = "Prueba permiso denegado", 
            creado_por = self.usuario
        )

        registros_iniciales = Registro_Movimientos.objects.count()

        with self.assertRaises(PermissionDenied):
            Registro_Movimientos.objects.all().delete()

        self.assertEqual(
            registros_iniciales, 
            Registro_Movimientos.objects.count()
        )

    def test_save_directo_con_pk_existente_no_sobrescribe(self):
        movimiento = Registro_Movimientos.objects.create(
            fecha_caja=date.today(), estacion=self.estacion, cuenta=self.cuenta,
            tipo_movimiento=Tipo_movimiento.SALIDA, monto=Decimal("-5633.70"),
            descripcion="Original", creado_por=self.usuario,
        )
        monto_original = movimiento.monto

        duplicado = Registro_Movimientos(
            pk=movimiento.pk, fecha_caja=date.today(), estacion=self.estacion,
            cuenta=self.cuenta, tipo_movimiento=Tipo_movimiento.SALIDA,
            monto=Decimal("-1000.00"), descripcion="Intento de sobrescribir",
            creado_por=self.usuario, creado_en=timezone.now(),
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                duplicado.save()

        movimiento.refresh_from_db()
        self.assertEqual(movimiento.monto, monto_original)
        self.assertEqual(movimiento.descripcion, "Original")

    def test_permiso_denegado_bulk_update(self):
        movimiento = Registro_Movimientos.objects.create(
            fecha_caja=date.today(), estacion=self.estacion, cuenta=self.cuenta,
            tipo_movimiento=Tipo_movimiento.SALIDA, monto=Decimal("-5633.70"),
            descripcion="Prueba bulk", creado_por=self.usuario,
        )
        monto_original = movimiento.monto
        movimiento.monto = Decimal("1.00")

        with self.assertRaises(PermissionDenied):
            with transaction.atomic():
                Registro_Movimientos.objects.bulk_update([movimiento], ["monto"])


        movimiento.refresh_from_db()
        self.assertEqual(movimiento.monto, monto_original)

    def test_bulk_create_upsert_no_sobrescribe(self):
        movimiento = Registro_Movimientos.objects.create(
            fecha_caja=date.today(), estacion=self.estacion, cuenta=self.cuenta,
            tipo_movimiento=Tipo_movimiento.SALIDA, monto=Decimal("-5633.70"),
            descripcion="Original", creado_por=self.usuario,
        )
        monto_original = movimiento.monto
        duplicado = Registro_Movimientos(
            pk=movimiento.pk, fecha_caja=date.today(), estacion=self.estacion,
            cuenta=self.cuenta, tipo_movimiento=Tipo_movimiento.SALIDA,
            monto=Decimal("-1.00"), descripcion="Upsert", creado_por=self.usuario,
        )
        with self.assertRaises(PermissionDenied):
            Registro_Movimientos.objects.bulk_create(
                [duplicado], update_conflicts=True,
                unique_fields=["pk"], update_fields=["monto"],
            )
        movimiento.refresh_from_db()
        self.assertEqual(movimiento.monto, monto_original)
