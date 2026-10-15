from django.test import TestCase
import sys, traceback
from io import StringIO
from datetime import date, datetime, timedelta
from decimal import Decimal
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.contrib.auth.models import Group
from django.core.management import call_command
from apps.movs.models import Registro_Movimientos, Tipo_movimiento
from apps.catalogos.models import Estacion, Cuenta, TipoCuenta

class ModeloRegistroTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", stdout=StringIO())
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
            tipo_cuenta = "Activos",
            cuenta_activa = True
        )

        cls.estacion_inactiva = Estacion.objects.create(
            numero_estacion=2,
            estacion="JACAL",
            estacion_activa=False
        )

        cls.cuenta_inactiva = Cuenta.objects.create(
            numero_cuenta = "90-00-00-00-00",
            nombre_cuenta = "Otros",
            cuenta_activa = False
        )
    
    def datos(self, **cambios):
        base = dict(
            fecha_caja=date.today(),
            estacion=self.estacion,
            cuenta=self.cuenta,
            tipo_movimiento=Tipo_movimiento.ENTRADA,
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
            tipo_movimiento=Tipo_movimiento.ENTRADA,
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
        movimiento = Registro_Movimientos.objects.create(
            fecha_caja = date.today(),
            estacion = self.estacion,
            cuenta = self.cuenta,
            tipo_movimiento = Tipo_movimiento.SALIDA,
            monto = Decimal("-5633.70"),
            descripcion = "Prueba llenado automatico", 
            creado_por = self.usuario
        ) 
        registros_finales = Registro_Movimientos.objects.count()
        self.assertEqual(registros_iniciales + 1, registros_finales)
        self.assertIsNotNone(movimiento.creado_en)
        self.assertIsInstance(movimiento.creado_en, datetime)

    def test_movimiento_fecha_futura(self):
        self.client.force_login(self.usuario)
        registros_iniciales = Registro_Movimientos.objects.count()
        response = self.client.post(reverse("movs:registro"),{
            "fecha_caja" : date.today() + timedelta(days = 1),
            "estacion" : self.estacion.pk,
            "cuenta" : self.cuenta.pk,
            "tipo_movimiento" : Tipo_movimiento.ENTRADA,
            "monto" : Decimal("-4523.00"),
            "descripcion" : "Salida de dinero", 
        })

        self.assertEqual(response.status_code, 200)
        registros_finales = Registro_Movimientos.objects.count()
        self.assertEqual(registros_iniciales, registros_finales)

    def test_movimiento_registrado_correctamente(self):
        self.client.force_login(self.usuario)
        registros_iniciales = Registro_Movimientos.objects.count()
        response = self.client.post(reverse("movs:registro"),{
            "fecha_caja" : date.today(),
            "estacion" : self.estacion.pk,
            "cuenta" : self.cuenta.pk,
            "tipo_movimiento" : Tipo_movimiento.ENTRADA,
            "monto" : Decimal("-452.00"),
            "descripcion" : "Salida de dinero", 
        })

        #self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("movs:registro"))
        registros_finales = Registro_Movimientos.objects.count()
        self.assertEqual(registros_iniciales + 1, registros_finales)

    def test_registro_con_estacion_yo_cuenta_inactiva(self):
        registros_iniciales = Registro_Movimientos.objects.count()
        self.client.force_login(self.usuario)
        response = self.client.post(reverse("movs:registro"),{
            "fecha_caja" : date.today(),
            "estacion" : self.estacion_inactiva,
            "cuenta" : self.cuenta_inactiva,
            "tipo_movimiento" : "Salida",
            "monto" : Decimal("1000.00"),
            "descripcion" : "Registro con datos de catalogo inactivos.", 
        })
        self.assertEqual(response.status_code, 200)  
        registros_finales = Registro_Movimientos.objects.count()
        self.assertEqual(registros_iniciales, registros_finales)       

    def test_registro_con_estacion_yo_cuenta_inexistente(self):
        registros_iniciales = Registro_Movimientos.objects.count()
        self.client.force_login(self.usuario)
        response = self.client.post(reverse("movs:registro"),{
            "fecha_caja" : date.today(),
            "estacion" : "ESTACION_NO_EXISTE",
            "cuenta" : "1234-5678-9101",
            "tipo_movimiento" : "Salida",
            "monto" : Decimal("1000.00"),
            "descripcion" : "Registro con estación y cuanta no registrados", 
        })
        self.assertEqual(response.status_code, 200)  
        registros_finales = Registro_Movimientos.objects.count()
        self.assertEqual(registros_iniciales, registros_finales) 

    def test_registro_con_validaciones_modelo(self):
        registros_iniciales = Registro_Movimientos.objects.count()
        self.client.force_login(self.usuario)
        #Más decimales y dígitos del límite
        #Descripción sobrepasa los límites
        response = self.client.post(reverse("movs:registro"),{
            "fecha_caja" : date.today(),
            "estacion" : self.estacion,
            "cuenta" : self.cuenta,
            "tipo_movimiento" : Tipo_movimiento.ENTRADA,
            "monto" : Decimal("1023456789342.520"),
            "descripcion" : "Validación de reglas desde campos del modelo"
            "También se agrega una descripción que supera el límite de lo establecido", 
        })
        self.assertEqual(response.status_code, 200)  
        registros_finales = Registro_Movimientos.objects.count()
        self.assertEqual(registros_iniciales, registros_finales)       
