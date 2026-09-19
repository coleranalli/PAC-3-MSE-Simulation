from pathlib import Path
import matplotlib.pyplot as plt

def plot_distribution(results, metric_name, output_path, title, x_label, bins=20):
    """creates and saves histogram for one Monte Carlo metric"""

    if len(results) == 0:
        raise ValueError("Results cannot be empty.")

    values = []

    for result in results:

        if metric_name not in result:
            raise ValueError(f"Metric {metric_name} does not exist in results")

        value = result[metric_name]

        if value is not None:
            values.append(value)

        if len(values) == 0:
            raise ValueError(f"Metric {metric_name} has no value")

        output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        plt.figure()

        plt.hist(values, bins=bins)
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel("Number of Trials")
        plt.tight_layout()
        plt.savefig(output_path)

        plt.close()