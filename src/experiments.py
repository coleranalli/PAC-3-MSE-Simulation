import simpy
import csv
import statistics

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

def export_results_to_csv(results, output_path):
    """writes Monte Carlo trial results to csv"""

    if len(results) == 0:
        raise ValueError("Results cannot be empty.")

    fieldnames = list(results[0].keys())

    with open(output_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

def calculate_percentile(values, percentile):
    """
    calculates percentile w/ linear interpolation
    
    y = y1 + (x - x1)(slope)
    """

    if len(values) == 0:
        raise ValueError("Values cannot be empty.")

    if percentile < 0 or percentile > 100:
        raise ValueError("Percentile must be beteen 0 and 100")

    sorted_values = sorted(values)

    if len(sorted_values) == 1:
        return sorted_values[0]

    position = (percentile / 100) * (len(sorted_values) - 1)

    lower_index = int(position)
    upper_index = min(lower_index + 1, len(sorted_values) - 1)

    fraction = (position - lower_index)

    lower_value = sorted_values[lower_index]

    upper_value = sorted_values[upper_index]

    return(lower_value + fraction * (upper_value-lower_value))

def summarize_monte_carlo(results,metric_names):
    """Calculates aggregate statistics for selected metrics."""

    if len(results) == 0:
        raise ValueError("Results cannot be empty.")

    summary_rows = []

    for metric_name in metric_names:

        values = []

        for result in results:

            if metric_name not in result:
                raise ValueError(
                    f"Metric {metric_name}"
                    f"does not exist in results"
                )

            value = result[metric_name]

            if value is not None:
                values.append(value)

            if len(values) == 0:
                raise ValueError(
                    f"Metric {metric_name}"
                    f"has no numeric values."
                )

            mean_value = statistics.mean(values)

            median_value = statistics.median(values)

            if len(values) == 1:
                standard_deviation = 0
            else:
                standard_deviation = (statistics.stdev(values))

            minimum = min(values)

            percentile_5 = calculate_percentile(values,5)
            percentile_95 = calculate_percentile(values,95)

            maximum = max(values)

            summary_row = {
                "metric": metric_name,
                "mean": mean_value,
                "standard_deviation":standard_deviation,
                "minimum": minimum,
                "percentile_5": percentile_5,
                "median": median_value,
                "percentile_95": percentile_95,
                "maximum": maximum
            }

        summary_rows.append(summary_row)

    return summary_rows