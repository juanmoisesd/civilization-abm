"""
generate_figures.py
-------------------
Genera todas las figuras del paper a partir de los resultados experimentales.

Figuras producidas
------------------
Figure_1_baseline_panel.png      — Panel de la simulación baseline (4 sub-paneles)
Figure_2_fiscal_policy.png       — Efecto de la política fiscal
Figure_3_initial_inequality.png  — Paradoja de la desigualdad inicial
Figure_4_network_topology.png    — Efecto de la topología de red
Figure_5_floor_policy.png        — Contrafuego del piso mínimo
Figure_6_gini_heatmap.png        — Mapa de calor resumen de Gini × condición

Uso
---
    python paper/generate_figures.py

Requiere que experiments.run ya se haya ejecutado (results/ debe existir).
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import seaborn as sns

# --------------------------------------------------------------------------
# Configuración global de estilo PLOS ONE
# --------------------------------------------------------------------------
matplotlib.rcParams.update({
    "font.family":       "serif",
    "font.serif":        ["Times New Roman", "DejaVu Serif"],
    "font.size":         10,
    "axes.titlesize":    11,
    "axes.labelsize":    10,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "legend.fontsize":   9,
    "figure.dpi":        300,
    "savefig.dpi":       300,
    "savefig.bbox":      "tight",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.linewidth":    0.8,
    "grid.alpha":        0.3,
    "grid.linewidth":    0.5,
})

PALETTE   = sns.color_palette("colorblind")   # accesible para daltónicos
OUT_DIR   = Path(__file__).parent / "figures"
DATA_DIR  = Path(__file__).parent.parent / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def load_condition(name: str) -> pd.DataFrame:
    """Carga el CSV raw de una condición."""
    p = DATA_DIR / f"{name}_raw.csv"
    if not p.exists():
        raise FileNotFoundError(f"No encontrado: {p}\nEjecuta primero: python -m experiments.run")
    return pd.read_csv(p)


def mean_sd_by_step(df: pd.DataFrame, col: str):
    g = df.groupby("Step")[col]
    return g.mean(), g.std()


def lorenz(array):
    a = np.sort(np.asarray(array, dtype=float))
    return np.linspace(0, 1, len(a)), np.cumsum(a) / a.sum()


def save(fig, name: str):
    path = OUT_DIR / name
    fig.savefig(path, dpi=300, bbox_inches="tight")
    print(f"  ✔ {path.name}")
    plt.close(fig)


# --------------------------------------------------------------------------
# Figure 1 — Baseline dynamics panel
# --------------------------------------------------------------------------

def figure_1_baseline():
    """4-panel figure showing baseline simulation dynamics."""
    print("Figure 1 — Baseline dynamics panel...")
    df = load_condition("tax_progressive")   # = baseline (same as ineq_medium/net_small_world)

    fig = plt.figure(figsize=(7.5, 6))
    gs  = gridspec.GridSpec(2, 2, hspace=0.42, wspace=0.38)

    # A — Gini evolution
    ax_a = fig.add_subplot(gs[0, 0])
    mean, sd = mean_sd_by_step(df, "Gini")
    ax_a.plot(mean.index, mean.values, color=PALETTE[0], lw=1.8, label="Mean")
    ax_a.fill_between(mean.index, mean - sd, mean + sd,
                      color=PALETTE[0], alpha=0.18, label="±1 SD")
    ax_a.axhline(mean.iloc[-1], color=PALETTE[0], ls="--", lw=0.8, alpha=0.7)
    ax_a.set_title("(A) Gini Index Evolution")
    ax_a.set_xlabel("Simulation step"); ax_a.set_ylabel("Gini coefficient")
    ax_a.set_ylim(0, 0.65)
    ax_a.legend(frameon=False, loc="upper right")

    # B — Social class fractions
    ax_b = fig.add_subplot(gs[0, 1])
    for col, label, color in [("UpperClass","Upper class", PALETTE[2]),
                               ("LowerClass", "Lower class", PALETTE[3])]:
        m, s = mean_sd_by_step(df, col)
        ax_b.plot(m.index, m * 100, color=color, lw=1.8, label=label)
        ax_b.fill_between(m.index, (m - s) * 100, (m + s) * 100,
                          color=color, alpha=0.15)
    ax_b.set_title("(B) Social Class Fractions")
    ax_b.set_xlabel("Simulation step"); ax_b.set_ylabel("Fraction of agents (%)")
    ax_b.legend(frameon=False)

    # C — Mean wealth evolution
    ax_c = fig.add_subplot(gs[1, 0])
    m, s = mean_sd_by_step(df, "MeanWealth")
    ax_c.plot(m.index, m.values, color=PALETTE[1], lw=1.8)
    ax_c.fill_between(m.index, m - s, m + s, color=PALETTE[1], alpha=0.18)
    ax_c.set_title("(C) Mean Wealth")
    ax_c.set_xlabel("Simulation step"); ax_c.set_ylabel("Wealth units")

    # D — Mean reputation
    ax_d = fig.add_subplot(gs[1, 1])
    m, s = mean_sd_by_step(df, "MeanReputation")
    ax_d.plot(m.index, m.values, color=PALETTE[4], lw=1.8)
    ax_d.fill_between(m.index, m - s, m + s, color=PALETTE[4], alpha=0.18)
    ax_d.axhline(1.0, color="gray", ls=":", lw=0.8)
    ax_d.set_title("(D) Mean Reputation")
    ax_d.set_xlabel("Simulation step"); ax_d.set_ylabel("Reputation score")

    fig.suptitle(
        "Fig. 1. Baseline simulation dynamics (progressive tax, small-world network,\n"
        "σ₀ = 0.8, N = 100 agents, 30 replications). Shading = ±1 SD.",
        fontsize=9, y=1.01
    )
    save(fig, "Figure_1_baseline_panel.png")


# --------------------------------------------------------------------------
# Figure 2 — Effect of fiscal policy
# --------------------------------------------------------------------------

def figure_2_fiscal_policy():
    print("Figure 2 — Fiscal policy comparison...")
    conditions = {
        "tax_none":        ("No taxation",        PALETTE[3]),
        "tax_flat":        ("Flat tax (5%)",       PALETTE[1]),
        "tax_progressive": ("Progressive tax",     PALETTE[0]),
    }

    fig, axes = plt.subplots(1, 3, figsize=(7.5, 3.2))
    metrics   = [("Gini","Gini coefficient"), ("MeanWealth","Mean wealth"),
                 ("MeanReputation","Mean reputation")]

    for ax, (col, ylabel) in zip(axes, metrics):
        for name, (label, color) in conditions.items():
            df = load_condition(name)
            m, s = mean_sd_by_step(df, col)
            ax.plot(m.index, m.values, color=color, lw=1.8, label=label)
            ax.fill_between(m.index, m - s, m + s, color=color, alpha=0.15)
        ax.set_xlabel("Simulation step")
        ax.set_ylabel(ylabel)

    axes[0].set_title("(A) Inequality")
    axes[1].set_title("(B) Aggregate Wealth")
    axes[2].set_title("(C) Reputation")
    axes[0].legend(frameon=False, fontsize=8)

    fig.suptitle(
        "Fig. 2. Effect of fiscal policy on wealth inequality, aggregate wealth,\n"
        "and reputation dynamics (30 replications; shading = ±1 SD).",
        fontsize=9
    )
    fig.tight_layout()
    save(fig, "Figure_2_fiscal_policy.png")


# --------------------------------------------------------------------------
# Figure 3 — Paradox of initial inequality
# --------------------------------------------------------------------------

def figure_3_initial_inequality():
    print("Figure 3 — Initial inequality paradox...")
    conditions = {
        "ineq_low":    ("σ = 0.3 (low)",    PALETTE[0]),
        "ineq_medium": ("σ = 0.8 (medium)", PALETTE[1]),
        "ineq_high":   ("σ = 1.5 (high)",   PALETTE[3]),
    }

    fig, axes = plt.subplots(1, 3, figsize=(7.5, 3.2))

    # Panel A — Gini evolution
    for name, (label, color) in conditions.items():
        df = load_condition(name)
        m, s = mean_sd_by_step(df, "Gini")
        axes[0].plot(m.index, m.values, color=color, lw=1.8, label=label)
        axes[0].fill_between(m.index, m - s, m + s, color=color, alpha=0.15)
    axes[0].set_title("(A) Gini Index")
    axes[0].set_xlabel("Simulation step"); axes[0].set_ylabel("Gini coefficient")
    axes[0].legend(frameon=False, fontsize=8)

    # Panel B — Final Gini bar chart
    final_ginis = {}
    final_errs  = {}
    for name, (label, _) in conditions.items():
        df = load_condition(name)
        last = df[df["Step"] == df["Step"].max()]["Gini"]
        final_ginis[label] = last.mean()
        final_errs[label]  = last.std()
    labels  = list(final_ginis.keys())
    values  = [final_ginis[l] for l in labels]
    errors  = [final_errs[l] for l in labels]
    colors  = [c for _, (_, c) in conditions.items()]
    bars = axes[1].bar(range(len(labels)), values, color=colors,
                       yerr=errors, capsize=4, edgecolor="white", width=0.6)
    axes[1].set_xticks(range(len(labels)))
    axes[1].set_xticklabels([l.split(" ")[0] for l in labels])
    axes[1].set_title("(B) Final Gini (mean ± SD)")
    axes[1].set_ylabel("Gini coefficient")
    for bar, val in zip(bars, values):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                     f"{val:.3f}", ha="center", va="bottom", fontsize=8)

    # Panel C — Total wealth bar chart
    final_wealth = {}
    for name, (label, _) in conditions.items():
        df = load_condition(name)
        last = df[df["Step"] == df["Step"].max()]["TotalWealth"]
        final_wealth[label] = last.mean()
    values_w = [final_wealth[l] for l in labels]
    axes[2].bar(range(len(labels)), values_w, color=colors, edgecolor="white", width=0.6)
    axes[2].set_xticks(range(len(labels)))
    axes[2].set_xticklabels([l.split(" ")[0] for l in labels])
    axes[2].set_title("(C) Final Total Wealth")
    axes[2].set_ylabel("Total wealth units")
    axes[2].set_yscale("log")

    fig.suptitle(
        "Fig. 3. The redistribution amplification paradox: high initial wealth dispersion (σ=1.5)\n"
        "produces the lowest final Gini of all conditions tested (30 replications; shading = ±1 SD).",
        fontsize=9
    )
    fig.tight_layout()
    save(fig, "Figure_3_initial_inequality.png")


# --------------------------------------------------------------------------
# Figure 4 — Effect of network topology
# --------------------------------------------------------------------------

def figure_4_network_topology():
    print("Figure 4 — Network topology comparison...")
    conditions = {
        "net_none":        ("No network",   PALETTE[3]),
        "net_small_world": ("Small-world",  PALETTE[0]),
        "net_scale_free":  ("Scale-free",   PALETTE[2]),
    }

    fig, axes = plt.subplots(1, 2, figsize=(7.5, 3.2))

    # Panel A — Gini evolution
    for name, (label, color) in conditions.items():
        df = load_condition(name)
        m, s = mean_sd_by_step(df, "Gini")
        axes[0].plot(m.index, m.values, color=color, lw=1.8, label=label)
        axes[0].fill_between(m.index, m - s, m + s, color=color, alpha=0.15)
    axes[0].set_title("(A) Gini Index by Network Topology")
    axes[0].set_xlabel("Simulation step"); axes[0].set_ylabel("Gini coefficient")
    axes[0].legend(frameon=False)

    # Panel B — Clustering vs Gini scatter
    final_data = []
    for name, (label, color) in conditions.items():
        df = load_condition(name)
        last = df[df["Step"] == df["Step"].max()]
        final_data.append({
            "label":       label,
            "color":       color,
            "gini":        last["Gini"].mean(),
            "clustering":  last["NetworkClustering"].mean(),
        })
    for row in final_data:
        axes[1].scatter(row["clustering"], row["gini"],
                        color=row["color"], s=120, zorder=5, edgecolors="white", lw=0.8)
        axes[1].annotate(row["label"], (row["clustering"], row["gini"]),
                         textcoords="offset points", xytext=(6, 3), fontsize=8)
    axes[1].set_xlabel("Network clustering coefficient")
    axes[1].set_ylabel("Final Gini coefficient")
    axes[1].set_title("(B) Clustering vs. Inequality")

    fig.suptitle(
        "Fig. 4. Effect of social network topology on wealth inequality dynamics.\n"
        "Network effects are modest (ΔGini < 0.006) compared to fiscal policy effects.",
        fontsize=9
    )
    fig.tight_layout()
    save(fig, "Figure_4_network_topology.png")


# --------------------------------------------------------------------------
# Figure 5 — Floor policy backfire
# --------------------------------------------------------------------------

def figure_5_floor_policy():
    print("Figure 5 — Floor policy backfire...")
    conditions = {
        "floor_off": ("No floor",     PALETTE[0]),
        "floor_on":  ("Floor active", PALETTE[3]),
    }

    fig, axes = plt.subplots(1, 3, figsize=(7.5, 3.2))

    # Panel A — Gini
    for name, (label, color) in conditions.items():
        df = load_condition(name)
        m, s = mean_sd_by_step(df, "Gini")
        axes[0].plot(m.index, m.values, color=color, lw=1.8, label=label)
        axes[0].fill_between(m.index, m - s, m + s, color=color, alpha=0.18)
    axes[0].set_title("(A) Gini Index")
    axes[0].set_xlabel("Simulation step"); axes[0].set_ylabel("Gini coefficient")
    axes[0].legend(frameon=False)

    # Panel B — Total wealth
    for name, (label, color) in conditions.items():
        df = load_condition(name)
        m, s = mean_sd_by_step(df, "TotalWealth")
        axes[1].plot(m.index, m.values, color=color, lw=1.8, label=label)
        axes[1].fill_between(m.index, m - s, m + s, color=color, alpha=0.18)
    axes[1].set_title("(B) Total Wealth")
    axes[1].set_xlabel("Simulation step"); axes[1].set_ylabel("Total wealth units")

    # Panel C — Class distribution bar chart (final step)
    class_data = {}
    for name, (label, _) in conditions.items():
        df = load_condition(name)
        last = df[df["Step"] == df["Step"].max()]
        upper  = last["UpperClass"].mean()
        lower  = last["LowerClass"].mean()
        middle = 1 - upper - lower
        class_data[label] = [lower * 100, middle * 100, upper * 100]

    labels   = list(class_data.keys())
    x        = np.arange(len(labels))
    width    = 0.5
    bottoms  = [0, 0]
    class_labels = ["Lower", "Middle", "Upper"]
    class_colors = [PALETTE[3], PALETTE[1], PALETTE[2]]

    stacks = np.array([class_data[l] for l in labels])
    for i, (cl, cc) in enumerate(zip(class_labels, class_colors)):
        axes[2].bar(x, stacks[:, i], width,
                    bottom=np.sum(stacks[:, :i], axis=1),
                    color=cc, label=cl, edgecolor="white")
    axes[2].set_xticks(x); axes[2].set_xticklabels(labels)
    axes[2].set_title("(C) Class Distribution (final step)")
    axes[2].set_ylabel("Fraction of agents (%)")
    axes[2].legend(frameon=False, fontsize=8, loc="lower right")

    fig.suptitle(
        "Fig. 5. The floor policy backfire effect: minimum wealth guarantee increases the Gini\n"
        "coefficient (+3.5%), reduces total wealth (−37.8%), and polarizes class structure.",
        fontsize=9
    )
    fig.tight_layout()
    save(fig, "Figure_5_floor_policy.png")


# --------------------------------------------------------------------------
# Figure 6 — Summary heatmap
# --------------------------------------------------------------------------

def figure_6_summary_heatmap():
    print("Figure 6 — Summary heatmap...")
    master = pd.read_csv(DATA_DIR / "all_conditions.csv")
    last   = master[master["Step"] == master["Step"].max()]
    table  = last.groupby("condition")[["Gini", "MeanWealth", "TotalWealth",
                                        "UpperClass", "LowerClass", "MeanReputation"]].mean().round(3)

    # Ordenar por Gini
    table = table.sort_values("Gini")

    # Normalizar cada columna para el mapa de calor
    normed = (table - table.min()) / (table.max() - table.min())

    fig, ax = plt.subplots(figsize=(7.5, 5))
    sns.heatmap(
        normed, ax=ax,
        annot=table,           # muestra valores reales
        fmt=".3f",
        cmap="RdYlGn_r",
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": "Normalized value (0=min, 1=max)", "shrink": 0.8},
        annot_kws={"size": 8},
    )
    ax.set_title(
        "Fig. 6. Summary heatmap of final-step outcome metrics across all 11 experimental conditions.\n"
        "Annotated values are raw means (30 replications). Color encodes normalized rank within each metric.",
        fontsize=9, pad=12
    )
    ax.set_xlabel(""); ax.set_ylabel("")
    ax.set_xticklabels(["Gini", "Mean\nWealth", "Total\nWealth",
                        "Upper\nClass", "Lower\nClass", "Mean\nReputation"],
                       rotation=0, ha="center")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    fig.tight_layout()
    save(fig, "Figure_6_summary_heatmap.png")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))
    print(f"\nGenerando figuras → {OUT_DIR}/\n")

    figure_1_baseline()
    figure_2_fiscal_policy()
    figure_3_initial_inequality()
    figure_4_network_topology()
    figure_5_floor_policy()
    figure_6_summary_heatmap()

    print(f"\n✔ 6 figuras guardadas en {OUT_DIR}/")
    print("  Listas para insertar en el manuscrito (300 dpi, PLOS ONE specs).\n")
