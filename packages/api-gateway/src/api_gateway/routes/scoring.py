from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ..scoring.scorer import calculate_score
from ..scoring.config import default_tech_template
from ..scoring.models import ScoringTemplate, FinalScore
from ..security import get_api_key

router = APIRouter()

class ScoringRequest(BaseModel):
    """Request model for scoring calculation"""
    financial_metrics: Dict[str, Any]
    template_name: Optional[str] = "default_tech"

class ScoringResponse(BaseModel):
    """Response model for scoring calculation"""
    score: FinalScore
    template_used: str
    metrics_processed: int
    missing_metrics: list

@router.post("/calculate", response_model=ScoringResponse)
async def calculate_company_score(
    request: ScoringRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Calculate a financial score for a company based on provided metrics.
    
    Args:
        request: Contains financial metrics and optional template name
        api_key: API authentication (handled by dependency)
    
    Returns:
        ScoringResponse with calculated score and metadata
    """
    try:
        # For now, we only support the default tech template
        if request.template_name and request.template_name != "default_tech":
            raise HTTPException(
                status_code=400,
                detail=f"Template '{request.template_name}' not supported. Available: 'default_tech'"
            )
        
        # Use the default tech template
        template = default_tech_template
        
        # Calculate the score
        score_result = calculate_score(request.financial_metrics, template)
        
        # Collect missing metrics for reporting
        missing_metrics = []
        for dimension in template.dimensions:
            for metric_rule in dimension.metrics:
                if metric_rule.name not in request.financial_metrics:
                    missing_metrics.append(f"{dimension.name}.{metric_rule.name}")
        
        return ScoringResponse(
            score=score_result,
            template_used=template.name,
            metrics_processed=len(request.financial_metrics),
            missing_metrics=missing_metrics
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Scoring error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/templates")
async def list_available_templates(api_key: str = Depends(get_api_key)):
    """
    List all available scoring templates.
    
    Returns:
        Dictionary of available templates with their descriptions
    """
    return {
        "templates": {
            "default_tech": {
                "name": default_tech_template.name,
                "description": default_tech_template.description,
                "dimensions": [dim.name for dim in default_tech_template.dimensions],
                "total_weight": sum(dim.weight for dim in default_tech_template.dimensions)
            }
        }
    }

@router.get("/template/{template_name}")
async def get_template_details(
    template_name: str,
    api_key: str = Depends(get_api_key)
):
    """
    Get detailed information about a specific scoring template.
    
    Args:
        template_name: Name of the template to retrieve
        
    Returns:
        Detailed template configuration
    """
    if template_name != "default_tech":
        raise HTTPException(
            status_code=404,
            detail=f"Template '{template_name}' not found"
        )
    
    return {
        "template": default_tech_template.model_dump(),
        "metrics_required": [
            f"{dim.name}.{metric.name}" 
            for dim in default_tech_template.dimensions
            for metric in dim.metrics
        ]
    }
