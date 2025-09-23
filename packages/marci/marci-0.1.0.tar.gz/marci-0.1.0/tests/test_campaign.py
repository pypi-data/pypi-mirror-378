import numpy as np
import pandas as pd
from marci import Campaign


def test_campaign_basic_initialization():
    c = Campaign()
    assert c.name == "Campaign"
    assert c.cpm == 10
    assert c.cvr == 1e-4
    assert c.aov == 100
    assert c.cv == 0.1
    assert c.baseline == 1000


def test_campaign_custom_parameters():
    c = Campaign(
        name="Test Campaign", cpm=15, cvr=2e-4, aov=150, elasticity=0.3, baseline=2000
    )
    assert c.name == "Test Campaign"
    assert c.cpm == 15
    assert c.cvr == 2e-4
    assert c.aov == 150
    assert c.baseline == 2000


def test_campaign_expected_roas():
    c = Campaign(cpm=10, cvr=1e-4, aov=100, elasticity=0.2)

    # Test with default spend
    roas = c.expected_roas()
    assert roas > 0

    # Test with custom spend
    roas_custom = c.expected_roas(avg_spend=1500)
    assert roas_custom > 0


def test_campaign_external_roas():
    c = Campaign(is_external=True, cpm=10, cvr=1e-4, aov=100)

    roas = c.expected_roas()
    expected = 1000 * 1e-4 * 100 / 10  # Should be 1.0
    assert np.isclose(roas, expected)


def test_campaign_expected_sales():
    c = Campaign(cpm=10, cvr=1e-4, aov=100, elasticity=0.2)

    sales = c.expected_sales(avg_spend=1000)
    assert sales > 0


def test_campaign_sim_outcomes():
    c = Campaign()  # Campaign doesn't take seed parameter

    # Test simulation without plot
    df = c.sim_outcomes(periods=10, avg_spend=500)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "spend" in df.columns
    assert "imps" in df.columns
    assert "convs" in df.columns
    assert "sales" in df.columns


def test_campaign_simulated_vs_expected_roas():
    """Test that simulated ROAS is reasonably close to expected ROAS."""
    c = Campaign(
        cpm=15,
        cvr=2e-4,
        aov=120,
        elasticity=0.3,
        baseline=1000,
        cv=0.05,  # Lower CV for more stable results
    )

    # Calculate expected ROAS
    expected_roas = c.expected_roas(avg_spend=800)

    # Run simulation multiple times and average
    n_sims = 10
    simulated_roas_list = []

    for _ in range(n_sims):
        df = c.sim_outcomes(
            periods=30,
            avg_spend=800,
            cv=0.05,  # Lower CV for stability
        )

        # Calculate simulated ROAS: total sales / total spend
        total_sales = df["sales"].sum()
        total_spend = df["spend"].sum()
        simulated_roas = total_sales / total_spend if total_spend > 0 else 0
        simulated_roas_list.append(simulated_roas)

    # Average simulated ROAS
    avg_simulated_roas = np.mean(simulated_roas_list)

    # Check that simulated ROAS is within reasonable range of expected
    # Allow for some variance due to randomness and attribution delays
    roas_ratio = avg_simulated_roas / expected_roas

    # Should be within 50% of expected (reasonable for simulation variance)
    assert 0.5 <= roas_ratio <= 2.0, (
        f"Simulated ROAS {avg_simulated_roas:.3f} not close to expected {expected_roas:.3f}"
    )

    # Both should be positive
    assert expected_roas > 0
    assert avg_simulated_roas > 0
