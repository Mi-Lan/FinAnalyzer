from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, ValidationError
from typing import Dict, Any, Optional, List
from ..scoring.scorer import calculate_score
from ..scoring.models import ScoringTemplate, FinalScore
from ..security import get_api_key
from ..database import fetch_template_by_name, fetch_all_template_names

router = APIRouter()

class ScoringRequest(BaseModel):
    """Request model for scoring calculation"""
    financial_metrics: Dict[str, Any]
    template_name: str = "Technology Sector Scoring Model V1" # Default to a known template name

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
    Calculate a financial score for a company based on provided metrics and a stored template.
    
    Args:
        request: Contains financial metrics and the name of the template to use.
        api_key: API authentication (handled by dependency)
    
    Returns:
        ScoringResponse with calculated score and metadata
    """
    try:
        # Fetch the template from the database
        db_template = await fetch_template_by_name(request.template_name)
        if not db_template:
            raise HTTPException(
                status_code=404,
                detail=f"Template '{request.template_name}' not found."
            )
        
        # Parse the JSON template into our Pydantic model
        try:
            template = ScoringTemplate.model_validate(db_template['template'])
        except (ValidationError, KeyError) as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse scoring template '{request.template_name}': {e}"
            )
        
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
    except HTTPException:
        raise # Re-raise HTTPException to avoid being caught by the generic Exception handler
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

class TemplateInfo(BaseModel):
    name: str

@router.get("/templates", response_model=List[TemplateInfo])
async def list_available_templates(api_key: str = Depends(get_api_key)):
    """
    List all available scoring templates by name.
    
    Returns:
        A list of available template names.
    """
    template_names = await fetch_all_template_names()
    return [{"name": name} for name in template_names]

class TemplateDetailResponse(BaseModel):
    template: ScoringTemplate
    metrics_required: List[str]

@router.get("/template/{template_name}", response_model=TemplateDetailResponse)
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
    db_template = await fetch_template_by_name(template_name)
    if not db_template:
        raise HTTPException(
            status_code=404,
            detail=f"Template '{template_name}' not found"
        )
    
    try:
        template_model = ScoringTemplate.model_validate(db_template['template'])
    except (ValidationError, KeyError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse scoring template '{template_name}': {e}"
        )

    metrics_required = [
        f"{dim.name}.{metric.name}" 
        for dim in template_model.dimensions
        for metric in dim.metrics
    ]

    return TemplateDetailResponse(
        template=template_model,
        metrics_required=metrics_required
    )
