from . import views
from django.urls import path

app_name = "movs"

urlpatterns = [
        path("", views.registrar_movimiento, name = "registro"),
        path("consulta", views.consulta_movimientos, name = "consulta")
    ]