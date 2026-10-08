from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.core.management import call_command



class PermissionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles")       
        cls.user_wo_perm = get_user_model().objects.create_user(
            username = "user1_perm", password = "rt678ijhgt5"
        )
        cls.user_w_perm = get_user_model().objects.create_user(
                    username = "user2_perm", password = "cftyuijhy65r"
                )
        cls.user_w_perm.groups.add(Group.objects.get(name="Auditor"))
        
    def test_user_sin_grupo_restriccion(self):
        self.client.force_login(self.user_wo_perm)
        response = self.client.get(reverse("movs:registro"))
        self.assertEqual(response.status_code, 403)

    def test_user_con_permiso(self):
        self.client.force_login(self.user_w_perm)
        response = self.client.get(reverse("movs:registro"))
        self.assertEqual(response.status_code, 200)

    def test_user_tipo_permisos(self):
        value = self.user_w_perm.has_perm("movs.delete_registrarcargo")
        self.assertEqual(value, False)