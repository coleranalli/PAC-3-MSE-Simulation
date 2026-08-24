from pathlib import Path

import simpy

from model_builder import build_model_from_configuration
from order import Order
from simulation import (SimulationRunner,
    get_deterministic_shipment_delay
)


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

def test_deterministic_shipment_delay():
    model = build_test_model()

    supplier_order = Order("TEST1","S1","M1","AP",1)

    manufacturer_order = Order("TEST2","S6","M1","Motor Case",1)

    supplier_delay = get_deterministic_shipment_delay(
        model,supplier_order
    )

    manufacturer_delay = get_deterministic_shipment_delay(
        model,manufacturer_order
    )

    assert supplier_delay == 7
    assert manufacturer_delay == 0

test_deterministic_shipment_delay()

def test_supplier_shipment_uses_simulated_time():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(model,env)

    ap_inventory = model.get_inventory("M1","AP")

    starting_inventory = ap_inventory.on_hand

    order = model.create_order(
        origin_id="S1",
        destination_id="M1",
        item_name="AP",
        quantity=10
    )

    process = env.process(
        runner.shipment_process(order)
    )

    # partial shipment process
    env.run(until=1)

    assert env.now == 1

    assert order.status == "shipped"

    assert model.shipments[0].status == "in_transit"

    assert ap_inventory.on_hand == starting_inventory

    assert ap_inventory.on_order == 10

    # finish shipment process
    env.run(until=process)

    assert env.now == 7

    assert order.status == "complete"

    assert model.shipments[0].status == "delivered"

    assert ap_inventory.on_hand == starting_inventory + 10

    assert ap_inventory.on_order == 0

test_supplier_shipment_uses_simulated_time()

def test_s6_production_uses_simulated_time():
    model = build_test_model()

    env = simpy.Environment()
    runner = SimulationRunner(model, env)

    s6 = model.nodes["S6"]

    composite_inventory = s6.input_inventories[
        "Composite"
    ]

    motor_case_inventory = s6.output_inventory

    starting_composite = composite_inventory.on_hand
    starting_motor_cases = motor_case_inventory.on_hand

    quantity = 2

    process = env.process(
        runner.production_process(
            "S6",
            quantity
        )
    )

    # Run partway through production.
    env.run(until=1)

    required_composite = (
        s6.recipe["Composite"] * quantity
    )

    # Inputs should already be reserved/consumed.
    assert composite_inventory.on_hand == (
        starting_composite - required_composite
    )

    # Finished output should not exist yet.
    assert motor_case_inventory.on_hand == (
        starting_motor_cases
    )

    # Finish production.
    env.run(until=process)

    assert env.now == 45

    # Inputs should not be consumed a second time.
    assert composite_inventory.on_hand == (
        starting_composite - required_composite
    )

    # Finished Motor Cases now become available.
    assert motor_case_inventory.on_hand == (
        starting_motor_cases + quantity
    )

test_s6_production_uses_simulated_time()

def test_production_does_not_start_without_inputs():
    model = build_test_model()

    env = simpy.Environment()
    runner = SimulationRunner(model, env)

    s6 = model.nodes["S6"]

    composite_inventory = s6.input_inventories[
        "Composite"
    ]

    motor_case_inventory = s6.output_inventory

    # remove all available composite
    composite_inventory.on_hand = 0

    starting_output = motor_case_inventory.on_hand

    process = env.process(
        runner.production_process(
            "S6",
            1
        )
    )

    env.run(until=process)

    assert env.now == 0

    assert motor_case_inventory.on_hand == (
        starting_output
    )

test_production_does_not_start_without_inputs()

def test_inputs_are_reserved_when_production_starts():
    model = build_test_model()

    env = simpy.Environment()
    runner = SimulationRunner(model, env)

    s6 = model.nodes["S6"]

    composite_inventory = (s6.input_inventories["Composite"])

    motor_case_inventory = (s6.output_inventory)

    starting_composite = (composite_inventory.on_hand)

    starting_output = (motor_case_inventory.on_hand)

    process = env.process(
        runner.production_process("S6",1)
    )

    # advance to production period
    env.run(until=1)

    assert composite_inventory.on_hand == (starting_composite - 1)

    # motor case not finished
    assert motor_case_inventory.on_hand == (starting_output)

    env.run(until=process)

    assert env.now == 45

    assert motor_case_inventory.on_hand == (starting_output + 1)

test_inputs_are_reserved_when_production_starts()

def test_daily_capacity_starts_overlapping_production():
    model = build_test_model()

    env = simpy.Environment()
    runner = SimulationRunner(model, env)

    s6 = model.nodes["S6"]

    composite_inventory = (s6.input_inventories["Composite"])

    motor_case_inventory = (s6.output_inventory)

    starting_composite = (composite_inventory.on_hand)

    starting_output = (motor_case_inventory.on_hand)

    env.process(
        runner.daily_production_controller("S6")
    )

    # runs through production launches til day 4
    env.run(until=4)

    # total started by 4 = 5.2 = 5
    assert composite_inventory.on_hand == (
        starting_composite - 5
    )

    # requires 46 days
    assert motor_case_inventory.on_hand == (starting_output)

test_daily_capacity_starts_overlapping_production()