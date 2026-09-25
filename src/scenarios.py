import copy

SUPPORTED_DIRECT_OVERRIDES = {"disruption_probability"}

SUPPORTED_MULTIPLIERS = {
    "capacity_multiplier" : "capacity",
    "lead_time_multiplier" : "lead_time"
}

def apply_node_overrides(node_rows, node_overrides):
    """
    returns a copied node with an override applied.
    
    importantly does not change the original config!
    """


    updated_rows = copy.deepcopy(node_rows) # prevent changes to node_rows

    for node_id, overrides in node_overrides.items():

        if node_id not in updated_rows:
            raise ValueError(
                f"Scenario node {node_id} does not exist."
            )

        for parameter,value in overrides.items():

            if parameter in SUPPORTED_DIRECT_OVERRIDES:

                if parameter == "disruption_probability":
                    if value < 0 or value > 1:
                        raise ValueError(
                            "Disruption probability must be between 0 & 1"
                            )
                    
                updated_rows[node_id][parameter] = value

            elif parameter in SUPPORTED_MULTIPLIERS:

                if value <= 0:
                    raise ValueError(f"{parameter} must be greater than zero.")

                base_parameter = SUPPORTED_MULTIPLIERS[parameter]
                baseline_value = updated_rows[node_id][base_parameter]
                updated_rows[node_id][base_parameter] = baseline_value * value

            else:
                raise ValueError(
                    f"Unspported scenario parameter: {parameter}"
                )
            
    return updated_rows