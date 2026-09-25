class SimulationMetrics:
    """stores all measurements collected during a sim"""

    def __init__(self, manufacturer_ids=None):

        if manufacturer_ids is None:
            manufacturer_ids = ["S6", "M1", "A1"]

        self.production_starts = {}
        self.production_completions = {}
        self.daily_history = []
        self.starved_days = {}
        self.unstarted_units_due_to_storage = {}

        # start at 0
        for manufacturer_id in manufacturer_ids:
            self.production_starts[manufacturer_id] = 0
            self.production_completions[manufacturer_id] = 0

            self.starved_days[manufacturer_id] = 0
            self.unstarted_units_due_to_storage[manufacturer_id] = 0

    def record_production_start(self, manufacturer_id, quantity=1):
        """adds successfully started production units to counter"""

        if quantity <= 0:
            raise ValueError("Production quantity must be greater than zero.")

        if manufacturer_id not in self.production_starts:
            self.production_starts[manufacturer_id] = 0

        self.production_starts[manufacturer_id] += quantity

    def record_production_completion(self, manufacturer_id, quantity=1):
        """adds successfully finished production units to counter"""

        if quantity <= 0:
            raise ValueError("Production quantity must be greater than zero.")

        if manufacturer_id not in self.production_completions:
            self.production_completions[manufacturer_id] = 0

        self.production_completions[manufacturer_id] += quantity

    def record_daily_snapshot(self, simulation_time, model, final_assembler):
        """records one daily observation of sim state"""

        inventories_snapshot = {}

        for node_id in model.inventories:
            inventories_snapshot[node_id] = {}

            for item_name in model.inventories[node_id]:
                inventory = model.inventories[node_id][item_name]

                inventories_snapshot[node_id][item_name] = {
                    "on_hand" : inventory.on_hand,
                    "on_order" : inventory.on_order,
                    "backorders" : inventory.backorders
                }

        snapshot = {
            "simulation_time" : simulation_time,
            "inventories" : inventories_snapshot,
            "external_demand" : final_assembler.external_demand,
            "fulfilled_demand" : final_assembler.fulfilled_demand,
            "backlog" : final_assembler.backlog,
            "production_starts" : self.production_starts.copy(),  # ensures frozen dict for this day
            "production_completions" : self.production_completions.copy()  # samesies
        }

        self.daily_history.append(snapshot)

    def get_on_hand_history(self, node_id, item_name):
        """returns daily on-hand values for an inventory"""

        values = []

        for snapshot in self.daily_history:

            inventories = snapshot["inventories"]

            if node_id not in inventories:
                raise ValueError(
                    f"No inventory history exists for node {node_id}."
                )

            if item_name not in inventories[node_id]:
                raise ValueError(
                    f"No inventory history exists for {item_name} at node {node_id}"
                )

            value = inventories[node_id][item_name]["on_hand"]

            values.append(value)

        return values

    def get_average_on_hand(self, node_id, item_name):
        """calculates average daily on_hand inventory"""

        values = self.get_on_hand_history(node_id, item_name)

        if len(values) == 0:
            return None

        average = sum(values) / len(values)

        return average

    def get_max_on_hand(self, node_id, item_name):
        """returns highest observed on-hand inventory"""
        values = self.get_on_hand_history(node_id, item_name)

        if len(values) == 0:
            return None

        return max(values)

    def get_stockout_days(self, node_id, item_name):
        """counts days where on-hand inventory is zero"""

        values = self.get_on_hand_history(node_id, item_name)

        stockout_days = 0  # initalize dat!

        for value in values:

            if value == 0:
                stockout_days += 1

        return stockout_days

    def record_starvation(self, manufacturer_id, unstarted_units):
        """records a day where production was limited by missing inputs"""

        if unstarted_units <= 0:
            raise ValueError("Unstarted units must be greater than zero")

        if manufacturer_id not in self.starved_days:
            self.starved_days[manufacturer_id] = 0
            self.unstarted_units_due_to_storage[manufacturer_id] = 0

        self.starved_days[manufacturer_id] += 1

        self.unstarted_units_due_to_storage[
            manufacturer_id
        ] += unstarted_units

    def get_disruption_count(self, disruption_log, node_id):
        """counts diruption events for one node"""

        disruption_count = 0  # initializzzeeee

        for disruption in disruption_log:

            if disruption["node_id"] == node_id:
                disruption_count += 1

        return disruption_count

    def get_disrupted_days(self, disruption_log, node_id, simulation_horizon):
        """calculates disruption time inside sim horizon"""

        disrupted_days = 0  # mhm

        for disruption in disruption_log:

            if disruption["node_id"] != node_id:
                continue

            start_time = disruption["start_time"]
            end_time = disruption["end_time"]

            bounded_start = max(0,start_time)

            bounded_end = min(simulation_horizon, end_time)  # >365

            if bounded_end > bounded_start:
                disrupted_days += (bounded_end - bounded_start)

        return disrupted_days
