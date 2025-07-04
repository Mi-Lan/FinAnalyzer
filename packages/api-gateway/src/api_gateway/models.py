from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


# Database models (matching Prisma schema)
class Company(BaseModel):
    id: str
    name: str
    ticker: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    score: Optional[int] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class FinancialData(BaseModel):
    id: str
    companyId: str
    type: str
    year: int
    period: str
    data: Dict[str, Any]
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class MetricScores(BaseModel):
    profitability: int
    growth: int
    balanceSheet: int
    capitalAllocation: int
    valuation: int
    overall: int


class AnalysisInsights(BaseModel):
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    risks: List[str]
    recommendation: Optional[str] = None


class AnalysisResult(BaseModel):
    id: str
    companyId: str
    templateId: str
    score: int
    insights: AnalysisInsights
    metricScores: MetricScores
    createdAt: datetime
    updatedAt: datetime


class CompanyWithAnalysis(BaseModel):
    id: str
    name: str
    ticker: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    score: Optional[int] = None
    insights: Optional[AnalysisInsights] = None
    createdAt: datetime
    updatedAt: datetime


# API request/response models
class CompanyDetailsResponse(BaseModel):
    company: Company
    financialData: List[FinancialData]
    latestFinancials: Optional[FinancialData] = None
    analysisResult: Optional[AnalysisResult] = None 