"""
Reglas institucionales aplicables al modelo.

Diseñadas como funciones puras que reciben el modelo
y modifican el estado de los agentes.

Compatible con Mesa 3.x: usa model.agents (AgentSet).
"""


def flat_tax(model, rate: float = 0.05) -> float:
    """
    Impuesto proporcional a la riqueza de cada agente.
    Los ingresos se redistribuyen de forma igualitaria.

    Parámetros
    ----------
    rate : float
        Fracción de riqueza recaudada (0–1).

    Retorna
    -------
    total_collected : float
    """
    agents = list(model.agents)
    collected = []
    for agent in agents:
        tax = agent.wealth * rate
        agent.wealth -= tax
        collected.append(tax)

    total = sum(collected)
    share = total / len(agents) if agents else 0
    for agent in agents:
        agent.wealth += share

    return total


def progressive_tax(model, brackets=None) -> float:
    """
    Impuesto progresivo por tramos de riqueza.

    brackets : list of (threshold, rate)
        Ejemplo: [(20, 0.05), (50, 0.10), (100, 0.20)]
    """
    if brackets is None:
        brackets = [(20, 0.05), (50, 0.10), (float("inf"), 0.20)]

    agents = list(model.agents)
    collected = []
    for agent in agents:
        for threshold, rate in brackets:
            if agent.wealth <= threshold:
                tax = agent.wealth * rate
                break
        else:
            tax = agent.wealth * brackets[-1][1]
        agent.wealth = max(0.0, agent.wealth - tax)
        collected.append(tax)

    total = sum(collected)
    share = total / len(agents) if agents else 0
    for agent in agents:
        agent.wealth += share

    return total


def reputation_penalty(model, threshold: float = 0.3, penalty: float = 0.5):
    """
    Agentes con reputación por debajo del umbral pierden riqueza
    (sanción social institucionalizada).
    """
    for agent in model.agents:
        if agent.reputation < threshold:
            agent.wealth = max(0.0, agent.wealth - penalty)


def enforce_minimum_wealth(model, minimum: float = 1.0):
    """
    Garantía de riqueza mínima (piso social).
    La diferencia se descuenta proporcionalmente del resto.
    """
    agents = list(model.agents)
    deficit = sum(max(0.0, minimum - a.wealth) for a in agents)
    if deficit == 0:
        return

    rich = [a for a in agents if a.wealth > minimum * 2]
    if not rich:
        return

    contrib_per = deficit / len(rich)
    for agent in rich:
        agent.wealth = max(minimum, agent.wealth - contrib_per)

    for agent in agents:
        if agent.wealth < minimum:
            agent.wealth = minimum
