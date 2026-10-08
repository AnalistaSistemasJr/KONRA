from django.test import TestCase
from django.urls import URLPattern, URLResolver, get_resolver, reverse

PUBLICAS = {"users/login/",
            "users/logout/"}
IGNORAR_PREFIJOS = ("admin/",)


def rutas(patrones=None, prefijo=""):
    patrones = get_resolver().url_patterns if patrones is None else patrones
    for p in patrones:
        texto = prefijo + str(p.pattern)
        if isinstance(p, URLResolver):
            yield from rutas(p.url_patterns, texto)
        elif isinstance(p, URLPattern):
            yield texto


class NegarPorDefectoTests(TestCase):
    def test_ninguna_ruta_responde_200_a_un_anonimo(self):
        login = reverse("users:login")
        for ruta in rutas():
            if ruta in PUBLICAS or ruta.startswith(IGNORAR_PREFIJOS) or "<" in ruta:
                continue
            with self.subTest(ruta=ruta):
                resp = self.client.get("/" + ruta)
                self.assertNotEqual(resp.status_code, 200)
                if resp.status_code == 302:
                    self.assertIn(login, resp["Location"])