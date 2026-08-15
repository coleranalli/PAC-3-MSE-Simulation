from order import Order
from shipment import Shipment

# Test Area
print("testing Order and Shipment together")
print()

# M1 requests 10 units of AP from S1
order2 = Order("O2", "S1", "M1", "AP", 10)

print("Order status:", order2.status)

# supplier ships the material
shipment2 = Shipment(
    "SH2", order2.order_id, order2.origin_id,
    order2.destination_id, order2.item_name, order2.quantity
)

order2.mark_shipped()

print("Order status:", order2.status)
print("Shipment status:", shipment2.status)

# material arrives
shipment2.mark_delivered()
order2.mark_complete()

print("Order status:", order2.status)
print("Shipment status:", shipment2.status)