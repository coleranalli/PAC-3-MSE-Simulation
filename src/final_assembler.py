from manufacturer import Manufacturer

class FinalAssembler(Manufacturer):
    """simulates the final assembly of the propulsion module.
    
    inherits production behavior from Manufacturer & adds customer demand.
    
    external demand that cannot be satisfied remains in backlog.
    """

    def __init__(self, node_id, name, location, capacity, lead_time,
        variability, disruption_probability, disruption_duration,
        shortage_idle_cost, recipe, input_inventories, output_inventory,
        external_demand=0):

        # initializing everything inherited from supplier
        super().__init__(node_id, name, location, capacity, lead_time,
            variability, disruption_probability, disruption_duration,
            shortage_idle_cost, recipe, input_inventories, output_inventory)

        if external_demand < 0:
            raise ValueError("External demand cannot be negative.")

        # total demand recieved
        self.external_demand = external_demand

        # total demand successfully satisfied
        self.fulfilled_demand = 0

        # starting demand begins as unfulfilled demand
        self.backlog = external_demand

    def add_external_demand(self, quantity):
        """
        adds new demand for final modeled unit.
        
        new demand increases backlog because it hasn't been fulfilled.
        """

        if quantity <= 0:
            raise ValueError("External demand cannot be below 0.")

        self.external_demand += quantity
        self.backlog += quantity

    def fulfill_demand(self):
        """
        uses final product inventory to fulfill backlog.
        
        method fulfills as much demand as possible.
        
        returns quantity of demand fulfilled.
        """

        if self.backlog == 0:
            return 0

        # determines how much demand can be satisfied
        if self.output_inventory.on_hand >= self.backlog:
            quantity_to_fulfill = self.backlog
        else:
            quantity_to_fulfill = self.output_inventory.on_hand

        # removes final units from inventory
        self.output_inventory.remove_inventory(quantity_to_fulfill)

        # update demand statistics
        self.fulfilled_demand += quantity_to_fulfill
        self.backlog -= quantity_to_fulfill

        return quantity_to_fulfill

    def get_info(self):
        return (
            f"{super().get_info()}\n"
            f"External Demand: {self.external_demand}"
            f"Fulfilled Demand: {self.fulfilled_demand}"
            f"Backlog: {self.backlog}"
        )