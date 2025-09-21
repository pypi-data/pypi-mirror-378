import requests
from typing import List, Dict, Optional

class UFVFetchError(Exception):
    pass

class BCBAPIUFV:
    BASE_URL = "https://www.bcb.gob.bo/librerias/charts/ufv.php"

    def _parse_valor(self, item: Dict) -> Optional[float]:
        # Intenta múltiples claves comunes
        for key in ("valor", "dato", "ufv", "UFV", "value"):
            if key in item:
                raw = str(item[key]).strip()
                raw = raw.replace(",", ".")  # por si viene con coma decimal
                try:
                    val = float(raw)
                    if val > 0:
                        return val
                except ValueError:
                    continue
        return None

    def consumir_endpoint(self, fecha_inicio: str, fecha_fin: Optional[str] = None, timeout: int = 10) -> List[Dict]:
        if not fecha_fin:
            fecha_fin = fecha_inicio

        url = f"{self.BASE_URL}?cFecIni={fecha_inicio}&cFecFin={fecha_fin}"
        try:
            headers = {"User-Agent": "impuestos_package/1.0 (+https://pypi.org/)"}
            r = requests.get(url, timeout=timeout, headers=headers)
            r.raise_for_status()
            data = r.json()
            if not isinstance(data, list) or not data:
                raise UFVFetchError("La API UFV devolvió un formato inesperado o vacío.")
            # Valida que al menos las puntas tengan valor parseable
            if self._parse_valor(data[0]) is None or self._parse_valor(data[-1]) is None:
                raise UFVFetchError("No se pudieron leer valores UFV válidos para las fechas.")
            return data
        except requests.RequestException as e:
            raise UFVFetchError(f"Error de red al consultar UFV: {e}") from e
        except ValueError as e:
            raise UFVFetchError(f"Respuesta no JSON o inválida: {e}") from e
