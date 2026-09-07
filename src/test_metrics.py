from pathlib import Path

import simpy

from model_builder import build_model_from_configuration
from simulation import SimulationRunner

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