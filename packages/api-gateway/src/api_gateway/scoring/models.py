from pydantic import BaseModel, Field
from typing import List, Dict, Union

class Threshold(BaseModel):
    """Defines a single threshold for scoring a metric."""
    value: float
    score: int

class MetricScoringRule(BaseModel):
    """Defines the rules for scoring a single financial metric."""
    name: str
    weight: float = Field(..., ge=0, le=1, description="Weight of this metric within its dimension.")
    thresholds: List[Threshold]
    # Determines if a higher metric value is better (e.g., revenue growth) or worse (e.g., debt-to-equity).
    higher_is_better: bool = True

class DimensionScoringConfig(BaseModel):
    """Configuration for scoring one of the five key dimensions."""
    name: str
    weight: float = Field(..., ge=0, le=1, description="Weight of this dimension in the final score.")
    metrics: List[MetricScoringRule]

class ScoringTemplate(BaseModel):
    """A full template defining how to score a company, often sector-specific."""
    id: str
    name: str
    description: str
    dimensions: List[DimensionScoringConfig]

class Score(BaseModel):
    """Represents a calculated score for a metric, dimension, or overall."""
    name: str
    score: int = Field(..., ge=0, le=100)
    # Explanation of how the score was derived (e.g., which threshold was met).
    justification: str 

class MetricScore(Score):
    """Detailed score for a single metric."""
    value: Union[float, str] # The actual value of the metric
    weight: float

class DimensionScore(Score):
    """Aggregated score for a dimension."""
    weight: float
    metric_scores: List[MetricScore]

class FinalScore(BaseModel):
    """The final, comprehensive scoring result for a company."""
    overall_score: int = Field(..., ge=0, le=100)
    dimension_scores: List[DimensionScore]
    insufficient_data_flags: List[str] = Field(default_factory=list, description="List of metrics that were missing data.")
