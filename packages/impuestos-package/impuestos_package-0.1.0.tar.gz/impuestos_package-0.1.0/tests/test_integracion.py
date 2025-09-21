from impuestos_package.calculadora import CalculadoraDeuda

# Dummy con _parse_valor incluido, igual que en test_calculadora
class _BaseDummy:
    def _parse_valor(self, item):
        raw = str(item.get("valor", "")).replace(",", ".").strip()
        try:
            val = float(raw)
            return val if val > 0 else None
        except ValueError:
            return None

class DummyAPI(_BaseDummy):
    def consumir_endpoint(self, fi, ff, timeout=10):
        # UFV venc (fi) = 2.00000; UFV pago (ff) = 2.10000
        return [{"valor": "2.00000"}, {"valor": "2.10000"}]

def test_integracion_monkeypatch(monkeypatch):
    # Sustituye BCBAPIUFV por nuestro Dummy SOLO en este test
    monkeypatch.setattr("impuestos_package.calculadora.BCBAPIUFV", DummyAPI)

    calc = CalculadoraDeuda(
        TO=1000,
        fecha_inicio="2024-01-01",
        fecha_fin="2024-02-01",
        tasa=12,
        dias=30,
        porcentaje=10
    )
    res = calc.calcular()
    assert res["TO"] == 1000.00
    assert res["MV"] == 50.00
    assert res["I"] == 10.50
    assert res["S"] == 100.00
    assert res["DT"] == 1160.50
