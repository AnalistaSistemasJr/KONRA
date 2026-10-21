from django.test import SimpleTestCase

from apps.catalogos.normalize import normalizar_texto


class NormalizarRubroTest(SimpleTestCase):

    def test_elimina_acentos_y_espacios_externos(self):
        self.assertEqual(normalizar_texto(" NÓMINA "),"nomina")

    def test_colision_enie(self):
        self.assertEqual(normalizar_texto("Peña"),"peña")

    def test_colapsa_espacios_internos(self):
        self.assertEqual(normalizar_texto("Gasto    Operativo"),"gasto operativo")

    def test_texto_ya_normalizado(self):
        self.assertEqual(normalizar_texto("nomina"),"nomina")

    def test_idempotente(self):
        texto = " NÓMINA "

        self.assertEqual(
            normalizar_texto(
                normalizar_texto(texto)
            ),
            normalizar_texto(texto),
        )

    def test_cadena_vacia(self):
        self.assertEqual(normalizar_texto(""), "")

    def test_solo_espacios(self):
        self.assertEqual(normalizar_texto("   "), "")

    def test_none(self):
        self.assertEqual(normalizar_texto(None),"")

    def test_elimina_caracter_invisible(self):
        self.assertEqual(normalizar_texto("NÓ\u200bMINA"),"nomina")

    def test_normalizacion_de_la_enie(self):
        norm_1 = normalizar_texto("Peña")
        norm_2 = normalizar_texto("Pen\u0303a")
        self.assertNotEqual(norm_1, "pena")
        self.assertNotEqual(norm_2, "pena")
        self.assertEqual(norm_1, norm_2)
        self.assertEqual(norm_1, "peña")