from __future__ import annotations

class MantenimientoValor:
    """
    Calcula el Mantenimiento de Valor (MV) usando UFV.

    Fórmula:
        MV = TO * ( (UFV_pago / UFV_venc) - 1 )

    Parámetros
    ----------
    TO : float
        Total Original (monto base).
    ufv_pago : float
        Valor de la UFV en la fecha de pago.
    ufv_venc : float
        Valor de la UFV en la fecha de vencimiento.

    Reglas:
    - TO no puede ser negativo.
    - UFV_pago y UFV_venc deben ser > 0.
    """
    def __init__(self, TO: float, ufv_pago: float, ufv_venc: float) -> None:
        if TO < 0:
            raise ValueError("El monto TO no puede ser negativo.")
        if ufv_pago <= 0 or ufv_venc <= 0:
            raise ValueError("Los valores UFV deben ser mayores que cero.")

        self.TO = float(TO)
        self.ufv_pago = float(ufv_pago)
        self.ufv_venc = float(ufv_venc)

    def calcular(self) -> float:
        mv = self.TO * ((self.ufv_pago / self.ufv_venc) - 1.0)
        return round(mv, 2)
