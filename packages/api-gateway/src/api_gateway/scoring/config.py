from .models import ScoringTemplate, DimensionScoringConfig, MetricScoringRule, Threshold

# A default template for scoring technology companies.
# This serves as a baseline and can be replaced by templates loaded from a database.
default_tech_template = ScoringTemplate(
    id="tech_v1",
    name="Technology Sector Scoring Model V1",
    description="A standard scoring model for established technology companies.",
    dimensions=[
        # 1. Profitability
        DimensionScoringConfig(
            name="Profitability",
            weight=0.25,
            metrics=[
                MetricScoringRule(
                    name="gross_margin",
                    weight=0.4,
                    higher_is_better=True,
                    thresholds=[
                        Threshold(value=0.6, score=90),
                        Threshold(value=0.4, score=70),
                        Threshold(value=0.2, score=40),
                        Threshold(value=0.0, score=10)
                    ]
                ),
                MetricScoringRule(
                    name="net_profit_margin",
                    weight=0.6,
                    higher_is_better=True,
                    thresholds=[
                        Threshold(value=0.20, score=95),
                        Threshold(value=0.10, score=75),
                        Threshold(value=0.05, score=50),
                        Threshold(value=0.0, score=20)
                    ]
                ),
            ]
        ),
        # 2. Growth
        DimensionScoringConfig(
            name="Growth",
            weight=0.25,
            metrics=[
                MetricScoringRule(
                    name="revenue_growth_qoq",
                    weight=0.7,
                    higher_is_better=True,
                    thresholds=[
                        Threshold(value=0.15, score=95), # >15% growth is excellent
                        Threshold(value=0.05, score=70), # >5% is good
                        Threshold(value=0.0, score=40),  # >0% is okay
                        Threshold(value=-1.0, score=10) # Negative growth is bad
                    ]
                ),
                MetricScoringRule(
                    name="eps_growth_qoq",
                    weight=0.3,
                    higher_is_better=True,
                    thresholds=[
                        Threshold(value=0.15, score=90),
                        Threshold(value=0.05, score=70),
                        Threshold(value=0.0, score=40),
                        Threshold(value=-1.0, score=10)
                    ]
                ),
            ]
        ),
        # 3. Balance Sheet
        DimensionScoringConfig(
            name="Balance Sheet",
            weight=0.20,
            metrics=[
                MetricScoringRule(
                    name="debt_to_equity",
                    weight=0.5,
                    higher_is_better=False, # Lower is better
                    thresholds=[
                        Threshold(value=0.2, score=90), # < 0.2 is great
                        Threshold(value=0.5, score=70), # < 0.5 is good
                        Threshold(value=1.0, score=40), # < 1.0 is okay
                        Threshold(value=2.0, score=10)  # > 2.0 is risky
                    ]
                ),
                MetricScoringRule(
                    name="current_ratio",
                    weight=0.5,
                    higher_is_better=True,
                    thresholds=[
                        Threshold(value=2.0, score=90),
                        Threshold(value=1.5, score=75),
                        Threshold(value=1.0, score=50),
                        Threshold(value=0.5, score=10)
                    ]
                )
            ]
        ),
        # 4. Capital Allocation
        DimensionScoringConfig(
            name="Capital Allocation",
            weight=0.15,
            metrics=[
                MetricScoringRule(
                    name="return_on_equity",
                    weight=1.0,
                    higher_is_better=True,
                    thresholds=[
                        Threshold(value=0.25, score=95),
                        Threshold(value=0.15, score=75),
                        Threshold(value=0.10, score=50),
                        Threshold(value=0.0, score=20)
                    ]
                )
            ]
        ),
        # 5. Valuation
        DimensionScoringConfig(
            name="Valuation",
            weight=0.15,
            metrics=[
                MetricScoringRule(
                    name="pe_ratio",
                    weight=1.0,
                    higher_is_better=False, # Lower is generally better
                    thresholds=[
                        Threshold(value=15, score=90),
                        Threshold(value=25, score=70),
                        Threshold(value=40, score=40),
                        Threshold(value=60, score=10)
                    ]
                )
            ]
        )
    ]
)
