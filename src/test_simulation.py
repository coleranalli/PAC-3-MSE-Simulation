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