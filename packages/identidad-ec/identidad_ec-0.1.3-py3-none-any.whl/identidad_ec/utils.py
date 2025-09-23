def detectar_identificacion(numero: str) -> str:
    """
    Detecta el tipo de identificación según su longitud.
    """
    if len(numero) == 10:
        return "Cédula"
    elif len(numero) == 13:
        return "RUC"
    else:
        return "Inválido"


def validar_identificacion(numero: str, estricto: bool = False) -> dict:
    """
    Valida automáticamente un número de cédula o RUC ecuatoriano.
    
    Parámetros:
        numero (str): Número a validar.
        estricto (bool): Aplica validación estricta de módulo 11 para RUC jurídica/pública.
    
    Retorna:
        dict: {"valido": bool, "tipo": str, "mensaje": str}
    """
    tipo = detectar_identificacion(numero)

    if tipo == "Cédula":
        from identidad_ec.cedula import validar_cedula
        return validar_cedula(numero)

    elif tipo == "RUC":
        from identidad_ec.ruc import validar_ruc
        return validar_ruc(numero, estricto=estricto)

    else:
        return {"valido": False, "tipo": None, "mensaje": "Número inválido"}
