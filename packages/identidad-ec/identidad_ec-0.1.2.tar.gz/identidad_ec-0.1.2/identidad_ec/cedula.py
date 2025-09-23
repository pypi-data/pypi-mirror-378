def validar_cedula(cedula: str) -> dict:
    """
    Valida una cédula ecuatoriana de 10 dígitos.
    Retorna un diccionario con detalles.
    """
    resultado = {"valido": False, "tipo": "cedula", "mensaje": "", "provincia": None}

    # Condición 1: Longitud
    if len(cedula) != 10 or not cedula.isdigit():
        resultado["mensaje"] = "La cédula debe tener 10 dígitos numéricos"
        return resultado

    # Condición 2: Código de provincia (01-24)
    provincia = int(cedula[:2])
    if provincia < 1 or provincia > 24:
        resultado["mensaje"] = "Código de provincia inválido"
        return resultado
    provincias = {
        1: "Azuay", 2: "Bolívar", 3: "Cañar", 4: "Carchi", 5: "Cotopaxi",
        6: "Chimborazo", 7: "El Oro", 8: "Esmeraldas", 9: "Guayas", 10: "Imbabura",
        11: "Loja", 12: "Los Ríos", 13: "Manabí", 14: "Morona Santiago",
        15: "Napo", 16: "Pastaza", 17: "Pichincha", 18: "Tungurahua",
        19: "Zamora Chinchipe", 20: "Galápagos", 21: "Sucumbíos",
        22: "Orellana", 23: "Santo Domingo", 24: "Santa Elena"
    }
    resultado["provincia"] = provincias.get(provincia)

    # Condición 3: Tercer dígito < 6
    if int(cedula[2]) >= 6:
        resultado["mensaje"] = "El tercer dígito no es válido para persona natural"
        return resultado

    # Condición 4: Algoritmo módulo 10
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0
    for i in range(9):
        valor = int(cedula[i]) * coeficientes[i]
        if valor >= 10:
            valor -= 9  # suma de dígitos equivalente
        suma += valor

    decena_superior = ((suma + 9) // 10) * 10
    digito_verificador = decena_superior - suma if decena_superior - suma != 10 else 0

    if digito_verificador == int(cedula[9]):
        resultado["valido"] = True
        resultado["mensaje"] = "Cédula válida"
    else:
        resultado["mensaje"] = "Dígito verificador incorrecto"

    return resultado
