import pytest
from impuestos_package.sancion import Sancion

def test_sancion_basico():
    s = Sancion(1000, 20).calcular()
    assert s == 200.0

def test_sancion_to_negativo():
    with pytest.raises(ValueError):
        Sancion(-100, 10)

def test_sancion_porcentaje_negativo():
    with pytest.raises(ValueError):
        Sancion(100, -5)
