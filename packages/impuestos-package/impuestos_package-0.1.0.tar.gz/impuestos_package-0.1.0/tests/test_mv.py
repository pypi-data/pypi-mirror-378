import pytest
from impuestos_package.mv import MantenimientoValor

def test_mv_basico():
    mv = MantenimientoValor(1000, 2.5, 2.0).calcular()
    assert mv == 250.0  # 1000 * ((2.5/2.0)-1) = 250

def test_mv_to_negativo():
    with pytest.raises(ValueError):
        MantenimientoValor(-100, 2.5, 2.0)

def test_mv_ufv_cero():
    with pytest.raises(ValueError):
        MantenimientoValor(1000, 0, 2.0)
    with pytest.raises(ValueError):
        MantenimientoValor(1000, 2.0, 0)
