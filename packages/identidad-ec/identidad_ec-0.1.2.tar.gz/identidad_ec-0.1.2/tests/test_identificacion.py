import pytest
from identidad_ec.utils import validar_identificacion

# --- CÉDULAS ---
def test_cedula_valida():
    cedula = "1710034065"
    resultado = validar_identificacion(cedula)
    assert resultado["valido"] is True
    assert resultado["tipo"] == "cedula"

def test_cedula_invalida():
    cedula = "1710034060"
    resultado = validar_identificacion(cedula)
    assert resultado["valido"] is False
    assert resultado["tipo"] == "cedula"

# --- RUC PERSONA NATURAL ---
def test_ruc_persona_natural_valido():
    ruc = "1710034065001"  # Cédula válida + 001
    resultado = validar_identificacion(ruc)
    assert resultado["valido"] is True
    assert resultado["tipo"] == "RUC Persona Natural"

# --- RUC PERSONA JURÍDICA ---
def test_ruc_juridica_flexible():
    ruc = "0791842368001"  # Jurídica ficticia
    resultado = validar_identificacion(ruc)
    assert resultado["valido"] is True
    assert resultado["tipo"] == "RUC Persona Jurídica"

def test_ruc_juridica_estricto():
    ruc = "0791842368001"
    resultado = validar_identificacion(ruc, estricto=True)
    assert resultado["valido"] is False
    assert resultado["tipo"] == "RUC Persona Jurídica"

# --- RUC ENTIDAD PÚBLICA ---
def test_ruc_publica_flexible():
    ruc = "1760001550001"  # Pública ficticia
    resultado = validar_identificacion(ruc)
    assert resultado["valido"] is True
    assert resultado["tipo"] == "RUC Entidad Pública"

def test_ruc_publica_estricto():
    ruc = "1760001550001"
    resultado = validar_identificacion(ruc, estricto=True)
    # Dependiendo del dígito verificador, puede ser True/False
    # Ajusta con un RUC público válido
