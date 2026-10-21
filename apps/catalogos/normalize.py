import unicodedata


def normalizar_texto(texto):
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