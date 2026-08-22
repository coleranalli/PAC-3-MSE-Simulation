from pathlib import Path

from final_assembler import FinalAssembler
from manufacturer import Manufacturer
from model_builder import build_model_from_configuration
from supplier import Supplier


project_root = Path(__file__).resolve().parents[1]

nodes_path = project_root / "data" / "nodes.csv"
links_path = project_root / "data" / "links.csv"
recipes_path = project_root / "data" / "recipes.csv"

def test_model_builder_creates_all_nodes():
    model = build_model_from_configuration(
        nodes_path,
        links_path,
        recipes_path
    )

    assert len(model.nodes) == 8

    assert isinstance(model.nodes["S1"], Supplier)
    assert isinstance(model.nodes["S5"], Supplier)

    assert isinstance(model.nodes["S6"], Manufacturer)
    assert isinstance(model.nodes["M1"], Manufacturer)

    assert isinstance(model.nodes["A1"], FinalAssembler)

test_model_builder_creates_all_nodes()

def test_manufacturer_recipes_are_connected():
    model = build_model_from_configuration(
        nodes_path,
        links_path,
        recipes_path
    )

    s6 = model.nodes["S6"]
    m1 = model.nodes["M1"]
    a1 = model.nodes["A1"]

    assert "Composite" in s6.input_inventories

    assert len(m1.input_inventories) == 5
    assert "AP" in m1.input_inventories
    assert "Motor Case" in m1.input_inventories

    assert "Propulsion Module" in a1.input_inventories

test_manufacturer_recipes_are_connected()

def test_model_builder_registers_inventories():
    model = build_model_from_configuration(
        nodes_path,
        links_path,
        recipes_path
    )

    assert len(model.inventories) == 3

    assert model.get_inventory(
        "M1",
        "AP"
    ) is not None

    assert model.get_inventory(
        "M1",
        "Motor Case"
    ) is not None

    assert model.get_inventory(
        "M1",
        "Propulsion Module"
    ) is not None

    assert model.get_inventory(
        "S6",
        "Composite"
    ) is not None

    assert model.get_inventory(
        "A1",
        "Propulsion Module"
    ) is not None

test_model_builder_registers_inventories()

def test_output_inventory_is_registered_with_model():
    model = build_model_from_configuration(
        nodes_path,
        links_path,
        recipes_path
    )

    m1 = model.nodes["M1"]

    registered_inventory = model.get_inventory(
        "M1",
        "Propulsion Module"
    )

    assert registered_inventory is m1.output_inventory

test_output_inventory_is_registered_with_model()

def test_model_builder_creates_all_links():
    model = build_model_from_configuration(
        nodes_path,
        links_path,
        recipes_path
    )

    assert len(model.transport_links) == 7

    ap_link = model.find_transport_link("S1","M1","AP")

    assert ap_link is not None

    assert ap_link.origin_id == "S1"
    assert ap_link.destination_id == "M1"
    assert ap_link.item_name == "AP"
    assert ap_link.lead_time == 7

    motor_case_link = model.find_transport_link("S6","M1","Motor Case")

    assert motor_case_link is not None

test_model_builder_creates_all_links()