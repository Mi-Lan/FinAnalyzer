from fastapi import FastAPI, APIRouter, Depends
from .security import get_api_key
from .models import (
    Company,
    CompanyDetailsResponse,
    ScreeningResult,
    BulkAnalysisJob,
    BulkAnalysisRequest,
    FinancialData,
    AnalysisResult,
    AnalysisInsights,
    MetricScores,
    ScreeningResultCompany,
)
from typing import List
from datetime import datetime

app = FastAPI()
router = APIRouter(prefix="/api", dependencies=[Depends(get_api_key)])

# Dummy data for now
dummy_company = Company(
    id="1", 
    name="Apple Inc.", 
    ticker="AAPL", 
    sector="Technology",
    industry="Consumer Electronics",
    createdAt=datetime.now(), 
    updatedAt=datetime.now()
)

dummy_financials = FinancialData(
    id="1", 
    companyId="1", 
    year=2023, 
    period="FY",
    data={
        "incomeStatement": {"revenue": 383285000000, "netIncome": 96995000000},
        "balanceSheet": {"totalAssets": 352583000000, "totalLiabilities": 290437000000},
        "cashFlow": {"operatingCashFlow": 110543000000, "freeCashFlow": 99584000000}
    },
    createdAt=datetime.now(), 
    updatedAt=datetime.now()
)

dummy_analysis_result = AnalysisResult(
    id="1", 
    companyId="1", 
    templateId="1", 
    score=85,
    insights=AnalysisInsights(
        summary="Strong financial performance with robust cash generation.", 
        strengths=["High cash flow", "Strong market position"], 
        weaknesses=["High valuation"], 
        opportunities=["AI integration", "Services growth"], 
        risks=["Regulatory pressure", "Market saturation"], 
        recommendation="BUY"
    ),
    metricScores=MetricScores(
        profitability=90, 
        growth=80, 
        balanceSheet=85, 
        capitalAllocation=88, 
        valuation=70, 
        overall=85
    ),
    createdAt=datetime.now(), 
    updatedAt=datetime.now()
)

@router.get("/companies", response_model=List[Company])
def get_companies():
    return [dummy_company]


@router.get("/companies/{ticker}", response_model=CompanyDetailsResponse)
def get_company(ticker: str):
    return CompanyDetailsResponse(
        company=dummy_company,
        financialData=[dummy_financials],
        latestFinancials=dummy_financials,
        analysisResult=dummy_analysis_result
    )


@router.get("/analysis/screen", response_model=ScreeningResult)
def get_analysis_screen():
    return ScreeningResult(
        companies=[
            ScreeningResultCompany(
                company=dummy_company,
                latestFinancials=dummy_financials,
                analysis=dummy_analysis_result
            )
        ],
        totalCount=1,
        filters={}
    )


@router.get("/analysis/bulk/{job_id}", response_model=BulkAnalysisJob)
def get_bulk_analysis(job_id: str):
    return BulkAnalysisJob(
        id=job_id, 
        status="COMPLETED", 
        progress=1.0, 
        createdAt=datetime.now(), 
        updatedAt=datetime.now()
    )


@router.post("/analysis/bulk", response_model=BulkAnalysisJob)
def post_bulk_analysis(request: BulkAnalysisRequest):
    return BulkAnalysisJob(
        id="new_job_id", 
        status="PENDING", 
        progress=0.0, 
        createdAt=datetime.now(), 
        updatedAt=datetime.now()
    )


app.include_router(router)
