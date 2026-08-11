from shipment import Shipment

# test Area

# making a simple shipment object from S1 to M1
shipment1 = Shipment("SH1", "01", "S1", "M1", "AP", 10)

print("Testing Shipment attributes")
print()

print("Shipment ID:", shipment1.shipment_id)
print("Order ID:", shipment1.order_id)
print("Origin:", shipment1.origin_id)
print("Destination:", shipment1.destination_id)
print("Item:", shipment1.item_name)
print("Quantity:", shipment1.quantity)
print("Status:", shipment1.status)

# marking as delivered test
print()
print("Testing shipment delivery")

shipment1.mark_delivered()

print("Status:", shipment1.status)

# get info test
print()
print("Testing get_info()")
print()

print(shipment1.get_info())

# bad input test
shipment1 = Shipment("SH1", "01", "S1", "M1", "AP", -5)