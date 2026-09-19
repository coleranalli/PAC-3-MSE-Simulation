from plotting import plot_distribution

def test_distribution_plot_is_created(tmp_path):

    results = [
        {"final_units_produced": 100},
        {"final_units_produced": 120},
        {"final_units_produced": 110}
    ]

    output_path = (tmp_path / "distribution.png")

    plot_distribution(
        results,
        "final_units_produced",
        output_path,
        "Test Distribution",
        "Final Units"
    )

    assert output_path.exists()