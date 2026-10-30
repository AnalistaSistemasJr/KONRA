from django.test import TestCase
from decimal import Decimal
from datetime import date
from django.core.management import call_command, CommandError
from apps.movs.management.commands import config_si
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group
from django.db import IntegrityError, transaction
from django.contrib.auth import get_user_model
from apps.movs.models import SaldoInicial
from io import StringIO
from apps.movs.validacion_si import parsear_saldo_inicial, _PATRON_SALDO_INICIAL


class SaldoInicialTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", stdout=StringIO())
        cls.usuario = get_user_model().objects.create_superuser(
            username="user.prueba", 
            password = "prueba-123-xyz"
        )

    def test_monto_si_valido(self):
        montos_si = ["52000000.78", " 677.97 ", "1.0", "14", "0", "1.61", "123456789012.54", "100\n"]
        for monto in montos_si:
            resultado = parsear_saldo_inicial(monto)
            self.assertIsInstance(resultado, Decimal)

    def test_monto_si_invalido(self):
        montos_si = ["abc", "NaN", "Infinity", "-5", "1e3", "1_000", 
                     "1,000.00", "100.001", "1000000000000", "１２３"]
        for monto in montos_si:
            with self.assertRaises(ValueError):
                parsear_saldo_inicial(monto)

    def test_suma_de_montos(self):
        resultado = parsear_saldo_inicial("0.32") + parsear_saldo_inicial("131.21")
        self.assertIsInstance(resultado, Decimal)
        self.assertEqual(resultado, Decimal("131.53"))

    def test_segunda_fila_con_bulk_create_lanza_integrity_error(self):
        SaldoInicial.objects.bulk_create([
            SaldoInicial(
                monto = "1000.00",
                fecha_referencia = "2026-10-01",
                creado_por = self.usuario,
            )
        ])

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SaldoInicial.objects.bulk_create([
                    SaldoInicial(
                        monto = "2000.00",
                        fecha_referencia = "2026-10-02",
                        creado_por = self.usuario,
                    )
                ])

    def test_unico_false_lanza_integrity_error(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SaldoInicial.objects.bulk_create([
                    SaldoInicial(
                        monto="1000.00",
                        fecha_referencia="2026-10-01",
                        creado_por=self.usuario,
                        unico=False,
                    )
                ])

    def _fila(self, **extra):
        datos = dict(monto=Decimal("10.00"), fecha_referencia=date(2026, 10, 1),
                    creado_por=self.usuario)
        datos.update(extra)
        return SaldoInicial(**datos)

    def test_base_rechaza_segunda_fila(self):
        SaldoInicial.objects.create(monto=Decimal("10.00"),
            fecha_referencia=date(2026, 10, 1), creado_por=self.usuario)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SaldoInicial.objects.bulk_create([self._fila(monto=Decimal("5.00"))])
        self.assertEqual(SaldoInicial.objects.count(), 1)

    def test_base_rechaza_unico_falso(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SaldoInicial.objects.bulk_create([self._fila(unico=False)])
        self.assertEqual(SaldoInicial.objects.count(), 0)

    def test_base_rechaza_monto_negativo(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SaldoInicial.objects.bulk_create([self._fila(monto=Decimal("-1.00"))])
        self.assertEqual(SaldoInicial.objects.count(), 0)

class ComandoSaldoInicialTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", stdout=StringIO())
        cls.usuario = get_user_model().objects.create_superuser(
            username="user.prueba", 
            password = "prueba-123-xyz"
        )


    def test_simulacion_no_escribe(self):
        salida = StringIO()
        call_command(
            "config_si",
            "345.65",
            fecha = "2026-10-29",
            usuario = "user.prueba",
            stdout = salida
        )
        self.assertEqual(SaldoInicial.objects.count(), 0)
        self.assertIn("Simulación", salida.getvalue())

    def test_aplicar_con_confirmacion_crea_el_saldo(self):
        call_command(
            "config_si", "1000.00",
            fecha="2026-10-01", usuario="user.prueba",
            aplicar=True, confirmar_monto="1000.00",
            stdout=StringIO(),
        )
        saldo = SaldoInicial.objects.get()
        self.assertEqual(saldo.monto, Decimal("1000.00"))
        self.assertEqual(saldo.fecha_referencia, date(2026, 10, 1))
        self.assertEqual(saldo.creado_por, self.usuario)

    def test_aplicar_confirmacion_saldo_diferente(self):
        with self.assertRaisesMessage(
            CommandError,
            "Los montos ingresados deben de coincidir",
        ):
            salida = StringIO()
            call_command(
                "config_si", "1000.00",
                fecha="2026-10-01", usuario="user.prueba",
                aplicar=True, confirmar_monto="1001.00",
                stdout=salida,
            )

        self.assertEqual(SaldoInicial.objects.count(), 0)

    def test_aplicar_sin_confirmacion_saldo(self):
        with self.assertRaisesMessage(
            CommandError,
            "escribe el monto nuevamente",
        ):
            salida = StringIO()
            call_command(
                "config_si", "1000.00",
                fecha="2026-10-01", usuario="user.prueba",
                aplicar=True,
                stdout=salida,
            )

        self.assertEqual(SaldoInicial.objects.count(), 0)

    def test_aplicar_confirmacion_monto_no_valido(self):
        with self.assertRaisesMessage(
            CommandError,
            "Monto del saldo inicial inválido",
        ):
            salida = StringIO()
            call_command(
                "config_si", "1000.00",
                fecha="2026-10-01", usuario="user.prueba",
                aplicar=True, confirmar_monto="10e10",
                stdout=salida,
            )

        self.assertEqual(SaldoInicial.objects.count(), 0)

    def test_aplicar_monto_inicial_vacio(self):
        with self.assertRaisesMessage(
            CommandError,
            "El monto del saldo inicial es obligatorio",
        ):
            salida = StringIO()
            call_command(
                "config_si", "",
                fecha="2026-10-01", usuario="user.prueba",
                aplicar=True, confirmar_monto="",
                stdout=salida,
            )

        self.assertEqual(SaldoInicial.objects.count(), 0)

    def test_saldo_existente_no_se_guarda(self):
        call_command(
            "config_si", "1000.00",
            fecha="2026-10-01", usuario="user.prueba",
            aplicar=True, confirmar_monto="1000.00",
            stdout=StringIO(),
        )
        self.assertEqual(SaldoInicial.objects.count(), 1)

        with self.assertRaisesMessage(
            CommandError,
            "Ya existe un saldo inicial registrado",
        ):
            salida = StringIO()
            call_command(
                "config_si", "1000.00",
                fecha="2026-10-01", usuario="user.prueba",
                aplicar=True, confirmar_monto="1000.00",
                stdout=salida,
            )

        self.assertEqual(SaldoInicial.objects.count(), 1)


    def test_entradas_invalidas_no_escriben(self):

        usuario_inactivo = get_user_model().objects.create_superuser(
            username="user.inactivo", 
            password = "prueba-123-xyz",
            is_active = False
        )

        casos = [
            {
                "nombre": "monto invalido",
                "args": {
                    "monto": "abc",
                    "fecha": "2026-10-29",
                    "usuario": "user.admin",
                },
            },
            {
                "nombre": "fecha mal formada",
                "args": {
                    "monto": "100.00",
                    "fecha": "29-10-2026",
                    "usuario": "user.admin",
                },
            },
            {
                "nombre": "fecha futura",
                "args": {
                    "monto": "100.00",
                    "fecha": "2099-01-01",
                    "usuario": "user.admin",
                },
            },
            {
                "nombre": "usuario inexistente",
                "args": {
                    "monto": "100.00",
                    "fecha": "2026-10-29",
                    "usuario": "no.existe",
                },
            },
            {
                "nombre": "usuario inactivo",
                "args": {
                    "monto": "100.00",
                    "fecha": "2026-10-29",
                    "usuario": usuario_inactivo.username,
                },
            },
        ]

        for caso in casos:
            with self.subTest(caso=caso["nombre"]):
                with self.assertRaises(CommandError):
                    call_command(
                        "config_si",
                        caso["args"]["monto"],
                        fecha=caso["args"]["fecha"],
                        usuario=caso["args"]["usuario"],
                    )

                self.assertEqual(
                    SaldoInicial.objects.count(),
                    0,
                )

    def test_save_existente_lanza_permission_denied(self):
        call_command(
            "config_si",
            "1000.00",
            fecha="2026-10-01",
            usuario="user.prueba",
            aplicar=True,
            confirmar_monto="1000.00",
        )

        saldo = SaldoInicial.objects.get()

        saldo.monto = 2000

        with self.assertRaises(PermissionDenied):
            saldo.save()

    def test_delete_lanza_permission_denied(self):
        call_command(
            "config_si",
            "1000.00",
            fecha="2026-10-01",
            usuario="user.prueba",
            aplicar=True,
            confirmar_monto="1000.00",
        )

        saldo = SaldoInicial.objects.get()

        with self.assertRaises(PermissionDenied):
            saldo.delete()

    def test_saldo_inmutable(self):
        call_command(
            "config_si",
            "1000.00",
            fecha="2026-10-01",
            usuario="user.prueba",
            aplicar=True,
            confirmar_monto="1000.00",
        )

        saldo = SaldoInicial.objects.get()
        monto_original = saldo.monto

        saldo.monto = 9999

        with self.assertRaises(PermissionDenied):
            saldo.save()

        saldo.refresh_from_db()

        self.assertEqual(
            saldo.monto,
            monto_original,
        )


class PermisosEscrituraModelo(TestCase):
    def test_ningun_grupo_tiene_permisos_saldo_inicial(self):
        call_command("setup_roles", stdout=StringIO())
        grupos = Group.objects.all()
        for grupo in grupos:
            with self.subTest(grupo=grupo.name):
                self.assertFalse(
                    grupo.permissions.filter(
                        content_type__app_label="movs",
                        content_type__model="saldoinicial",
                    ).exists()
                )

