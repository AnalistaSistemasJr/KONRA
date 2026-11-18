from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.http import HttpResponse
from apps.movs.forms import RegistrarForm
from apps.movs.models import Registro_Movimientos
from django.views.generic import TemplateView
from apps.movs.saldos import saldo_de_caja, SaldoInicialNoConfigurado


@never_cache
@login_required
@permission_required('movs.add_registro_movimientos', raise_exception=True)
def registrar_movimiento(request):
    if request.method == 'POST':
        form = RegistrarForm(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.creado_por = request.user
            registro.save()
            return redirect("movs:registro")
    else:
        form = RegistrarForm()
    context = {'form':form}
    return render(request, "movs/registro.html", context)

@never_cache
@login_required
@permission_required('movs.view_registro_movimientos', raise_exception=True)
def consulta_movimientos(request):
    movimientos = (
        Registro_Movimientos.objects
        .filter(creado_por=request.user)
        .select_related("estacion", "cuenta")
        .order_by("-fecha_caja")
    )

    context = {"movimientos": movimientos}
    return render(request, "movs/consulta_movs.html", context)