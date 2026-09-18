from pathlib import Path

from experiments import run_monte_carlo, export_results_to_csv


project_root = Path(__file__).resolve().parents[1]

nodes_path = project_root / "data" / "nodes.csv"
links_path = project_root / "data" / "links.csv"
recipes_path = project_root / "data" / "recipes.csv"

results_directory = (project_root / "results")
results_directory.mkdir(exist_ok=True)

results = run_monte_carlo(
    nodes_path,
    links_path,
    recipes_path,
    simulation_days=365,
    number_of_trials=3,
    base_seed=1000
)

metric_names = [
    "final_units_produced",
    "service_level",
    "ending_backlog",
    "disruptions"
]

output_path = (results_directory / "stochastic_runs.csv")
export_results_to_csv(results,output_path)

for result in results:

    print(
        result["trial_number"],
        result["random_seed"],
        result["final_units_produced"],
        result["service_level"],
        result["disruptions"]
    )

from experiments import (
    run_monte_carlo,
    summarize_monte_carlo,
    export_results_to_csv
)

summary_results = summarize_monte_carlo(results, metric_names)

summary_path = (results_directory / "stochastic_summary.csv")

export_results_to_csv(summary_results,summary_path)