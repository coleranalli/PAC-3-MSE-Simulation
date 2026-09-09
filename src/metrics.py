class SimulationMetrics:
    """stores all measurements collected during a sim"""

    def __init__(self, manufacturer_ids=None):

        if manufacturer_ids is None:
            manufacturer_ids = ["S6", "M1", "A1"]

        self.production_starts = {}
        self.production_completions = {}

        self.daily_history = []

        # start at 0
        for manufacturer_id in manufacturer_ids:
            self.production_starts[manufacturer_id] = 0
            self.production_completions[manufacturer_id] = 0

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