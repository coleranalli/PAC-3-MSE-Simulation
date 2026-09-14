from pathlib import Path

import simpy

from model_builder import build_model_from_configuration
from simulation import SimulationRunner
from metrics import SimulationMetrics

project_root = Path(__file__).resolve().parents[1]

nodes_path = project_root / "data" / "nodes.csv"
links_path = project_root / "data" / "links.csv"
recipes_path = project_root / "data" / "recipes.csv"

def build_test_model():
    return build_model_from_configuration(
        nodes_path,
        links_path,
        recipes_path
    )

def test_timed_production_counts_start_and_completion():
    model = build_test_model()
    env = simpy.Environment()
    runner = SimulationRunner(model, env)

    process = env.process(
        runner.production_process("S6", quantity=2)
    )

    env.run(until=1)

    assert runner.metrics.production_starts["S6"] == 2
    assert runner.metrics.production_completions["S6"] == 0

    env.run(until=process)

    assert runner.metrics.production_starts["S6"] == 2
    assert runner.metrics.production_completions["S6"] == 2

def test_completion_is_not_counted_before_lead_time():
    model = build_test_model()
    env = simpy.Environment()
    runner = SimulationRunner(model, env)

    s6 = model.nodes["S6"]

    env.process(runner.daily_production_controller("S6"))

    env.run(until=s6.lead_time)

    assert runner.metrics.production_starts["S6"] > 0
    assert runner.metrics.production_completions["S6"] == 0

    env.run(until=s6.lead_time + 0.1)

    assert runner.metrics.production_completions["S6"] > 0

def test_failed_production_start_does_not_increment_counter():
    model = build_test_model()
    env = simpy.Environment()
    runner = SimulationRunner(model, env)

    s6 = model.nodes["S6"]

    s6.input_inventories["Composite"].on_hand = 0

    process = env.process(
        runner.production_process("S6", quantity=1)
    )

    env.run(until=process)

    assert runner.metrics.production_starts["S6"] == 0
    assert runner.metrics.production_completions["S6"] == 0

def test_daily_history_records_once_per_day():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(model, env, daily_demand=0)

    runner.run(until=3)

    assert len(runner.metrics.daily_history) == 3

    assert (runner.metrics.daily_history[0]["simulation_time"] == 1)
    assert (runner.metrics.daily_history[1]["simulation_time"] == 2)
    assert (runner.metrics.daily_history[2]["simulation_time"] == 3)

def test_average_and_max_inventory():
    model = build_test_model()

    metrics = SimulationMetrics()

    a1 = model.nodes["A1"]

    final_inventory = model.get_inventory("A1","Final Modeled Unit")

    final_inventory.on_hand = 6

    metrics.record_daily_snapshot(1, model, a1)

    final_inventory.on_hand = 3

    metrics.record_daily_snapshot(2, model, a1)

    final_inventory.on_hand = 0

    metrics.record_daily_snapshot(3, model, a1)

    # avg comes out to 3, max to 6
    assert metrics.get_average_on_hand("A1", "Final Modeled Unit") == 3
    assert metrics.get_max_on_hand("A1", "Final Modeled Unit") == 6

def test_stockout_days_are_counted():
    model = build_test_model()

    metrics = SimulationMetrics()

    a1 = model.nodes["A1"]

    final_inventory = model.get_inventory("A1", "Final Modeled Unit")

    daily_values = [4, 0, 0, 2]

    day = 1

    for value in daily_values:

        final_inventory.on_hand = value

        metrics.record_daily_snapshot(day, model, a1)

        day += 1

    assert metrics.get_stockout_days("A1", "Final Modeled Unit") == 2

def test_starvation_is_recorded_when_imputs_missing():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(model, env, daily_demand=0)

    s6 = model.nodes["S6"]

    s6.input_inventories["Composite"].on_hand = 0

    env.process(runner.daily_production_controller("S6"))

    env.run(until=1)

    assert (runner.metrics.starved_days["S6"] == 1)
    assert (runner.metrics.unstarted_units_due_to_storage["S6"] == 1)

def test_disruption_count_is_recorded():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(
        model, env, stochastic=True, random_seed=42, daily_demand=0
    )

    s6 = model.nodes["S6"]

    s6.disruption_probability = 1.0
    s6.disruption_duration = "3"

    disruption_started = (runner.check_for_disruption("S6"))

    assert disruption_started is True
    assert runner.metrics.get_disruption_count(
        runner.disruption_log, "S6"
    ) == 1

def test_disrupted_days_are_bounded_by_horizon():
    model = build_test_model()

    metrics = SimulationMetrics()

    disruption_log = [
        {
            "node_id": "S6",
            "start_time": 8,
            "duration": 5,
            "end_time": 13
        }
    ]

    disrupted_days = (
        metrics.get_disrupted_days(
            disruption_log,"S6",simulation_horizon=10
        )
    )

    assert disrupted_days == 2

def test_disruption_for_other_node_is_not_counted():
    metrics = SimulationMetrics()

    disruption_log = [
        {
            "node_id": "S1",
            "start_time": 2,
            "duration": 3,
            "end_time": 5
        }
    ]

    assert metrics.get_disruption_count(disruption_log, "S6") == 0

def test_summary_uses_a1_completions_for_final_units():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(model,env,daily_demand=0)

    final_inventory = model.get_inventory(
        "A1", "Final Modeled Unit"
    )

    final_inventory.on_hand = 0

    runner.metrics.production_completions["A1"] = 7

    summary = runner.get_summary()

    assert summary["final_units_produced"] == 7

    assert summary["final_units_on_hand"] == 0

def test_summary_calculates_service_level():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(model,env)

    a1 = model.nodes["A1"]

    a1.external_demand = 10
    a1.fulfilled_demand = 8
    a1.backlog = 2

    summary = runner.get_summary()

    assert summary["external_demand"] == 10
    assert summary["fulfilled_demand"] == 8
    assert summary["ending_backlog"] == 2

    assert summary["service_level"] == 0.8

def test_summary_service_level_is_none_without_demand():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(model,env,daily_demand=0)

    summary = runner.get_summary()

    assert summary["external_demand"] == 0

    assert summary["service_level"] is None