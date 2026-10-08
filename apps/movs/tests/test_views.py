from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command

class UserTestAuth(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles")
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

    def test_login_correcto(self):
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