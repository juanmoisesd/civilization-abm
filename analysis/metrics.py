"""
Métricas cuantitativas para análisis de civilización.

Todas las funciones reciben arrays de numpy o listas Python
y retornan escalares o DataFrames para facilitar la integración
con experimentos y publicación científica.

Compatible con Mesa 3.x: usa model.agents (AgentSet).
"""

import numpy as np
import pandas as pd
from scipy.stats import entropy


# -----------------------------------------------------------------------
# Desigualdad económica
# -----------------------------------------------------------------------

def gini(array) -> float:
    """
    Índice de Gini.  0 = igualdad perfecta, 1 = desigualdad máxima.

    Referencias
    -----------
    Sen (1973). On Economic Inequality. Oxford University Press.
    """
    array = np.asarray(array, dtype=float)
    if array.size == 0 or array.sum() == 0:
        return 0.0
    if np.any(array < 0):
        array = array - array.min()
    array += 1e-10
    array = np.sort(array)
    n = len(array)
    index = np.arange(1, n + 1)
    return float(((2 * index - n - 1) * array).sum() / (n * array.sum()))


def theil_index(array) -> float:
    """
    Índice de Theil T.  Mayor sensibilidad en la cola alta.
    """
    array = np.asarray(array, dtype=float)
    array = array[array > 0]
    if array.size == 0:
        return 0.0
    mu = array.mean()
    return float(np.mean((array / mu) * np.log(array / mu)))


def palma_ratio(array) -> float:
    """
    Ratio de Palma: riqueza del 10% superior / riqueza del 40% inferior.
    Más sensible a desigualdad extrema que el Gini.
    """
    array = np.sort(np.asarray(array, dtype=float))
    n = len(array)
    bottom_40 = array[:int(n * 0.4)].sum()
    top_10 = array[int(n * 0.9):].sum()
    if bottom_40 == 0:
        return float("inf")
    return float(top_10 / bottom_40)


def lorenz_curve(array):
    """
    Retorna (x, y) para trazar la curva de Lorenz.

    Returns
    -------
    x : np.ndarray  — fracción acumulada de población (0–1)
    y : np.ndarray  — fracción acumulada de riqueza   (0–1)
    """
    array = np.sort(np.asarray(array, dtype=float))
    n = len(array)
    x = np.linspace(0, 1, n)
    y = np.cumsum(array) / array.sum()
    return x, y


# -----------------------------------------------------------------------
# Estructura social
# -----------------------------------------------------------------------

def class_distribution(agents) -> dict:
    """
    Fracción de agentes en cada clase social.
    Acepta tanto listas como AgentSet de Mesa 3.x.
    """
    classes = [a.social_class for a in agents]
    n = len(classes)
    counts = {"lower": 0, "middle": 0, "upper": 0}
    for c in classes:
        counts[c] = counts.get(c, 0) + 1
    return {k: v / n for k, v in counts.items()}


def social_mobility(wealth_t0, wealth_t1, n_bins: int = 5) -> float:
    """
    Fracción de agentes que cambiaron de quintil entre t0 y t1.
    Valores altos → mayor movilidad social.
    """
    w0 = np.asarray(wealth_t0, dtype=float)
    w1 = np.asarray(wealth_t1, dtype=float)
    bins0 = pd.qcut(w0, q=n_bins, labels=False, duplicates="drop")
    bins1 = pd.qcut(w1, q=n_bins, labels=False, duplicates="drop")
    moved = np.sum(bins0 != bins1)
    return float(moved / len(w0))


# -----------------------------------------------------------------------
# Entropía y complejidad
# -----------------------------------------------------------------------

def wealth_entropy(array, n_bins: int = 20) -> float:
    """
    Entropía de Shannon de la distribución de riqueza.
    Mayor entropía → distribución más homogénea.
    """
    array = np.asarray(array, dtype=float)
    counts, _ = np.histogram(array, bins=n_bins)
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    return float(entropy(probs, base=2))


def strategy_entropy(agents) -> float:
    """
    Diversidad de estrategias en la población (bits).
    Acepta tanto listas como AgentSet de Mesa 3.x.
    """
    strategies = [a.strategy for a in agents]
    unique, counts = np.unique(strategies, return_counts=True)
    probs = counts / counts.sum()
    return float(entropy(probs, base=2))


# -----------------------------------------------------------------------
# Estabilidad sistémica
# -----------------------------------------------------------------------

def coefficient_of_variation(array) -> float:
    """CV = σ/μ.  Medida de dispersión relativa."""
    array = np.asarray(array, dtype=float)
    mu = array.mean()
    if mu == 0:
        return 0.0
    return float(array.std() / mu)


def system_stability(gini_series) -> float:
    """
    Estabilidad como inverso de la varianza del Gini en las últimas N iteraciones.
    Valores altos → sistema más estable.
    """
    series = np.asarray(gini_series, dtype=float)
    var = series.var()
    if var == 0:
        return float("inf")
    return float(1.0 / var)


# -----------------------------------------------------------------------
# Resumen consolidado
# -----------------------------------------------------------------------

def summary_statistics(model) -> pd.Series:
    """
    Retorna un pd.Series con todas las métricas principales del modelo
    en el estado actual.

    Compatible con Mesa 3.x: usa model.agents (AgentSet).
    """
    agent_list = list(model.agents)
    wealths = np.array([a.wealth for a in agent_list])
    reps    = np.array([a.reputation for a in agent_list])

    stats = {
        "n_agents":         len(wealths),
        "mean_wealth":      float(wealths.mean()),
        "median_wealth":    float(np.median(wealths)),
        "std_wealth":       float(wealths.std()),
        "gini":             gini(wealths),
        "theil":            theil_index(wealths),
        "palma":            palma_ratio(wealths),
        "cv":               coefficient_of_variation(wealths),
        "wealth_entropy":   wealth_entropy(wealths),
        "mean_reputation":  float(reps.mean()),
        "strategy_entropy": strategy_entropy(agent_list),
    }
    return pd.Series(stats)
