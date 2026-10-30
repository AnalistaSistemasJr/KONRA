import re
from decimal import Decimal

_PATRON_SALDO_INICIAL = re.compile(r"[0-9]{1,12}(\.[0-9]{1,2})?")

def parsear_saldo_inicial(texto):
    if texto is None or texto == '':
        raise ValueError("El monto del saldo inicial es obligatorio.")
    texto = texto.strip()
    if not _PATRON_SALDO_INICIAL.fullmatch(texto):
        raise ValueError(
            f"Monto del saldo inicial inválido {texto}: use solo dígitos 0-9, hasta 12 enteros y "
            "hasta 2 decimales (ej. 1500.24). Sin signo, comas ni notación científica."
        )
    return Decimal(texto)