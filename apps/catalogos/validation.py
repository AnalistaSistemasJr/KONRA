import re

NUMERO_CUENTA_PATRON = r"[0-9]{2}(-[0-9]{2}){4}"
_NUMERO_CUENTA_RE = re.compile(NUMERO_CUENTA_PATRON)

def es_numero_cuenta_valido(valor):
    return bool(valor) and _NUMERO_CUENTA_RE.fullmatch(valor) is not None