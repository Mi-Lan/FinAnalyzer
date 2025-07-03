import pytest
from api_gateway.scoring.scorer import calculate_score
from api_gateway.scoring.config import default_tech_template
from api_gateway.scoring.models import FinalScore

@pytest.fixture
def sample_metrics():
    """Provides a sample set of financial metrics for a hypothetical tech company."""
    return {
        "gross_margin": 0.75,         # High, should score well
        "net_profit_margin": 0.22,    # Excellent
        "revenue_growth_qoq": 0.18,   # Excellent
        "eps_growth_qoq": 0.20,       # Excellent
        "debt_to_equity": 0.1,        # Very low, excellent
        "current_ratio": 2.5,         # Strong
        "return_on_equity": 0.28,     # Very high
        "pe_ratio": 18                # Favorable
    }

def test_calculate_score_baseline(sample_metrics):
    """Tests the scoring logic with a complete, strong set of metrics."""
    result = calculate_score(sample_metrics, default_tech_template)

    assert isinstance(result, FinalScore)
    assert 75 < result.overall_score <= 100
    assert len(result.dimension_scores) == 5
    assert not result.insufficient_data_flags

    # Check profitability score (expected high)
    profitability = next(d for d in result.dimension_scores if d.name == "Profitability")
    assert profitability.score > 80

    # Check valuation score (lower PE is better)
    valuation = next(d for d in result.dimension_scores if d.name == "Valuation")
    assert valuation.score >= 70


def test_calculate_score_with_missing_data(sample_metrics):
    """Tests how the scorer handles missing metrics with re-normalization."""
    del sample_metrics["net_profit_margin"] # Remove a key metric from Profitability
    del sample_metrics["pe_ratio"] # Remove the only metric for Valuation

    result = calculate_score(sample_metrics, default_tech_template, on_missing_data='renormalize')

    assert isinstance(result, FinalScore)
    assert "Profitability:net_profit_margin" in result.insufficient_data_flags
    assert "Valuation:pe_ratio" in result.insufficient_data_flags

    # Check that profitability score is based only on gross_margin now
    profitability = next(d for d in result.dimension_scores if d.name == "Profitability")
    assert len(profitability.metric_scores) == 1
    assert profitability.metric_scores[0].name == "gross_margin"
    # The score for the dimension should be the score of the single metric, as its weight is renormalized to 100%
    assert profitability.score == profitability.metric_scores[0].score 

    # Check that valuation score is 0 since no metrics were available
    valuation = next(d for d in result.dimension_scores if d.name == "Valuation")
    assert valuation.score == 0
    assert len(valuation.metric_scores) == 0


def test_calculate_score_with_poor_metrics():
    """Tests scoring with weak metrics to ensure scores are appropriately low."""
    poor_metrics = {
        "gross_margin": 0.1,
        "net_profit_margin": -0.05,
        "revenue_growth_qoq": -0.1,
        "eps_growth_qoq": -0.15,
        "debt_to_equity": 3.0,
        "current_ratio": 0.8,
        "return_on_equity": 0.05,
        "pe_ratio": 80
    }
    result = calculate_score(poor_metrics, default_tech_template)

    assert isinstance(result, FinalScore)
    assert 0 < result.overall_score < 40
    
    # Check profitability score (expected very low)
    profitability = next(d for d in result.dimension_scores if d.name == "Profitability")
    assert profitability.score < 30

    # Check balance sheet score (expected very low)
    balance_sheet = next(d for d in result.dimension_scores if d.name == "Balance Sheet")
    assert balance_sheet.score < 30


def test_higher_and_lower_is_better_logic():
    """
    Tests that 'higher_is_better=False' metrics (like debt_to_equity and pe_ratio)
    are scored correctly.
    """
    metrics = {
        "debt_to_equity": 0.1,   # Excellent (low is good)
        "pe_ratio": 100          # Poor (high is bad)
    }
    
    # Isolate Balance Sheet and Valuation dimensions for this test
    test_template = default_tech_template.model_copy(deep=True)
    test_template.dimensions = [
        d for d in test_template.dimensions if d.name in ["Balance Sheet", "Valuation"]
    ]

    # Clean up metrics not in use for this test
    for dim in test_template.dimensions:
        if dim.name == "Balance Sheet":
            dim.metrics = [m for m in dim.metrics if m.name == "debt_to_equity"]
        if dim.name == "Valuation":
            dim.metrics = [m for m in dim.metrics if m.name == "pe_ratio"]


    result = calculate_score(metrics, test_template)

    balance_sheet = next(d for d in result.dimension_scores if d.name == "Balance Sheet")
    valuation = next(d for d in result.dimension_scores if d.name == "Valuation")

    # debt_to_equity of 0.1 is very good, should get a high score
    assert balance_sheet.metric_scores[0].score > 80
    
    # pe_ratio of 100 is very high/bad, should get a low score
    assert valuation.metric_scores[0].score < 20
