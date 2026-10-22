from django.test import TestCase
from django.core.management import call_command, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from apps.catalogos.models import Estacion, Cuenta, Rubro
from io import StringIO
from unittest.mock import patch
from tempfile import NamedTemporaryFile
from apps.catalogos.management.commands.import_cuentas import Command

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

        cls.rubro = Rubro.objects.create(rubro="Sueldos")

    def datos(self, **cambios):
        base = dict(
            numero_cuenta = "99-99-99-99-99",
            nombre_cuenta = "Cuenta de capital",
            tipo_cuenta = "Capital",
            rubro = self.rubro,
            especificacion = "",
            cuenta_activa = True
        )
        base.update(cambios)
        return base

    def test_cuenta_duplicada(self):
        Cuenta.objects.create(**self.datos())
        with self.assertRaises(IntegrityError), transaction.atomic():
            Cuenta.objects.create(**self.datos(numero_cuenta = "99-99-99-99-99", nombre_cuenta = "Cuenta de activo"))

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

    def test_numero_cuenta_invalido(self):
        cuenta = Cuenta(**self.datos(
            numero_cuenta="cuenta 01", 
            nombre_cuenta="Cuenta de activo"
        ))
        with self.assertRaises(ValidationError):
            cuenta.full_clean()
     

class ImportarCuentasCommandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rubro = Rubro.objects.create(rubro="Sueldos")

    def crear_csv(self, contenido):
        archivo = NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            delete=False,
            encoding="utf-8-sig"
        )
        archivo.write(contenido)
        archivo.close()
        return archivo.name

    def test_simulacion_no_escribe_registros(self):
        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            "10-00-00-00-00,Caja,Activos,Sueldos,EFECTIVO,true\n"
        )

        salida = StringIO()

        call_command(
            "import_cuentas",
            ruta,
            stdout=salida
        )

        self.assertEqual(Cuenta.objects.count(), 0)
        self.assertIn("Simulación exitosa", salida.getvalue())

    def test_aplicar_crea_registros(self):
        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            "10-00-00-00-00,Caja,Activos,Sueldos,Saldos,true\n"
            "20-00-00-00-00,Bancos,Activos,Sueldos,Saldos,true\n"
        )

        call_command(
            "import_cuentas",
            ruta,
            aplicar=True,
        )

        self.assertEqual(Cuenta.objects.count(), 2)

    def test_mismo_archivo_dos_veces_no_duplica(self):
        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            "10-00-00-00-00,Caja,Activos,Sueldos,Sueldos,true\n"
            "20-00-00-00-00,Bancos,Activos,Sueldos,Sueldos,true\n"
        )

        call_command("import_cuentas", ruta, aplicar=True)

        self.assertEqual(Cuenta.objects.count(), 2)

        call_command("import_cuentas", ruta, aplicar=True)

        self.assertEqual(Cuenta.objects.count(), 2)

    def test_rollback_si_hay_fila_invalida_al_final(self):
        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            "10-00-00-00-00,Caja,Activos,Sueldos,Efectivo,true\n"
            "20-00-00-00-00,Bancos,Activos,Sueldos,Bancos,true\n"
            "30-00-00-00-00,Cuenta inválida,TIPO_INEXISTENTE,Sueldos,Prueba,true\n"
        )

        with self.assertRaises(Exception):
            call_command(
                "import_cuentas",
                ruta,
                aplicar=True,
            )

        self.assertEqual(Cuenta.objects.count(), 0)

    def test_numero_cuenta_duplicado_en_csv(self):
        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            "00-00-00-00-00,Caja,Activos,Sueldos,EFECTIVO,true\n"
            "00-00-00-00-00,Bancos,Activos,Sueldos,BANCOS,true\n"
        )

        with self.assertRaisesMessage(
            CommandError,
            "duplicado"
        ):
            call_command("import_cuentas", ruta)

        self.assertEqual(Cuenta.objects.count(), 0)

    def test_espacios_sobrantes_se_eliminan(self):
        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            " 10-00-00-00-00 , Caja General , Activos , Sueldos , EFECTIVO , true\n"
        )

        call_command(
            "import_cuentas",
            ruta,
            aplicar=True,
        )

        cuenta = Cuenta.objects.get()

        self.assertEqual(cuenta.numero_cuenta, "10-00-00-00-00")
        self.assertEqual(cuenta.nombre_cuenta, "Caja General")

    def test_espacios_no_generan_duplicados(self):
        ruta1 = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            "10-00-00-00-00,Caja,Activos,Sueldos,EFECTIVO,true\n"
        )

        ruta2 = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            " 10-00-00-00-00 ,Caja,Activos,Sueldos,EFECTIVO,true\n"
        )

        call_command("import_cuentas", ruta1, aplicar=True)
        call_command("import_cuentas", ruta2, aplicar=True)

        self.assertEqual(Cuenta.objects.count(), 1)

    def test_archivo_inexistente(self):
        with self.assertRaisesMessage(
            CommandError,
            "no existe"
        ):
            call_command(
                "import_cuentas",
                "archivo_que_no_existe.csv"
        )

    def test_encabezados_faltantes(self):
        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta\n"
            "10-00-00-00-00,Caja\n"
        )

        with self.assertRaisesMessage(
            CommandError,
            "columnas obligatorias"
        ):
            call_command(
                "import_cuentas",
                ruta
            )

    def test_error_generico_al_leer_archivo(self):
        with patch(
            "apps.catalogos.management.commands.import_cuentas.open",
            side_effect=Exception("error lectura")
        ):
            with self.assertRaisesMessage(
                CommandError,
                "Error al leer el archivo: error lectura"
            ):
                call_command(
                    "import_cuentas",
                    "archivo.csv"
                )

    def test_archivo_vacio(self):
        ruta = self.crear_csv("")

        with self.assertRaisesMessage(
            CommandError,
            "El archivo CSV está vacío o no contiene encabezados válidos."
        ):
            call_command(
                "import_cuentas",
                ruta
            )

    def test_fila_invalida_lanza_commanderror(self):
        filas = [
            {
                "numero_cuenta": "10-00-00-00-00",
                "nombre_cuenta": "Caja",
                "tipo_cuenta": "Activos",
                "rubro": "Sueldos",
                "especificacion": "Efectivo",
                "cuenta_activa": "true",
            },
            {
                "numero_cuenta": "",
                "nombre_cuenta": "Bancos",
                "tipo_cuenta": "Activos",
                "rubro": "Sueldos",
                "especificacion": "Bancos",
                "cuenta_activa": "true",
            },
        ]

        comando = Command()

        with self.assertRaises(CommandError): 
            comando.validar(filas)

    def test_error_escritura_hace_rollback(self):
        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            "10-00-00-00-00,Caja,Activos,Sueldos,Efectivo,true\n"
        )

        with patch(
            "apps.catalogos.management.commands.import_cuentas.Cuenta.objects.update_or_create",
            side_effect=Exception("fallo bd")
        ):
            with self.assertRaisesMessage(
                CommandError,
                "Error al escribir en la base de datos"
            ):
                call_command(
                    "import_cuentas",
                    ruta,
                    aplicar=True
                )

        self.assertEqual(
            Cuenta.objects.count(),
            0
        )

    def test_rollback_si_falla_segunda_fila(self):
        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            "10-00-00-00-00,Caja,Activos,Sueldos,Efectivo,true\n"
            "20-00-00-00-00,Caja 2,Pasivos,Sueldos,Efectivo,true\n"
            "30-00-00-00-00,Caja 3,Pasivos,Sueldos,Efectivo,true"
        )

        llamadas = 0

        def falla_segunda(*args, **kwargs):
            nonlocal llamadas
            llamadas += 1

            if llamadas == 2:
                raise Exception("fallo en segunda fila")

            return (
                Cuenta.objects.create(
                    numero_cuenta="10-00-00-00-00",
                    nombre_cuenta="Caja 2",
                    tipo_cuenta="Pasivos",
                    rubro=self.rubro,
                    especificacion="Efectivo",
                    cuenta_activa=True
                ),
                True,
            )

        with patch(
            "apps.catalogos.management.commands.import_cuentas.Cuenta.objects.update_or_create",
            side_effect=falla_segunda,
        ):
            with self.assertRaises(CommandError):
                call_command(
                    "import_cuentas",
                    ruta,
                    aplicar=True,
                )

        self.assertEqual(Cuenta.objects.count(), 0)

    def test_rubro_inexistente_en_simulacion(self):
        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            "10-00-00-00-00,Caja,ACTIVO,Rubro Inexistente,General,true\n"
        )

        with self.assertRaisesMessage(
            CommandError,
            "no existe"
        ):
            call_command(
                "import_cuentas",
                ruta,
            )

    def test_rubro_inexistente_con_aplicar(self):
        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            "10-00-00-00-00,Caja,ACTIVO,Rubro Inexistente,General,true\n"
        )

        with self.assertRaisesMessage(
            CommandError,
            "no existe"
        ):
            call_command(
                "import_cuentas",
                ruta,
                aplicar=True,
            )

    def test_rubro_desactivado(self):
        Rubro.objects.create(
            rubro="Nómina",
            rubro_activo=False,
        )

        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            "10-00-00-00-00,Caja,ACTIVO,Nómina,General,true\n"
        )

        with self.assertRaisesMessage(
            CommandError,
            "está desactivado"
        ):
            call_command(
                "import_cuentas",
                ruta,
            )

    def test_resuelve_rubro_normalizado(self):
        Rubro.objects.create(
            rubro="Nómina",
            rubro_activo=True,
        )

        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            "10-00-00-00-00,Caja,Activos,   NÓMINA   ,General,true\n"
        )

        call_command(
            "import_cuentas",
            ruta,
            aplicar=True,
        )
        self.assertEqual(Cuenta.objects.count(),1)

    def test_cuenta_conserva_su_rubro_aun_si_se_reordena(self):
        rubro_a = Rubro.objects.create(
            rubro="Nómina",
            rubro_activo=True,
        )

        rubro_b = Rubro.objects.create(
            rubro="Viáticos",
            rubro_activo=True,
        )

        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            "10-00-00-00-00,Cuenta A,Activos,Nómina,General,true\n"
            "20-00-00-00-00,Cuenta B,Activos,Viáticos,General,true\n"
        )

        call_command(
            "import_cuentas",
            ruta,
            aplicar=True,
        )

        self.assertEqual(
            Cuenta.objects.get(numero_cuenta="10-00-00-00-00").rubro,
            rubro_a,
        )

        self.assertEqual(
            Cuenta.objects.get(numero_cuenta="20-00-00-00-00").rubro,
            rubro_b,
        )

    def test_numero_cuenta_valido(self):
        cuenta = Cuenta(
            numero_cuenta="01-01-01-01-01",
            nombre_cuenta="Caja",
            rubro=self.rubro,
        )

        cuenta.full_clean()

    def test_numero_cuenta_invalido_en_csv(self):
        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            "1000,Caja,Activos,Nomina,General,true\n"
        )

        with self.assertRaises(CommandError) as exc:
            call_command(
                "import_cuentas",
                ruta,
                aplicar=True,
            )

        self.assertIn(
            "Número de cuenta inválido",
            str(exc.exception),
        )

        self.assertEqual(
            Cuenta.objects.count(),
            0,
        )

    def test_cada_cuenta_conserva_el_rubro_de_su_fila(self):
        rubro_a = Rubro.objects.create(rubro="Nómina")
        rubro_b = Rubro.objects.create(rubro="Viáticos")
        rubro_c = Rubro.objects.create(rubro="Servicios")

        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            "09-01-01-01-01,Cuenta A,Activos,Nómina,General,true\n"
            "01-01-01-01-01,Cuenta B,Activos,Viáticos,General,true\n"
            "05-01-01-01-01,Cuenta C,Activos,Servicios,General,true\n"
        )
        call_command("import_cuentas", ruta, aplicar=True)

        self.assertEqual(Cuenta.objects.get(numero_cuenta="09-01-01-01-01").rubro, rubro_a)
        self.assertEqual(Cuenta.objects.get(numero_cuenta="01-01-01-01-01").rubro, rubro_b)
        self.assertEqual(Cuenta.objects.get(numero_cuenta="05-01-01-01-01").rubro, rubro_c)

    def test_fila_buena_y_fila_con_rubro_inexistente_no_escribe_nada(self):
        Rubro.objects.create(rubro="Nómina")
        rubros_antes = Rubro.objects.count()
        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            "01-01-01-01-01,Caja,Activos,Nómina,General,true\n"
            "01-01-01-01-02,Banco,Activos,Inexistente,General,true\n"
        )
        for aplicar in (False, True):
            with self.subTest(aplicar=aplicar):
                with self.assertRaises(CommandError) as exc:
                    call_command("import_cuentas", ruta, aplicar=aplicar)
                self.assertIn("Fila 3", str(exc.exception))
                self.assertIn("Inexistente", str(exc.exception))
                self.assertEqual(Cuenta.objects.count(), 0)
                self.assertEqual(Rubro.objects.count(), rubros_antes)

    def test_numero_cuenta_invalido_tambien_falla_en_simulacion(self):
        Rubro.objects.create(rubro="Nómina")
        ruta = self.crear_csv(
            "numero_cuenta,nombre_cuenta,tipo_cuenta,rubro,especificacion,cuenta_activa\n"
            "01-01-01-01-01,Caja,Activos,Nómina,General,true\n"
            "1000,Banco,Activos,Nómina,General,true\n"
        )
        with self.assertRaises(CommandError) as exc:
            call_command("import_cuentas", ruta)
        self.assertIn("Fila 3", str(exc.exception))
        self.assertIn("Número de cuenta inválido", str(exc.exception))
        self.assertEqual(Cuenta.objects.count(), 0)