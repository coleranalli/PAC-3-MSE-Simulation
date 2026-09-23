from pathlib import Path
import time

import simpy

from model_builder import build_model_from_configuration
from simulation import SimulationRunner
from experiments import run_monte_carlo, export_results_to_csv, summarize_monte_carlo

from plotting import plot_distribution

#================================================#
# paths
#================================================#

project_root = Path(__file__).resolve().parents[1]

nodes_path = project_root / "data" / "nodes.csv"

links_path = project_root / "data" / "links.csv"

recipes_path = project_root / "data" / "recipes.csv"

results_directory = project_root / "results"

plots_directory = results_directory / "plots"

results_directory.mkdir(parents=True, exist_ok=True)

plots_directory.mkdir(parents=True, exist_ok=True)

#================================================#
# settings
#================================================#

SIMULATION_DAYS = 365
NUMBER_OF_TRIALS = 1000
BASE_SEED = 1000
DAILY_DEMAND = 1

#================================================#
# deterministic base
#================================================#

print()
print("Running deterministic baseline for sim...")

deterministic_model = (
    build_model_from_configuration(
    nodes_path, links_path, recipes_path
    )
)

deterministic_env = simpy.Environment()

deterministic_runner = SimulationRunner(
    deterministic_model, deterministic_env,
    stochastic=False, daily_demand=DAILY_DEMAND
)

deterministic_runner.run(until=SIMULATION_DAYS)

deterministic_summary = (deterministic_runner.get_summary())

deterministic_summary["scenario"] = ("deterministic baseline")

deterministic_output_path = (
    results_directory / "determinstic_baseline_summary.csv"
)

export_results_to_csv([deterministic_summary], deterministic_output_path)

print("Deterministic baseline complete.")

#================================================#
# monte carlo base
#================================================#

print()
print(
    f"Running {NUMBER_OF_TRIALS} Monte Carlo trials..."
)

start_time = time.perf_counter()

results = run_monte_carlo(
    nodes_path,
    links_path,
    recipes_path,
    simulation_days=SIMULATION_DAYS,
    number_of_trials=NUMBER_OF_TRIALS,
    base_seed=BASE_SEED,
    daily_demand=DAILY_DEMAND
)

end_time = time.perf_counter()

runtime_seconds = end_time - start_time

print("Monte Carlo trials in progress...")

#================================================#
# export trial results
#================================================#

runs_output_path = results_directory / "week4_stochastic_baseline_runs.csv"

export_results_to_csv(results, runs_output_path)

#================================================#
# aggregate statistics
#================================================#

metric_names = [
    "final_units_produced",
    "service_level",
    "ending_backlog",
    "a1_throughput_per_day",
    "disruptions"
]

summary_results = (summarize_monte_carlo(results, metric_names))

summary_output_path = results_directory / "week4_stochastic_baseline_summary.csv"

export_results_to_csv(summary_results, summary_output_path)

#================================================#
# distribution plots
#================================================#

plot_distribution (
    results, 
    "final_units_produced", 
    plots_directory / "final_units_distribution.png", 
    "Distribution of Final Units Produced",
    "Final Modeled Units Produced"
    )

plot_distribution(
    results,
    "service_level",
    plots_directory / "service_level_distribution.png",
    "Distribution of Service Level",
    "Service Level"
)

#================================================#
# experiment summary
#================================================#

print()
print("Week 4 Monte Carlo baseline complete.")
print("-------------------------------------")

print(f"Simulation Horizon: {SIMULATION_DAYS} days.")

print(f"Trials: {NUMBER_OF_TRIALS}")

print(f"Base Seed: {BASE_SEED}")

print(f"Final Trial Seed: {BASE_SEED + NUMBER_OF_TRIALS - 1}")

print(f"Runtime: {round(runtime_seconds, 2)} seconds")

print(f"Trials: {NUMBER_OF_TRIALS}")

#================================================#
# final KPI resuts
#================================================#

print()
print("Final Results")
print("-------------")

for row in summary_results:

    print()
    print(f"Metric: {row["metric"]}")

    print(f"Mean: {row["mean"]}")

    print(f"5th Percentile: {row["percentile_5"]}")

    print(f"Median: {row["median"]}")

    print(f"95th Percentile: {row["percentile_95"]}")

    print(f"Minimum: {row["minimum"]}")

    print(f"Maximum: {row["maximum"]}")

#================================================#
# output locations
#================================================#

print()
print("Files written to:")

print(deterministic_output_path)

print(runs_output_path)

print(summary_output_path)

print(plots_directory / "final_units_distribution.png")

print(plots_directory / "service_level_distribution.png")

#================================================#
# end
#================================================#

print("Simulation Complete.")