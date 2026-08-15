class Order:
    """
    represents a replenishment request in the supply chain
    
    an order records what material and how much of it was requested,
    and where that material should come and go to.
    
    the order is not responsible for actually moving inventory,
    as shipment object will represent the material in transit.
    """

    def __init__(self, order_id, origin_id, destination_id, item_name, quantity):
        """initializes args necessary for an order request"""

        # ensuring non-empty and positive entires
        if order_id == "":
            raise ValueError("Order ID cannot be empty.")

        if origin_id == "":
            raise ValueError("Origin ID cannot be empty.")

        if destination_id == "":
            raise ValueError("Destination ID cannot be empty.")

        if item_name == "":
            raise ValueError("Item Name cannot be empty.")

        if quantity <= 0:
            raise ValueError("Order quantity must be greater than 0.")

        # sec1: order_id
        self.order_id = order_id

        # sec2: coming & going
        self.origin_id = origin_id
        self.destination_id = destination_id

        # sec3: name and amount
        self.item_name = item_name
        self.quantity = quantity

        # sec4: status (newly created is pending)
        self.status = "pending"

    def mark_shipped(self):
        """
        marks the order as shipped.
        
        a shipment object will later represent the material actually moving.
        """
        self.status = "shipped"

    def mark_complete(self):
        """
        marks the order as complete.
        
        this will eventually happen once ordered material reaches its destination.
        """
        self.status = "complete"

    def get_info(self):
        """
        returns the important information about the order
        """

        return (
            f"Order ID: {self.order_id}\n"
            f"Origin: {self.origin_id}\n"
            f"Destination: {self.destination_id}\n"
            f"Item: {self.item_name}\n"
            f"Quantity: {self.quantity}\n"
            f"Status: {self.status}"
        )
