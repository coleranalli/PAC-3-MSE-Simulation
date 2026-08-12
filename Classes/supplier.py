from node import Node

class Supplier(Node):
    """
    represents a supplier facility in the supply chain.
    
    inherits basic facility info from node & adds supplier info.
    
    supplier stores:
    - production capacity
    - item it supplies
    - disruption of info
    - queue of replenishment orders
    
    supplier does not own inventory stored at receiving facilities.
    """

    def __init__(self, node_id, name, location, capacity, 
        output_item, disruption_probability, disruption_duration):

        # initializing inherited attributes
        super().__init__(node_id, name, location)

        # preventing negative capacity
        if capacity < 0:
            raise ValueError("Capacity cannot be negative.")

        if output_item == "":
            raise ValueError("Output item cannot be empty.")

        # keeping probability between 1 and 0
        if (
            disruption_probability < 0
            or disruption_probability > 1
        ):
            raise ValueError(
                "Disruption probability must be between 0 and 1."
            )

        if disruption_duration == "":
            raise ValueError("Disruption duration cannot be empty.")

        # initializing others
        self.capacity = capacity
        self.output_item = output_item

        self.disruption_probability = disruption_probability
        self.disruption_duration = disruption_duration

        # orders are stored in the order they are received
        self.order_queue = []

    def add_order(self, order):
        """adds order object to the end of the queue."""

        self.order_queue.append(order)

    def get_next_order(self):
        """
        returns first order waiting in the queue.
        
        order is not removed from queue, returns None if no queue.
        """

        if len(self.order_queue) > 0:
            return self.order_queue[0]

        return None

    def remove_next_order(self):
        """
        removes and returns the first order in queue.

        no orders waiting returns None.
        """

        if len(self.order_queue) > 0:
            order = self.order_queue.pop(0)
            return order

        return None


    def get_queue_length(self):
        """returns length of queue (literally)"""

        return len(self.order_queue)


    def get_info(self):
        """returns basic info about supplier & node"""

        return (
            f"{super().get_info()}\n"
            f"Capacity: {self.capacity}\n"
            f"Output Item: {self.output_item}\n"
            f"Disruption Probability: "
            f"{self.disruption_probability}\n"
            f"Disruption Duration: "
            f"{self.disruption_duration}\n"
            f"Orders Waiting: {self.get_queue_length()}"
        )