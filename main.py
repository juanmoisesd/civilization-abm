"""
main.py — Punto de entrada rápido para Civilization ABM.

Ejecuta una simulación única con parámetros por defecto,
muestra el panel de métricas y guarda los resultados.

Uso
---
    python main.py
    python main.py --steps 300 --agents 150 --tax progressive
    python main.py --no-plot --output results/test
"""

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from model.model import CivilModel
from analysis.metrics import summary_statistics
from analysis.plots import (
    plot_gini_evolution,
    plot_wealth_time_series,
    plot_class_evolution,
    plot_wealth_distribution,
    plot_lorenz,
    plot_network,
    plot_summary_panel,
)


def parse_args():
    p = argparse.ArgumentParser(description="Civilization ABM — ejecución rápida")
    p.add_argument("--steps",    type=int,   default=200,          help="Pasos de simulación")
    p.add_argument("--agents",   type=int,   default=100,          help="Número de agentes")
    p.add_argument("--ineq",     type=float, default=0.8,          help="Desigualdad inicial (σ)")
    p.add_argument("--tax",      type=str,   default="progressive",help="Política fiscal: flat|progressive|none")
    p.add_argument("--network",  type=str,   default="small_world",help="Red: small_world|scale_free|none")
    p.add_argument("--floor",    action="store_true",               help="Activar piso social")
    p.add_argument("--seed",     type=int,   default=42,           help="Semilla aleatoria")
    p.add_argument("--output",   type=str,   default="results",    help="Carpeta de resultados")
    p.add_argument("--no-plot",  action="store_true",               help="Omitir visualizaciones")
    return p.parse_args()


def main():
    args = parse_args()

    tax_policy = None if args.tax == "none" else args.tax
    network_type = None if args.network == "none" else args.network

    print("\n" + "=" * 50)
    print("  CIVILIZATION ABM — Simulación única")
    print("=" * 50)
    print(f"  Agentes     : {args.agents}")
    print(f"  Pasos       : {args.steps}")
    print(f"  Desigualdad : {args.ineq}")
    print(f"  Política    : {tax_policy or 'ninguna'}")
    print(f"  Red         : {network_type or 'ninguna'}")
    print(f"  Piso social : {'sí' if args.floor else 'no'}")
    print(f"  Semilla     : {args.seed}")
    print("=" * 50 + "\n")

    # ---------------------------------------------------------------
    # Construcción y ejecución del modelo
    # ---------------------------------------------------------------
    model = CivilModel(
        N=args.agents,
        initial_inequality=args.ineq,
        tax_policy=tax_policy,
        network_type=network_type,
        enforce_floor=args.floor,
        seed=args.seed,
    )

    print("Ejecutando simulación...", end="", flush=True)
    for step in range(args.steps):
        model.step()
        if (step + 1) % 50 == 0:
            print(f" {step + 1}", end="", flush=True)
    print(" ✔\n")

    # ---------------------------------------------------------------
    # Datos y métricas
    # ---------------------------------------------------------------
    model_df = model.datacollector.get_model_vars_dataframe()
    stats = summary_statistics(model)

    print("─── Métricas finales ──────────────────────────")
    for k, v in stats.items():
        print(f"  {k:<22} {v:.4f}")
    print("─" * 46 + "\n")

    # ---------------------------------------------------------------
    # Guardar resultados
    # ---------------------------------------------------------------
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    model_df.to_csv(out / "model_timeseries.csv")
    stats.to_csv(out / "final_metrics.csv", header=["value"])
    print(f"Resultados guardados en: {out}/")

    # ---------------------------------------------------------------
    # Visualizaciones
    # ---------------------------------------------------------------
    if not args.no_plot:
        print("Generando figuras...")

        fig_panel = plot_summary_panel(
            model_df,
            model.schedule.agents,
            model.network,
        )
        fig_panel.savefig(out / "summary_panel.png", dpi=150, bbox_inches="tight")

        fig_gini = plot_gini_evolution(model_df)
        fig_gini.savefig(out / "gini_evolution.png", dpi=150, bbox_inches="tight")

        fig_wealth = plot_wealth_time_series(model_df)
        fig_wealth.savefig(out / "wealth_timeseries.png", dpi=150, bbox_inches="tight")

        fig_class = plot_class_evolution(model_df)
        fig_class.savefig(out / "class_evolution.png", dpi=150, bbox_inches="tight")

        fig_dist = plot_wealth_distribution(model.schedule.agents, step=args.steps)
        fig_dist.savefig(out / "wealth_distribution.png", dpi=150, bbox_inches="tight")

        wealths = [a.wealth for a in model.schedule.agents]
        fig_lorenz = plot_lorenz(wealths)
        fig_lorenz.savefig(out / "lorenz_curve.png", dpi=150, bbox_inches="tight")

        if model.network is not None:
            fig_net = plot_network(model.network, model.schedule.agents)
            fig_net.savefig(out / "social_network.png", dpi=150, bbox_inches="tight")

        print(f"Figuras guardadas en: {out}/")
        plt.show()

    print("\n✔ Ejecución completada.\n")


if __name__ == "__main__":
    main()
