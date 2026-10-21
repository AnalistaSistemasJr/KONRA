import importlib

from django.apps import apps as django_apps
from django.test import TestCase

from apps.catalogos.models import Rubro


class Migracion0010Test(TestCase):

    def test_conflicto_no_modifica_datos(self):
        r1 = Rubro.objects.bulk_create([
            Rubro(rubro="Nómina", clave="x1"),
            Rubro(rubro="Nomina", clave="x2"),
        ])

        mig = importlib.import_module(
            "apps.catalogos.migrations.0010_poblar_claves_rubros"
        )

        with self.assertRaises(RuntimeError) as exc:
            mig.poblar_claves(django_apps, None)

        self.assertIn("Nómina", str(exc.exception))
        self.assertIn("Nomina", str(exc.exception))

        self.assertEqual(
            Rubro.objects.get(rubro="Nómina").clave,
            "x1"
        )

        self.assertEqual(
            Rubro.objects.get(rubro="Nomina").clave,
            "x2"
        )

    def test_recalcula_claves_normalizadas(self):
        Rubro.objects.bulk_create([
            Rubro(rubro="Nómina", clave="aaa"),
            Rubro(rubro="Pen\u0303a", clave="bbb"),
        ])

        mig = importlib.import_module("apps.catalogos.migrations.0010_poblar_claves_rubros")

        mig.poblar_claves(django_apps, None)

        self.assertEqual(
            Rubro.objects.get(rubro="Nómina").clave,
            "nomina"
        )

        self.assertEqual(
            Rubro.objects.get(rubro="Pen\u0303a").clave,
            "peña"
        )

    def test_rubro_vacio_lanza_error(self):
        Rubro.objects.bulk_create([
            Rubro(rubro="", clave="xxx"),
        ])

        mig = importlib.import_module(
            "apps.catalogos.migrations.0010_poblar_claves_rubros"
        )

        with self.assertRaises(RuntimeError) as exc:
            mig.poblar_claves(django_apps, None)

        self.assertIn(
            "clave vacía",
            str(exc.exception)
        )

        self.assertEqual(
            Rubro.objects.get().clave,
            "xxx"
        )

    def test_normalizar_congelado(self):
        mig = importlib.import_module(
            "apps.catalogos.migrations.0010_poblar_claves_rubros"
        )

        self.assertEqual(
            mig._normalizar_congelado("Nómina"),
            "nomina"
        )

        self.assertEqual(
            mig._normalizar_congelado("Peña"),
            "peña"
        )

        self.assertEqual(
            mig._normalizar_congelado("  GASTOS   VARIOS "),
            "gastos varios"
        )

        self.assertEqual(
            mig._normalizar_congelado(None),
            ""
        )

    def test_normalizar_congelado_elimina_caracter_cf(self):
        mig = importlib.import_module(
            "apps.catalogos.migrations.0010_poblar_claves_rubros"
        )

        self.assertEqual(
            mig._normalizar_congelado("No\u200Bmina"),
            "nomina"
        )