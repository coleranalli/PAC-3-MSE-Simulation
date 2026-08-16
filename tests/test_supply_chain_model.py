from node import Node
from supplier import Supplier
from inventory import Inventory
from transport_link import TransportLink
from supply_chain_model import SupplyChainModel
from manufacturer import Manufacturer

# Test Area

# creating model
model = SupplyChainModel()

# create nodes

s1 = Supplier("S1", "AMPAC", "Cedar City, UT", 
    1.25, "AP", 0.004, "2-5")

# simple node to test replenishment behavior
m1 = Node("M1", "L3Harris", "Camden, AR")

model.add_node(s1)
model.add_node(m1)

# create AP inventory at M1
ap_inventory = Inventory("AP",5,10,10,1.25,100)

model.add_inventory("M1", inventory=ap_inventory)

# create S1 -> M1 transport link
ap_link = TransportLink("S1","M1","AP",7,2,0.10)

model.add_transport_link(ap_link)

# verifying setup
print("Testing model setup")
print()

print("Number of nodes:", len(model.nodes))
print(
    "AP on hand:",
    model.get_inventory("M1", "AP").on_hand
)
print(
    "Transport link found:",
    model.find_transport_link("S1", "M1", "AP") is not None
)

# reorder test
print()
print("Testing reorder")
print()

order = model.create_reorder_if_needed("S1", "M1", "AP")

print("Order created:", order is not None)
print("Order ID:", order.order_id)
print("Order status:", order.status)

print("AP on hand:", ap_inventory.on_hand)

print("AP on order:", ap_inventory.on_order)

print("Inventory position:", ap_inventory.get_inventory_position())

print("Supplier queue length:", s1.get_queue_length())

# duplicate order prevention
print()
print("Testing duplicate reorder prevention")
print()

second_order = model.create_reorder_if_needed("S1", "M1", "AP")

print("Second order:", second_order)
print("Number of orders:", len(model.orders))

# shipment creation
print()
print("Testing shipment creation")
print()

shipment = model.create_shipment(order)

print("Shipment ID:", shipment.shipment_id)
print("Shipment status:", shipment.status)
print("Order status:", order.status)

print("Supplier queue length:", s1.get_queue_length())

print("AP on order:", ap_inventory.on_order)

# delivery test
print()
print("Testing shipment delivery")
print()

model.deliver_shipment(shipment)

print("Shipment status:", shipment.status)
print("Order status:", order.status)

print("AP on hand:", ap_inventory.on_hand)

print("AP on order:", ap_inventory.on_order)

print("Inventory position:", ap_inventory.get_inventory_position())

# regression checks for the supplier-origin S1 -> M1 path
assert shipment.origin_id == "S1"
assert shipment.destination_id == "M1"
assert shipment.item_name == "AP"
assert shipment.status == "delivered"
assert order.status == "complete"
assert s1.get_queue_length() == 0
assert ap_inventory.on_hand == 15
assert ap_inventory.on_order == 0

# statistic check
print()
print("Testing statistics")
print()

print("Orders Created:", model.statistics["orders_created"])

print("Shipments Created:", model.statistics["shipments_created"])

print("Shipments Delivered:", model.statistics["shipments_delivered"])


def test_supplier_order_shipment_delivery_path():
    """Regression test for a supplier-origin S1 -> M1 replenishment."""
    test_model = SupplyChainModel()

    test_supplier = Supplier(
        "S1", "AMPAC", "Cedar City, UT", 1.25, "AP", 0.004, "2-5"
    )
    test_destination = Node("M1", "L3Harris", "Camden, AR")

    test_model.add_node(test_supplier)
    test_model.add_node(test_destination)

    test_inventory = Inventory("AP", 5, 10, 10, 1.25, 100)
    test_model.add_inventory("M1", inventory=test_inventory)

    test_link = TransportLink("S1", "M1", "AP", 7, 2, 0.10)
    test_model.add_transport_link(test_link)

    test_order = test_model.create_reorder_if_needed("S1", "M1", "AP")
    test_shipment = test_model.create_shipment(test_order)
    test_model.deliver_shipment(test_shipment)

    assert test_shipment.status == "delivered"
    assert test_order.status == "complete"
    assert test_supplier.get_queue_length() == 0
    assert test_inventory.on_hand == 15
    assert test_inventory.on_order == 0



def test_manufacturer_output_removed_when_shipment_created():
    """Manufactured material must leave output inventory when shipped."""
    test_model = SupplyChainModel()

    input_inventory = Inventory("Test Input", 0, 0, 0, 0, 0)
    output_inventory = Inventory("Motor Case", 2, 0, 0, 0, 0)
    receiving_inventory = Inventory("Motor Case", 0, 0, 1, 0, 0)

    manufacturer = Manufacturer(
        "S6",
        "GD OTS",
        "Lincoln, NE",
        1.30,
        45,
        10,
        0.009,
        "3-7",
        120,
        {"Test Input": 1},
        {"Test Input": input_inventory},
        output_inventory
    )
    destination = Node("M1", "L3Harris", "Camden, AR")

    test_model.add_node(manufacturer)
    test_model.add_node(destination)
    test_model.add_inventory("M1", receiving_inventory)
    test_model.add_transport_link(
        TransportLink("S6", "M1", "Motor Case", 45, 10, 0.05)
    )

    test_order = test_model.create_order("S6", "M1", "Motor Case", 1)
    test_model.create_shipment(test_order)

    assert output_inventory.on_hand == 1
    assert test_order.status == "shipped"
