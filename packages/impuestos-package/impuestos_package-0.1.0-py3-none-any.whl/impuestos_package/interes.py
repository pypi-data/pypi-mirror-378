class Interes:
    def __init__(self, TO: float, MV: float, tasa: float, dias: int):
        """
        TO: Total Original
        MV: Mantenimiento de Valor
        tasa: Tasa anual en porcentaje (ej. 3.5 para 3.5%)
        dias: días para el cálculo
        """
        if TO < 0 or MV < 0 or tasa < 0 or dias < 0:
            raise ValueError("Ningún valor puede ser negativo.")
        self.TO = TO
        self.MV = MV
        self.tasa = tasa
        self.dias = dias

    def calcular(self) -> float:
        """
        I = (TO + MV) * (tasa% / 100) * (dias / 360)
        """
        interes = (self.TO + self.MV) * (self.tasa / 100.0) * (self.dias / 360.0)
        return round(interes, 2)
