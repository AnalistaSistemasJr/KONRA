from collections import defaultdict

from django.db import migrations

import unicodedata

def _normalizar_congelado(texto):
    """
    Copia congelada.
    No importar de normalize.py porque una migración debe conservar
    exactamente la regla con la que fue creada.
    """
    if texto is None:
        return ""

    texto = " ".join(texto.split()).casefold()
    texto = unicodedata.normalize('NFC', texto)

    resultado = []

    for caracter in texto:
        if unicodedata.category(caracter) == "Cf":
            continue

        if caracter == "ñ":
            resultado.append("ñ")
            continue

        descompuesto = unicodedata.normalize("NFKD", caracter)

        resultado.extend(
            c
            for c in descompuesto
            if unicodedata.category(c) != "Mn"
        )

    return "".join(resultado)

def poblar_claves(apps, schema_editor):
    Rubro = apps.get_model("catalogos", "Rubro")

    
    grupos = defaultdict(list)

    for rubro in Rubro.objects.all():
        clave = _normalizar_congelado(rubro.rubro)
        if not clave:
            raise RuntimeError(f"El rubro {rubro.rubro} genera una clave vacía")
        grupos[clave].append(rubro)

    conflictos = {
        clave: [r.rubro for r in rubros]
        for clave, rubros in grupos.items()
        if len(rubros) > 1
    }

    if conflictos:
        detalle = "\n".join(
            f"{clave}: {', '.join(nombres)}"
            for clave, nombres in conflictos.items()
        )

        raise RuntimeError(
            "Rubros con la misma clave:\n"
            + detalle
        )

    for clave, (rubro,) in grupos.items():
        Rubro.objects.filter(
            pk=rubro.pk
        ).update(
            clave=clave
        )

class Migration(migrations.Migration):

    dependencies = [
        ("catalogos", "0009_rubro_clave"),
    ]

    operations = [
        migrations.RunPython(
            poblar_claves,
            migrations.RunPython.noop,
        ),
    ]