from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.catalogos.models import Cuenta, Rubro


class ConstraintsCuentaTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rubro = Rubro.objects.create(rubro="Nómina")

    def _cuenta(self, numero):
        return Cuenta(
            numero_cuenta=numero,
            nombre_cuenta="Prueba",
            tipo_cuenta="Activos",
            rubro=self.rubro,
        )

    def test_base_rechaza_formato_invalido(self):
        invalidos = [
            "1000",
            "",
            "01-01-01-01-0",
            "01-01-01-01-01-01",
            "01-01-01-01-01\n",   # decide si ^...$ basta en PostgreSQL
            "０１-01-01-01-01",
        ]
        for numero in invalidos:
            with self.subTest(numero=numero):
                with self.assertRaises(IntegrityError):
                    with transaction.atomic():
                        Cuenta.objects.bulk_create([self._cuenta(numero)])
        self.assertEqual(Cuenta.objects.count(), 0)

    def test_base_acepta_formato_valido(self):
        Cuenta.objects.bulk_create([self._cuenta("01-01-01-01-01")])
        self.assertEqual(Cuenta.objects.count(), 1)


class ConstraintsRubroTest(TestCase):
    def test_base_rechaza_clave_vacia(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Rubro.objects.bulk_create([Rubro(rubro="x", clave="")])
        self.assertEqual(Rubro.objects.count(), 0)

    def test_save_rechaza_rubro_solo_espacios(self):
        with self.assertRaises(ValidationError):
            Rubro.objects.create(rubro="    ")
        self.assertEqual(Rubro.objects.count(), 0)

    def test_full_clean_no_falla_al_editar_el_mismo_rubro(self):
        rubro = Rubro.objects.create(rubro="Nómina")
        rubro.full_clean()            # sin cambios
        rubro.rubro = "NÓMINA"        # mismo rubro, otra escritura
        rubro.full_clean()            # exclude(pk=...) evita el falso positivo

    def test_full_clean_detecta_duplicado_distinto_pk(self):
        Rubro.objects.create(rubro="Nómina")
        with self.assertRaises(ValidationError) as exc:
            Rubro(rubro="NOMINA").full_clean()
        self.assertIn("Ya existe un rubro", str(exc.exception))