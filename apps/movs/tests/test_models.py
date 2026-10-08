from django.test import TestCase
from datetime import date
from decimal import Decimal

#Devuelve el modelo de autenticación del usuario, utilizada en el modelo, para cambiar settings.AUTH_USER_MODEL
from django.contrib.auth import get_user_model
#Detecta datos inválidos
from django.core.exceptions import ValidationError
#Rechazo de operaciones de la base de datos / pruebas de transacciones (si hay un dato corrupto a la mitad
#del proceso, hace rollback, limpia todo)
from django.db import IntegrityError, transaction
#Protección de errores, evita que se eliminen datos protegidos
from django.db.models.deletion import ProtectedError

#Importar modelos creados
from apps.movs.models import RegistrarCargo
from django.contrib.auth.models import Group
from django.core.management import call_command

class ModeloRegistroTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles")
        cls.usuario = get_user_model().objects.create_user(
            username="user1", 
            password = "prueba-123-xyz"
            )
        cls.usuario.groups.add(Group.objects.get(name="Auditor"))

    def datos(self, **cambios):
        base = dict(
            estacion = "ESNILOS",
            concepto = "GASTO DE PRUEBA",
            monto = Decimal("20.00"),
            fecha = date(26,1,1),
            creado_por = self.usuario
        )
        base.update(cambios)
        return base

    def test_Case_Registro(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            RegistrarCargo.objects.create(**self.datos(monto = Decimal("0.00")))


