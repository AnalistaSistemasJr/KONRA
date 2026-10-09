import csv
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.catalogos.models import Cuenta


class Command(BaseCommand):
    help = "Importa el catálogo de cuentas desde un CSV (por defecto solo simula)."

    def add_arguments(self, parser):
        parser.add_argument("archivo", type=str, help="Ruta del archivo CSV")
        parser.add_argument("--aplicar", action="store_true", help="Escribe en la base")

    def leer(self, ruta_archivo):
        """Lee el archivo CSV y devuelve una lista de diccionarios."""
        try:
            with open(ruta_archivo, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                return list(reader)
        except FileNotFoundError:
            raise CommandError(f"El archivo '{ruta_archivo}' no existe.")
        except Exception as e:
            raise CommandError(f"Error al leer el archivo: {e}")

    def validar(self, filas):
        """Valida que los datos del CSV sean correctos antes de operar."""
        if not filas:
            raise CommandError("El archivo CSV está vacío o no contiene encabezados válidos.")

        columnas_requeridas = {
            "numero_cuenta", 
            "nombre_cuenta", 
            "tipo_cuenta", 
            "rubro", 
            "especificacion", 
            "cuenta_activa"
        } 
        columnas_csv = set(filas[0].keys())
        
        if not columnas_requeridas.issubset(columnas_csv):
            faltantes = columnas_requeridas - columnas_csv
            raise CommandError(f"El CSV no contiene las columnas obligatorias: {faltantes}")

        codigos_vistos = set()
        for num_fila, fila in enumerate(filas, start=2):
            numero = fila.get("numero_cuenta", "").strip()
            nombre = fila.get("nombre_cuenta", "").strip()
            tipo = fila.get("tipo_cuenta", "").strip()
            rubro = fila.get("rubro", "").strip()
            especificacion = fila.get("especificacion", "").strip()
            activa = fila.get("cuenta_activa", "").strip().lower()

            if not numero or not nombre:
                raise CommandError(f"Fila {num_fila}: 'numero_cuenta' y 'nombre_cuenta' son obligatorios.")
            
            if numero in codigos_vistos:
                raise CommandError(f"Fila {num_fila}: El número de cuenta '{numero}' está duplicado en el CSV.")
            
            codigos_vistos.add(numero)

    def handle(self, *args, **options):
        archivo = options["archivo"]
        aplicar = options["aplicar"]

        filas = self.leer(archivo)
        self.validar(filas)

        if not aplicar:
            self.stdout.write(
                self.style.WARNING(
                    f"Simulación exitosa: {len(filas)} filas válidas analizadas. Usa --aplicar para escribir."
                )
            )
            return

        try:
            with transaction.atomic():
                filas_ordenadas = sorted(filas, key=lambda x: len(x.get("numero_cuenta", "")))
                
                cuentas_creadas = 0
                for fila in filas_ordenadas:
                    es_activa = fila["cuenta_activa"].strip().lower() in ["true", "1", "si", "sí", "yes"]
                    cuenta, creado = Cuenta.objects.update_or_create(
                        numero_cuenta=fila["numero_cuenta"].strip(),
                        defaults={
                            "nombre_cuenta": fila["nombre_cuenta"].strip(),
                            "tipo_cuenta": fila["tipo_cuenta"].strip(),
                            "rubro": fila["rubro"].strip(),
                            "especificacion": fila["especificacion"].strip(),
                            "cuenta_activa": es_activa,
                        }
                    )
                    if creado:
                        cuentas_creadas += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"¡Éxito! Se procesaron {len(filas_ordenadas)} cuentas ({cuentas_creadas} nuevas creadas)."
                    )
                )

        except Exception as e:
            raise CommandError(f"Error al escribir en la base de datos (Rollback aplicado): {e}")