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

    def production_process(self, manufacturer_id, quantity=1):
        """
        waits for manufacturer's processing time, then performas production
        """

        # make sure node exists
        if manufacturer_id not in self.model.nodes:
            raise ValueError(
                f"Manufacturer {manufacturer_id} does not exist"
            )

        manufacturer = self.model.nodes[manufacturer_id]

        # only manufacturer objects can use this
        if not isinstance(manufacturer, Manufacturer):
            raise ValueError(
                f"Node {manufacturer_id} is not a manufacturer"
            )

        if quantity <= 0:
            raise ValueError(
                "Production quantity must be greater than zero."
            )

        # no production if inputs are not available
        if not manufacturer.consume_inputs(quantity):
            return False

        # wait for processing lead time
        yield self.env.timeout(manufacturer.lead_time)

        manufacturer.complete_production(quantity)

        return True

    def production_completion_process(self,manufacturer,quantity):
        """waits for production process to complete"""

        yield self.env.timeout(manufacturer.lead_time)

        manufacturer.complete_production(quantity)

    def daily_production_controller(self,manufacturer_id):
        """
        attempts a production start each day.

        capacity = average number of whole units completed per day
        """

        if manufacturer_id not in self.model.nodes:
            raise ValueError(
                f"Manufacturer {manufacturer_id} does not exist."
            )

        manufacturer = self.model.nodes[manufacturer_id]

        if not isinstance(manufacturer, Manufacturer):
            raise ValueError(
                f"Node {manufacturer_id} is not a manufacturer."
            )

        if manufacturer.capacity <= 0:
            raise ValueError(
                "Manufacturer capacity must be greater than zero."
            )

        # unused fractional capacity storage
        capacity_balance = 0

        while True:

            # each new day = one more day of capcity
            capacity_balance += manufacturer.capacity

            units_allowed = int(capacity_balance)

            capacity_balance -= units_allowed

            for unit_number in range(units_allowed):

                # no amterial = stop starting units
                if not manufacturer.can_produce(1):
                    break

                manufacturer.consume_inputs(1)

                # unit can process simaltaneously with other units
                self.env.process(
                    self.production_completion_process(manufacturer,1)
                )

            # move to next day
            yield self.env.timeout(1)