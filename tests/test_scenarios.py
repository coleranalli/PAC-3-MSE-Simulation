from pathlib import Path

import pytest

from config_loader import load_nodes
from scenarios import apply_node_overrides


project_root = Path(__file__).resolve().parents[1]

nodes_path = project_root / "data" / "nodes.csv"

def test_disruption_probability_override():

    original_nodes = load_nodes(nodes_path)

    original_probability = (
        original_nodes["S6"]["disruption_probability"]
    )

    changed_nodes = apply_node_overrides(
        original_nodes, {"S6": {"disruption_probability": 0.0}}
    )

    assert changed_nodes["S6"]["disruption_probability"] == 0.0

    assert (original_nodes["S6"]["disruption_probability"] == 
        original_probability)

    assert (changed_nodes["M1"]["disruption_probability"] ==
        original_nodes["M1"]["disruption_probability"])

def test_capacity_multiplier():

    original_nodes = load_nodes(nodes_path)

    original_capacity = original_nodes["M1"]["capacity"]

    changed_nodes = apply_node_overrides(
        original_nodes, {"M1": {"capacity_multiplier": 0.80}}
    )

    assert (changed_nodes["M1"]["capacity"] 
        == pytest.approx(original_capacity*0.80))

    assert original_nodes["M1"]["capacity"] == original_capacity


def test_lead_time_multiplier():

    original_nodes = load_nodes(nodes_path)

    original_lead_time = original_nodes["S1"]["lead_time"]

    changed_nodes = apply_node_overrides(
        original_nodes,{"S1": {"lead_time_multiplier": 1.20}}
    )

    assert (changed_nodes["S1"]["lead_time"]
        == pytest.approx(original_lead_time * 1.20))


def test_unknown_node_rejected():

    original_nodes = load_nodes(nodes_path)

    with pytest.raises(ValueError):

        apply_node_overrides(
            original_nodes,
            {"BAD_NODE": {"disruption_probability": 0.0}}
        )


def test_unknown_parameter_rejected():

    original_nodes = load_nodes(nodes_path)

    with pytest.raises(ValueError):

        apply_node_overrides(
            original_nodes,
            {"S6": {"fake_parameter": 123}}
        )