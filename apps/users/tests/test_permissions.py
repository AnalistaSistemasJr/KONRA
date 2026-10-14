from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from django.core.management import call_command, CommandError
from unittest.mock import patch
from io import StringIO

class PermissionsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", stdout=StringIO())     
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

    @patch.dict(
        "apps.users.management.commands.setup_roles.ROLES",
        {
            "Auditor": [
                "movs.permiso_inventado_123456"
            ]
        },
        clear=True,
    )
    def test_error_si_permiso_no_existe(self):

        with self.assertRaises(CommandError) as exc:
            call_command("setup_roles", stdout=StringIO())

        self.assertEqual(
            str(exc.exception),
            "El permiso movs.permiso_inventado_123456 no existe en el rol Auditor"
        )

    @patch.dict(
        "apps.users.management.commands.setup_roles.ROLES",
        {},
        clear=True,
    )
    def test_crea_rol_nuevo(self):

        permiso = Permission.objects.first()

        with patch.dict(
            "apps.users.management.commands.setup_roles.ROLES",
            {
                "Rol_nuevo": [
                    f"{permiso.content_type.app_label}.{permiso.codename}"
                ]
            },
            clear=True,
        ):
            call_command("setup_roles", stdout=StringIO())

        self.assertTrue(
            Group.objects.filter(name="Rol_nuevo").exists()
        )

    def test_actualiza_permisos_de_rol_existente(self):

        grupo = Group.objects.create(
            name="Rol_super_admin"
        )

        permiso = Permission.objects.first()

        with patch.dict(
            "apps.users.management.commands.setup_roles.ROLES",
            {
                "Rol_super_admin": [
                    f"{permiso.content_type.app_label}.{permiso.codename}"
                ]
            },
            clear=True,
        ):
            call_command("setup_roles", stdout=StringIO())

        grupo.refresh_from_db()

        self.assertEqual(
            grupo.permissions.count(),
            1
        )

        self.assertIn(
            permiso,
            grupo.permissions.all()
        )