from identidad_ec.ruc import validar_ruc

def test_ruc_persona_natural():
    # Un RUC válido debería construirse con una cédula válida + '001'
    ruc = "0705672830001"  # (Ejemplo ficticio)
    assert validar_ruc(ruc)["valido"] == True

def test_ruc_invalido():
    assert validar_ruc("0999999999999")["valido"] == False

def test_ruc_juridico_valido():
    ruc = "0791842368001"  # Ficticio
    resultado = validar_ruc(ruc)
    assert resultado["valido"] == True
    assert resultado["tipo"] == "RUC Persona Jurídica"

def test_ruc_publico_valido():
    ruc = "0760001900001"  # Ficticio
    resultado = validar_ruc(ruc)
    assert resultado["valido"] == True
    assert resultado["tipo"] == "RUC Entidad Pública"