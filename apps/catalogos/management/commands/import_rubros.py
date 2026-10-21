import csv
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.catalogos.models import Rubro
import unicodedata
from apps.catalogos.normalize import normalizar_texto

class Command(BaseCommand):
    help = "Importa el catálogo de rubros desde un CSV (por defecto solo simula)."

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
            "rubro",
            "rubro_activo"
        } 
        columnas_csv = set(filas[0].keys())
        
        if not columnas_requeridas.issubset(columnas_csv):
            faltantes = columnas_requeridas - columnas_csv
            raise CommandError(f"El CSV no contiene las columnas obligatorias: {faltantes}")

        codigos_vistos = set()
        for num_fila, fila in enumerate(filas, start=2):
            rubro = fila.get("rubro", "")
            clave = normalizar_texto(rubro)
            activo = fila.get("rubro_activo", "").strip()

            if not clave:
                raise CommandError(f"Fila {num_fila}: 'rubro' es un campo obligatorio")
            
            if clave in codigos_vistos:
                raise CommandError(f"Fila {num_fila}: El rubro '{rubro}' está duplicado en el CSV.")
            
            codigos_vistos.add(clave)

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
                filas_ordenadas = sorted(filas, key=lambda x: len(x.get("rubro", "")))
                
                rubros_creados = 0
                for fila in filas_ordenadas:
                    es_activo = fila["rubro_activo"].strip().lower() in ["true", "1", "si", "sí", "yes"]
                    nombre_rubro = " ".join(fila["rubro"].split())
                    clave = normalizar_texto(nombre_rubro)
                    rubro, creado = Rubro.objects.update_or_create(
                        clave = clave,
                        defaults={
                            "rubro": nombre_rubro,
                            "rubro_activo": es_activo,
                        }
                    )
                    if creado:
                        rubros_creados += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"¡Éxito! Se procesaron {len(filas_ordenadas)} rubros ({rubros_creados} nuevos rubros)."
                    )
                )

        except Exception as e:
            raise CommandError(f"Error al escribir en la base de datos (Rollback aplicado): {e}")