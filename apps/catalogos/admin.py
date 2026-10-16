from django.contrib import admin
from .models import Estacion, Cuenta, Rubro

class CatalogoAdmin(admin.ModelAdmin):

    def has_delete_permission(
        self,
        request,
        obj=None
    ):
        return False


@admin.register(Estacion)
class EstacionAdmin(CatalogoAdmin):

    search_fields = [
        "estacion",
        "numero_estacion",
        "razon_social",
    ]

    list_display = [
        "numero_estacion",
        "estacion",
        "razon_social",
        "estacion_activa",
    ]

    list_filter = [
        "estacion_activa",
    ]

@admin.register(Cuenta)
class CuentaAdmin(CatalogoAdmin):
    search_fields = [
        "numero_cuenta",
        "nombre_cuenta",
        "tipo_cuenta",
        "rubro",
        "especificacion",
    ]

    list_display = [
        "numero_cuenta",
        "nombre_cuenta",
        "tipo_cuenta",
        "rubro",
        "especificacion",
        "cuenta_activa",
    ]

    list_filter = [
        "tipo_cuenta",
        "cuenta_activa",
    ]

@admin.register(Rubro)
class RubroAdmin(CatalogoAdmin):
    search_fields = [
        "id",
        "rubro",
        "rubro_activo",
    ]

    list_display = [
        "id",
        "rubro",
        "rubro_activo",
    ]

    list_filter = [
        "rubro"
    ]