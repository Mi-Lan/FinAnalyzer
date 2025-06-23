from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# Database models (matching Prisma schema)
class Company(BaseModel):
    id: str
    name: str
    ticker: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

class FinancialData(BaseModel):
    id: str
    companyId: str
    year: int
    period: str  # "Q1", "Q2", "Q3", "Q4", "FY"
    data: Dict[str, Any]  # This will store the FMP data as JSON
    createdAt: datetime
    updatedAt: datetime

class AnalysisTemplate(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    sectors: List[str]
    template: Dict[str, Any]
    createdAt: datetime
    updatedAt: datetime

class AnalysisInsights(BaseModel):
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    risks: List[str]
    recommendation: str  # 'BUY' | 'HOLD' | 'SELL'

class MetricScores(BaseModel):
    profitability: float
    growth: float
    balanceSheet: float
    capitalAllocation: float
    valuation: float
    overall: float

class AnalysisResult(BaseModel):
    id: str
    companyId: str
    templateId: str
    jobId: Optional[str] = None
    score: float
    insights: AnalysisInsights
    metricScores: MetricScores
    createdAt: datetime
    updatedAt: datetime

class BulkAnalysisJob(BaseModel):
    id: str
    status: str  # 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED'
    progress: float
    createdAt: datetime
    updatedAt: datetime

# API request/response models
class BulkAnalysisRequest(BaseModel):
    tickers: List[str]

class ScreeningResultCompany(BaseModel):
    company: Company
    latestFinancials: FinancialData
    analysis: AnalysisResult

class ScreeningResult(BaseModel):
    companies: List[ScreeningResultCompany]
    totalCount: int
    filters: Dict[str, Any]

class CompanyDetailsResponse(BaseModel):
    company: Company
    financialData: List[FinancialData]
    latestFinancials: FinancialData
    analysisResult: AnalysisResult 