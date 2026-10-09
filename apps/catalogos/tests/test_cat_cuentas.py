from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import IntegrityError, transaction
from apps.catalogos.models import Estacion, Cuenta

class ModeloCatalogoTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('setup_roles')
        cls.usuario_sin_grupo = get_user_model().objects.create_user(
            username = "user1",
            password = "ft6789okjh"
        )
        cls.usuario_con_grupo = get_user_model().objects.create_user(
            username = "user2",
            password = "cr567uhde3"
        )
        cls.usuario_con_grupo.groups.add(Group.objects.get(name = "Auditor"))

        cls.usuario_soporte = get_user_model().objects.create_user(
            username = "user_soporte",
            password = "ftuhbv45678uh",
            is_staff = True
        )    
        cls.usuario_soporte.groups.add(Group.objects.get(name = "Soporte"))

    def datos(self, **cambios):
        base = dict(
            numero_cuenta = "00-00-00-00-00",
            nombre_cuenta = "Cuenta de capital",
            tipo_cuenta = "Capital",
            rubro = "capital contable",
            especificacion = "",
            cuenta_activa = True
        )
        base.update(cambios)
        return base

    def test_cuenta_duplicada(self):
        Cuenta.objects.create(**self.datos())
        with self.assertRaises(IntegrityError), transaction.atomic():
            Cuenta.objects.create(**self.datos(numero_cuenta = "00-00-00-00-00", nombre_cuenta = "Cuenta de activo"))

        self.assertEqual(Cuenta.objects.count(), 1)

    def test_permisos_usuario_catalogo_cuenta(self):
        for perm in ["delete", "add", "change", "view"]:
            self.assertFalse(
                self.usuario_sin_grupo.has_perm(
                    f"catalogos.{perm}_cuenta"
                )
            )

    def test_permiso_delete_catalogo_cuenta(self):
        self.assertFalse(
            self.usuario_soporte.has_perm("catalogos.delete_cuenta")
        )

    def test_accesos_sin_perm_catalogo_cuenta(self):
        self.client.force_login(self.usuario_con_grupo)
        response = self.client.get(f"/admin/catalogos/cuenta/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/",response["Location"])


    def test_delete_registro_catalogo_cuenta(self):
        cuenta_delete = Cuenta.objects.create(**self.datos())
        cuentas_iniciales = Cuenta.objects.count()
        self.client.force_login(self.usuario_soporte)
        response = self.client.get(f"/admin/catalogos/cuenta/{cuenta_delete.pk}/delete/")
        self.assertEqual(response.status_code, 403)
        cuentas_finales = Cuenta.objects.count()
        self.assertEqual(cuentas_iniciales,cuentas_finales)
        