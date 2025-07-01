from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


# Database models (matching Prisma schema)
class Company(BaseModel):
    id: str
    name: str
    ticker: str
    sector: str
    industry: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class FinancialData(BaseModel):
    id: str
    companyId: str
    year: int
    period: str  # "Q1", "Q2", "Q3", "Q4", "FY"
    type: str  # e.g., "income-statement", "balance-sheet-statement", "10-K", "10-Q"
    data: Dict[str, Any]  # This will store the FMP data as JSON
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


# API request/response models
class CompanyDetailsResponse(BaseModel):
    company: Company
    financialData: List[FinancialData]
    latestFinancials: Optional[FinancialData] = None
    analysisResult: Optional[Dict[str, Any]] = None 