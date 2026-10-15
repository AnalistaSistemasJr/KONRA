from django.test import TestCase
from django.urls import reverse
from django.core.management import call_command, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import IntegrityError, transaction
from apps.catalogos.models import Estacion, Cuenta
from unittest.mock import patch
from io import StringIO
from tempfile import NamedTemporaryFile
from apps.catalogos.management.commands.import_estaciones import Command

class ModeloCatalogoTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", stdout=StringIO())
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


class ImportarEstacionesCommandTest(TestCase):

    def crear_csv(self, contenido):
        archivo = NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            delete=False,
            encoding="utf-8"
        )
        archivo.write(contenido)
        archivo.close()
        return archivo.name

    def test_simulacion_no_crea_registros(self):
        ruta = self.crear_csv(
            "numero_estacion,estacion,razon_social,estacion_activa\n"
            "100,ESTACION NORTE,GASOLINERA SA,true\n"
        )

        salida = StringIO()

        call_command(
            "import_estaciones",
            ruta,
            stdout=salida
        )

        self.assertEqual(Estacion.objects.count(), 0)

        self.assertIn(
            "Simulación exitosa",
            salida.getvalue()
        )

    def test_aplicar_crea_estaciones(self):
        ruta = self.crear_csv(
            "numero_estacion,estacion,razon_social,estacion_activa\n"
            "100,ESTACION NORTE,GASOLINERA SA,true\n"
            "101,ESTACION SUR,GASOLINERA SA,true\n"
        )

        call_command(
            "import_estaciones",
            ruta,
            aplicar=True
        )

        self.assertEqual(
            Estacion.objects.count(),
            2
        )

    def test_mismo_archivo_dos_veces_no_duplica(self):
        ruta = self.crear_csv(
            "numero_estacion,estacion,razon_social,estacion_activa\n"
            "100,ESTACION NORTE,GASOLINERA SA,true\n"
            "101,ESTACION SUR,GASOLINERA SA,true\n"
        )

        call_command(
            "import_estaciones",
            ruta,
            aplicar=True
        )

        self.assertEqual(
            Estacion.objects.count(),
            2
        )

        call_command(
            "import_estaciones",
            ruta,
            aplicar=True)

        self.assertEqual(
            Estacion.objects.count(),
            2
        )

    def test_fila_invalida_sin_numero_estacion(self):
        ruta = self.crear_csv(
            "numero_estacion,estacion,razon_social,estacion_activa\n"
            ",ESTACION NORTE,GASOLINERA SA,true\n"
        )

        with self.assertRaises(CommandError):
            call_command(
                "import_estaciones",
                ruta
            )

        self.assertEqual(
            Estacion.objects.count(),
            0
        )

    def test_rollback_si_hay_filas_invalidas(self):
        ruta = self.crear_csv(
            "numero_estacion,estacion,razon_social,estacion_activa\n"
            "100,ESTACION NORTE,GASOLINERA SA,true\n"
            "200,ESTACION ESTE,GASOLINERA SA,false\n"
            "NUM_EST,ESTACION SUR,GASOLINERA SA,true\n"
        )

        with self.assertRaises(Exception):
            call_command(
                "import_estaciones",
                ruta,
                aplicar=True,
            )

        self.assertEqual(Estacion.objects.count(), 0)

    def test_rollback_si_falla_segunda_fila(self):
        ruta = self.crear_csv(
            "numero_estacion,estacion,razon_social,estacion_activa\n"
            "100,ESTACION NORTE,GASOLINERA SA,true\n"
            "101,ESTACION SUR,GASOLINERA SA,true\n"
        )

        llamadas = 0

        def falla_segunda(*args, **kwargs):
            nonlocal llamadas
            llamadas += 1

            if llamadas == 2:
                raise Exception("fallo en segunda fila")

            return (
                Estacion.objects.create(
                    numero_estacion=100,
                    estacion="ESTACION NORTE",
                    razon_social="GASOLINERA SA",
                    estacion_activa=True,
                ),
                True,
            )

        with patch(
            "apps.catalogos.management.commands.import_estaciones.Estacion.objects.update_or_create",
            side_effect=falla_segunda,
        ):
            with self.assertRaises(CommandError):
                call_command(
                    "import_estaciones",
                    ruta,
                    aplicar=True,
                )

        self.assertEqual(Estacion.objects.count(), 0)

    def test_numero_estacion_duplicado(self):
        ruta = self.crear_csv(
            "numero_estacion,estacion,razon_social,estacion_activa\n"
            "100,ESTACION NORTE,GASOLINERA SA,true\n"
            "100,ESTACION SUR,GASOLINERA SA,true\n"
        )

        with self.assertRaisesMessage(
            CommandError,
            "duplicado"
        ):
            call_command(
                "import_estaciones",
                ruta
            )

        self.assertEqual(
            Estacion.objects.count(),
            0
        )

    def test_espacios_sobrantes_se_eliminan(self):
        ruta = self.crear_csv(
            "numero_estacion,estacion,razon_social,estacion_activa\n"
            " 100, ESTACION NORTE , GASOLINERA SA , true\n"
        )

        call_command(
            "import_estaciones",
            ruta,
            aplicar=True
        )

        estacion = Estacion.objects.get()

        self.assertEqual(
            estacion.numero_estacion,
            100
        )

        self.assertEqual(
            estacion.estacion,
            "ESTACION NORTE"
        )

        self.assertEqual(
            estacion.razon_social,
            "GASOLINERA SA"
        )

    def test_espacios_no_generan_duplicados(self):
        ruta1 = self.crear_csv(
            "numero_estacion,estacion,razon_social,estacion_activa\n"
            "100,ESTACION NORTE,GASOLINERA SA,true\n"
        )

        ruta2 = self.crear_csv(
            "numero_estacion,estacion,razon_social,estacion_activa\n"
            " 100 ,ESTACION NORTE,GASOLINERA SA,true\n"
        )

        call_command(
            "import_estaciones",
            ruta1,
            aplicar=True
        )

        call_command(
            "import_estaciones",
            ruta2,
            aplicar=True
        )

        self.assertEqual(
            Estacion.objects.count(),
            1
        )

    def test_encabezados_faltantes(self):
        ruta = self.crear_csv(
            "numero_estacion,estacion\n"
            "100,ESTACION NORTE\n"
        )

        with self.assertRaisesMessage(
            CommandError,
            "columnas obligatorias"
        ):
            call_command(
                "import_estaciones",
                ruta
            )

    def test_archivo_vacio(self):
        ruta = self.crear_csv("")

        with self.assertRaisesMessage(
            CommandError,
            "vacío"
        ):
            call_command(
                "import_estaciones",
                ruta
            )

    def test_error_generico_al_leer_archivo(self):
        with patch(
            "apps.catalogos.management.commands.import_estaciones.open",
            side_effect=Exception("error de lectura")
        ):
            with self.assertRaisesMessage(
                CommandError,
                "Error al leer el archivo: error de lectura"
            ):
                call_command(
                    "import_estaciones",
                    "archivo.csv"
                )

    def test_error_escritura_hace_rollback(self):
        ruta = self.crear_csv(
            "numero_estacion,estacion,razon_social,estacion_activa\n"
            "100,ESTACION NORTE,GASOLINERA SA,true\n"
        )

        with patch(
            "apps.catalogos.management.commands.import_estaciones.Estacion.objects.update_or_create",
            side_effect=Exception("fallo bd")
        ):
            with self.assertRaisesMessage(
                CommandError,
                "Error al escribir en la base de datos"
            ):
                call_command(
                    "import_estaciones",
                    ruta,
                    aplicar=True
                )

        self.assertEqual(
            Estacion.objects.count(),
            0
        )

    def test_leer_archivo_inexistente(self):
        comando = Command()

        with self.assertRaisesMessage(
            CommandError,
            "El archivo 'archivo_inexistente.csv' no existe."
        ):
            comando.leer("archivo_inexistente.csv")