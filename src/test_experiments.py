from pathlib import Path

from experiments import (
    run_single_trial,
    run_monte_carlo
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