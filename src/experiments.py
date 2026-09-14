import simpy

from model_builder import build_model_from_configuration
from simulation import SimulationRunner

# this module builds and runs several sims at once

def run_single_trial(nodes_path, links_path, recipes_path, 
    simulation_days, random_seed, daily_demand=1):
    model = build_model_from_configuration(
        nodes_path,
        links_path,
        recipes_path
    )

    env = simpy.Environment()

    runner = SimulationRunner(model, env, stochastic=True, 
        random_seed=random_seed, daily_demand=daily_demand)

    runner.run(until=simulation_days)

    summary = runner.get_summary()

    summary["random_seed"] = random_seed

    return summary

def run_monte_carlo(nodes_path,links_path,recipes_path,simulation_days,
    number_of_trials,base_seed=1000,daily_demand=1):
    """runs several independent stochastic simulations."""

    if number_of_trials <= 0:
        raise ValueError(
            "Number of trials must be greater than zero."
        )

    results = []

    for trial_number in range(1, number_of_trials + 1):
        trial_seed = (base_seed + trial_number - 1)

        summary = run_single_trial(nodes_path,links_path,
            recipes_path,simulation_days,trial_seed,daily_demand
        )

        summary["trial_number"] = trial_number

        results.append(summary)

    return results