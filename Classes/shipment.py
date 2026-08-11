class Shipment:
    """
    class representing material in transit between supplier 
    & manufacturer.
    
    Order = material being requested
    Shipment = material moving through supply chain
    """

    def __init__(self, shipment_id, order_id, origin_id,
        destination_id, item_name, quantity):

        # validating all information

        if shipment_id == "":
            raise ValueError("Shipment ID cannot be empty.")

        if order_id == "":
            raise ValueError("Order ID cannot be empty.")

        if origin_id == "":
            raise ValueError("Origin ID cannot be empty.")

        if destination_id == "":
            raise ValueError("Destination ID cannot be empty.")

        if item_name == "":
            raise ValueError("Item name cannot be empty.")

        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")

        # sec1: shipment module ids
        self.shipment_id = shipment_id
        self.order_id = order_id

        # sec2: coming & going ids
        self.origin_id = origin_id
        self.destination_id = destination_id

        # sec3: item info
        self.item_name = item_name
        self.quantity = quantity

        # sec4: shipment begins in transit
        self.status = "in_transit"

    def mark_delivered(self):
        """
        marks the shipment as delivered.
        
        inventry updates/order completion are to be
        handled by SupplyChainModel.
        """

        self.status = "delivered"

    def get_info(self):
        """returns important info about the shipment"""

        return (
            f"Shipment ID: {self.shipment_id}\n"
            f"Order ID: {self.order_id}\n"
            f"Origin: {self.origin_id}\n"
            f"Destination: {self.destination_id}\n"
            f"Item: {self.item_name}\n"
            f"Quantity: {self.quantity}\n"
            f"Status: {self.status}"        
        )