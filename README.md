# Civilization ABM

> Simulación basada en agentes (ABM) de una civilización artificial con dinámica económica, estructura social y redes de interacción.
> Construida sobre **Mesa** (Python), diseñada para publicación científica reproducible.

---

## Características

| Módulo | Descripción |
|---|---|
| **Agentes** | Individuos con riqueza, reputación, estrategia y clase social dinámica |
| **Economía** | Intercambio, acumulación, impuesto proporcional y progresivo |
| **Sociedad** | Clases sociales emergentes (baja / media / alta), movilidad |
| **Normas** | Sanción por reputación, piso social garantizado |
| **Red** | Mundo pequeño (Watts-Strogatz) o libre de escala (Barabási-Albert) |
| **Métricas** | Gini, Theil, Palma, Lorenz, entropía, movilidad social |
| **Experimentos** | 11 condiciones × 30 réplicas, totalmente automatizadas |
| **Reproducibilidad** | Semillas fijas, Docker, resultados en CSV/Parquet |

---

## Estructura del repositorio

```
civilization-abm/
│
├── model/
│   ├── agents.py          # Clase CivilAgent
│   ├── model.py           # Clase CivilModel + reporters
│   ├── rules.py           # Políticas institucionales
│   └── environment.py     # Construcción y actualización de red social
│
├── experiments/
│   ├── run.py             # Motor de experimentos (CLI)
│   └── configs.yaml       # 11 condiciones experimentales
│
├── analysis/
│   ├── metrics.py         # Gini, Theil, Palma, entropía, movilidad
│   └── plots.py           # Figuras para paper (panel, Lorenz, red)
│
├── notebooks/
│   └── exploration.ipynb  # Análisis interactivo
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── results/               # Generado al ejecutar (ignorado por git)
├── requirements.txt
└── main.py                # Ejecución rápida
```

---

## Instalación

```bash
# 1. Clonar
git clone https://github.com/usuario/civilization-abm.git
cd civilization-abm

# 2. Entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Dependencias
pip install -r requirements.txt
```

---

## Ejecución rápida

```bash
# Simulación con parámetros por defecto (200 pasos, 100 agentes)
python main.py

# Personalizada
python main.py --steps 300 --agents 150 --tax flat --network scale_free

# Sin visualización (solo datos)
python main.py --no-plot --output results/run1
```

### Opciones de `main.py`

| Parámetro | Valores | Default |
|---|---|---|
| `--steps` | int | 200 |
| `--agents` | int | 100 |
| `--ineq` | float | 0.8 |
| `--tax` | flat / progressive / none | progressive |
| `--network` | small_world / scale_free / none | small_world |
| `--floor` | flag | False |
| `--seed` | int | 42 |
| `--output` | path | results/ |

---

## Experimentos sistemáticos

```bash
# Todas las condiciones (≈ 11 × 30 réplicas)
python -m experiments.run

# Solo una condición
python -m experiments.run --condition tax_progressive

# Personalizado
python -m experiments.run --steps 300 --replications 50
```

### Condiciones experimentales (configs.yaml)

| Experimento | Variable | Niveles |
|---|---|---|
| 1 | Desigualdad inicial | 0.3 / 0.8 / 1.5 |
| 2 | Política fiscal | ninguna / plana / progresiva |
| 3 | Topología de red | ninguna / mundo-pequeño / libre-de-escala |
| 4 | Piso social | off / on |

---

## Con Docker

```bash
# Construir imagen
docker build -t civilization-abm -f docker/Dockerfile .

# Ejecutar experimentos
docker run --rm -v $(pwd)/results:/app/results civilization-abm

# Jupyter Notebook
docker run --rm -p 8888:8888 -v $(pwd):/app civilization-abm \
  jupyter notebook --ip=0.0.0.0 --no-browser --allow-root

# docker-compose
cd docker && docker-compose up notebook
```

---

## Outputs generados

```
results/
├── model_timeseries.csv        # Serie temporal de métricas
├── final_metrics.csv           # Resumen estadístico final
├── summary_panel.png           # Figura multi-panel (paper)
├── gini_evolution.png
├── wealth_distribution.png
├── lorenz_curve.png
├── social_network.png
├── all_conditions.csv          # Dataset consolidado
└── final_metrics_table.csv     # Tabla comparativa de condiciones
```

---

## Métricas implementadas

| Métrica | Módulo | Descripción |
|---|---|---|
| Índice de Gini | `metrics.gini` | Desigualdad económica |
| Índice de Theil | `metrics.theil_index` | Sensible a la cola alta |
| Ratio de Palma | `metrics.palma_ratio` | Top 10% / Bottom 40% |
| Curva de Lorenz | `metrics.lorenz_curve` | Visualización de desigualdad |
| Entropía de riqueza | `metrics.wealth_entropy` | Homogeneidad de la distribución |
| Movilidad social | `metrics.social_mobility` | Cambio de quintil entre t0 y t1 |
| Estabilidad sistémica | `metrics.system_stability` | Inverso de varianza del Gini |
| Clustering de red | `environment.network_clustering` | Cohesión de la red social |

---

## Base científica

- **Framework**: [Mesa](https://github.com/projectmesa/mesa) — ABM estándar en Python
- **Modelo de riqueza**: Basado en modelos de intercambio aleatorio (Dragulescu & Yakovenko, 2000)
- **Red social**: Watts & Strogatz (1998); Barabási & Albert (1999)
- **Desigualdad**: Gini (1912); Theil (1967); Palma (2011)
- **Estrategias**: Axelrod (1984), teoría de juegos evolutiva

---

## Citación

```bibtex
@software{civilization_abm,
  title   = {Civilization ABM: Agent-Based Simulation of Artificial Civilizations},
  year    = {2026},
  url     = {https://github.com/usuario/civilization-abm},
  note    = {Built on Mesa framework}
}
```

---

## Licencia

MIT — libre para uso académico y comercial con atribución.

## How to Cite

If you use this repository in your research, please cite:

> de la Serna, J. M. (2026). *Civilization Abm*. Universidad Internacional de La Rioja (UNIR).
> https://github.com/juanmoisesd/civilization-abm 

See `CITATION.cff` for formatted references.
