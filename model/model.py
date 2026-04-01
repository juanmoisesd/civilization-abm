"""
CivilModel: modelo principal de la civilización artificial.

Integra agentes, red social, reglas institucionales y
recolección de datos para análisis posterior.
"""

import numpy as np
from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from .agents import CivilAgent
from .environment import build_small_world, build_scale_free, network_clustering
from .rules import flat_tax, progressive_tax, reputation_penalty, enforce_minimum_wealth


# -----------------------------------------------------------------------
# Funciones de reporte (model-level reporters)
# -----------------------------------------------------------------------

def compute_gini(model) -> float:
    """Índice de Gini sobre la distribución de riqueza."""
    wealths = np.array([a.wealth for a in model.schedule.agents])
    if len(wealths) == 0 or wealths.sum() == 0:
        return 0.0
    sorted_w = np.sort(wealths)
    n = len(sorted_w)
    cum = np.cumsum(sorted_w)
    return float((n + 1 - 2 * cum.sum() / cum[-1]) / n)


def mean_wealth(model) -> float:
    return float(np.mean([a.wealth for a in model.schedule.agents]))


def total_wealth(model) -> float:
    return float(sum(a.wealth for a in model.schedule.agents))


def upper_class_fraction(model) -> float:
    agents = model.schedule.agents
    return sum(1 for a in agents if a.social_class == "upper") / len(agents)


def lower_class_fraction(model) -> float:
    agents = model.schedule.agents
    return sum(1 for a in agents if a.social_class == "lower") / len(agents)


def mean_reputation(model) -> float:
    return float(np.mean([a.reputation for a in model.schedule.agents]))


def network_clustering_reporter(model) -> float:
    if model.network is not None:
        return network_clustering(model.network)
    return 0.0


# -----------------------------------------------------------------------
# Modelo
# -----------------------------------------------------------------------

class CivilModel(Model):
    """
    Simulación de civilización artificial basada en agentes.

    Parámetros
    ----------
    N : int
        Número de agentes.
    initial_inequality : float
        Escala de dispersión de la riqueza inicial (σ log-normal).
        Mayor valor → mayor desigualdad inicial.
    tax_policy : str | None
        'flat' | 'progressive' | None
    network_type : str
        'small_world' | 'scale_free' | None
    enforce_floor : bool
        Activar garantía de riqueza mínima.
    seed : int | None
        Semilla aleatoria para reproducibilidad.
    """

    def __init__(
        self,
        N: int = 100,
        initial_inequality: float = 0.8,
        tax_policy: str = "progressive",
        network_type: str = "small_world",
        enforce_floor: bool = False,
        seed: int = None,
    ):
        super().__init__()
        self.num_agents = N
        self.tax_policy = tax_policy
        self.enforce_floor = enforce_floor
        self.schedule = RandomActivation(self)
        self._step_count = 0

        if seed is not None:
            import random, numpy as np
            random.seed(seed)
            np.random.seed(seed)

        # Crear agentes
        for i in range(N):
            import random as rnd
            wealth = max(1.0, rnd.lognormvariate(2.3, initial_inequality))
            agent = CivilAgent(i, self, initial_wealth=wealth)
            self.schedule.add(agent)

        # Red social
        self.network = None
        if network_type == "small_world":
            self.network = build_small_world(self.schedule.agents)
        elif network_type == "scale_free":
            self.network = build_scale_free(self.schedule.agents)

        # Recolector de datos
        self.datacollector = DataCollector(
            model_reporters={
                "Gini": compute_gini,
                "MeanWealth": mean_wealth,
                "TotalWealth": total_wealth,
                "UpperClass": upper_class_fraction,
                "LowerClass": lower_class_fraction,
                "MeanReputation": mean_reputation,
                "NetworkClustering": network_clustering_reporter,
            },
            agent_reporters={
                "Wealth": "wealth",
                "Reputation": "reputation",
                "Strategy": "strategy",
                "SocialClass": "social_class",
            },
        )

    # ------------------------------------------------------------------
    # Propiedad de riqueza media (usada por agentes)
    # ------------------------------------------------------------------

    @property
    def mean_wealth(self) -> float:
        agents = self.schedule.agents
        if not agents:
            return 0.0
        return sum(a.wealth for a in agents) / len(agents)

    # ------------------------------------------------------------------
    # Paso del modelo
    # ------------------------------------------------------------------

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        self._apply_institutions()
        self._step_count += 1

    def _apply_institutions(self):
        """Aplica reglas institucionales al final de cada paso."""
        if self.tax_policy == "flat":
            flat_tax(self, rate=0.05)
        elif self.tax_policy == "progressive":
            progressive_tax(self)

        reputation_penalty(self)

        if self.enforce_floor:
            enforce_minimum_wealth(self, minimum=1.0)
