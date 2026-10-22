from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.management import call_command, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from apps.catalogos.models import Cuenta, Estacion, Rubro
from unittest.mock import patch
from io import StringIO
from django.db import IntegrityError, transaction
from tempfile import NamedTemporaryFile
from apps.catalogos.management.commands.import_rubros import Command

class ModeloCataloTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rubro = Rubro.objects.create(
            rubro = "rubro_1",
            rubro_activo = True
        )

    def test_no_permite_mismo_rubro_por_mayusculas(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Rubro.objects.create(
                    rubro="RUBRO_1",
                    rubro_activo=True,
                )

    def test_no_permite_mismo_rubro_por_acentos(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Rubro.objects.create(
                    rubro="rúbro_1",
                    rubro_activo=True,
                )

    def test_genera_clave(self):
        rubro = Rubro.objects.create(
            rubro=" NÓMINA "
        )

        self.assertEqual(
            rubro.clave,
            "nomina",
        )

    def test_conserva_enie_en_clave(self):
        rubro = Rubro.objects.create(
            rubro="Peña"
        )

        self.assertEqual(
            rubro.clave,
            "peña",
        )

    def test_colapsa_espacios(self):
        rubro = Rubro.objects.create(
            rubro="Gasto     Operativo"
        )

        self.assertEqual(
            rubro.rubro,
            "Gasto Operativo",
        )

    def test_clean_detecta_duplicado_por_clave(self):
        Rubro.objects.create(rubro="rubro prueba")
        rubro_duplicado = Rubro(rubro="RUBRO PRUEBA")

        with self.assertRaises(ValidationError) as context:
            rubro_duplicado.clean()

        self.assertIn("rubro", context.exception.message_dict)
        self.assertEqual(
            context.exception.message_dict["rubro"], 
            ["Ya existe un rubro registrado con ese nombre"]
        )


class CommandCatalogoTest(TestCase):
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
            "Rubró_1,true"
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

        self.assertEqual(Rubro.objects.count(), 0)

    def test_str_retorna_nombre_rubro(self):
        rubro = Rubro.objects.create(
            rubro="Sueldos",
            rubro_activo=True,
        )

        self.assertEqual(str(rubro), "Sueldos")

    def test_importa_nomina_con_variantes(self):
        ruta = self.crear_csv(
            "rubro,rubro_activo\n"
            "Nómina,true\n"
        )

        call_command("import_rubros", ruta, aplicar=True)

        ruta2 = self.crear_csv(
            "rubro,rubro_activo\n"
            "NÓMINA,true\n"
        )

        call_command("import_rubros", ruta2, aplicar=True)
        self.assertEqual(Rubro.objects.count(), 1)

    def test_rubro_solo_espacios_full_clean(self):
        rubro = Rubro(
            rubro="     "
        )

        with self.assertRaises(ValidationError) as exc:
            rubro.full_clean()

        self.assertIn(
            "El rubro no puede quedar vacío",
            str(exc.exception)
        )

    def test_rubro_solo_espacios_no_valido(self):
        rubro = Rubro(
            rubro="     "
        )

        with self.assertRaises(ValidationError) as exc:
            rubro.save()

        self.assertIn(
            "El rubro no puede quedar vacío",
            str(exc.exception)
        )
        
    def test_rubro_vacio_en_csv_indica_fila(self):
        Rubro.objects.create(rubro="Nómina")
        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            "01-01-01-01-01,Caja,Activos,,General,true\n"
        )
        for aplicar in (False, True):
            with self.subTest(aplicar=aplicar):
                with self.assertRaises(CommandError) as exc:
                    call_command("import_cuentas", ruta, aplicar=aplicar)
                self.assertIn("Fila 2", str(exc.exception))
                self.assertIn("no existe", str(exc.exception))
                self.assertEqual(Cuenta.objects.count(), 0)