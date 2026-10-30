from django.core.management.base import BaseCommand, CommandError
from apps.movs.models import SaldoInicial
from datetime import datetime, date
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from django.contrib.auth import get_user_model
from apps.movs.validacion_si import parsear_saldo_inicial

class Command(BaseCommand):
    help = "Inserta el monto inicial para comenzar un proceso"

    def add_arguments(self, parser):
        parser.add_argument("monto", type=str, help="Monto del saldo inicial")
        parser.add_argument("--fecha", type=str, required = True, help="Fecha inicio: aaaa-m-d")
        parser.add_argument("--usuario", type=str, required = True, help="Nombre de quien realiza el movimiento")
        parser.add_argument("--aplicar", action="store_true", help = "Escribir en la base")
        parser.add_argument("--confirmar-monto", type=str, help="Confirmar monto a ingresar")

    def validar(self, **options):
        try:
            monto = parsear_saldo_inicial(options['monto'])
        except ValueError as exc:
            raise CommandError(str(exc))

        try:
            fecha = datetime.strptime(options["fecha"],"%Y-%m-%d").date()
        except ValueError:
            raise CommandError("La fecha debe tener formato AAAA-MM-DD")

        if fecha > timezone.localdate():
            raise CommandError("La fecha no debe de ser futura")

        User = get_user_model()

        try:
            usuario = User.objects.get(username = options['usuario'])
        except User.DoesNotExist:
            raise CommandError(
                f"El usuario {options['usuario']} no existe"
            )

        if not usuario.is_active:
            raise CommandError(
                f"El usuario {options['usuario']} no está activo"
            )

        if SaldoInicial.objects.exists():
            raise CommandError(
                "Ya existe un saldo inicial registrado."
            )

        return monto, fecha, usuario
        
    def handle(self, *args, **options):
        monto, fecha, usuario = self.validar(**options)
        aplicar = options['aplicar']
        monto_confirmacion = options['confirmar_monto']

        db_name = settings.DATABASES["default"]["NAME"]

        if not aplicar:
            self.stdout.write("")
            self.stdout.write("Simulación")
            self.stdout.write(f"Monto   : {monto}")
            self.stdout.write(f"Fecha   : {fecha}")
            self.stdout.write(f"Usuario : {usuario.username}")
            self.stdout.write(f"Base    : {db_name}")
            self.stdout.write("")
            return

        if monto_confirmacion is None:
            raise CommandError("Para aplicar, escribe el monto nuevamente con --confirmar-monto")

        try:
            monto_confirmacion = parsear_saldo_inicial(monto_confirmacion)
        except ValueError as exc:
            raise CommandError(str(exc))

        if monto != monto_confirmacion:
            raise CommandError(
                "Los montos ingresados deben de coincidir"
            )

        with transaction.atomic():

            SaldoInicial.objects.create(
                monto=monto,
                fecha_referencia=fecha,
                creado_por=usuario,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "¡Se ha configurado el saldo inicial con éxito!"
                )
            )