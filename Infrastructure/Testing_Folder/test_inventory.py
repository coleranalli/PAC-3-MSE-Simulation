from inventory import Inventory

# Test Area

# creates a test inventory
ap_inventory = Inventory(item_name="AP", on_hand=60, reorder_point=40, 
    reorder_quantity=50, holding_cost=1, shortage_cost=5)

print("Starting inventory")
print("On hand:", ap_inventory.on_hand)
print("On order:", ap_inventory.on_order)
print("Backorders:", ap_inventory.backorders)
print("Inventory position:", ap_inventory.get_inventory_position())

print()

# Inventory position is 60, so it should not reorder yet.
print("Should reorder:", ap_inventory.should_reorder())

# Use 25 units.
success = ap_inventory.remove_inventory(25)

print()
print("After using 25 units")
print("Removal successful:", success)
print("On hand:", ap_inventory.on_hand)
print("Inventory position:", ap_inventory.get_inventory_position())
print("Should reorder:", ap_inventory.should_reorder())

# Pretending the supply chain created an order.
if ap_inventory.should_reorder():
    ap_inventory.record_replenishment_order(ap_inventory.reorder_quantity)

print()
print("After placing replenishment order")
print("On hand:", ap_inventory.on_hand)
print("On order:", ap_inventory.on_order)
print("Inventory position:", ap_inventory.get_inventory_position())
print("Should reorder again:", ap_inventory.should_reorder())

# Receive part of the outstanding order.
ap_inventory.receive_replenishment(20)

print()
print("After receiving 20 units")
print("On hand:", ap_inventory.on_hand)
print("On order:", ap_inventory.on_order)
print("Inventory position:", ap_inventory.get_inventory_position())

# bad inventory test

# print()
# print("Testing insufficient inventory")

# success = ap_inventory.remove_inventory(100)

# print("Removal successful:", success)
# print("On hand:", ap_inventory.on_hand)