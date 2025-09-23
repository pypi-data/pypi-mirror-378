from identidad_ec.cedula import validar_cedula

# ----------------------------
# Validación de RUC en Ecuador
# ----------------------------

def validar_ruc(ruc: str, estricto: bool = False) -> dict:
    """
    Valida un RUC ecuatoriano (Persona Natural, Jurídica o Pública).
    Retorna un diccionario con detalles del resultado.
    """

    # Debe tener exactamente 13 dígitos
    if not ruc.isdigit() or len(ruc) != 13:
        return {"valido": False, "tipo": None, "mensaje": "El RUC debe tener 13 dígitos"}

    provincia = int(ruc[0:2])
    tercer_digito = int(ruc[2])
    base_num = ruc[0:10]  # primeros 10 dígitos
    sufijo = ruc[10:13]   # últimos 3 dígitos (ej: '001')

    # Validar rango de provincias
    if provincia < 1 or provincia > 24:
        return {"valido": False, "tipo": None, "mensaje": "Código de provincia inválido"}

    # Persona Natural
    if tercer_digito < 6:
        if sufijo != "001":
            return {"valido": False, "tipo": "RUC Persona Natural", "mensaje": "El RUC debe terminar en 001"}
        cedula_valida = validar_cedula(base_num)
        if not cedula_valida["valido"]:
            return {"valido": False, "tipo": "RUC Persona Natural", "mensaje": "La base del RUC no es una cédula válida"}
        return {"valido": True, "tipo": "RUC Persona Natural", "mensaje": "RUC válido"}

    # Persona Jurídica (Privada o Extranjera) -> tercer dígito = 9
    if tercer_digito == 9:
        if sufijo != "001":
            return {"valido": False, "tipo": "RUC Persona Jurídica", "mensaje": "El RUC debe terminar en 001"}
        if estricto:
            if not _validar_modulo_11(ruc[0:9], int(ruc[9]), [4,3,2,7,6,5,4,3,2]):
                return {"valido": False, "tipo": "RUC Persona Jurídica", "mensaje": "Dígito verificador incorrecto"}
        return {"valido": True, "tipo": "RUC Persona Jurídica", "mensaje": "RUC válido"}

    # Entidad Pública -> tercer dígito = 6
    if tercer_digito == 6:
        if sufijo != "001":
            return {"valido": False, "tipo": "RUC Entidad Pública", "mensaje": "El RUC debe terminar en 001"}
        if not _validar_modulo_11(ruc[0:8], int(ruc[8]), [3,2,7,6,5,4,3,2]):
            return {"valido": False, "tipo": "RUC Entidad Pública", "mensaje": "Dígito verificador incorrecto"}
        return {"valido": True, "tipo": "RUC Entidad Pública", "mensaje": "RUC válido"}

    return {"valido": False, "tipo": None, "mensaje": "Formato de RUC no válido"}


def _validar_modulo_11(numeros: str, digito_verificador: int, coeficientes: list) -> bool:
    """
    Algoritmo de Módulo 11 utilizado para validar RUCs jurídicos y públicos.
    """
    suma = sum(int(numeros[i]) * coeficientes[i] for i in range(len(coeficientes)))
    residuo = suma % 11
    resultado = 11 - residuo
    if resultado == 11:
        resultado = 0
    return resultado == digito_verificador
