class SimulationMetrics:
    """stores all measurements collected during a sim"""

    def __init__(self, manufacturer_ids=None):

        if manufacturer_ids is None:
            manufacturer_ids = ["S6", "M1", "A1"]

        self.production_starts = {}
        self.production_completions = {}

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
