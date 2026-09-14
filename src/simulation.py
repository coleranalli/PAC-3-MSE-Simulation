from manufacturer import Manufacturer
from supplier import Supplier
import random
from metrics import SimulationMetrics
from final_assembler import FinalAssembler

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

def sample_variable_lead_time(
    random_generator, 
    lead_time, 
    variability
    ):
    """
    samples lead time using baseline lead time & variability
    
    uniform distribution between lead_time +/- variability
    """

    if lead_time < 0:
        return ValueError("Lead time cannot be negative.")

    if variability is None or variability == 0:
        return lead_time

    if variability < 0:
        raise ValueError("Variability cannot be negative.")

    minimum_time = max(0, lead_time-variability)

    maximum_time = (lead_time + variability)

    sampled_time = random_generator.uniform(
        minimum_time, maximum_time
    )

    return sampled_time

def sample_disruption_duration(random_generator, disruption_duration):
    """samples a disruption duration from range.
    
    makes "3-7" -> random(3,7)"""

    if disruption_duration is None:
        raise ValueError("Disruption duration must be created.")

    duration_text = str(disruption_duration).strip()

    if "-" in duration_text:
        parts = duration_text.split("-")
        minimum_duration = int(parts[0])
        maximum_duration = int(parts[1])

        if minimum_duration < 0:
            raise ValueError("Disruption duration must be greater than zero.")

        if maximum_duration < minimum_duration:
            raise ValueError("Invalid disruption duration range.")

        return random_generator.randint(minimum_duration, maximum_duration)

    duration = int (duration_text)

    if duration <= 0:
        raise ValueError("Disruption duration must e greater than 0.")

    return duration
    
class SimulationRunner:
    """controls timed simulation process"""

    def __init__(self, model, environment=None,
        stochastic=False, random_seed=None, daily_demand=1):

        self.model=model
        self.stochastic = stochastic

        if daily_demand < 0:
            raise ValueError("Demand must be positive.")
        self.daily_demand = daily_demand

        if environment is None:
            import simpy
            environment = simpy.Environment()
        
        self.env = environment

        # seperate rng for this sim
        self.random_generator = random.Random(
            random_seed
        )

        # time until node is avaialable again
        self.disrupted_until = {}

        # disruption events for later reporting
        self.disruption_log = []

        self.controllers_started = False

        self.metrics = SimulationMetrics()


    def shipment_process(self, order):
        """creates a shipment, waits for lead time, then delivers."""

        # creating shipment
        shipment = self.model.create_shipment(order)

        delay = self.get_shipment_delay(order)

        origin_node = self.model.nodes[order.origin_id]

        # if node is a supplier, enact supplier delay process
        if isinstance(origin_node, Supplier):

            yield self.env.process(self.supplier_delay_process(
                origin_node, delay
            ))

        else:
            yield self.env.timeout(delay)

        # delivery occurs
        self.model.deliver_shipment(shipment)

        return shipment

    def get_production_delay(self, manufacturer):
        """returns processing time for one production lot"""

        if not self.stochastic:
            return manufacturer.lead_time

        return sample_variable_lead_time(
            self.random_generator,
            manufacturer.lead_time,
            manufacturer.variability
        )

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

        # inputs reserved, prod start
        self.metrics.record_production_start(manufacturer_id, quantity)

        # wait for processing lead time
        production_delay = self.get_production_delay(manufacturer)

        yield self.env.timeout(production_delay)

        manufacturer.complete_production(quantity)

        self.metrics.record_production_completion(
            manufacturer_id, quantity)

        return True

    def production_completion_process(self,manufacturer,quantity):
        """complete production lot after processing time is up"""

        production_delay = self.get_production_delay(manufacturer)

        yield self.env.timeout(production_delay)

        manufacturer.complete_production(quantity)

        self.metrics.record_production_completion(
            manufacturer.node_id, quantity)

    def daily_demand_controller(self):
        """
        Adds external demand to A1 once per day to stimulate model.
        
        Order:
        1. Add today's demand
        2. Attempt to fulfill all backlog from FMU inventory
        3. advance one day
        """

        if "A1" not in self.model.nodes:
            raise ValueError("Final assembler does not exist.")

        final_assembler = self.model.nodes["A1"]

        if not isinstance(final_assembler, FinalAssembler):
            raise ValueError("A1 is not the Final Assembler.")

        while True:
            if self.daily_demand > 0:
                final_assembler.add_external_demand(self.daily_demand)

            final_assembler.fulfill_demand()

            yield self.env.timeout(1)

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
            if self.is_node_disrupted(manufacturer_id):
                yield self.env.timeout(1)
                continue

            disruption_started = (self.check_for_disruption(manufacturer_id))

            if disruption_started:
                yield self.env.timeout(1)
                continue

            # facility operating normally today
            capacity_balance += manufacturer.capacity

            units_allowed = int(capacity_balance)

            capacity_balance -= units_allowed

            for unit_number in range(units_allowed):

                if not manufacturer.can_produce(1):
                    unstarted_units = (units_allowed - unit_number)

                    self.metrics.record_starvation(manufacturer_id, unstarted_units)

                    break

                manufacturer.consume_inputs(1)

                self.metrics.record_production_start(manufacturer_id,1)

                self.env.process(
                    self.production_completion_process(manufacturer,1)
                )

            yield self.env.timeout(1)

    def get_shipment_delay(self, order):
        """
        returns the shipment delay for an order.
        
        deterministic just uses base lead_time, stochastic adds
        configured variability.
        """

        deterministic_delay = (get_deterministic_shipment_delay(
            self.model, order)
            )

        # manufacturer shipments have no additional modeled transport time
        if deterministic_delay == 0:
            return 0

        if not self.stochastic:
            return deterministic_delay

        transport_link = self.model.find_transport_link(
            order.origin_id,
            order.destination_id,
            order.item_name
        )

        if transport_link is None:
            raise ValueError(
                "No matching transport link exists."
            )
        
        return sample_variable_lead_time(
            self.random_generator,
            deterministic_delay,
            transport_link.variability
        )

    def is_node_disrupted(self, node_id):
        """returns true if node is disrupted"""

        disrupted_until = self.disrupted_until.get(node_id,0)

        if self.env.now < disrupted_until:
            return True

        return False

    def check_for_disruption(self, node_id):
        """checks if node disruption occurs during the current day"""

        node = self.model.nodes[node_id]

        # no randomness in deterministic models
        if not self.stochastic:
            return False

        # if already disrupted, no more rng
        if self.is_node_disrupted(node_id):
            return True

        random_value = self.random_generator.random()

        if random_value >= node.disruption_probability:
            return False

        duration = sample_disruption_duration(
            self.random_generator,
            node.disruption_duration
        )
    
        disruption_start = self.env.now
        disruption_end = disruption_start + duration
        self.disrupted_until[node_id] = disruption_end

        self.disruption_log.append(
            {
                "node_id": node_id,
                "start_time": disruption_start,
                "duration": duration,
                "end_time": disruption_end
            }
        )

        return True

    def supplier_delay_process(self, supplier, delay):
        """
        waits for a supplier order to complete.

        remaining suppluier lead time decreases unless disrupted.
        """

        # deterministic keeps same behavior
        if not self.stochastic:
            yield self.env.timeout(delay)
            return

        remaining_delay = delay

        while remaining_delay > 0:

            # supplier already sirupted
            if self.is_node_disrupted(supplier.node_id):
                yield self.env.timeout(1)
                continue

            disruption_started = (self.check_for_disruption(
                supplier.node_id
            ))

            if disruption_started:
                yield self.env.timeout(1)
                continue

            time_step = min(1, remaining_delay)

            yield self.env.timeout(time_step)

            remaining_delay -= time_step

    def supplier_replenishment_controller(self):
        """
        checks supplier-supplied inventories supplied once per day.
        
        when inventory needs supplying, and reaches reorder point,
        replinishing supply order and supply shipment process begin.
        
        supply.
        """

        while True:

            for transport_link in self.model.transport_links:

                origin_node = self.model.nodes[
                    transport_link.origin_id
                ]

            # suppliers only
                if not isinstance(origin_node, Supplier):
                    continue

                destination_id = transport_link.destination_id

                item_name = transport_link.item_name

                inventory = self.model.get_inventory(
                    destination_id, item_name
                )

                if inventory is None:
                    continue

                if inventory.should_reorder():

                    order = self.model.create_order(
                        origin_id = transport_link.origin_id,
                        destination_id = destination_id,
                        item_name = item_name,
                        quantity = inventory.reorder_quantity
                    )

                    self.env.process(self.shipment_process(order))

            yield self.env.timeout(1)

    def intermediate_replenishment_controller(self):
        """
        moves manufacturer output to downstream manufacturers when
        downstream node requires that item for production.

        any currently avaialble upstream inventory becomes shipment.
        """

        while True:

            for transport_link in self.model.transport_links:

                origin_node = self.model.nodes[
                    transport_link.origin_id
                ]

                destination_node = self.model.nodes[
                    transport_link.destination_id
                ]

                # only manufacturer origin links
                if not isinstance(origin_node, Manufacturer):
                    continue

                # destination has to consume material through recipe
                if not isinstance(destination_node, Manufacturer):
                    continue

                item_name = transport_link.item_name

                # actually verify downstream node needs item
                if item_name not in destination_node.recipe:
                    continue

                downstream_inventory = (
                    self.model.get_inventory(
                        transport_link.destination_id, item_name)
                )

                upstream_inventory = (
                    self.model.get_inventory(
                        transport_link.origin_id, item_name)
                )

                if downstream_inventory is None:
                    continue

                if upstream_inventory is None:
                    continue

                required_per_unit = (
                    destination_node.recipe[
                        item_name
                    ]
                )

                # if downstream node already has enough material to
                # start a unit, no transfer is needed yet
                if downstream_inventory.can_fulfill(
                    required_per_unit
                ):
                    continue

                # no duplicates DH
                if downstream_inventory.on_order > 0:
                    continue

                available_quantity = (upstream_inventory.on_hand)

                if available_quantity <= 0:
                    continue

                order = self.model.create_order(
                    origin_id=transport_link.origin_id,
                    destination_id=transport_link.destination_id,
                    item_name=item_name,
                    quantity=available_quantity
                )

                self.env.process(self.shipment_process(order))

            yield self.env.timeout(1)

    def start_controllers(self):
        """auto starts continuous sim controllers"""

        if self.controllers_started:
            return

        self.controllers_started = True

        # supplier reorder monitor
        self.env.process(
            self.supplier_replenishment_controller()
        )

        # intermediate manufacturer transfers
        self.env.process(self.intermediate_replenishment_controller())

        # production processes
        manufacturer_ids = ["S6","M1","A1"]

        for manufacturer_id in manufacturer_ids:
            self.env.process(
                self.daily_production_controller(manufacturer_id)
            )

        # customer demand for FMU
        self.env.process(self.daily_demand_controller())

    def record_daily_metrics(self):
        """records current end of day sim state"""

        if "A1" not in self.model.nodes:
            raise ValueError("Final assembler A1 does not exist")

        final_assembler = self.model.nodes["A1"]

        self.metrics.record_daily_snapshot(
            self.env.now,self.model, final_assembler
        )

    def run(self, until):
        """
        starts sim controllers and runs supply chain
        until requested sim end time. one observation is recorded after
        one simulated day.
        """

        if until <= self.env.now:
            raise ValueError(
                "Sim end time must be greater than current sim time."
            )

        self.start_controllers()

        while self.env.now + 1 <= until:

            next_day = self.env.now + 1
            self.env.run(until=next_day)
            self.record_daily_metrics()

        if self.env.now < until:
            self.env.run(until=until)

    def get_summary(self):
        """returns basic info about sim"""

        s6_output = self.model.get_inventory("S6","Motor Case")

        m1_output = self.model.get_inventory("M1","Propulsion Module")

        a1_output = self.model.get_inventory("A1","Final Modeled Unit")

        a1 = self.model.nodes["A1"]

        if a1.external_demand == 0:
            service_level = None
        else:
            service_level = (a1.fulfilled_demand / a1.external_demand)

        manufactuer_ids = ["S6", "M1", "A1"]

        if self.env.now == 0:
            simulation_days = None
        else:
            simulation_days = self.env.now

        summary = {

            "simulation_time": self.env.now,

            "daily_demand": self.daily_demand,

            "final_units_produced":
                self.metrics.production_completions["A1"],

            "external_demand":
                a1.external_demand,

            "fulfilled_demand":
                a1.fulfilled_demand,

            "ending_backlog":
                a1.backlog,

            "service_level":
                service_level,

            "orders_created":
                self.model.statistics["orders_created"],

            "shipments_created":
                self.model.statistics["shipments_created"],

            "shipments_delivered":
                self.model.statistics["shipments_delivered"],

            "disruptions":
                len(self.disruption_log)
            }
        
        manufacturer_ids = ["S6", "M1", "A1"]

        for manufacturer_id in manufacturer_ids:

            key_name = manufacturer_id.lower()

            starts = (
                self.metrics.production_starts[manufacturer_id]
            )

            completions = (
                self.metrics.production_completions[manufacturer_id]
            )

            summary[f"{key_name}_production_starts"] = starts
            summary[f"{key_name}_production_completions"] = completions

            if simulation_days is None:
                throughput = None
            else:
                throughput = (completions / simulation_days)

            summary[f"{key_name}_throughput_per_day"] = throughput
            summary[f"{key_name}_starved_days"] = self.metrics.starved_days[
                manufacturer_id
            ]
            summary[f"{key_name}_unstarted_units_due_to_storage"] = (
                self.metrics.unstarted_units_due_to_storage[manufacturer_id]
            )

        for node_id in self.model.nodes:
            key_name = node_id.lower()

            summary[f"{key_name}_disruption_count"
                ] = self.metrics.get_disruption_count(
                    self.disruption_log, node_id
                )

            summary[f"{key_name}_disrupted_days"
                ] = self.metrics.get_disrupted_days(
                    self.disruption_log, node_id, self.env.now
                )

        for node_id in self.model.inventories:

            for item_name in self.model.inventories[node_id]:
                item_key = (item_name.lower().replace(" ", "_"))
                inventory_key = (
                    f"inventory_"
                    f"{node_id.lower()}_"
                    f"{item_key}"
                )

            inventory = (
                self.model.inventories[node_id][item_name]
            )

            summary[f"{inventory_key}_ending_on_hand"
                ] = inventory.on_hand

            summary[f"{inventory_key}_average_on_hand"
                ] = self.metrics.get_average_on_hand(node_id,item_name
            )

            summary[f"{inventory_key}_maximum_on_hand"
                ] = self.metrics.get_max_on_hand(node_id,item_name
            )

            summary[f"{inventory_key}_stockout_days"
                ] = self.metrics.get_stockout_days(node_id,item_name
            )

        s6_output = self.model.get_inventory(
            "S6","Motor Case"
        )

        m1_output = self.model.get_inventory(
            "M1","Propulsion Module"
        )

        a1_output = self.model.get_inventory(
            "A1","Final Modeled Unit"
        )

        summary["motor_cases_on_hand"] = (
            s6_output.on_hand
        )

        summary["propulsion_modules_on_hand"] = (
            m1_output.on_hand
        )

        summary["final_units_on_hand"] = (
            a1_output.on_hand
        )

        return summary
        