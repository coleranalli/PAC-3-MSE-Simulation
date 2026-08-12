from order import Order


# Test Area

# basic replenishment order
order1 = Order("O1", "S1", "M1", "AP", 10)


print("Testing Order attributes")
print()

print("Order ID:", order1.order_id)
print("Origin:", order1.origin_id)
print("Destination:", order1.destination_id)
print("Item:", order1.item_name)
print("Quantity:", order1.quantity)
print("Status:", order1.status)

# status changes testing

print()
print("Testing order status")

order1.mark_shipped()

print("After shipment:", order1.status)

order1.mark_complete()

print("After completion:", order1.status)

