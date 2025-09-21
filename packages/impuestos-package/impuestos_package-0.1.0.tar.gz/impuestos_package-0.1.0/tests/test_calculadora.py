import pytest
from impuestos_package.calculadora import CalculadoraDeuda

# --- Dummies con _parse_valor incluido ---
class _BaseDummy:
    def _parse_valor(self, item):
        # mismo comportamiento esperado por calculadora: lee "valor" y lo convierte a float > 0
        raw = str(item.get("valor", "")).replace(",", ".").strip()
        try:
            val = float(raw)
            return val if val > 0 else None
        except ValueError:
            return None

class DummyAPI_OK(_BaseDummy):
    def consumir_endpoint(self, fi, ff, timeout=10):
        return [{"valor": "2.00000"}, {"valor": "2.10000"}]

class DummyAPI_BAD(_BaseDummy):
    def consumir_endpoint(self, fi, ff, timeout=10):
        # valores inválidos para forzar el error
        return [{"valor": "0"}, {"valor": "0"}]

def test_calculadora_flujo_ok(monkeypatch):
    monkeypatch.setattr("impuestos_package.calculadora.BCBAPIUFV", DummyAPI_OK)
    calc = CalculadoraDeuda(TO=1000.0, fecha_inicio="2024-01-01", fecha_fin="2024-02-01",
                            tasa=12.0, dias=30, porcentaje=10.0)
    res = calc.calcular()
    assert res["TO"] == 1000.00
    assert res["MV"] == 50.00           # 1000 * ((2.1/2.0)-1)
    assert res["I"] == 10.50            # (1000+50)*0.12*(30/360)
    assert res["S"] == 100.00           # 1000 * 0.10
    assert res["DT"] == 1160.50

def test_calculadora_error_ufv(monkeypatch):
    monkeypatch.setattr("impuestos_package.calculadora.BCBAPIUFV", DummyAPI_BAD)
    calc = CalculadoraDeuda(TO=500, fecha_inicio="2024-01-01", fecha_fin="2024-01-02",
                            tasa=10, dias=10, porcentaje=5)
    res = calc.calcular()
    assert "error" in res

@pytest.mark.parametrize("kwargs", [
    dict(TO=-1,  fecha_inicio="2024-01-01", fecha_fin="2024-01-02", tasa=10, dias=10, porcentaje=5),
    dict(TO=100, fecha_inicio="2024-01-01", fecha_fin="2024-01-02", tasa=10, dias=-1, porcentaje=5),
    dict(TO=100, fecha_inicio="2024-01-01", fecha_fin="2024-01-02", tasa=10, dias=10, porcentaje=-5),
])
def test_calculadora_validaciones(kwargs):
    with pytest.raises(ValueError):
        CalculadoraDeuda(**kwargs)

def test_calculadora_sin_interes_ni_sancion(monkeypatch):
    monkeypatch.setattr("impuestos_package.calculadora.BCBAPIUFV", DummyAPI_OK)
    calc = CalculadoraDeuda(TO=800.0, fecha_inicio="2024-01-01", fecha_fin="2024-02-01",
                            tasa=0.0, dias=30, porcentaje=0.0)
    res = calc.calcular()
    assert res["MV"] == 40.00
    assert res["I"] == 0.00
    assert res["S"] == 0.00
    assert res["DT"] == 840.00

