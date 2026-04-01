"""
Motor de experimentos para Civilization ABM.

Ejecuta todas las condiciones definidas en configs.yaml,
guarda resultados en CSV/Parquet y calcula estadísticas de resumen.

Uso
---
    python -m experiments.run                  # todas las condiciones
    python -m experiments.run --condition tax_progressive
    python -m experiments.run --steps 300 --replications 50
"""

import argparse
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

# Permitir imports relativos al ejecutar como script
sys.path.insert(0, str(Path(__file__).parent.parent))

from model.model import CivilModel
from analysis.metrics import gini, theil_index, palma_ratio, summary_statistics

warnings.filterwarnings("ignore")


# -----------------------------------------------------------------------
# Carga de configuración
# -----------------------------------------------------------------------

def load_config(path: str = None) -> dict:
    default = Path(__file__).parent / "configs.yaml"
    path = Path(path) if path else default
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# -----------------------------------------------------------------------
# Ejecución de una réplica
# -----------------------------------------------------------------------

def run_single(
    condition: dict,
    steps: int,
    n_agents: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Corre una réplica y retorna (model_df, agent_df_final).

    Returns
    -------
    model_df : métricas del modelo en cada paso
    agent_df : snapshot de agentes en el último paso
    """
    model = CivilModel(
        N=n_agents,
        initial_inequality=condition.get("initial_inequality", 0.8),
        tax_policy=condition.get("tax_policy", "progressive"),
        network_type=condition.get("network_type", "small_world"),
        enforce_floor=condition.get("enforce_floor", False),
        seed=seed,
    )

    for _ in range(steps):
        model.step()

    model_df = model.datacollector.get_model_vars_dataframe()
    agent_df = model.datacollector.get_agent_vars_dataframe()

    # Snapshot del último paso
    last_step = agent_df.index.get_level_values("Step").max()
    agent_df_final = agent_df.xs(last_step, level="Step")

    return model_df, agent_df_final


# -----------------------------------------------------------------------
# Ejecución de una condición con N réplicas
# -----------------------------------------------------------------------

def run_condition(
    condition: dict,
    steps: int,
    replications: int,
    n_agents: int,
    seed_base: int,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Ejecuta todas las réplicas de una condición y retorna un DataFrame
    con estadísticas agregadas por paso (media ± SD a través de réplicas).
    """
    all_model_dfs = []

    for rep in range(replications):
        seed = seed_base + rep
        if verbose:
            print(f"  Condición '{condition['name']}' — réplica {rep + 1}/{replications}", end="\r")

        model_df, _ = run_single(condition, steps, n_agents, seed)
        model_df["replication"] = rep
        model_df["condition"] = condition["name"]
        all_model_dfs.append(model_df.reset_index())

    if verbose:
        print()

    combined = pd.concat(all_model_dfs, ignore_index=True)
    return combined


# -----------------------------------------------------------------------
# Resumen estadístico por condición
# -----------------------------------------------------------------------

def compute_summary(combined: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa por condición y paso; calcula media y desviación estándar.
    """
    numeric_cols = combined.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ("Step", "replication")]

    summary = (
        combined.groupby(["condition", "Step"])[numeric_cols]
        .agg(["mean", "std"])
    )
    summary.columns = ["_".join(c) for c in summary.columns]
    return summary.reset_index()


# -----------------------------------------------------------------------
# Tabla de métricas finales (último paso)
# -----------------------------------------------------------------------

def final_metrics_table(combined: pd.DataFrame) -> pd.DataFrame:
    """
    Para cada condición, métricas promedio del último paso de simulación.
    Útil para tabla de resultados en el paper.
    """
    last_step = combined["Step"].max()
    final = combined[combined["Step"] == last_step].copy()

    numeric_cols = final.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ("Step", "replication")]

    table = final.groupby("condition")[numeric_cols].agg(
        mean=("Gini", "mean") if "Gini" in numeric_cols else "mean"
    )
    # Recalcular de forma más limpia
    table = final.groupby("condition")[numeric_cols].mean().round(4)
    return table


# -----------------------------------------------------------------------
# Guardar resultados
# -----------------------------------------------------------------------

def save_results(
    combined: pd.DataFrame,
    summary: pd.DataFrame,
    output_dir: str,
    condition_name: str,
):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # CSV por condición
    cpath = out / f"{condition_name}_raw.csv"
    combined.to_csv(cpath, index=False)

    # Parquet (más eficiente para datasets grandes)
    try:
        combined.to_parquet(out / f"{condition_name}_raw.parquet", index=False)
    except Exception:
        pass  # parquet opcional (requiere pyarrow/fastparquet)

    # Resumen
    summary.to_csv(out / f"{condition_name}_summary.csv", index=False)


# -----------------------------------------------------------------------
# Punto de entrada
# -----------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Civilization ABM Experiment Runner")
    p.add_argument("--config", default=None, help="Ruta al archivo configs.yaml")
    p.add_argument("--condition", default=None, help="Ejecutar solo esta condición")
    p.add_argument("--steps", type=int, default=None, help="Pasos de simulación")
    p.add_argument("--replications", type=int, default=None, help="Réplicas por condición")
    p.add_argument("--output", default=None, help="Directorio de salida")
    p.add_argument("--quiet", action="store_true", help="Suprimir salida")
    return p.parse_args()


def main():
    args = parse_args()
    cfg = load_config(args.config)

    g = cfg["global"]
    steps = args.steps or g["steps"]
    replications = args.replications or g["replications"]
    n_agents = g["n_agents"]
    seed_base = g["seed_base"]
    output_dir = args.output or g["output_dir"]
    verbose = not args.quiet

    conditions = cfg["conditions"]
    if args.condition:
        conditions = [c for c in conditions if c["name"] == args.condition]
        if not conditions:
            print(f"Condición '{args.condition}' no encontrada en configs.yaml")
            sys.exit(1)

    if verbose:
        print(f"\n{'='*55}")
        print(f"  Civilization ABM — Experimentos")
        print(f"  Condiciones : {len(conditions)}")
        print(f"  Réplicas    : {replications}")
        print(f"  Pasos       : {steps}")
        print(f"  Agentes     : {n_agents}")
        print(f"  Output      : {output_dir}/")
        print(f"{'='*55}\n")

    all_combined = []
    t0 = time.time()

    for cond in conditions:
        if verbose:
            print(f"▶ Condición: {cond['name']}")
        combined = run_condition(cond, steps, replications, n_agents, seed_base, verbose)
        summary = compute_summary(combined)
        save_results(combined, summary, output_dir, cond["name"])
        all_combined.append(combined)

    # Dataset consolidado de todas las condiciones
    master = pd.concat(all_combined, ignore_index=True)
    master.to_csv(Path(output_dir) / "all_conditions.csv", index=False)

    # Tabla de métricas finales
    final_table = final_metrics_table(master)
    final_table.to_csv(Path(output_dir) / "final_metrics_table.csv")

    elapsed = time.time() - t0
    if verbose:
        print(f"\n✔ Completado en {elapsed:.1f}s")
        print(f"  Archivos guardados en: {output_dir}/")
        print(f"\n{final_table.to_string()}\n")


if __name__ == "__main__":
    main()
