from order import Order
from shipment import Shipment
from supplier import Supplier
from manufacturer import Manufacturer

class SupplyChainModel:
    """
    coordinates objects in the supply chain.
    
    stores:
    - nodes
    - inventories
    - transport links
    - orders
    - shipments
    - basic stats about the model
    
    manual simulation rn
    """

    def __init__(self):

        # store nodes by node_id
        self.nodes = {}

        # store inventories by node_id, then item_name
        self.inventories = {}

        # transport links stored in a list
        self.transport_links = []

        # orders and shipments created during model operation
        self.orders = []
        self.shipments = []

        # automatically creating unique ids
        self.next_order_number = 1
        self.next_shipment_number = 1

        # simple stats dictionary
        self.statistics = {
            "orders_created": 0,
            "shipments_created": 0,
            "shipments_delivered": 0
        }

    def add_node(self,node):
        """adds node, supplier, manufacturer, or FinalAssembler to network"""

        if node.node_id in self.nodes:
            raise ValueError(f"Node {node.node_id} already exists.")

        self.nodes[node.node_id] = node

    def add_inventory(self, node_id, inventory):
        """associates inventory object with node"""

        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} doesn't exist.")

        # creates inventory dictionary if this is its first inventory
        if node_id not in self.inventories:
            self.inventories[node_id] = {}

        if inventory.item_name in self.inventories[node_id]:
            raise ValueError(
                f"{inventory.item_name} inventory already exists "
                f"at node {node_id}."
            )

        self.inventories[node_id][inventory.item_name] = inventory

    def get_inventory(self, node_id, item_name):
        """
        returns an inventory object for an item at a certain node
        
        returns none if that inventory doesn't exist
        """

        if node_id not in self.inventories:
            return None

        if item_name not in self.inventories[node_id]:
            return None

        return self.inventories[node_id][item_name]

    def add_transport_link(self, transport_link):
        """adds transport link to the network"""

        if transport_link.origin_id not in self.nodes:
            raise ValueError(
                f"Origin node {transport_link.origin_id}"
                f"does not exist"
                )

        if transport_link.destination_id not in self.nodes:
            raise ValueError(
                f"Destination node "
                f"{transport_link.destination_id} does not exist"
            )

        # prevent duplicate links for the same movement
        existing_link = self.find_transport_link(
            transport_link.origin_id,
            transport_link.destination_id,
            transport_link.item_name
        )

        if existing_link is not None:
            raise ValueError("Transport link already exists")

        self.transport_links.append(transport_link)

    def find_transport_link(self, origin_id, 
        destination_id, item_name):
        """
        finds the transportlink matching a requested node.
        
        returns none ifn no matching link exists.
        """

        for transport_link in self.transport_links:

            if transport_link.matches_route(
                origin_id, destination_id, item_name
            ):
                return transport_link

        return None

    def get_order_by_id(self, order_id):
        """finds an order using its id."""

        for order in self.orders:
            if order.order_id == order_id:
                return order

        return None

    def create_order(self, origin_id, destination_id,
        item_name, quantity):
        """creates a replenishment order.
        
        this method:
        - records quanttity as on_order at the destination
        - adds order to a supplier queue if origin is a supplier
        """

        if origin_id not in self.nodes:
            raise ValueError(
                f"Origin node {origin_id} does not exist"
            )

        if destination_id not in self.nodes:
            raise ValueError(
                f"Destination node {destination_id} does not exist."
            )

        # valid trasnport link must exist

        transport_link = self.find_transport_link(
            origin_id, destination_id, item_name
        )

        if transport_link is None:
            raise ValueError("No matching transport link exists.")

        # destination must have inventory for the item
        inventory = self.get_inventory(
            destination_id, item_name)

        if inventory is None:
            raise ValueError(
                f"{item_name} does not exist "
                f"at node {destination_id}."
            )

        # generate next order id
        order_id = "O" + str(self.next_order_number)

        self.next_order_number += 1

        order = Order(order_id=order_id, origin_id=origin_id,
            destination_id=destination_id, item_name=item_name,
            quantity=quantity)

        self.orders.append(order)

        # record expected replenishment
        inventory.record_replenishment_order(quantity)

        # suppliers maintain their own queues
        origin_node = self.nodes[origin_id]

        if isinstance(origin_node, Supplier):
            origin_node.add_order(order)

        self.statistics["orders_created"] += 1

        return order

    def create_reorder_if_needed(self, origin_id, destination_id, item_name):
        """
        checks the destination inventory's reorder policy.
        
        if reorder is needed, an Order is creared using that
        inventory's reorder quantity.
        
        returns the new Order if one is created; none if none is needed.
        """

        inventory = self.get_inventory(destination_id, item_name)

        if inventory is None:
            raise ValueError(
                f"{item_name} inventory does not exist "
                f"at node {destination_id}."
            )

        if inventory.should_reorder():

            order = self.create_order(origin_id=origin_id, destination_id=destination_id,
                item_name=item_name, quantity=inventory.reorder_quantity)

            return order

        return None

    def create_shipment(self, order):
        """
        creates shipment from an existing pending order.
        
        order is marked as shipped, & if origin is a supplier, the
        next order is in its queue
        """

        if order.status != "pending":
            raise ValueError("Only pending orders can be shipped.")

        transport_link = self.find_transport_link(
            order.origin_id, order.destination_id, order.item_name
        )

        if transport_link is None:
            raise ValueError("No matching transport link exists.")

        origin_node = self.nodes[order.origin_id]

        # processing of orders by suppliers (FIFO)
        if isinstance(origin_node, Supplier):

            next_order = origin_node.get_next_order()

            if next_order is None:
                raise ValueError("Supplier has no order waiting.")

            if next_order.order_id != order.order_id:
                raise ValueError("Supplier orders must be shipped "
                    "in FIFO order.")

            origin_node.remove_next_order()

        # manufactured products must exist at manufacturing node
        # before they can be shipped
        if isinstance(origin_node, Manufacturer):

            if not origin_node.output_inventory.can_fulfill(
            order.quantity):
                raise ValueError("Manufacturer does not have enough output "
                "inventory to fill this order.")

        origin_node.output_inventory.remove_inventory(order.quantity)

        # Generate the next shipment ID.
        shipment_id = ("SH" + str(self.next_shipment_number))

        self.next_shipment_number += 1

        shipment = Shipment(shipment_id=shipment_id,order_id=order.order_id,
            origin_id=order.origin_id,destination_id=order.destination_id,
            item_name=order.item_name,quantity=order.quantity)

        self.shipments.append(shipment)

        order.mark_shipped()

        self.statistics["shipments_created"] += 1

        return shipment

    def deliver_shipment(self, shipment):
        """
        delivers an in-transit shipment.
        
        this method:
        - moves qiantity from on-order to on-hand
        - marks shipment as delivered
        - marks related order complete
        """

        if shipment.status != "in_transit":
            raise ValueError("Only in-transit shipments can be delivered.")

        inventory = self.get_inventory(shipment.destination_id,
            shipment.item_name)

        if inventory is None:
            raise ValueError(
                f"{shipment.item_name} inventory does not exist "
                f"at node {shipment.destination_id}."
            )

        # move from on-order to available
        inventory.receive_replenishment(shipment.quantity)

        shipment.mark_delivered()

        # find and complete order connected to shipment
        order = self.get_order_by_id(shipment.order_id)

        if order is not None:
            order.mark_complete()

        # add to statistics
        self.statistics["shipments_delivered"] += 1