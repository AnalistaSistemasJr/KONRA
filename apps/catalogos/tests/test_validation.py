from django.test import TestCase
from apps.catalogos.validation import es_numero_cuenta_valido, NUMERO_CUENTA_PATRON


class ValidationsTest(TestCase):

    def test_patron_valido(self):
        numero = "10-00-00-00-00"
        self.assertTrue(es_numero_cuenta_valido(numero), 
            f"El valor {numero} no cumple con el patrón establecido")

    def test_patron_ancho_completo(self):
        for numero in ["０１-01-01-01-01", "٠١-01-01-01-01"]:
            with self.subTest(numero=numero):
                self.assertFalse(es_numero_cuenta_valido(numero))

    def test_patron_letras_y_espacios(self):
        for numero in ["ab-01-01-01-01", " 01-01-01-01-01", "01-01-01-01-01 "]:
            with self.subTest(numero=numero):
                self.assertFalse(es_numero_cuenta_valido(numero))

    def test_patron_invalido(self):
        numeros = ["01-01-01-01-0", "01-01-01-01-01-01", "01-01-01-01-01\n", "", None]

        for text_eval in numeros:
            self.assertFalse(es_numero_cuenta_valido(text_eval), 
                f"El texto {text_eval} SÍ cumple con el patrón establecido")