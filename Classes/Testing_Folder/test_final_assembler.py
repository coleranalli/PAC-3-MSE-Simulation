from final_assembler import FinalAssembler
from inventory import Inventory

# input inventory
propulsion_inventory = Inventory("Propulsion Module",5,0,0,0,0)

# final assembled units to be stored here initially
final_inventory = Inventory("Final Modeled Unit",0,0,0,0,0)

# basic test recipe
recipe = {"Propulsion Module": 1}

input_inventories = {"Propulsion Module": propulsion_inventory}

assembler = FinalAssembler("A1","Lockheed Martin","Camden, AR",
    1,1,0,0,"0",0,recipe=recipe, input_inventories=input_inventories, 
    output_inventory=final_inventory)

# demand test
print("Testing external demand")
print()

assembler.add_external_demand(4)

print("External Demand:", assembler.external_demand)
print("Fulfilled Demand:", assembler.fulfilled_demand)
print("Backlog:", assembler.backlog)

# trying to fill demand before production
print()
print("Testing demand with no finished inventory")

fulfilled = assembler.fulfill_demand()

print("Quantity Fulfilled:", fulfilled)
print("Final Inventory:", final_inventory.on_hand)
print("Backlog:", assembler.backlog)


# inherited production test
print()
print("Producing 3 final units")

success = assembler.produce(3)

print("Production Successful:", success)
print("Propulsion Modules:", propulsion_inventory.on_hand)
print("Final Inventory:", final_inventory.on_hand)

# fulfilling backlog
print()
print("Fulfilling demand")

fulfilled = assembler.fulfill_demand()

print("Quantity Fulfilled:", fulfilled)
print("External Demand:", assembler.external_demand)
print("Fulfilled Demand:", assembler.fulfilled_demand)
print("Backlog:", assembler.backlog)
print("Final Inventory:", final_inventory.on_hand)

# finishing remaining demand
print()
print("Producing another unit")

assembler.produce(1)

print("Final Inventory:", final_inventory.on_hand)
print("Backlog:", assembler.backlog)

fulfilled = assembler.fulfill_demand()

print()
print("Final demand results")

print("Quantity Fulfilled:", fulfilled)
print("External Demand:", assembler.external_demand)
print("Fulfilled Demand:", assembler.fulfilled_demand)
print("Backlog:", assembler.backlog)
print("Final Inventory:", final_inventory.on_hand)