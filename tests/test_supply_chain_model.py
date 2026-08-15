from node import Node
from supplier import Supplier
from inventory import Inventory
from transport_link import TransportLink
from supply_chain_model import SupplyChainModel

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

# statistic check
print()
print("Testing statistics")
print()

print("Orders Created:", model.statistics["orders_created"])

print("Shipments Created:", model.statistics["shipments_created"])

print("Shipments Delivered:", model.statistics["shipments_delivered"])