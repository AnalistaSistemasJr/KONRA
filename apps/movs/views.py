from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from apps.movs.forms import RegistrarForm

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

