from manufacturer import Manufacturer
from supplier import Supplier

def get_deterministic_shipment_delay(model, order):
    """
    returns the non-probalisitc shipment delay.
    
    supplier lead time = order to availability time.

    manufactuer lead time = production time (no delay)
    """

    transport_link = model.find_transport_link(
        order.origin_id,
        order.destination_id,
        order.item_name
    )

    if transport_link is None:
        raise ValueError("No matching transport link exists.")

    origin_node = model.nodes[order.origin_id]

    if isinstance(origin_node, Supplier):
        return transport_link.lead_time

    if isinstance(origin_node, Manufacturer):
        return 0

    raise ValueError(
        "Shipment origin must be a supplier or manufacturer."
    )

class SimulationRunner:
    """controls timed simulation process"""

    def __init__(self, model, environment=None):

        self.model=model
        if environment is None:
            import simpy
            environment = simpy.Environment()

        self.env = environment

    def shipment_process(self, order):
        """
        creates a shipment, waits for lead time, then delivers.
        """

        # creating shipment
        shipment = self.model.create_shipment(order)

        # determine how ong shipment should take
        delay = get_deterministic_shipment_delay(
            self.model, order
        )

        # pause process for simulated delay
        yield self.env.timeout(delay)

        # delivery occurs
        self.model.deliver_shipment(shipment)

        return shipment