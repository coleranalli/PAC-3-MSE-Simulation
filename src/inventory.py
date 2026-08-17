class Inventory():
    """class that represents the inventory of a particular item at one facility
    
    Keeps track of:
        - material on hand
        - material on order
        - backorders
        - reorder policy info
        - costs related to inventory
    """
    def __init__(self, item_name, on_hand, reorder_point, reorder_quantity, holding_cost, 
        shortage_cost, on_order=0, backorders=0):
        """initializes inventory object, ensures non-negative values"""

        if on_hand < 0:
            raise ValueError('On-hand inventory cannot be negative.')
        if on_order < 0:
            raise ValueError('On-order inventory cannot be negative.')
        if backorders < 0:
            raise ValueError('Backorders cannot be negative.')

        # due to N/A's in csv files, changing to ensure compatability
        if reorder_point is not None and reorder_point < 0:
            raise ValueError('Reorder point cannot be negative.')
        if reorder_quantity is not None and reorder_quantity < 0:
            raise ValueError('Reoder quantity cannot be negative.')
        if holding_cost is not None and holding_cost < 0:
            raise ValueError('Holding cost cannot be negative.')
        if shortage_cost is not None and shortage_cost < 0:
            raise ValueError('Shortage cost cannot be negative.')

        # sec1: item in question
        self.item_name = item_name

        # sec2: item amounts avaialble
        self.on_hand = on_hand
        self.on_order = on_order
        self.backorders = backorders

        # sec3: reorder timing & amounts
        self.reorder_point = reorder_point
        self.reorder_quantity = reorder_quantity

        # sec4: item holding & shortage costs
        self.holding_cost = holding_cost
        self.shortage_cost = shortage_cost

    def get_inventory_position(self):
        """
        calculates the inventory position. 

        includes material already ordered since it is 
        expected to arrive later.
        """

        inventory_position = self.on_hand + self.on_order - self.backorders

        return inventory_position
    
    def should_reorder(self):
        """determines if a replenishment order must be placed
        
        needed if inventory position is at or below reorder point, and 
        if the material is not already on order (preventing duplicates)
        """
        # none indicates no reorder policy
        if self.reorder_point is None or self.reorder_quantity is None:
            return False
    
        if (
            self.get_inventory_position() <= self.reorder_point
            and self.on_order == 0
        ):
            return True

        return False

    def can_fulfill(self, quantity):
        """
        checks if there is enough on hand inventory to 
        provide the requested quantity
        """

        if quantity < 0:
            raise ValueError("Requested quantity cannot be negative")

        if self.on_hand >= quantity:
            return True

        return False

    def remove_inventory(self, quantity):
        """
        removes material from on-hand inventory.
        
        returns true if inventory was successfully removed,
        returns false if there wasn't enough inventory
        
        important in case a manufacturer consumes multiple inputs"""

        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        if self.can_fulfill(quantity):
            self.on_hand -= quantity
            return True

        return False

    def add_inventory(self, quantity):
        """
        adds material directly to on-hand inventory
        
        can be used later for when a manufacturer produces an output item
        """

        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        
        self.on_hand += quantity

    def record_replenishment_order(self,quantity):
        """
        records material that was ordered but has not arrived yet
        
        method doesn't create an order subject, just updates invetory state
        """

        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        
        self.on_order += quantity

    def receive_replenishment(self, quantity):
        """
        recieves material from an outstanding replenishment order.
        
        quantity moves from on_order to on_hand
        """

        if quantity < 0:
            raise ValueError("Recieved quantity cannot be negative.")

        if quantity > self.on_order:
            raise ValueError("Recieved quantity cannot be greater than quantity")

        self.on_order -= quantity
        self.on_hand += quantity

    def add_backorder(self, quantity):
        """adds unmet demand to a backorder quantity"""

        if quantity < 0:
            raise ValueError("Backorder quantity cannot be negative")

        self.backorders += quantity

    def reduce_backorder(self, quantity):
        """reduces the existing backorder quantity"""

        if quantity > self.backorders:
            raise ValueError("Cannot reduce backorders by more than the current backorder.")

        self.backorders -= quantity