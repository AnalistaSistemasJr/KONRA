from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.contrib.auth.models import Group
from datetime import date, timedelta
from io import StringIO
from apps.movs.models import Registro_Movimientos, Tipo_movimiento
from apps.catalogos.models import Estacion, Cuenta, TipoCuenta

class RegistrarFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", stdout=StringIO())
        cls.usuario_sin_grupo = get_user_model().objects.create_user(
            username = "user1_no_grupo",
            password = "hjkjgt6787tf"
        )
        cls.usuario_con_grupo = get_user_model().objects.create_user(
            username = "user2_con_grupo",
            password = "cftyujnbvfe4567"
        )
        cls.usuario_con_grupo.groups.add(Group.objects.get(name = "Visualizador"))
        cls.usuario_con_permisos = get_user_model().objects.create_user(
            username = "user3_con_permisos",
            password = "dr78ijr45tf"
        )
        cls.usuario_con_permisos.groups.add(Group.objects.get(name = "Auditor"))

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

    def test_anonimo_get_post_capturar(self):
        registros_iniciales = Registro_Movimientos.objects.count()

        #GET
        response = self.client.get(reverse("movs:registro"))
        self.assertEqual(response.status_code, 302)

        #POST
        response = self.client.post(
            reverse("movs:registro"),
            {
                "estacion": "HIDRO",
                "concepto": "prueba registro con post",
                "monto": 340,
                "fecha": date.today()
            })
        self.assertEqual(response.status_code, 302)
        registros_finales = Registro_Movimientos.objects.count()
        self.assertEqual(registros_iniciales, registros_finales, "Se registro un movimiento con un usuario no autenticado")


    def test_user_sin_grupo_captura(self):
        registros_iniciales = Registro_Movimientos.objects.count()
        self.client.force_login(self.usuario_sin_grupo)
        response = self.client.get(reverse("movs:registro"))
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse("movs:registro"),
            {
                "estacion": "HIDRO",
                "concepto": "prueba registro con post",
                "monto": 340,
                "fecha": date.today()
            })
        self.assertEqual(response.status_code, 403)
        registros_finales = Registro_Movimientos.objects.count()
        self.assertEqual(registros_iniciales, registros_finales, "Se registro un movimiento con un usuario sin rol")

    def test_user_con_grupo_sin_permisos_captura(self):
        registros_iniciales = Registro_Movimientos.objects.count()
        self.client.force_login(self.usuario_con_grupo)
        response = self.client.get(reverse("movs:registro"))
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse("movs:registro"),
            {
                "estacion": "HIDRO",
                "concepto": "prueba registro con post",
                "monto": 340,
                "fecha": date.today()
            })
        self.assertEqual(response.status_code, 403)
        registros_finales = Registro_Movimientos.objects.count()
        self.assertEqual(registros_iniciales, registros_finales, "Se registro un movimiento con un usuario sin permisos")

    def test_user_con_permisos_visualizacion(self):
        self.client.force_login(self.usuario_con_permisos)
        response = self.client.get(reverse("movs:registro"))
        self.assertEqual(response.status_code, 200)

    def test_user_con_permisos_captura(self):
        registros_iniciales = Registro_Movimientos.objects.count()
        self.client.force_login(self.usuario_con_permisos)
        response = self.client.post(
            reverse("movs:registro"),
            {
                "fecha_caja": date.today(),
                "estacion": self.estacion.pk,
                "cuenta": self.cuenta.pk,
                "tipo_movimiento": Tipo_movimiento.ENTRADA,
                "monto": "420.00",
                "descripcion": "prueba registro con post usuario con permisos",
            }
        )
        self.assertEqual(response.status_code, 302)
        registros_finales = Registro_Movimientos.objects.count()
        self.assertEqual(registros_iniciales + 1, registros_finales, "No se registró el movimientos del usuario con acceso")
        registro = Registro_Movimientos.objects.latest("id")
        self.assertEqual(registro.creado_por, self.usuario_con_permisos, "ID de usuario diferente al logeado")

    def test_user_con_permisos_modifica_id_user_captura(self):
        registros_iniciales = Registro_Movimientos.objects.count()
        self.client.force_login(self.usuario_con_permisos)
        response = self.client.post(
            reverse("movs:registro"),
            {
                "fecha_caja": date.today(),
                "estacion": self.estacion.pk,
                "cuenta": self.cuenta.pk,
                "tipo_movimiento": Tipo_movimiento.ENTRADA,
                "monto": "420.00",
                "descripcion": "prueba registro con post usuario con permisos",
            }
        )
        self.assertEqual(response.status_code, 302)
        registros_finales = Registro_Movimientos.objects.count()
        self.assertEqual(registros_iniciales + 1, registros_finales, "No se registró el movimientos del usuario con acceso")
        registro = Registro_Movimientos.objects.latest("id")
        self.assertEqual(registro.creado_por, self.usuario_con_permisos, "ID de usuario modificado por el usuario")

    def test_user_con_permisos_dato_invalido_captura(self):
        registros_iniciales = Registro_Movimientos.objects.count()
        self.client.force_login(self.usuario_con_permisos)
        response = self.client.post(
            reverse("movs:registro"),
            {
                "fecha_caja": date.today(),
                "estacion": self.estacion.pk,
                "cuenta": self.cuenta.pk,
                "tipo_movimiento": Tipo_movimiento.ENTRADA,
                "monto": "0.00",
                "descripcion": "prueba registro con post usuario con permisos",
            }
        )
        self.assertEqual(response.status_code, 200)
        registros_finales = Registro_Movimientos.objects.count()
        self.assertEqual(registros_iniciales, registros_finales, "No se registró el movimientos del usuario con acceso")
        self.assertTrue(response.context["form"].errors)

    def test_post_sin_csrf_token(self):
        registros_iniciales = Registro_Movimientos.objects.count()
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.usuario_con_permisos)

        response = cliente.post(
            reverse("movs:registro"),
            {
                "estacion": "HIDRO",
                "concepto": "Prueba CSRF",
                "monto": 420,
                "fecha": date.today(),
            }
        )

        self.assertEqual(response.status_code, 403)
        registros_finales = Registro_Movimientos.objects.count()

        self.assertEqual(registros_iniciales, registros_finales )

    def test_validacion_restriccion_monto_limite(self):
        registros_iniciales = Registro_Movimientos.objects.count()
        self.client.force_login(self.usuario_con_permisos)
        for monto in ["2000000.00","-3000000.00"]:
            response = self.client.post(
                reverse("movs:registro"),
                {
                    "fecha_caja": date.today(),
                    "estacion": self.estacion.pk,
                    "cuenta": self.cuenta.pk,
                    "tipo_movimiento": Tipo_movimiento.ENTRADA,
                    "monto": monto,
                    "descripcion": "prueba registro con post usuario con permisos",
                }
            )
            self.assertEqual(response.status_code, 200)
        self.assertEqual(Registro_Movimientos.objects.count(), registros_iniciales)

    def test_validacion_restriccion_monto_aceptado(self):
        registros_iniciales = Registro_Movimientos.objects.count()
        self.client.force_login(self.usuario_con_permisos)
        for monto in ["200000.00","-300000.00"]:
            response = self.client.post(
                reverse("movs:registro"),
                {
                    "fecha_caja": date.today(),
                    "estacion": self.estacion.pk,
                    "cuenta": self.cuenta.pk,
                    "tipo_movimiento": Tipo_movimiento.ENTRADA,
                    "monto": monto,
                    "descripcion": "prueba registro con post usuario con permisos",
                }
            )
            self.assertEqual(response.status_code, 302)
        self.assertGreater(Registro_Movimientos.objects.count(), registros_iniciales)