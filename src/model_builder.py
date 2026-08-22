from config_loader import load_recipes, load_configuration
from final_assembler import FinalAssembler
from inventory import Inventory
from manufacturer import Manufacturer
from supplier import Supplier
from supply_chain_model import SupplyChainModel
from transport_link import TransportLink

def create_receiving_inventory(origin_row, item_name): # i.e. ["S1"],"AP"
    """
    creates inventory for an item at reveiving facility.
    
    inventory assumptions come from the node that supplies item.
    """

    inventory = Inventory(
        item_name=item_name,
        on_hand=origin_row["opening_inventory"],
        reorder_point=origin_row["reorder_point"],
        reorder_quantity=origin_row["reorder_quantity"],
        holding_cost=origin_row["holding_cost"],
        shortage_cost=origin_row["shortage_idle_cost"]
    )

    return inventory

def create_unmanaged_output_inventory(item_name): # for S6 and M1
    """
    creates an internal inventory for finished product.
    
    filled through actual manufacturing versus automatic reorder.
    """

    inventory = Inventory(
        item_name=item_name,
        on_hand=0,
        reorder_point=None,
        reorder_quantity=None,
        holding_cost=None,
        shortage_cost=None
    )

    return inventory

def build_model_from_configuration(nodes_path, links_path, recipes_path):
    """builds supply chain from csv files"""

    node_rows, link_rows = load_configuration(nodes_path, links_path)
    recipes = load_recipes(recipes_path)

    model = SupplyChainModel()
    receiving_inventories = {}

    for link_row in link_rows:
        origin_id = link_row["origin_id"]
        destination_id = link_row["destination_id"]
        item_name = link_row["item_name"]

        origin_row = node_rows[origin_id]

        inventory = create_receiving_inventory(origin_row, item_name)

        receiving_inventories[(destination_id, item_name)] = inventory

        # creating 5 supplier nodes
        supplier_ids = ["S1","S2","S3","S4","S5"]

    for node_id in supplier_ids:
        row = node_rows[node_id]

        supplier = Supplier(
            node_id=node_id,
            name=row["name"],
            location=row["location"],
            capacity=row["capacity"],
            output_item=row["output_item"],
            disruption_probability=row["disruption_probability"],
            disruption_duration=row["disruption_duration"]            
        )

        model.add_node(supplier)

    # s6 consuming carbon fiber to make motor case
    s6_row = node_rows["S6"]

    s6_output = create_unmanaged_output_inventory(
        s6_row["output_item"]
        )

    s6_inputs = {}

    for item_name in recipes["S6"]:
        inventory = receiving_inventories[
            ("S6", item_name)
        ]

    s6_inputs[item_name] = inventory

    s6 = Manufacturer(
        node_id="S6",
        name=s6_row["name"],
        location=s6_row["location"],
        capacity=s6_row["capacity"],
        lead_time=s6_row["lead_time"],
        variability=s6_row["variability"],
        disruption_probability=s6_row["disruption_probability"],
        disruption_duration=s6_row["disruption_duration"],
        shortage_idle_cost=s6_row["shortage_idle_cost"],
        recipe=recipes["S6"],
        input_inventories=s6_inputs,
        output_inventory=s6_output
    )

    model.add_node(s6)

    m1_row = node_rows["M1"]

    m1_output = create_unmanaged_output_inventory(
            m1_row["output_item"]
        )

    m1_inputs = {}

    for item_name in recipes["M1"]:
        inventory = receiving_inventories[("M1", item_name)]

        m1_inputs[item_name] = inventory

    m1 = Manufacturer(
        node_id="M1",
        name=m1_row["name"],
        location=m1_row["location"],
        capacity=m1_row["capacity"],
        lead_time=m1_row["lead_time"],
        variability=m1_row["variability"],
        disruption_probability=m1_row["disruption_probability"],
        disruption_duration=m1_row["disruption_duration"],
        shortage_idle_cost=m1_row["shortage_idle_cost"],
        recipe=recipes["M1"],
        input_inventories=m1_inputs,
        output_inventory=m1_output
    )

    model.add_node(m1)

    # a1 consumes propulsion modules to produce interceptors

    a1_row = node_rows["A1"]

    a1_output = Inventory(
        item_name=a1_row["output_item"],
        on_hand=a1_row["opening_inventory"],
        reorder_point=a1_row["reorder_point"],
        reorder_quantity=a1_row["reorder_quantity"],
        holding_cost=a1_row["holding_cost"],
        shortage_cost=a1_row["shortage_idle_cost"]
    )

    a1_inputs = {}

    for item_name in recipes["A1"]:
        inventory = receiving_inventories[
            ("A1", item_name)
        ]

        a1_inputs[item_name] = inventory

    a1 = FinalAssembler(
        node_id="A1",
        name=a1_row["name"],
        location=a1_row["location"],
        capacity=a1_row["capacity"],
        lead_time=a1_row["lead_time"],
        variability=a1_row["variability"],
        disruption_probability=a1_row["disruption_probability"],
        disruption_duration=a1_row["disruption_duration"],
        shortage_idle_cost=a1_row["shortage_idle_cost"],
        recipe=recipes["A1"],
        input_inventories=a1_inputs,
        output_inventory=a1_output
    )

    model.add_node(a1)

    # register all receiving inventories with the model
    for inventory_key in receiving_inventories:
        destination_id = inventory_key[0]
        item_name = inventory_key[1]

        inventory = receiving_inventories[inventory_key]

        model.add_inventory(destination_id, inventory)

    model.add_inventory("S6", s6_output)
    model.add_inventory("M1", m1_output)
    model.add_inventory("A1", a1_output)

    for link_row in link_rows:

        origin_id = link_row["origin_id"]
        destination_id = link_row["destination_id"]
        item_name = link_row["item_name"]

        origin_row = node_rows[origin_id]

        transport_link = TransportLink(
            origin_id=origin_id,
            destination_id=destination_id,
            item_name=item_name,
            lead_time=origin_row["lead_time"],
            variability=origin_row["variability"],
            transportation_delay_probability=(
            origin_row["transportation_delay_probability"]  
            )
        )

        model.add_transport_link(transport_link)

    return model
