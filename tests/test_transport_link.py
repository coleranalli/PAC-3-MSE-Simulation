from transport_link import TransportLink

# Test Area

# basic object creation
link1 = TransportLink("S1","M1","AP",7,2,0.1)

print("Testing transportation attributes and such")
print()

print("Origin:", link1.origin_id)
print("Destination:", link1.destination_id)
print("Item:", link1.item_name)
print("Lead Time:", link1.lead_time)
print("Variability:", link1.variability)
print(
    "Transportation Delay Probability:",
    link1.transportation_delay_probability
)

# route testing check
print()
print("Testing route matching")
print()

# correct route check
correct_route = link1.matches_route(
    "S1",
    "M1",
    "AP"
)

# terribly, horribly incorrect route check
wrong_route = link1.matches_route(
    "S2",
    "M1",
    "Aluminum"
)

print("Correct route:", correct_route)
print("Wrong route:", wrong_route)

# get_info test
print()
print("Testing get_info()")
print()

print(link1.get_info())

# insidious probability input
link1 = TransportLink("S1","M1","AP",7,2,1.5)