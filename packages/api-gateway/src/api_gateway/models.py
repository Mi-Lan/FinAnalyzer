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

class FMPFinancialStatement(BaseModel):
    date: str
    symbol: str
    reportedCurrency: str
    cik: str
    filingDate: str
    acceptedDate: str
    calendarYear: Optional[str] = None
    period: str
    link: Optional[str] = None
    finalLink: Optional[str] = None

class FMPIncomeStatement(FMPFinancialStatement):
    revenue: float
    costOfRevenue: float
    grossProfit: float
    researchAndDevelopmentExpenses: float
    generalAndAdministrativeExpenses: float
    sellingAndMarketingExpenses: float
    sellingGeneralAndAdministrativeExpenses: float
    otherExpenses: float
    operatingExpenses: float
    costAndExpenses: float
    interestIncome: float
    interestExpense: float
    depreciationAndAmortization: float
    ebitda: float
    ebit: float
    operatingIncome: float
    totalOtherIncomeExpensesNet: float
    incomeBeforeTax: float
    incomeTaxExpense: float
    netIncome: float
    netIncomeFromContinuingOperations: float
    netIncomeFromDiscontinuedOperations: float
    otherAdjustmentsToNetIncome: float
    bottomLineNetIncome: float
    netIncomeDeductions: float
    netInterestIncome: float
    nonOperatingIncomeExcludingInterest: float
    eps: Optional[float] = None
    epsDiluted: Optional[float] = None
    weightedAverageShsOut: float
    weightedAverageShsOutDil: float

class FMPBalanceSheetStatement(FMPFinancialStatement):
    cashAndCashEquivalents: float
    shortTermInvestments: float
    cashAndShortTermInvestments: float
    netReceivables: float
    accountsReceivables: float
    otherReceivables: float
    inventory: float
    prepaids: float

    otherCurrentAssets: float
    totalCurrentAssets: float
    propertyPlantEquipmentNet: float
    goodwill: float
    intangibleAssets: float
    goodwillAndIntangibleAssets: float
    longTermInvestments: float
    taxAssets: float
    otherNonCurrentAssets: float
    totalNonCurrentAssets: float
    otherAssets: float
    totalAssets: float
    totalPayables: float
    accountPayables: float
    otherPayables: float
    accruedExpenses: float
    shortTermDebt: float
    capitalLeaseObligationsCurrent: float
    taxPayables: float
    deferredRevenue: float
    otherCurrentLiabilities: float
    totalCurrentLiabilities: float
    longTermDebt: float
    capitalLeaseObligationsNonCurrent: Optional[float] = None
    deferredRevenueNonCurrent: float
    deferredTaxLiabilitiesNonCurrent: float
    otherNonCurrentLiabilities: float
    totalNonCurrentLiabilities: float
    otherLiabilities: float
    capitalLeaseObligations: float
    totalLiabilities: float
    treasuryStock: float
    preferredStock: float
    commonStock: float
    retainedEarnings: float
    additionalPaidInCapital: float
    accumulatedOtherComprehensiveIncomeLoss: float
    otherTotalStockholdersEquity: float
    totalStockholdersEquity: float
    totalEquity: float
    minorityInterest: float
    totalLiabilitiesAndTotalEquity: float
    totalInvestments: float
    totalDebt: float
    netDebt: float

class FMPCashFlowStatement(FMPFinancialStatement):
    netIncome: float
    depreciationAndAmortization: float
    deferredIncomeTax: float
    stockBasedCompensation: float
    changeInWorkingCapital: float
    accountsReceivables: float
    inventory: float
    accountsPayables: float
    otherWorkingCapital: float
    otherNonCashItems: float
    netCashProvidedByOperatingActivities: float
    investmentsInPropertyPlantAndEquipment: float
    acquisitionsNet: float
    purchasesOfInvestments: float
    salesMaturitiesOfInvestments: float
    otherInvestingActivities: float
    netCashProvidedByInvestingActivities: float
    netDebtIssuance: float
    longTermNetDebtIssuance: float
    shortTermNetDebtIssuance: float
    netStockIssuance: float
    netCommonStockIssuance: float
    commonStockIssuance: float
    commonStockRepurchased: float
    netPreferredStockIssuance: float
    netDividendsPaid: float
    commonDividendsPaid: float
    preferredDividendsPaid: float
    otherFinancingActivities: float
    netCashProvidedByFinancingActivities: float
    effectOfForexChangesOnCash: float
    netChangeInCash: float
    cashAtEndOfPeriod: float
    cashAtBeginningOfPeriod: float
    operatingCashFlow: float
    capitalExpenditure: float
    freeCashFlow: float
    incomeTaxesPaid: float
    interestPaid: float

class FMPFinancialStatements(BaseModel):
    incomeStatement: FMPIncomeStatement
    balanceSheet: FMPBalanceSheetStatement
    cashFlow: FMPCashFlowStatement

class FinancialData(BaseModel):
    id: str
    companyId: str
    year: int
    period: str  # "Q1", "Q2", "Q3", "Q4", "FY"
    data: FMPFinancialStatements
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

class BulkAnalysisRequest(BaseModel):
    tickers: List[str] 