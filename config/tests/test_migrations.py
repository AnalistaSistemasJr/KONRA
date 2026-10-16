from io import StringIO
from django.core.management import call_command
from django.test import TestCase


class MigracionesTest(TestCase):
    def test_no_hay_migraciones_pendientes(self):
        salida = StringIO()
        try:
            call_command(
                "makemigrations", "--check", "--dry-run",
                stdout=salida, stderr=salida,
            )
        except SystemExit:
            self.fail(
                "Hay cambios en los modelos sin su migración:\n" + salida.getvalue()
            )