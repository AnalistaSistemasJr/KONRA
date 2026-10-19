from django.test import TestCase
from django.core.management import call_command, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from apps.catalogos.models import Cuenta, Estacion, Rubro
from unittest.mock import patch
from io import StringIO
from tempfile import NamedTemporaryFile
from apps.catalogos.management.commands.import_rubros import Command


class ModeloCatalogoTest(TestCase):
    @classmethod
    def setUpClass(cls):
        return super().setUpClass()

    def crear_csv(self, contenido):
        archivo = NamedTemporaryFile(
            mode = "w",
            suffix = ".csv",
            delete = False,
            encoding = "utf-8-sig"
        )

        archivo.write(contenido)
        archivo.close
        return archivo.name

    def test_simulacion_sin_registros(self):
        ruta = self.crear_csv(
            "rubro,rubro_activo\n"
            "rubro_1,true\n"
            "rubro_2,true"
        )

        salida = StringIO()

        call_command(
            "import_rubros",
            ruta,
            stdout = salida
        )

        self.assertEqual(Rubro.objects.count(), 0)
        self.assertIn("Simulación exitosa", salida.getvalue())

    def test_aplicar_crea_rubros(self):
        ruta = self.crear_csv(
            "rubro,rubro_activo\n"
            "rubro_1,true\n"
            "rubro_2,true"
        )

        call_command(
            "import_rubros",
            ruta,
            aplicar = True
        )

        self.assertEqual(Rubro.objects.count(), 2)

    def test_error_lectura_archivo_vacio(self):
        ruta = self.crear_csv("")

        with self.assertRaisesMessage(
            CommandError,
            "vacío"
        ):
            call_command(
                "import_rubros",
                ruta
            )

    def test_error_generico_al_leer_archivo(self):
        with patch(
            "apps.catalogos.management.commands.import_rubros.open",
            side_effect=Exception("error de lectura")
        ):
            with self.assertRaisesMessage(
                CommandError,
                "Error al leer el archivo: error de lectura"
            ):
                call_command(
                    "import_rubros",
                    "archivo.csv"
                )

    def test_carga_archivo_dos_veces(self):
        ruta = self.crear_csv(
            "rubro,rubro_activo\n"
            "rubro_1,true\n"
            "rubro_2,true"
        )

        call_command(
            "import_rubros",
            ruta,
            aplicar = True
        )

        self.assertEqual(Rubro.objects.count(),2)
        call_command(
            "import_rubros",
            ruta,
            aplicar = True
        )
        self.assertEqual(Rubro.objects.count(),2)

    def test_leer_archivo_inexistente(self):
        comando = Command()

        with self.assertRaisesMessage(
            CommandError,
            "El archivo 'archivo_inexistente.csv' no existe."
        ):
            comando.leer("archivo_inexistente.csv")

    def test_archivo_sin_columnas_obligatorias(self):
        ruta = self.crear_csv(
            "nombre,rubro_activo\n" 
            "rubro prueba,true"
        )

        with self.assertRaisesMessage(CommandError, "El CSV no contiene las columnas obligatorias"):
            call_command("import_rubros", ruta, aplicar = True)

    def test_archivo_datos_faltantes(self):
        ruta = self.crear_csv(
            "rubro,rubro_activo\n" 
            ",true"
        )

        with self.assertRaisesMessage(CommandError, "campo obligatorio"):
            call_command("import_rubros", ruta, aplicar = True)

        self.assertEqual(Rubro.objects.count(), 0)

    def test_registros_duplicados(self):
        ruta = self.crear_csv(
            "rubro,rubro_activo\n"
            "rubro_1,true\n"
            "rubró_1,true"
        )

        with self.assertRaisesMessage(CommandError, "duplicado en el CSV"):
            call_command("import_rubros", ruta, aplicar = True)    

        self.assertEqual(Rubro.objects.count(), 0)

    def test_rollback_si_falla_segunda_fila(self):
        ruta = self.crear_csv(
            "rubro,rubro_activo\n"
            "rubro_1,true\n"
            "rubro_2,true\n"
            "rubro_3,true\n"
            "rubro_4,true"
        )

        llamadas = 0

        def falla_segunda(*args, **kwargs):
            nonlocal llamadas
            llamadas += 1

            if llamadas == 2:
                raise Exception("fallo en segunda fila")

            return (
                Rubro.objects.create(
                    rubro="rubro_1",
                    rubro_activo=True,
                ),
                True,
            )

        with patch(
            "apps.catalogos.management.commands.import_rubros.Rubro.objects.update_or_create",
            side_effect=falla_segunda,
        ):
            with self.assertRaises(CommandError):
                call_command(
                    "import_rubros",
                    ruta,
                    aplicar=True,
                )

        self.assertEqual(Estacion.objects.count(), 0)

    def test_str_retorna_nombre_rubro(self):
        rubro = Rubro.objects.create(
            rubro="Sueldos",
            rubro_activo=True,
        )

        self.assertEqual(str(rubro), "Sueldos")