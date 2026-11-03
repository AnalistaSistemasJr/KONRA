from decimal import Decimal

from django.db.models import Case, DecimalField, F, Sum, Value, When
from django.db.models.functions import Coalesce

from apps.movs.models import Registro_Movimientos, SaldoInicial, Tipo_movimiento

CERO = Decimal("0.00")
_DEC = DecimalField(max_digits=14, decimal_places=2)


class SaldoInicialNoConfigurado(Exception):
    """No existe saldo inicial: el saldo de caja no se puede calcular."""


def _suma_tipo(tipo):
    return Coalesce(
        Sum(
            Case(
                When(tipo_movimiento=tipo, then=F("monto")),
                default=Value(CERO),
                output_field=_DEC,
            ),
            output_field=_DEC,
        ),
        Value(CERO),
        output_field=_DEC,
    )


def _agregados():
    return {
        "entradas": _suma_tipo(Tipo_movimiento.ENTRADA),
        "salidas": _suma_tipo(Tipo_movimiento.SALIDA),
    }


def saldo_de_movimientos(queryset=None, hasta=None):
    """Entradas menos Salidas. Una sola consulta; no incluye el saldo inicial."""
    if queryset is None:
        queryset = Registro_Movimientos.objects.all()
    if hasta is not None:
        queryset = queryset.filter(fecha_caja__lte = hasta)
    r = queryset.aggregate(**_agregados())
    return r["entradas"] -r["salidas"]


def saldo_de_caja(hasta=None):
    """Saldo inicial más movimientos. Dos consultas."""
    inicial = SaldoInicial.objects.values_list("monto", flat=True).first()
    if inicial is None:
        raise SaldoInicialNoConfigurado("No hay saldo inicial configurado.")
    return inicial + saldo_de_movimientos(hasta=hasta)


def totales_por(campo, hasta=None):
    """Entradas, salidas (netas de devoluciones) y neto por 'cuenta' o 'estacion'."""
    if campo not in ("cuenta", "estacion"):
        raise ValueError("campo debe ser 'cuenta' o 'estacion'.")
    qs = Registro_Movimientos.objects.all()
    if hasta is not None:
        qs = qs.filter(fecha_caja__lte=hasta)
    filas = qs.values(campo).annotate(**_agregados()).order_by(campo)
    return [
        {
            campo: f[campo],
            "entradas": f["entradas"],
            "salidas": f["salidas"],
            "neto": f["entradas"] - f["salidas"],
        }
        for f in filas
    ]
