import pytest
from impuestos_package.ufv import BCBAPIUFV, UFVFetchError

def test_ufv_ok_requests_mock(requests_mock):
    base = "https://www.bcb.gob.bo/librerias/charts/ufv.php"
    # Simula 2 días con UFV válidos (con coma y punto decimal)
    requests_mock.get(
        f"{base}?cFecIni=2024-01-01&cFecFin=2024-01-02",
        json=[{"valor": "2,00000"}, {"valor": "2.10000"}],
        status_code=200,
    )
    api = BCBAPIUFV()
    data = api.consumir_endpoint("2024-01-01", "2024-01-02")
    assert isinstance(data, list)
    assert len(data) == 2

def test_ufv_error_status_code(requests_mock):
    base = "https://www.bcb.gob.bo/librerias/charts/ufv.php"
    requests_mock.get(
        f"{base}?cFecIni=2024-01-01&cFecFin=2024-01-02",
        status_code=500
    )
    api = BCBAPIUFV()
    with pytest.raises(UFVFetchError):
        api.consumir_endpoint("2024-01-01", "2024-01-02")

def test_ufv_respuesta_vacia(requests_mock):
    base = "https://www.bcb.gob.bo/librerias/charts/ufv.php"
    requests_mock.get(
        f"{base}?cFecIni=2024-01-01&cFecFin=2024-01-02",
        json=[],
        status_code=200
    )
    api = BCBAPIUFV()
    with pytest.raises(UFVFetchError):
        api.consumir_endpoint("2024-01-01", "2024-01-02")

def test_ufv_json_invalido(requests_mock):
    base = "https://www.bcb.gob.bo/librerias/charts/ufv.php"
    # Devuelve algo que no es lista
    requests_mock.get(
        f"{base}?cFecIni=2024-01-01&cFecFin=2024-01-02",
        json={"error": "formato inválido"},
        status_code=200
    )
    api = BCBAPIUFV()
    with pytest.raises(UFVFetchError):
        api.consumir_endpoint("2024-01-01", "2024-01-02")
