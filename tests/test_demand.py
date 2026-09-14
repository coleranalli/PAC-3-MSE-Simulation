from pathlib import Path

import simpy

from model_builder import build_model_from_configuration
from simulation import SimulationRunner


project_root = Path(__file__).resolve().parents[1]

nodes_path = project_root / "data" / "nodes.csv"
links_path = project_root / "data" / "links.csv"
recipes_path = project_root / "data" / "recipes.csv"


def build_test_model():
    model = build_model_from_configuration(
        nodes_path,
        links_path,
        recipes_path
    )

    return model

def test_demand_increments_once_per_day():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(model,env,daily_demand=1)

    a1 = model.nodes["A1"]

    env.process(runner.daily_demand_controller())

    env.run(until=3)

    assert a1.external_demand == 3

def test_existing_inventory_fulfills_demand():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(model,env,daily_demand=1)

    a1 = model.nodes["A1"]

    final_inventory = a1.output_inventory

    final_inventory.on_hand = 2

    env.process(runner.daily_demand_controller())

    env.run(until=1)

    assert a1.external_demand == 1
    assert a1.fulfilled_demand == 1
    assert a1.backlog == 0

    assert final_inventory.on_hand == 1

def test_insufficient_inventory_creates_backlog():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(model,env,daily_demand=1)

    a1 = model.nodes["A1"]

    final_inventory = a1.output_inventory

    final_inventory.on_hand = 0

    env.process(runner.daily_demand_controller())

    env.run(until=1)

    assert a1.external_demand == 1
    assert a1.fulfilled_demand == 0
    assert a1.backlog == 1

    assert final_inventory.on_hand == 0

def test_backlog_falls_when_inventory_becomes_available():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(model,env,daily_demand=1)

    a1 = model.nodes["A1"]

    final_inventory = a1.output_inventory

    final_inventory.on_hand = 0

    env.process(runner.daily_demand_controller())

    # Day 0 demand cannot be fulfilled.
    env.run(until=1)

    assert a1.backlog == 1

    # Finished units become available.
    final_inventory.add_inventory(2)

    # Day 1 adds another unit of demand,
    # then all existing backlog is fulfilled.
    env.run(until=2)

    assert a1.external_demand == 2
    assert a1.fulfilled_demand == 2
    assert a1.backlog == 0

    assert final_inventory.on_hand == 0
