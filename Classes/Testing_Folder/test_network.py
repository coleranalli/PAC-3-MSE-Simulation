"""AI-assisted test of supply chain network/model"""

from inventory import Inventory
from supplier import Supplier
from manufacturer import Manufacturer
from final_assembler import FinalAssembler
from transport_link import TransportLink
from supply_chain_model import SupplyChainModel


# ============================================================
# CREATE SUPPLY CHAIN MODEL
# ============================================================

model = SupplyChainModel()


# ============================================================
# CREATE INVENTORIES
# ============================================================

# ------------------------------------------------------------
# S6 INPUT AND OUTPUT INVENTORY
# ------------------------------------------------------------

composite_inventory = Inventory(
    item_name="Composite",
    on_hand=5,
    reorder_point=2,
    reorder_quantity=3,
    holding_cost=0,
    shortage_cost=0
)

s6_motor_case_output = Inventory(
    item_name="Motor Case",
    on_hand=0,
    reorder_point=0,
    reorder_quantity=0,
    holding_cost=0,
    shortage_cost=0
)


# ------------------------------------------------------------
# M1 INPUT AND OUTPUT INVENTORIES
# ------------------------------------------------------------

ap_inventory = Inventory(
    item_name="AP",
    on_hand=5,
    reorder_point=2,
    reorder_quantity=3,
    holding_cost=0,
    shortage_cost=0
)

aluminum_inventory = Inventory(
    item_name="Aluminum",
    on_hand=5,
    reorder_point=2,
    reorder_quantity=3,
    holding_cost=0,
    shortage_cost=0
)

htpb_inventory = Inventory(
    item_name="HTPB",
    on_hand=5,
    reorder_point=2,
    reorder_quantity=3,
    holding_cost=0,
    shortage_cost=0
)

motor_case_inventory = Inventory(
    item_name="Motor Case",
    on_hand=0,
    reorder_point=1,
    reorder_quantity=1,
    holding_cost=0,
    shortage_cost=0
)

inert_hardware_inventory = Inventory(
    item_name="Inert Hardware",
    on_hand=5,
    reorder_point=2,
    reorder_quantity=3,
    holding_cost=0,
    shortage_cost=0
)

m1_propulsion_output = Inventory(
    item_name="Propulsion Module",
    on_hand=0,
    reorder_point=0,
    reorder_quantity=0,
    holding_cost=0,
    shortage_cost=0
)


# ------------------------------------------------------------
# A1 INPUT AND OUTPUT INVENTORIES
# ------------------------------------------------------------

propulsion_inventory = Inventory(
    item_name="Propulsion Module",
    on_hand=0,
    reorder_point=1,
    reorder_quantity=1,
    holding_cost=0,
    shortage_cost=0
)

final_inventory = Inventory(
    item_name="Final Modeled Unit",
    on_hand=0,
    reorder_point=0,
    reorder_quantity=0,
    holding_cost=0,
    shortage_cost=0
)


# ============================================================
# CREATE SUPPLIERS
# ============================================================

s1 = Supplier(
    node_id="S1",
    name="AMPAC",
    location="Cedar City, UT",
    capacity=1.25,
    output_item="AP",
    disruption_probability=0.004,
    disruption_duration="2-5"
)

s2 = Supplier(
    node_id="S2",
    name="AMPAL",
    location="Palmerton, PA",
    capacity=1.50,
    output_item="Aluminum",
    disruption_probability=0.001,
    disruption_duration="3-7"
)

s3 = Supplier(
    node_id="S3",
    name="Resin Sol.",
    location="Channelview, TX",
    capacity=1.35,
    output_item="HTPB",
    disruption_probability=0.002,
    disruption_duration="3-6"
)

s4 = Supplier(
    node_id="S4",
    name="Toray",
    location="Spartanburg, SC",
    capacity=1.40,
    output_item="Composite",
    disruption_probability=0.005,
    disruption_duration="4-8"
)

s5 = Supplier(
    node_id="S5",
    name="L3Harris AMF",
    location="Huntsville, AL",
    capacity=1.45,
    output_item="Inert Hardware",
    disruption_probability=0.004,
    disruption_duration="4-10"
)


# ============================================================
# CREATE S6 MANUFACTURER
# ============================================================

# TEST RECIPE ONLY
# 1 Composite -> 1 Motor Case

s6_recipe = {
    "Composite": 1
}

s6_input_inventories = {
    "Composite": composite_inventory
}

s6 = Manufacturer(
    node_id="S6",
    name="GD OTS",
    location="Lincoln, NE",
    capacity=1.30,
    lead_time=45,
    variability=10,
    disruption_probability=0.009,
    disruption_duration="3-7",
    shortage_idle_cost=120,
    recipe=s6_recipe,
    input_inventories=s6_input_inventories,
    output_inventory=s6_motor_case_output
)


# ============================================================
# CREATE M1 MANUFACTURER
# ============================================================

# TEST RECIPE ONLY
#
# 1 AP
# 1 Aluminum
# 1 HTPB
# 1 Motor Case
# 1 Inert Hardware
#
# -> 1 Propulsion Module

m1_recipe = {
    "AP": 1,
    "Aluminum": 1,
    "HTPB": 1,
    "Motor Case": 1,
    "Inert Hardware": 1
}

m1_input_inventories = {
    "AP": ap_inventory,
    "Aluminum": aluminum_inventory,
    "HTPB": htpb_inventory,
    "Motor Case": motor_case_inventory,
    "Inert Hardware": inert_hardware_inventory
}

m1 = Manufacturer(
    node_id="M1",
    name="L3Harris APF",
    location="Camden, AR",
    capacity=1.10,
    lead_time=14,
    variability=4,
    disruption_probability=0.003,
    disruption_duration="2-5",
    shortage_idle_cost=250,
    recipe=m1_recipe,
    input_inventories=m1_input_inventories,
    output_inventory=m1_propulsion_output
)


# ============================================================
# CREATE A1 FINAL ASSEMBLER
# ============================================================

# TEST RECIPE ONLY
# 1 Propulsion Module -> 1 Final Modeled Unit

a1_recipe = {
    "Propulsion Module": 1
}

a1_input_inventories = {
    "Propulsion Module": propulsion_inventory
}

a1 = FinalAssembler(
    node_id="A1",
    name="Lockheed Martin",
    location="Camden, AR",
    capacity=1.20,
    lead_time=7,
    variability=2,
    disruption_probability=0.002,
    disruption_duration="1-3",
    shortage_idle_cost=400,
    recipe=a1_recipe,
    input_inventories=a1_input_inventories,
    output_inventory=final_inventory
)


# ============================================================
# ADD ALL NODES TO MODEL
# ============================================================

model.add_node(s1)
model.add_node(s2)
model.add_node(s3)
model.add_node(s4)
model.add_node(s5)
model.add_node(s6)
model.add_node(m1)
model.add_node(a1)

print("============================================================")
print("NETWORK SETUP")
print("============================================================")

print("Nodes in network:", len(model.nodes))


# ============================================================
# REGISTER RECEIVING INVENTORIES
# ============================================================

model.add_inventory(
    "S6",
    composite_inventory
)

model.add_inventory(
    "M1",
    ap_inventory
)

model.add_inventory(
    "M1",
    aluminum_inventory
)

model.add_inventory(
    "M1",
    htpb_inventory
)

model.add_inventory(
    "M1",
    motor_case_inventory
)

model.add_inventory(
    "M1",
    inert_hardware_inventory
)

model.add_inventory(
    "A1",
    propulsion_inventory
)


# ============================================================
# CREATE TRANSPORT LINKS
# ============================================================

model.add_transport_link(
    TransportLink(
        origin_id="S1",
        destination_id="M1",
        item_name="AP",
        lead_time=7,
        variability=2,
        transportation_delay_probability=0.10
    )
)

model.add_transport_link(
    TransportLink(
        origin_id="S2",
        destination_id="M1",
        item_name="Aluminum",
        lead_time=20,
        variability=5,
        transportation_delay_probability=0.05
    )
)

model.add_transport_link(
    TransportLink(
        origin_id="S3",
        destination_id="M1",
        item_name="HTPB",
        lead_time=14,
        variability=4,
        transportation_delay_probability=0.04
    )
)

model.add_transport_link(
    TransportLink(
        origin_id="S4",
        destination_id="S6",
        item_name="Composite",
        lead_time=30,
        variability=7,
        transportation_delay_probability=0.03
    )
)

model.add_transport_link(
    TransportLink(
        origin_id="S5",
        destination_id="M1",
        item_name="Inert Hardware",
        lead_time=30,
        variability=7,
        transportation_delay_probability=0.02
    )
)

model.add_transport_link(
    TransportLink(
        origin_id="S6",
        destination_id="M1",
        item_name="Motor Case",
        lead_time=45,
        variability=10,
        transportation_delay_probability=0.05
    )
)

model.add_transport_link(
    TransportLink(
        origin_id="M1",
        destination_id="A1",
        item_name="Propulsion Module",
        lead_time=14,
        variability=4,
        transportation_delay_probability=0.01
    )
)

print("Transport links:", len(model.transport_links))


# ============================================================
# TEST 1: S6 PRODUCES A MOTOR CASE
# ============================================================

print()
print("============================================================")
print("TEST 1 - S6 MOTOR CASE PRODUCTION")
print("============================================================")

print("Composite before production:", composite_inventory.on_hand)
print("Motor Cases before production:", s6_motor_case_output.on_hand)

success = s6.produce(1)

print()
print("Production successful:", success)
print("Composite after production:", composite_inventory.on_hand)
print("Motor Cases after production:", s6_motor_case_output.on_hand)


# ============================================================
# TEST 2: MOVE MOTOR CASE FROM S6 TO M1
# ============================================================

print()
print("============================================================")
print("TEST 2 - MOTOR CASE SHIPMENT S6 -> M1")
print("============================================================")

motor_case_order = model.create_order(
    origin_id="S6",
    destination_id="M1",
    item_name="Motor Case",
    quantity=1
)

print("Order ID:", motor_case_order.order_id)
print("Order status:", motor_case_order.status)
print("M1 Motor Cases on order:", motor_case_inventory.on_order)


motor_case_shipment = model.create_shipment(
    motor_case_order
)

print()
print("Shipment ID:", motor_case_shipment.shipment_id)
print("Shipment status:", motor_case_shipment.status)
print("Order status:", motor_case_order.status)

print(
    "Motor Cases remaining at S6:",
    s6_motor_case_output.on_hand
)

print(
    "Motor Cases on order at M1:",
    motor_case_inventory.on_order
)


model.deliver_shipment(
    motor_case_shipment
)

print()
print("After delivery:")

print(
    "Shipment status:",
    motor_case_shipment.status
)

print(
    "Order status:",
    motor_case_order.status
)

print(
    "Motor Cases at M1:",
    motor_case_inventory.on_hand
)

print(
    "Motor Cases on order at M1:",
    motor_case_inventory.on_order
)


# ============================================================
# TEST 3: M1 PRODUCES PROPULSION MODULE
# ============================================================

print()
print("============================================================")
print("TEST 3 - M1 PROPULSION MODULE PRODUCTION")
print("============================================================")

print("AP:", ap_inventory.on_hand)
print("Aluminum:", aluminum_inventory.on_hand)
print("HTPB:", htpb_inventory.on_hand)
print("Motor Case:", motor_case_inventory.on_hand)
print("Inert Hardware:", inert_hardware_inventory.on_hand)

print()
print("Can M1 produce:", m1.can_produce(1))

success = m1.produce(1)

print("Production successful:", success)

print()
print("Inventories after production:")

print("AP:", ap_inventory.on_hand)
print("Aluminum:", aluminum_inventory.on_hand)
print("HTPB:", htpb_inventory.on_hand)
print("Motor Case:", motor_case_inventory.on_hand)
print("Inert Hardware:", inert_hardware_inventory.on_hand)

print(
    "Propulsion Modules at M1:",
    m1_propulsion_output.on_hand
)


# ============================================================
# TEST 4: MOVE PROPULSION MODULE FROM M1 TO A1
# ============================================================

print()
print("============================================================")
print("TEST 4 - PROPULSION MODULE SHIPMENT M1 -> A1")
print("============================================================")

propulsion_order = model.create_order(
    origin_id="M1",
    destination_id="A1",
    item_name="Propulsion Module",
    quantity=1
)

print("Order ID:", propulsion_order.order_id)
print("Order status:", propulsion_order.status)

print(
    "Propulsion Modules on order at A1:",
    propulsion_inventory.on_order
)


propulsion_shipment = model.create_shipment(
    propulsion_order
)

print()
print("Shipment ID:", propulsion_shipment.shipment_id)
print("Shipment status:", propulsion_shipment.status)
print("Order status:", propulsion_order.status)

print(
    "Propulsion Modules remaining at M1:",
    m1_propulsion_output.on_hand
)


model.deliver_shipment(
    propulsion_shipment
)

print()
print("After delivery:")

print(
    "Shipment status:",
    propulsion_shipment.status
)

print(
    "Order status:",
    propulsion_order.status
)

print(
    "Propulsion Modules at A1:",
    propulsion_inventory.on_hand
)

print(
    "Propulsion Modules on order at A1:",
    propulsion_inventory.on_order
)


# ============================================================
# TEST 5: A1 RECEIVES EXTERNAL DEMAND
# ============================================================

print()
print("============================================================")
print("TEST 5 - EXTERNAL DEMAND")
print("============================================================")

a1.add_external_demand(1)

print("External demand:", a1.external_demand)
print("Fulfilled demand:", a1.fulfilled_demand)
print("Backlog:", a1.backlog)


# ============================================================
# TEST 6: A1 PRODUCES FINAL UNIT
# ============================================================

print()
print("============================================================")
print("TEST 6 - FINAL ASSEMBLY")
print("============================================================")

print(
    "Propulsion Modules before assembly:",
    propulsion_inventory.on_hand
)

print(
    "Can A1 produce:",
    a1.can_produce(1)
)

success = a1.produce(1)

print("Final assembly successful:", success)

print(
    "Propulsion Modules after assembly:",
    propulsion_inventory.on_hand
)

print(
    "Final inventory:",
    final_inventory.on_hand
)


# ============================================================
# TEST 7: FULFILL EXTERNAL DEMAND
# ============================================================

print()
print("============================================================")
print("TEST 7 - DEMAND FULFILLMENT")
print("============================================================")

fulfilled = a1.fulfill_demand()

print("Demand fulfilled this time:", fulfilled)
print("Total external demand:", a1.external_demand)
print("Total fulfilled demand:", a1.fulfilled_demand)
print("Backlog:", a1.backlog)
print("Final inventory:", final_inventory.on_hand)


# ============================================================
# FINAL MODEL STATISTICS
# ============================================================

print()
print("============================================================")
print("FINAL MODEL STATISTICS")
print("============================================================")

print(
    "Orders created:",
    model.statistics["orders_created"]
)

print(
    "Shipments created:",
    model.statistics["shipments_created"]
)

print(
    "Shipments delivered:",
    model.statistics["shipments_delivered"]
)


# ============================================================
# FINAL SUCCESS CHECKS
# ============================================================

print()
print("============================================================")
print("FINAL CHECK")
print("============================================================")

assert len(model.nodes) == 8
assert len(model.transport_links) == 7

assert s6_motor_case_output.on_hand == 0
assert motor_case_inventory.on_hand == 0

assert m1_propulsion_output.on_hand == 0
assert propulsion_inventory.on_hand == 0

assert final_inventory.on_hand == 0

assert a1.external_demand == 1
assert a1.fulfilled_demand == 1
assert a1.backlog == 0

assert model.statistics["orders_created"] == 2
assert model.statistics["shipments_created"] == 2
assert model.statistics["shipments_delivered"] == 2

print("ALL INTEGRATION TESTS PASSED!")