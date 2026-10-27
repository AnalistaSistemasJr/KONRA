from django.test import TestCase
from apps.movs.models import Registro_Movimientos
from django.core.management import call_command, CommandError
from django.contrib.auth.models import Group
from django.contrib import admin
from django.test import RequestFactory
from io import StringIO

ROLES_ESPERADOS = {
    "Capturista": {"view_registro_movimientos", "add_registro_movimientos"},
    "Auditor": {"view_registro_movimientos"},
}

class PermisosRegitroMovs(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('setup_roles', stdout = StringIO())

    def test_comando_crea_roles(self):
        call_command('setup_roles', stdout = StringIO())
        self.assertGreater(Group.objects.count(), 0) 

    def test_nombres_de_roles(self):
        self.assertEqual(
            set(Group.objects.values_list("name", flat=True)),
            {"Capturista", "Auditor", "Soporte"},
        )

    def test_permisos_exactos_por_rol(self):
        for nombre, esperados in ROLES_ESPERADOS.items():
            with self.subTest(rol=nombre):
                grupo = Group.objects.get(name=nombre)
                actuales = set(grupo.permissions.values_list("codename", flat=True))
                self.assertEqual(actuales, esperados)

    def test_no_delete_en_registro_movs(self):
        for grupo in Group.objects.all():
            for permiso in grupo.permissions.filter(content_type__app_label="movs"):
                self.assertFalse(
                    permiso.codename.startswith(("delete_", "change_")),
                    f"El rol '{grupo.name}' tiene el permiso '{permiso.codename}', el cual no está permitido"
                )

    def test_soporte_sin_permisos_de_movs(self):
        grupo = Group.objects.get(name="Soporte")
        permisos = set(grupo.permissions.filter(
            content_type__app_label="movs").values_list("codename", flat=True))
        self.assertEqual(permisos, set())


    def test_movimientos_no_estan_en_el_admin(self):
        self.assertNotIn(Registro_Movimientos, admin.site._registry)
