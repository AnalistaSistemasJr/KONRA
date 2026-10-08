from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from apps.users.roles import ROLES

class Command(BaseCommand):
    help = "Crea o actualiza los roles y sus permisos"
    def handle(self, *args, **options):
        for nombre, etiquetas in ROLES.items():
            grupo, _ = Group.objects.get_or_create(name = nombre)
            permisos = []
            for etiqueta in etiquetas:
                app_label, codename = etiqueta.split(".")
                try:
                    permisos.append(
                        Permission.objects.get(
                            content_type__app_label = app_label, codename = codename
                        )
                    )
                except Permission.DoesNotExist:
                    raise CommandError(f"El permiso {etiqueta} no existe en el rol {nombre}")
            grupo.permissions.set(permisos)
            self.stdout.write(f"Rol {nombre}: {len(permisos)} permiso(s)")