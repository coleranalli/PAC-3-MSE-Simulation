import csv

numeric_node_fields = [
    "opening_inventory",
    "capacity",
    "lead_time",
    "variability",
    "disruption_probability",
    "transportation_delay_probability",
    "holding_cost",
    "shortage_idle_cost",
    "reorder_point",
    "reorder_quantity"
]

def convert_csv_number(value, field_name):
    """converts a CSV number to flaot, preserves N/A as None."""

    cleaned_value = value.strip()

    if cleaned_value.upper() == "N/A":
        return None

    try:
        return float(cleaned_value)
    except ValueError as error:
        raise ValueError(
            f"{field_name} must be numeric or N/A. Received: {value}"
        ) from error

def load_nodes(nodes_path):
    """reads nodes.csv and return rows stored by node id"""

    nodes = {}

    with open(nodes_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
    
        if reader.fieldnames is None:
            raise ValueError("nodes.csv must contain a header row.")
    
        required_fields = [
            "node_id",
            "name",
            "location",
            "output_item",
            "opening_inventory",
            "capacity",
            "lead_time",
            "variability",
            "disruption_probability",
            "disruption_duration",
            "transportation_delay_probability",
            "holding_cost",
            "shortage_idle_cost",
            "reorder_point",                
            "reorder_quantity"
        ]

        for field_name in required_fields:
            if field_name not in reader.fieldnames:
                raise ValueError(
                    f"nodes.csv is missing required column: {field_name}"
                )

        for row in reader:
            node_id = row["node_id"].strip()

            if node_id == "":
                raise ValueError("Node ID cannot be empty in nodes.csv.")

            if node_id in nodes:
                raise ValueError(f"Duplicate node ID in nodes.csv: {node_id}")

            cleaned_row = dict(row)

            for field_name in numeric_node_fields:
                cleaned_row[field_name] = convert_csv_number(
                    row[field_name], field_name
                )

            nodes[node_id] = cleaned_row

    return nodes

def load_links(links_path):
    """Read the structural route definitions from links.csv."""

    links = []

    with open(links_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("links.csv must contain a header row.")

        required_fields = ["origin_id", "destination_id", "item_name"]

        for field_name in required_fields:
            if field_name not in reader.fieldnames:
                raise ValueError(
                    f"links.csv is missing required column: {field_name}"
                )

        for row in reader:
            cleaned_row = {
                "origin_id": row["origin_id"].strip(),
                "destination_id": row["destination_id"].strip(),
                "item_name": row["item_name"].strip()
            }

            if "" in cleaned_row.values():
                raise ValueError("Route fields in links.csv cannot be empty.")

            links.append(cleaned_row)

    return links

def load_configuration(nodes_path, links_path):
    """
    Load and validate the external deterministic network configuration.

    This function intentionally does not create recipes or simulation timing.
    Those decisions are separate from the verified node and route data.
    """

    nodes = load_nodes(nodes_path)
    links = load_links(links_path)

    for link in links:
        origin_id = link["origin_id"]
        destination_id = link["destination_id"]
        item_name = link["item_name"]

        if origin_id not in nodes:
            raise ValueError(
                f"Route origin {origin_id} does not exist in nodes.csv."
            )

        if destination_id not in nodes:
            raise ValueError(
                f"Route destination {destination_id} does not exist in nodes.csv."
            )

        expected_item = nodes[origin_id]["output_item"]

        if item_name != expected_item:
            raise ValueError(
                f"Route item {item_name} does not match {origin_id} "
                f"output item {expected_item}."
            )

    return nodes, links