from django.test import TestCase
from django.urls import reverse
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
            numero_estacion = 1,
            estacion = "EMPRESA PRUEBA",
            razon_social = "RAZON SOCIAL PRUEBA",
            estacion_activa = True
        )
        base.update(cambios)
        return base

    def test_estacion_duplicada(self):
        Estacion.objects.create(**self.datos())
        with self.assertRaises(IntegrityError), transaction.atomic():
            Estacion.objects.create(**self.datos(estacion = "empresa prueba"))

        self.assertEqual(Estacion.objects.count(), 1)

    def test_permisos_usuario_catalogo_estacion(self):
        for perm in ["delete", "add", "change", "view"]:
            self.assertFalse(
                self.usuario_sin_grupo.has_perm(
                    f"catalogos.{perm}_estacion"
                )
            )

    def test_permiso_delete_catalogo_estacion(self):
        self.assertFalse(
            self.usuario_soporte.has_perm("catalogos.delete_estacion")
        )

    def test_accesos_sin_perm_catalogo_estacion(self):
        self.client.force_login(self.usuario_con_grupo)
        response = self.client.get(f"/admin/catalogos/estacion/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/",response["Location"])


    def test_delete_registro_catalogo_estacion(self):
        estacion_delete = Estacion.objects.create(**self.datos())
        estaciones_iniciales = Estacion.objects.count()
        self.client.force_login(self.usuario_soporte)
        response = self.client.get(f"/admin/catalogos/estacion/{estacion_delete.pk}/delete/")
        self.assertEqual(response.status_code, 403)
        estaciones_finales = Estacion.objects.count()
        self.assertEqual(estaciones_iniciales,estaciones_finales)
        