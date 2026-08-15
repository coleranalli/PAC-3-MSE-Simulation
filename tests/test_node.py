from node import Node

# Test Area

# creates a basic test node
node1 = Node("S1", "AMPAC", "Cedar City, UT")

print("Testing Node attributes")
print()

print("Node ID:", node1.node_id)
print("Name:", node1.name)
print("Location:", node1.location)

print()

print("Testing get_info()")
print()
print(node1.get_info())

# bad input test

# print()
# print("Testing invalid node")

# bad_node = Node("", "Test Facility", "Test Location")