from identidad_ec.cedula import validar_cedula

def test_cedula_valida():
    cedula = "0705672830"  # Ejemplo real válido
    resultado = validar_cedula(cedula)
    assert resultado["valido"] == True
    assert resultado["provincia"] == "El Oro"

def test_cedula_invalida():
    cedula = "1710034060"
    resultado = validar_cedula(cedula)
    assert resultado["valido"] == False
