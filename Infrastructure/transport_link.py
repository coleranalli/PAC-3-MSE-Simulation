class TransportLink:
    """
    represents a connection between two nodes in a supply chain.
    
    TransportLink identifies:
    - where items come from
    - where items go
    - what items can move across the link
    - the lead time
    - lead time variability
    - transportation delay probability

    random variabiity and transportation delays not yet applied
    """

    def __init__(self, origin_id, destination_id, item_name, 
        lead_time, variability, transportation_delay_probability):

        # validates the information

        if origin_id == "":
            raise ValueError("Origin ID cannot be empty.")

        if destination_id == "":
            raise ValueError("Destination ID cannot be empty.")

        if item_name == "":
            raise ValueError("Item name cannot be empty.")

        # prevents negative lead time and variability

        if lead_time < 0:
            raise ValueError("Lead time cannot be negative.")

        if variability < 0:
            raise ValueError("Variability cannot be negative.")

        self.origin_id = origin_id
        self.destination_id = destination_id
        self.item_name = item_name

        self.lead_time = lead_time
        self.variability = variability
        self.transportation_delay_probability = (
            transportation_delay_probability
        )

        # keeps probability a number between 0 and 1
        if (transportation_delay_probability < 0 or transportation_delay_probability > 1):
            raise ValueError("Transportation delay probability must be between 0 and 1.")

    def matches_route(self, origin_id, destination_id, item_name):
        """
        checks whether the link matches requested movement
            
        will help SupplyChainModel verify the correct link later
        """
        if (
            self.origin_id == origin_id
            and self.destination_id == destination_id
            and self.item_name == item_name
        ):
            return True

        return False

    def get_info(self):
        """returns important info about the link"""

        return(
            f"Origin: {self.origin_id}\n"
            f"Destination: {self.destination_id}\n"
            f"Item: {self.item_name}\n"
            f"Lead Time: {self.lead_time}\n"
            f"Variability: {self.variability}\n"
            f"Transportation Delay Probability: "
            f"{self.transportation_delay_probability}"
        )