from django.test import TestCase
from django.core.management import call_command, CommandError
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.db import connection
from django.urls import reverse
from io import StringIO


class TestLogin(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('setup_roles', stdout = StringIO())

        cls.usuario_permitido = get_user_model().objects.create_user(
            username = "user2_perm", 
            password = "cftyuijhy65r"
        )
        cls.usuario_permitido.groups.add(Group.objects.get(name="Capturista"))

    def test_redireccion_a_login_despues_de_logout(self):
        # Login
        response = self.client.post(
            reverse("users:login"),
            {
                "username": "user2_perm",
                "password": "cftyuijhy65r"
            }
        )
        self.assertEqual(response.status_code, 302)

        # Logout
        response = self.client.post(reverse("users:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response["Location"])

        # Intento de acceso a vista protegida
        response = self.client.get(reverse("movs:consulta"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response["Location"])


    def test_rechazo_logout_por_get(self):
        response = self.client.post(
            reverse("users:login"), 
            {
                "username": "user2_perm", 
                "password": "cftyuijhy65r"
            }
        )
        response = self.client.get(reverse("users:logout"))
        self.assertEqual(response.status_code, 405)

        self.assertTrue("_auth_user_id" in self.client.session)

        response = self.client.get(reverse("movs:consulta"))
        self.assertEqual(response.status_code, 200)

    def test_registrar_movimiento_cache_control(self):
        self.client.post(
            reverse("users:login"),
            {
                "username": "user2_perm",
                "password": "cftyuijhy65r"
            }
        )

        response = self.client.get(reverse("movs:registro"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.has_header("Cache-Control"))

        cache_control = response["Cache-Control"]
        self.assertIn("no-store", cache_control)
        self.assertIn("no-cache", cache_control)
        self.assertIn("private", cache_control)

    def test_consulta_cache_control(self):
        self.client.post(
            reverse("users:login"),
            {
                "username": "user2_perm",
                "password": "cftyuijhy65r"
            }
        )

        response = self.client.get(reverse("movs:consulta"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.has_header("Cache-Control"))

        cache_control = response["Cache-Control"]
        self.assertIn("no-store", cache_control)
        self.assertIn("no-cache", cache_control)
        self.assertIn("private", cache_control)

    def test_sessionid_tiene_max_age_1800(self):
        self.client.post(
            reverse("users:login"),
            {
                "username": "user2_perm",
                "password": "cftyuijhy65r"
            }
        )

        response = self.client.get(reverse("movs:consulta"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("sessionid", response.cookies)
        self.assertEqual(
            int(response.cookies["sessionid"]["max-age"]),
            1800
        )

    def test_sessionid_se_renueva_en_cada_peticion(self):
        self.client.post(
            reverse("users:login"),
            {
                "username": "user2_perm",
                "password": "cftyuijhy65r"
            }
        )

        self.client.get(reverse("movs:consulta"))
        response = self.client.get(reverse("movs:consulta"))

        self.assertIn("sessionid", response.cookies)
        self.assertEqual(
            int(response.cookies["sessionid"]["max-age"]),
            1800
        )