from pathlib import Path

from experiments import run_monte_carlo


project_root = Path(__file__).resolve().parents[1]

nodes_path = project_root / "data" / "nodes.csv"
links_path = project_root / "data" / "links.csv"
recipes_path = project_root / "data" / "recipes.csv"

results = run_monte_carlo(
    nodes_path,
    links_path,
    recipes_path,
    simulation_days=365,
    number_of_trials=3,
    base_seed=1000
)

for result in results:

    print(
        result["trial_number"],
        result["random_seed"],
        result["final_units_produced"],
        result["service_level"],
        result["disruptions"]
    )