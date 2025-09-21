import pytest
from impuestos_package.interes import Interes

def test_interes_calculo_correcto():
    i = Interes(1000, 50, 12, 30)  # 12% anual, 30 días
    esperado = (1000 + 50) * (12/100) * (30/360)
    assert i.calcular() == round(esperado, 2)

def test_interes_valores_negativos():
    with pytest.raises(ValueError):
        Interes(-1, 0, 10, 10)
