from supplier import Supplier
from order import Order

# Test Area

# make sample supplier object
ampac = Supplier("S1", "AMPAC", "Cedar City, UT", 1.25,"AP", .004, "2-5")

print("Testing Supplier attributes")
print()

# returning basic info
print("Node ID:", ampac.node_id)
print("Name:", ampac.name)
print("Location:", ampac.location)
print("Capacity:", ampac.capacity)
print("Output Item:", ampac.output_item)
print("Disruption Probability:",
    ampac.disruption_probability)
print("Disruption Duration:",
    ampac.disruption_duration)
print("Queue Length:", ampac.get_queue_length())

# testing for inheritance
print()
print("Testing inherited Node method")
print()

print(ampac.get_info())

# testing order with supplier
order1 = Order("01","S1","M1","AP",10)
order2 = Order("02","S1","M1","AP",10)

print()
print("Testing order queue")
print()

ampac.add_order(order1)
ampac.add_order(order2)

print("Queue Length:", ampac.get_queue_length())

next_order = ampac.get_next_order()

print("Next Order:", next_order.order_id)
print("Queue Length:", ampac.get_queue_length())

# testing removing
removed_order = ampac.remove_next_order()

print()
print("Removed Order:", removed_order.order_id)
print("Queue Length:", ampac.get_queue_length())

next_order = ampac.get_next_order()

print("New Next Order:", next_order.order_id)

# removing the last order
ampac.remove_next_order()

print()
print("Testing empty queue")

next_order = ampac.get_next_order()

print("Next Order:", next_order)
print("Queue Length:", ampac.get_queue_length())