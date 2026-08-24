from node import Node

class Manufacturer(Node):
    """
    represents a manufacturing facility in the supply chain

    manufacturers:
    - consume one or more input materials
    - follows a production recipe
    - produces material to an output inventory

    inherits basic facility info from node
    """

    def __init__(self, node_id, name, location, capacity, lead_time,
        variability, disruption_probability, disruption_duration,
        shortage_idle_cost, recipe, input_inventories, output_inventory):

        # initializing inherited attributes
        super().__init__(node_id, name, location)

        # prevents negatives
        if capacity < 0:
            raise ValueError("Capacity cannot be negative.")

        if lead_time < 0:
            raise ValueError("Lead time cannot be negative.")

        if variability < 0:
            raise ValueError("Variability cannot be negative.")

        if (disruption_probability < 0
            or disruption_probability > 1):
            raise ValueError("Disruption probability must be between 0 and 1.")

        if disruption_duration == "":
            raise ValueError("Disruption duration cannot be empty.")

        if shortage_idle_cost < 0:
            raise ValueError("Shortage/idle cost cannot be negative.")

        if len(recipe) == 0:
            raise ValueError("Manufacturer recipe cannot be empty.")

        # preventing negative recipe quantities
        for item_name in recipe:

            required_quantity = recipe[item_name]

            if required_quantity <= 0:
                raise ValueError("Recipe quantities must be greater than zero.")

        # amount that can be produced per day
        self.capacity = capacity

        # production/processing duration
        self.lead_time = lead_time
        self.variability = variability

        # chances of these times being disrupted/extended
        self.disruption_probability = disruption_probability
        self.disruption_duration = disruption_duration

        # cost of not producing anything
        self.shortage_idle_cost = shortage_idle_cost

        # recipe input where key -> input item name,
        # value -> amount needed for one unit of output
        self.recipe = recipe

        # inventory input where key -> input item name,
        # value -> amount needed for one unit of output
        self.input_inventories = input_inventories

        # finished material storage
        self.output_inventory = output_inventory

    def can_produce(self, quantity=1):
        """
        checks if enough inputs exist to produce the quantity
        
        no inventory is consumed when method runs
        """

        if quantity <= 0:
            raise ValueError("Production quantity must be greater than zero.")

        # check every recipe input before consuming
        for item_name in self.recipe:

            required_per_unit = self.recipe[item_name]
            required_quantity = required_per_unit * quantity

            # if manufacturer doesn't have object in inventory,
            # production cannot occur
            if item_name not in self.input_inventories:
                return False

            inventory = self.input_inventories[item_name]

            if not inventory.can_fulfill(required_quantity):
                return False

        return True

    def consume_inputs(self, quantity=1):
        """
        removes required input materials when production begins.

        returns True when the inputs were successfully consumed.
        returns False when there are not enough inputs.
        """

        if quantity <= 0:
            raise ValueError(
                "Production quantity must be greater than zero."
            )

        if not self.can_produce(quantity):
            return False

        # all required inputs are available
        for item_name in self.recipe:

            required_per_unit = self.recipe[item_name]
            required_quantity = quantity * required_per_unit

            inventory = self.input_inventories[item_name]

            inventory.remove_inventory(required_quantity)

        return True

    def complete_production(self, quantity=1):
        """adds finished material to output inv when production completes"""

        if quantity <= 0:
            raise ValueError(
                "Production quantity must be greater than zero."
            )

        self.output_inventory.add_inventory(
            quantity
        )

        return True

    def produce(self, quantity=1):
        """immediately produces requested quantity"""

        if not self.consume_inputs(quantity):
            return False

        self.complete_production(quantity)

        return True

    def get_info(self):
        """returns important info about manufacturer."""
        return (
            f"{super().get_info()}\n"
            f"Capacity: {self.capacity}\n"
            f"Lead Time: {self.lead_time}\n"
            f"Variability: {self.variability}\n"
            f"Disruption Probability: "
            f"{self.disruption_probability}\n"
            f"Disruption Duration: "
            f"{self.disruption_duration}\n"
            f"Shortage/Idle Cost: "
            f"{self.shortage_idle_cost}\n"
            f"Output Item: "
            f"{self.output_inventory.item_name}"
        )