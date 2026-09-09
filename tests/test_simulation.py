from pathlib import Path

import simpy

from model_builder import build_model_from_configuration
from order import Order
from simulation import (
    SimulationRunner,
    get_deterministic_shipment_delay,
    sample_disruption_duration,
    sample_variable_lead_time
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
        runner.production_process("S6",quantity)
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
        runner.production_process("S6",1)
    )

    env.run(until=process)

    assert env.now == 0

    assert motor_case_inventory.on_hand == (
        starting_output
    )

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

def test_stochastic_supplier_delay_stays_in_range():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(
        model,
        env,
        stochastic=True,
        random_seed=42
    )

    order = model.create_order(
        origin_id="S1",
        destination_id="M1",
        item_name="AP",
        quantity=10
    )

    delay = runner.get_shipment_delay(order)

    # lead time 7, variability 2
    assert delay >= 5
    assert delay <= 9

def test_stochastic_production_delay_stays_in_range():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(model, env, stochastic=True,
        random_seed=42)

    s6 = model.nodes["S6"]

    delay = runner.get_production_delay(s6)

    # lead time 45, variability 10
    assert delay >= 35
    assert delay <= 55

def test_random_seed_reproduces_results():
    model1 = build_test_model()
    model2 = build_test_model()

    env1 = simpy.Environment()
    env2 = simpy.Environment()

    runner1 = SimulationRunner(model1,env1,
        stochastic=True,random_seed=100)

    runner2 = SimulationRunner(model2,env2,
        stochastic=True,random_seed=100)

    delay1 = runner1.get_production_delay(
        model1.nodes["S6"]
    )

    delay2 = runner2.get_production_delay(
        model2.nodes["S6"]
    )

    assert delay1 == delay2

def test_disruption_duration_stays_in_range():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(model, env,
        stochastic=True, random_seed=42)

    duration = sample_disruption_duration(
        runner.random_generator, "3-7"
    )

    assert duration >= 3
    assert duration <= 7

def test_disruption_can_start():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(model,env,
        stochastic=True, random_seed=42)

    s6 = model.nodes["S6"]

    # temporary guarentee of disruption
    s6.disruption_probability= 1.0

    disruption_started = (
        runner.check_for_disruption("S6")
    )

    assert disruption_started is True

    assert runner.is_node_disrupted("S6") is True

    assert len(runner.disruption_log) == 1

    event = runner.disruption_log[0]

    assert event["node_id"] == "S6"

    assert event["start_time"] == 0

    assert event["duration"] >= 3
    assert event["duration"] <= 7

    assert event["end_time"] == (
        event["start_time"] + event["duration"]
    )

def test_disruption_blocks_new_production():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(model,env,
        stochastic=True,random_seed=42)

    s6 = model.nodes["S6"]

    composite_inventory = (
        s6.input_inventories["Composite"]
    )

    starting_composite = (composite_inventory.on_hand)

    # make sure disruption 
    s6.disruption_probability = 1.0

    env.process(
        runner.daily_production_controller(
            "S6"
        )
    )

    # Only run one simulated day.
    env.run(until=1)

    # No material should have entered production.
    assert composite_inventory.on_hand == (
        starting_composite
    )

    assert runner.is_node_disrupted(
        "S6"
    ) is True

def test_supplier_disruption_pauses_fulfillment():
    model = build_test_model()
    env = simpy.Environment()
    runner = SimulationRunner(model,env,
        stochastic=True,random_seed=42)

    s1 = model.nodes["S1"]

    s1_to_m1 = model.find_transport_link("S1","M1","AP")

    s1_to_m1.variability = 0
    s1.disruption_probability = 0

    # initial 2 day disruption
    runner.disrupted_until["S1"] = 2

    order = model.create_order(
        origin_id="S1",
        destination_id="M1",
        item_name="AP",
        quantity=10
    )

    process = env.process(
        runner.shipment_process(order)
    )

    env.run(until=process)

    # 2 disrupted days, 7 normal days
    assert env.now == 9

    assert order.status == "complete"


def test_supplier_replenishment_controller_creates_order():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(model,env)

    ap_inventory = model.get_inventory("M1","AP")

    # force AP to reorder point
    ap_inventory.on_hand = (ap_inventory.reorder_point)

    ap_inventory.on_order = 0

    env.process(runner.supplier_replenishment_controller())

    env.run(until=1)

    assert len(model.orders) == 1

    order = model.orders[0]

    assert order.origin_id == "S1"
    assert order.destination_id == "M1"
    assert order.item_name == "AP"

    assert order.quantity == (ap_inventory.reorder_quantity)

    assert ap_inventory.on_order == (ap_inventory.reorder_quantity)


def test_supplier_replenishment_does_not_duplicate_order():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(model,env)

    ap_inventory = model.get_inventory("M1","AP")

    ap_inventory.on_hand = (ap_inventory.reorder_point)

    ap_inventory.on_order = 0

    env.process(runner.supplier_replenishment_controller())

    env.run(until=3)

   # shipment hasn't arrived, only one order exists
    assert len(model.orders) == 1


def test_intermediate_controller_moves_motor_cases():
    model = build_test_model()

    env = simpy.Environment()
    runner = SimulationRunner(model, env)

    s6_output = model.get_inventory("S6","Motor Case")

    m1_motor_cases = model.get_inventory("M1","Motor Case")

    # force empty downstream inv
    m1_motor_cases.on_hand = 0
    m1_motor_cases.on_order = 0

    # pretend s6 completed a batch
    s6_output.on_hand = 5

    env.process(runner.intermediate_replenishment_controller())

    env.run(until=1)

    assert len(model.orders) == 1

    order = model.orders[0]

    assert order.origin_id == "S6"
    assert order.destination_id == "M1"
    assert order.item_name == "Motor Case"
    assert order.quantity == 5

    assert s6_output.on_hand == 0
    assert m1_motor_cases.on_hand == 5
    assert order.status == "complete"

def test_intermediate_controller_waits_until_needed():
    model = build_test_model()

    env = simpy.Environment()
    runner = SimulationRunner(model, env)

    s6_output = model.get_inventory("S6","Motor Case")

    m1_motor_cases = model.get_inventory("M1","Motor Case")

    s6_output.on_hand = 5

    # M1 still has enough for one production unit.
    m1_motor_cases.on_hand = 1

    env.process(runner.intermediate_replenishment_controller())

    env.run(until=1)

    assert len(model.orders) == 0
    assert s6_output.on_hand == 5

def test_intermediate_controller_moves_propulsion_modules():
    model = build_test_model()

    env = simpy.Environment()
    runner = SimulationRunner(model, env)

    m1_output = model.get_inventory("M1","Propulsion Module")

    a1_input = model.get_inventory("A1","Propulsion Module")

    a1_input.on_hand = 0
    a1_input.on_order = 0

    m1_output.on_hand = 3

    env.process(runner.intermediate_replenishment_controller())

    env.run(until=1)

    assert m1_output.on_hand == 0
    assert a1_input.on_hand == 3

def test_full_network_produces_final_units():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(model,env,daily_demand=0)

    final_inventory = model.get_inventory("A1",
        "Final Modeled Unit"
    )

    starting_final_units = (final_inventory.on_hand)

    runner.run(until=120)

    assert env.now == 120

    assert final_inventory.on_hand > (
        starting_final_units
    )

def test_simulation_summary():
    model = build_test_model()

    env = simpy.Environment()

    runner = SimulationRunner(model,env)

    runner.run(until=30)

    summary = runner.get_summary()

    assert summary["simulation_time"] == 30
    assert summary["orders_created"] >= 0
    assert summary["shipments_created"] >= 0
    assert summary["disruptions"] == 0