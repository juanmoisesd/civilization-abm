"""
CivilAgent: unidad básica de la simulación.

Cada agente representa un individuo con recursos económicos,
reputación social y una estrategia de interacción.
"""

from mesa import Agent
import random


class CivilAgent(Agent):
    """
    Agente de civilización con atributos económicos y sociales.

    Atributos
    ---------
    wealth : float
        Riqueza acumulada del agente.
    reputation : float
        Reputación social (0.0 – 2.0). Influye en interacciones futuras.
    strategy : str
        'cooperative' | 'competitive' | 'neutral'
    social_class : str
        'lower' | 'middle' | 'upper'  — se actualiza dinámicamente.
    memory : list
        Historial de interacciones recientes (últimas 5).
    """

    STRATEGIES = ("cooperative", "competitive", "neutral")

    def __init__(self, unique_id, model, initial_wealth=None, strategy=None):
        super().__init__(unique_id, model)

        # Riqueza inicial con distribución log-normal (más realista)
        if initial_wealth is not None:
            self.wealth = float(initial_wealth)
        else:
            self.wealth = max(1.0, random.lognormvariate(2.3, 0.8))

        self.reputation = 1.0
        self.strategy = strategy or random.choice(self.STRATEGIES)
        self.social_class = "middle"
        self.memory = []

    # ------------------------------------------------------------------
    # Lógica de interacción
    # ------------------------------------------------------------------

    def interact(self, other):
        """Intercambio de riqueza según estrategias de ambos agentes."""
        if self.wealth <= 0:
            return

        # Monto base de transferencia
        transfer = min(1.0, self.wealth * 0.05)

        if self.strategy == "cooperative":
            # Dona al más pobre si tiene más riqueza
            if self.wealth > other.wealth:
                self._transfer_to(other, transfer)
        elif self.strategy == "competitive":
            # Extrae del más débil (baja reputación del receptor)
            if self.wealth < other.wealth:
                extracted = min(transfer, other.wealth)
                other.wealth -= extracted
                self.wealth += extracted
                other.reputation = max(0.0, other.reputation - 0.05)
        else:  # neutral — intercambio aleatorio
            if random.random() < 0.5 and self.wealth > other.wealth:
                self._transfer_to(other, transfer * 0.5)

        # Actualizar clase social y memoria
        self._update_class()
        self.memory.append(other.unique_id)
        if len(self.memory) > 5:
            self.memory.pop(0)

    def _transfer_to(self, other, amount):
        amount = min(amount, self.wealth)
        self.wealth -= amount
        other.wealth += amount
        self.reputation = min(2.0, self.reputation + 0.02)

    def _update_class(self):
        """Reclasificación dinámica por percentil de riqueza."""
        mean_w = self.model.mean_wealth
        if self.wealth < mean_w * 0.5:
            self.social_class = "lower"
        elif self.wealth < mean_w * 1.5:
            self.social_class = "middle"
        else:
            self.social_class = "upper"

    # ------------------------------------------------------------------
    # Paso del scheduler
    # ------------------------------------------------------------------

    def step(self):
        others = [a for a in self.model.schedule.agents if a is not self]
        if others:
            other = random.choice(others)
            self.interact(other)
