class Node:
    """
    base class for a facility in the supply chain. the node class
    stores information that is common to every facility in the network.
    
    parent class for: Supplier, Manufacturer, & FinalAssembler
    """

    def __init__(self, node_id, name, location):
        """intializes node class with the 3 consistent traits of all classes"""

        # ensuring all text values are provided

        if node_id == "":
            raise ValueError("Node ID cannot be empty.")

        if name == "":
            raise ValueError("Node name cannot be empty.")

        if location == "":
            raise ValueError("Node location cannot be empty.")

        self.node_id = node_id
        self.name = name
        self.location = location

    def get_info(self):
        """
        returns basic info about the node upon request.
        this method stays avaialble to all classes inherting from node.
        """

        return(
            f"Node ID: {self.node_id}\n"
            f"Name: {self.name}\n"
            f"Location: {self.location}"
        )