from __future__ import annotations

class Sancion:
    """
    Calcula la Sanción (S) como un porcentaje del Total Original.

    Fórmula:
        S = TO * (porcentaje / 100)

    Parámetros
    ----------
    TO : float
        Total Original (monto base).
    porcentaje : float
        Porcentaje de sanción (ej. 20 para 20%).

    Reglas:
    - TO no puede ser negativo.
    - porcentaje no puede ser negativo.
    """
    def __init__(self, TO: float, porcentaje: float) -> None:
        if TO < 0:
            raise ValueError("El monto TO no puede ser negativo.")
        if porcentaje < 0:
            raise ValueError("El porcentaje no puede ser negativo.")

        self.TO = float(TO)
        self.porcentaje = float(porcentaje)

    def calcular(self) -> float:
        sancion = self.TO * (self.porcentaje / 100.0)
        return round(sancion, 2)
