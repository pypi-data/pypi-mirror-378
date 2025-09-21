import logging
from .mv import MantenimientoValor
from .interes import Interes
from .sancion import Sancion
from .ufv import BCBAPIUFV, UFVFetchError

logger = logging.getLogger(__name__)

class CalculadoraDeuda:
    def __init__(self, TO: float, fecha_inicio: str, fecha_fin: str, tasa: float, dias: int, porcentaje: float):
        self.TO = TO
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.tasa = tasa
        self.dias = dias
        self.porcentaje = porcentaje

        if TO < 0:
            raise ValueError("TO no puede ser negativo.")
        if dias < 0:
            raise ValueError("dias no puede ser negativo.")
        if porcentaje < 0:
            raise ValueError("porcentaje no puede ser negativo.")

    def _obtener_ufvs(self):
        api = BCBAPIUFV()
        datos = api.consumir_endpoint(self.fecha_inicio, self.fecha_fin)
        ufv_venc = api._parse_valor(datos[0])
        ufv_pago = api._parse_valor(datos[-1])
        if not ufv_venc or not ufv_pago:
            raise UFVFetchError("Valores UFV inválidos para las fechas especificadas.")
        return ufv_venc, ufv_pago

    def calcular(self):
        try:
            ufv_venc, ufv_pago = self._obtener_ufvs()
        except UFVFetchError as e:
            return {"error": str(e)}

        mv = MantenimientoValor(self.TO, ufv_pago, ufv_venc).calcular()
        i = Interes(self.TO, mv, self.tasa, self.dias).calcular()
        s = Sancion(self.TO, self.porcentaje).calcular()
        dt = self.TO + mv + i + s

        logger.debug("TO=%s MV=%s I=%s S=%s DT=%s", self.TO, mv, i, s, dt)
        return {"TO": round(self.TO, 2), "MV": mv, "I": i, "S": s, "DT": round(dt, 2)}
