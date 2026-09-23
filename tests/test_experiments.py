from pathlib import Path
from model_builder import build_model_from_configuration
from experiments import (
    run_single_trial,
    run_monte_carlo,
    export_results_to_csv,
    summarize_monte_carlo,
    calculate_percentile
)
import pytest

project_root = Path(__file__).resolve().parents[1]

nodes_path = (
    project_root / "data" / "nodes.csv"
)

links_path = (
    project_root / "data" / "links.csv"
)

recipes_path = (
    project_root / "data" / "recipes.csv"
)

def test_single_trial_returns_summary():

    result = run_single_trial(nodes_path,links_path,
        recipes_path,simulation_days=10,random_seed=42)

    assert result["simulation_time"] == 10
    assert result["random_seed"] == 42
    assert "service_level" in result
    assert "final_units_produced" in result

def test_monte_carlo_returns_requested_trials():

    results = run_monte_carlo(nodes_path,links_path,recipes_path,
        simulation_days=10,number_of_trials=3,base_seed=100)

    assert len(results) == 3
    assert results[0]["trial_number"] == 1
    assert results[1]["trial_number"] == 2
    assert results[2]["trial_number"] == 3
    assert results[0]["random_seed"] == 100
    assert results[1]["random_seed"] == 101
    assert results[2]["random_seed"] == 102

def test_monte_carlo_is_reproducible():

    results_one = run_monte_carlo(nodes_path,links_path,recipes_path,
        simulation_days=30,number_of_trials=2,base_seed=500)

    results_two = run_monte_carlo(nodes_path,links_path,recipes_path,
        simulation_days=30,number_of_trials=2,base_seed=500)

    assert results_one == results_two

def test_monte_carlo_rejects_zero_trials():

    with pytest.raises(ValueError):

        run_monte_carlo(nodes_path,links_path,recipes_path,
            simulation_days=10,number_of_trials=0)

def test_single_trials_do_not_share_state():

    result_one = run_single_trial(
        nodes_path,
        links_path,
        recipes_path,
        simulation_days=30,
        random_seed=700
    )

    result_two = run_single_trial(
        nodes_path,
        links_path,
        recipes_path,
        simulation_days=30,
        random_seed=700
    )

    assert result_one == result_two

def test_trials_use_fresh_models():

    model_one = build_model_from_configuration(
        nodes_path,
        links_path,
        recipes_path
    )

    model_two = build_model_from_configuration(
        nodes_path,
        links_path,
        recipes_path
    )

    assert model_one is not model_two

    assert (
        model_one.nodes["A1"]
        is not model_two.nodes["A1"]
    )

    assert (
        model_one.get_inventory(
            "A1",
            "Final Modeled Unit"
        )
        is not
        model_two.get_inventory(
            "A1",
            "Final Modeled Unit"
        )
    )

def test_export_results_to_csv(tmp_path):
    results = [
        {
            "trial_number": 1,
            "random_seed": 100,
            "final_units_produced": 5
        },
        {
            "trial_number": 2,
            "random_seed": 101,
            "final_units_produced": 6
        }
    ]

    output_path = (tmp_path / "results.csv")
    export_results_to_csv(results, output_path)

    assert output_path.exists()

    file_contents = (output_path.read_text())

    assert "trial_number" in file_contents
    assert "100" in file_contents
    assert "101" in file_contents

def test_export_rejects_empty_results(tmp_path):

    output_path = (tmp_path / "results.csv")

    with pytest.raises(ValueError):

        export_results_to_csv([],output_path)

def test_monte_carlo_summary_statistics():

    results = [
        {"final_units_produced": 100},
        {"final_units_produced": 200},
        {"final_units_produced": 300}
    ]

    summary = summarize_monte_carlo(results,["final_units_produced"])

    assert len(summary) == 1

    row = summary[0]

    assert row["metric"] == (
        "final_units_produced"
    )

    assert row["mean"] == 200
    assert row["median"] == 200
    assert row["minimum"] == 100
    assert row["maximum"] == 300

def test_percentile_calculation():

    values = [0,10,20,30,40]

    assert calculate_percentile(values,0)== 0
    assert calculate_percentile(values,50)== 20
    assert calculate_percentile(values,100) == 40