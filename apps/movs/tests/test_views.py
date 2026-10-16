from django.test import TestCase
from django.urls import reverse
from django.db import connection
from datetime import date, datetime
from django.test.utils import CaptureQueriesContext
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from io import StringIO
from apps.movs.models import Registro_Movimientos, Tipo_movimiento
from apps.catalogos.models import Cuenta, Estacion, TipoCuenta, Rubro

class UserTestAuth(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", stdout=StringIO())
        cls.usuario = get_user_model().objects.create_user(
            username="user1prueba",
            password="345678uhbgt5"
        )
        cls.usuario.groups.add(Group.objects.get(name="Auditor"))
        cls.usuario_inactivo = get_user_model().objects.create_user(
             username="user2prueba",
             password="vgy8uhgfr567",
             is_active = False
        )

    def test_anonimo_es_redirigido_al_login(self):
        #Usuario anonimo intenta ingresar por medio de escribir url en barra de navegación
        response = self.client.get(reverse("movs:registro")) #Simulación que el navegador visite movs/
        self.assertEqual(response.status_code,302) #assertEqual(a, b, msg(op)), compara a == b
        self.assertIn(reverse("users:login"),response["Location"]) #busca users/login en la cadena de response

    def test_usuario_autenticado(self):
        #Login correcto y redirección correcta de usuario autenticado
        self.client.force_login(self.usuario)
        response = self.client.get(reverse("movs:registro"))
        self.assertEqual(response.status_code,200)

    def test_login_correcto(self):
        #Login correcto, usuario queda con sesión abierta, redirección por medio de url desde barra
        response = self.client.post(reverse("users:login"), {"username": "user1prueba", "password": "345678uhbgt5"})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse("movs:registro"))
        self.assertEqual(response.status_code, 200)

    def test_login_correcto_user_id(self):
        response = self.client.post(
            reverse("users:login"),
            {"username": "user1prueba", "password": "345678uhbgt5"},
        )
        self.assertRedirects(response, reverse("movs:registro"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_usuario_inactivo(self):
         #Ingreso usuario registrado pero inactivo, redirección a login al intentar entrar por barra de navegación
         response = self.client.post(reverse("users:login"), {"username": "user2prueba", "password": "vgy8uhgfr567"})
         self.assertEqual(response.status_code, 200)
         response = self.client.get(reverse("movs:registro"))
         self.assertEqual(response.status_code, 302)

    def test_login_exitoso_next_externo(self):
         #login de usuario exitoso, bloqueo de redirección a sitio no desaeado y confirmación de no encontrar la url en el url redirigido
         response = self.client.post(reverse("users:login") + "?next=https://sitio-malicioso.com",
                                     {"username": "user1prueba", "password": "345678uhbgt5"})
         
         self.assertEqual(response.status_code, 302)
         self.assertNotIn("sitio-malicioso", response["Location"])

    def test_next_interno_se_respeta(self):
        destino = reverse("admin:index")
        response = self.client.post(
            reverse("users:login") + f"?next={destino}",
            {"username": "user1prueba", "password": "345678uhbgt5"},
        )
        self.assertRedirects(response, destino, fetch_redirect_response=False)

class RegistroMovimientosViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", stdout=StringIO())
        cls.usuario_permisos = get_user_model().objects.create_user(
            username = "user_permisos",
            password = "cr567jbvt3"
        )
        cls.usuario_permisos.groups.add(Group.objects.get(name = "Auditor"))

        cls.estacion = Estacion.objects.create(
            numero_estacion = 1,
            estacion = "ESTACION 1",
            estacion_activa = True
        )

        cls.rubro = Rubro.objects.create(rubro="Sueldos")

        cls.cuenta = Cuenta.objects.create(
            numero_cuenta = "10-00-00-00-00",
            nombre_cuenta = "Cuenta testeo",
            tipo_cuenta = "Activos",
            rubro = cls.rubro,
            cuenta_activa = True
        )
    
    def test_lista_mismo_numero_consultas_con_cantidades_diferentes_movimientos(self):
        self.client.force_login(self.usuario_permisos)

        # Crear 3 movimientos
        for _ in range(3):
            Registro_Movimientos.objects.create(
                fecha_caja=date.today(),
                estacion=self.estacion,
                cuenta=self.cuenta,
                tipo_movimiento=Tipo_movimiento.ENTRADA,
                monto=100,
                descripcion="Prueba",
                creado_por=self.usuario_permisos,
            )

        with CaptureQueriesContext(connection) as ctx:
            self.client.get(reverse("movs:consulta"))

        consultas_con_3 = len(ctx)

        # Crear 10 más (total 13)
        for _ in range(10):
            Registro_Movimientos.objects.create(
                fecha_caja=date.today(),
                estacion=self.estacion,
                cuenta=self.cuenta,
                tipo_movimiento=Tipo_movimiento.ENTRADA,
                monto=100,
                descripcion="Prueba",
                creado_por=self.usuario_permisos,
            )

        with CaptureQueriesContext(connection) as ctx:
            self.client.get(reverse("movs:consulta"))

        consultas_con_13 = len(ctx)

        self.assertEqual(
            consultas_con_3,
            consultas_con_13
        )