from manufacturer import Manufacturer
from inventory import Inventory

# Test Area

# creating test input inventories

input_A = Inventory("Input A",10,0,0,0,0)
input_B = Inventory("Input B",0,0,0,0,0)

# output inventory
output_inventory = Inventory("Finished Product",0,0,0,0,0)

# dummy recipe
recipe = {
    "Input A": 2,
    "Input B": 1
}

input_inventories = {
    "Input A": input_A,
    "Input B": input_B
}

# creating manufacturer
manufacturer = Manufacturer("Test","Test Manufacturer","Test Location",
    1,1,0,0,"0",0,recipe=recipe,input_inventories=input_inventories,
    output_inventory=output_inventory)

# production availability test
print("Testing production availability")
print()

print(
    "Can produce:",
    manufacturer.can_produce(1)
)

print("Input A:", input_A.on_hand)
print("Input B:", input_B.on_hand)
print("Output:", output_inventory.on_hand)

# enough material for maufacturer now
print()
print("Adding Input B")

input_B.add_inventory(5)

print("Input B:", input_B.on_hand)

print()
print("Can produce:", manufacturer.can_produce(1))

# produce time
print()
print("Producing one unit")

success = manufacturer.produce(1)

print("Production successful:", success)

print()
print("Inventory after production")
print("Input A:", input_A.on_hand)
print("Input B:", input_B.on_hand)
print("Output:", output_inventory.on_hand)

# more units
print()
print("Producing two units")

success = manufacturer.produce(2)

print("Production successful:", success)

print("Input A:", input_A.on_hand)
print("Input B:", input_B.on_hand)
print("Output:", output_inventory.on_hand)

# shortage during production
print()
print("Testing production shortage")

success = manufacturer.produce(3)

print("Production successful:", success)

print("Input A:", input_A.on_hand)
print("Input B:", input_B.on_hand)
print("Output:", output_inventory.on_hand)