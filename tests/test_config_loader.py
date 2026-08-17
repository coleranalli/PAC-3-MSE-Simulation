from pathlib import Path

from config_loader import load_configuration, load_links, load_nodes, load_recipes

project_root = Path(__file__).resolve().parents[1]
nodes_path = project_root / "data" / "nodes.csv"
links_path = project_root / "data" / "links.csv"
recipes_path = project_root / "data" / "recipes.csv"

def test_load_nodes():
    nodes = load_nodes(nodes_path)

    assert len(nodes) == 8
    assert nodes["S1"]["capacity"] == 1.25
    assert nodes["S6"]["output_item"] == "Motor Case"
    assert nodes["M1"]["output_item"] == "Propulsion Module"
    assert nodes["A1"]["output_item"] == "Final Modeled Unit"
    assert nodes["M1"]["reorder_point"] is None

def test_load_links():
    links = load_links(links_path)

    assert len(links) == 7
    assert links[0] == {
        "origin_id": "S1",
        "destination_id": "M1",
        "item_name": "AP"
    }
    assert links[-1] == {
        "origin_id": "M1",
        "destination_id": "A1",
        "item_name": "Propulsion Module"
    }

def test_routes_output():
    nodes, links = load_configuration(nodes_path, links_path)

    assert len(nodes) == 8
    assert len(links) == 7

    for link in links:
        origin_id = link["origin_id"]
        assert link["item_name"] == nodes[origin_id]["output_item"]

def test_load_recipes():
    recipes = load_recipes(recipes_path)

    assert len(recipes) == 3

    assert recipes["S6"] == {
        "Composite": 1.0
    }

    assert recipes["M1"] == {
        "AP": 1.0,
        "Aluminum": 1.0,
        "HTPB": 1.0,
        "Motor Case": 1.0,
        "Inert Hardware": 1.0
    }

    assert recipes["A1"] == {
        "Propulsion Module": 1.0
    }