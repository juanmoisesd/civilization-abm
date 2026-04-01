"""
CivilModel: modelo principal de la civilización artificial.

Integra agentes, red social, reglas institucionales y
recolección de datos para análisis posterior.

Compatible con Mesa 3.x:
  - Sin RandomActivation: se usa model.agents.shuffle_do("step")
  - Sin unique_id explícito: Mesa asigna IDs automáticamente
  - model.agents es un AgentSet iterable
"""

import random as _random
import numpy as np
from mesa import Model
from mesa.datacollection import DataCollector

from .agents import CivilAgent
from .environment import build_small_world, build_scale_free, network_clustering
from .rules import flat_tax, progressive_tax, reputation_penalty, enforce_minimum_wealth


# -----------------------------------------------------------------------
# Funciones de reporte (model-level reporters)
# Mesa 3.x: model.agents en lugar de model.schedule.agents
# -----------------------------------------------------------------------

def compute_gini(model) -> float:
    """Índice de Gini sobre la distribución de riqueza."""
    wealths = np.array([a.wealth for a in model.agents])
    if len(wealths) == 0 or wealths.sum() == 0:
        return 0.0
    sorted_w = np.sort(wealths)
    n = len(sorted_w)
    cum = np.cumsum(sorted_w)
    return float((n + 1 - 2 * cum.sum() / cum[-1]) / n)


def mean_wealth_reporter(model) -> float:
    vals = [a.wealth for a in model.agents]
    return float(np.mean(vals)) if vals else 0.0


def total_wealth_reporter(model) -> float:
    return float(sum(a.wealth for a in model.agents))


def upper_class_fraction(model) -> float:
    agents = list(model.agents)
    if not agents:
        return 0.0
    return sum(1 for a in agents if a.social_class == "upper") / len(agents)


def lower_class_fraction(model) -> float:
    agents = list(model.agents)
    if not agents:
        return 0.0
    return sum(1 for a in agents if a.social_class == "lower") / len(agents)


def mean_reputation_reporter(model) -> float:
    vals = [a.reputation for a in model.agents]
    return float(np.mean(vals)) if vals else 0.0


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
        # Mesa 3.x acepta seed directamente en Model.__init__
        super().__init__(seed=seed)

        self.num_agents = N
        self.tax_policy = tax_policy
        self.enforce_floor = enforce_floor
        self._step_count = 0

        # Semilla adicional para el módulo random estándar
        if seed is not None:
            _random.seed(seed)
            np.random.seed(seed)

        # Crear agentes — Mesa 3.x los registra automáticamente en self.agents
        for _ in range(N):
            wealth = max(1.0, _random.lognormvariate(2.3, initial_inequality))
            CivilAgent(self, initial_wealth=wealth)

        # Red social (construida con la lista de agentes ya registrados)
        self.network = None
        agent_list = list(self.agents)
        if network_type == "small_world":
            self.network = build_small_world(agent_list)
        elif network_type == "scale_free":
            self.network = build_scale_free(agent_list)

        # Recolector de datos
        self.datacollector = DataCollector(
            model_reporters={
                "Gini":             compute_gini,
                "MeanWealth":       mean_wealth_reporter,
                "TotalWealth":      total_wealth_reporter,
                "UpperClass":       upper_class_fraction,
                "LowerClass":       lower_class_fraction,
                "MeanReputation":   mean_reputation_reporter,
                "NetworkClustering": network_clustering_reporter,
            },
            agent_reporters={
                "Wealth":      "wealth",
                "Reputation":  "reputation",
                "Strategy":    "strategy",
                "SocialClass": "social_class",
            },
        )

    # ------------------------------------------------------------------
    # Propiedad de riqueza media (usada por CivilAgent._update_class)
    # ------------------------------------------------------------------

    @property
    def mean_wealth(self) -> float:
        agents = list(self.agents)
        if not agents:
            return 0.0
        return sum(a.wealth for a in agents) / len(agents)

    # ------------------------------------------------------------------
    # Paso del modelo — Mesa 3.x: shuffle_do en lugar de schedule.step()
    # ------------------------------------------------------------------

    def step(self):
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")   # equivalente a RandomActivation
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
