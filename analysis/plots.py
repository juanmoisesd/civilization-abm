"""
Visualizaciones para el análisis de civilización ABM.

Todas las funciones retornan objetos matplotlib Figure
para permitir guardado flexible (.png / .pdf / .svg).
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import networkx as nx

from .metrics import lorenz_curve, gini

# Paleta consistente para publicación
PALETTE = sns.color_palette("muted")
plt.rcParams.update({
    "font.family": "serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
})


# -----------------------------------------------------------------------
# Series temporales
# -----------------------------------------------------------------------

def plot_gini_evolution(df: pd.DataFrame, ax=None) -> plt.Figure:
    """
    Evolución del índice de Gini a lo largo de la simulación.

    Parámetros
    ----------
    df : DataFrame con columna 'Gini' (output de datacollector).
    """
    fig, ax = (plt.subplots(figsize=(8, 4)) if ax is None else (ax.get_figure(), ax))
    ax.plot(df.index, df["Gini"], color=PALETTE[0], linewidth=2, label="Gini")
    ax.axhline(df["Gini"].mean(), color=PALETTE[0], linestyle="--",
               alpha=0.5, label=f"Media = {df['Gini'].mean():.3f}")
    ax.set_xlabel("Paso de simulación")
    ax.set_ylabel("Índice de Gini")
    ax.set_title("Evolución de la desigualdad económica")
    ax.legend(frameon=False)
    fig.tight_layout()
    return fig


def plot_wealth_time_series(df: pd.DataFrame) -> plt.Figure:
    """
    MeanWealth y TotalWealth en el mismo gráfico con doble eje Y.
    """
    fig, ax1 = plt.subplots(figsize=(8, 4))
    ax2 = ax1.twinx()

    ax1.plot(df.index, df["MeanWealth"], color=PALETTE[1], linewidth=2, label="Riqueza media")
    ax2.plot(df.index, df["TotalWealth"], color=PALETTE[2], linewidth=1.5,
             linestyle=":", label="Riqueza total")

    ax1.set_xlabel("Paso de simulación")
    ax1.set_ylabel("Riqueza media", color=PALETTE[1])
    ax2.set_ylabel("Riqueza total", color=PALETTE[2])
    ax1.set_title("Dinámica de la riqueza agregada")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, frameon=False)
    fig.tight_layout()
    return fig


def plot_class_evolution(df: pd.DataFrame) -> plt.Figure:
    """
    Evolución de las fracciones de clases sociales.
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.stackplot(
        df.index,
        df["LowerClass"],
        1 - df["LowerClass"] - df["UpperClass"],
        df["UpperClass"],
        labels=["Clase baja", "Clase media", "Clase alta"],
        colors=[PALETTE[3], PALETTE[1], PALETTE[0]],
        alpha=0.85,
    )
    ax.set_xlabel("Paso de simulación")
    ax.set_ylabel("Fracción de la población")
    ax.set_title("Estructura de clases sociales")
    ax.legend(loc="upper right", frameon=False)
    fig.tight_layout()
    return fig


# -----------------------------------------------------------------------
# Distribuciones
# -----------------------------------------------------------------------

def plot_wealth_distribution(agents, step: int = 0) -> plt.Figure:
    """
    Histograma + KDE de la distribución de riqueza.
    """
    wealths = [a.wealth for a in agents]
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.histplot(wealths, kde=True, color=PALETTE[0], ax=ax, bins=30, stat="density")
    ax.set_xlabel("Riqueza")
    ax.set_ylabel("Densidad")
    ax.set_title(f"Distribución de riqueza — paso {step}  (Gini={gini(wealths):.3f})")
    fig.tight_layout()
    return fig


def plot_lorenz(wealths, label: str = "Simulación") -> plt.Figure:
    """
    Curva de Lorenz con línea de igualdad perfecta.
    """
    x, y = lorenz_curve(wealths)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Igualdad perfecta")
    ax.plot(x, y, color=PALETTE[0], linewidth=2, label=label)
    ax.fill_between(x, x, y, alpha=0.15, color=PALETTE[0])
    ax.set_xlabel("Fracción acumulada de agentes")
    ax.set_ylabel("Fracción acumulada de riqueza")
    ax.set_title("Curva de Lorenz")
    ax.legend(frameon=False)
    fig.tight_layout()
    return fig


# -----------------------------------------------------------------------
# Red social
# -----------------------------------------------------------------------

def plot_network(graph: nx.Graph, agents, max_nodes: int = 200) -> plt.Figure:
    """
    Visualización del grafo social coloreado por clase social.
    """
    agent_map = {a.unique_id: a for a in agents}
    color_map_class = {"lower": "#e74c3c", "middle": "#3498db", "upper": "#2ecc71"}

    # Subgrafo si es muy grande
    nodes = list(graph.nodes)[:max_nodes]
    G = graph.subgraph(nodes)

    colors = [color_map_class.get(
        agent_map[n].social_class if n in agent_map else "middle", "#95a5a6"
    ) for n in G.nodes]

    sizes = [
        30 + agent_map[n].wealth * 2 if n in agent_map else 30
        for n in G.nodes
    ]

    fig, ax = plt.subplots(figsize=(9, 9))
    pos = nx.spring_layout(G, seed=42, k=0.5)
    nx.draw_networkx(
        G, pos=pos, ax=ax,
        node_color=colors, node_size=sizes,
        with_labels=False, edge_color="#cccccc",
        width=0.5, alpha=0.9,
    )
    # Leyenda manual
    for cls, col in color_map_class.items():
        ax.scatter([], [], c=col, label=cls.capitalize(), s=80)
    ax.legend(frameon=False, loc="upper left")
    ax.set_title("Red social — nodos coloreados por clase social")
    ax.axis("off")
    fig.tight_layout()
    return fig


# -----------------------------------------------------------------------
# Panel de resumen (figura multi-panel para paper)
# -----------------------------------------------------------------------

def plot_summary_panel(model_df: pd.DataFrame, agents, graph=None) -> plt.Figure:
    """
    Figura de 4 paneles lista para incluir en manuscrito.

    Parámetros
    ----------
    model_df : DataFrame del datacollector (model-level).
    agents   : lista de agentes al final de la simulación.
    graph    : nx.Graph o None.
    """
    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(2, 2, hspace=0.4, wspace=0.35)

    # Panel A — Gini
    ax_a = fig.add_subplot(gs[0, 0])
    ax_a.plot(model_df.index, model_df["Gini"], color=PALETTE[0], linewidth=2)
    ax_a.set_title("A. Índice de Gini", fontweight="bold")
    ax_a.set_xlabel("Paso"); ax_a.set_ylabel("Gini")

    # Panel B — Clases sociales
    ax_b = fig.add_subplot(gs[0, 1])
    ax_b.stackplot(
        model_df.index,
        model_df["LowerClass"],
        1 - model_df["LowerClass"] - model_df["UpperClass"],
        model_df["UpperClass"],
        labels=["Baja", "Media", "Alta"],
        colors=[PALETTE[3], PALETTE[1], PALETTE[0]],
        alpha=0.8,
    )
    ax_b.set_title("B. Estructura de clases", fontweight="bold")
    ax_b.set_xlabel("Paso"); ax_b.set_ylabel("Fracción")
    ax_b.legend(fontsize=8, frameon=False)

    # Panel C — Distribución de riqueza final
    ax_c = fig.add_subplot(gs[1, 0])
    wealths = [a.wealth for a in agents]
    sns.histplot(wealths, kde=True, color=PALETTE[2], ax=ax_c, bins=25, stat="density")
    ax_c.set_title("C. Distribución final de riqueza", fontweight="bold")
    ax_c.set_xlabel("Riqueza"); ax_c.set_ylabel("Densidad")

    # Panel D — Curva de Lorenz o red
    ax_d = fig.add_subplot(gs[1, 1])
    x, y = lorenz_curve(wealths)
    ax_d.plot([0, 1], [0, 1], "k--", linewidth=1)
    ax_d.plot(x, y, color=PALETTE[0], linewidth=2)
    ax_d.fill_between(x, x, y, alpha=0.15, color=PALETTE[0])
    ax_d.set_title("D. Curva de Lorenz", fontweight="bold")
    ax_d.set_xlabel("Fracción de agentes")
    ax_d.set_ylabel("Fracción de riqueza")

    fig.suptitle("Civilization ABM — Panel de métricas", fontsize=14, fontweight="bold")
    return fig
