from typing import Dict, List, Tuple, Optional
from .models import (
    ScoringTemplate, 
    MetricScoringRule, 
    FinalScore, 
    DimensionScore, 
    MetricScore
)

def _score_metric(value: float, rule: MetricScoringRule) -> Tuple[int, str]:
    """Scores a single metric based on its value and a set of threshold rules."""
    # Sort thresholds based on whether higher or lower values are better.
    sorted_thresholds = sorted(
        rule.thresholds, 
        key=lambda t: t.value, 
        reverse=rule.higher_is_better
    )
    
    for threshold in sorted_thresholds:
        if rule.higher_is_better and value >= threshold.value:
            return threshold.score, f"Value {value:.2f} met or exceeded threshold {threshold.value}"
        if not rule.higher_is_better and value <= threshold.value:
            return threshold.score, f"Value {value:.2f} met or was below threshold {threshold.value}"
            
    # If no threshold is met, return a default low score.
    return 0, f"Value {value:.2f} did not meet any defined thresholds."

def calculate_score(
    financial_metrics: Dict[str, float],
    template: ScoringTemplate,
    on_missing_data: str = 'renormalize' # or 'neutral'
) -> FinalScore:
    """
    Calculates a final score for a company based on its financial metrics and a scoring template.
    """
    dimension_scores: List[DimensionScore] = []
    insufficient_data_flags: List[str] = []
    
    for dim_config in template.dimensions:
        metric_scores: List[MetricScore] = []
        total_weight_for_dimension = 0.0
        
        # First, find available metrics and total their weight
        available_metrics: List[MetricScoringRule] = []
        for metric_rule in dim_config.metrics:
            if metric_rule.name in financial_metrics:
                available_metrics.append(metric_rule)
                total_weight_for_dimension += metric_rule.weight
            else:
                insufficient_data_flags.append(f"{dim_config.name}:{metric_rule.name}")

        # Score each available metric
        weighted_score_sum = 0.0
        for metric_rule in available_metrics:
            metric_value = financial_metrics[metric_rule.name]
            score, justification = _score_metric(metric_value, metric_rule)
            
            # Adjust weight if renormalizing, otherwise use original weight
            effective_weight = metric_rule.weight
            if on_missing_data == 'renormalize' and total_weight_for_dimension > 0:
                effective_weight = metric_rule.weight / total_weight_for_dimension

            weighted_score_sum += score * effective_weight
            
            metric_scores.append(MetricScore(
                name=metric_rule.name,
                score=score,
                justification=justification,
                value=metric_value,
                weight=metric_rule.weight # Log original weight for clarity
            ))
            
        # Handle case where a dimension has no available metrics
        if not available_metrics:
            dim_score = 0
            justification = "No metric data available for this dimension."
        else:
            dim_score = int(round(weighted_score_sum))
            justification = f"Aggregated score from {len(available_metrics)} metrics."

        dimension_scores.append(DimensionScore(
            name=dim_config.name,
            score=dim_score,
            justification=justification,
            weight=dim_config.weight,
            metric_scores=metric_scores
        ))

    # Calculate final overall score
    final_weighted_score = sum(ds.score * ds.weight for ds in dimension_scores)
    total_dimension_weight = sum(ds.weight for ds in dimension_scores)
    
    if total_dimension_weight == 0:
        overall_score = 0
    else:
        # Normalize the final score based on the sum of dimension weights (usually 1.0)
        overall_score = int(round(final_weighted_score / total_dimension_weight))
    
    return FinalScore(
        overall_score=overall_score,
        dimension_scores=dimension_scores,
        insufficient_data_flags=insufficient_data_flags
    )
