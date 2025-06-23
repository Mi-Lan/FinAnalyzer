from fastapi import FastAPI, APIRouter, Depends
from .security import get_api_key
from .models import (
    Company,
    CompanyDetailsResponse,
    ScreeningResult,
    BulkAnalysisJob,
    BulkAnalysisRequest,
    FinancialData,
    FMPFinancialStatements,
    FMPIncomeStatement,
    FMPBalanceSheetStatement,
    FMPCashFlowStatement,
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
dummy_company = Company(id="1", name="Apple Inc.", ticker="AAPL", createdAt=datetime.now(), updatedAt=datetime.now())
dummy_income_statement = FMPIncomeStatement(
    date="2023-12-31", symbol="AAPL", reportedCurrency="USD", cik="0000320193",
    filingDate="2024-02-01", acceptedDate="2024-02-01", period="FY",
    revenue=383285000000, costOfRevenue=214137000000, grossProfit=169148000000,
    researchAndDevelopmentExpenses=29915000000, generalAndAdministrativeExpenses=0,
    sellingAndMarketingExpenses=24933000000, sellingGeneralAndAdministrativeExpenses=24933000000,
    otherExpenses=0, operatingExpenses=54848000000, costAndExpenses=268985000000,
    interestIncome=3750000000, interestExpense=4965000000, depreciationAndAmortization=11519000000,
    ebitda=125820000000, ebit=114301000000, operatingIncome=114301000000,
    totalOtherIncomeExpensesNet=-224000000, incomeBeforeTax=113736000000, incomeTaxExpense=16741000000,
    netIncome=96995000000, netIncomeFromContinuingOperations=96995000000,
    netIncomeFromDiscontinuedOperations=0, otherAdjustmentsToNetIncome=0, bottomLineNetIncome=96995000000,
    netIncomeDeductions=0, netInterestIncome=0, nonOperatingIncomeExcludingInterest=0,
    eps=6.16, epsDiluted=6.13, weightedAverageShsOut=15744231000, weightedAverageShsOutDil=15812547000
)
dummy_balance_sheet = FMPBalanceSheetStatement(
    date="2023-09-30", symbol="AAPL", reportedCurrency="USD", cik="0000320193",
    filingDate="2023-11-03", acceptedDate="2023-11-02", period="FY",
    cashAndCashEquivalents=29965000000, shortTermInvestments=31454000000,
    cashAndShortTermInvestments=61419000000, netReceivables=60985000000, accountsReceivables=29699000000,
    otherReceivables=31286000000, inventory=6469000000, prepaids=0, otherCurrentAssets=19727000000,

    totalCurrentAssets=143566000000, propertyPlantEquipmentNet=43555000000,
    goodwill=0, intangibleAssets=0, goodwillAndIntangibleAssets=0, longTermInvestments=27297000000,
    taxAssets=0, otherNonCurrentAssets=43694000000, totalNonCurrentAssets=114546000000,
    otherAssets=0, totalAssets=352583000000, totalPayables=0, accountPayables=62612000000,
    otherPayables=0, accruedExpenses=0, shortTermDebt=29000000000, capitalLeaseObligationsCurrent=0,
    taxPayables=0, deferredRevenue=8560000000, otherCurrentLiabilities=56857000000,
    totalCurrentLiabilities=145308000000, longTermDebt=95183000000, capitalLeaseObligationsNonCurrent=0,
    deferredRevenueNonCurrent=0, deferredTaxLiabilitiesNonCurrent=0, otherNonCurrentLiabilities=49117000000,
    totalNonCurrentLiabilities=144300000000, otherLiabilities=0, capitalLeaseObligations=0,
    totalLiabilities=290437000000, treasuryStock=0, preferredStock=0, commonStock=70956000000,
    retainedEarnings=-9620000000, additionalPaidInCapital=0,
    accumulatedOtherComprehensiveIncomeLoss=-11440000000, otherTotalStockholdersEquity=0,
    totalStockholdersEquity=62146000000, totalEquity=62146000000, minorityInterest=0,
    totalLiabilitiesAndTotalEquity=352583000000, totalInvestments=58751000000,
    totalDebt=124183000000, netDebt=94218000000
)
dummy_cash_flow = FMPCashFlowStatement(
    date="2023-09-30", symbol="AAPL", reportedCurrency="USD", cik="0000320193",
    filingDate="2023-11-03", acceptedDate="2023-11-02", period="FY",
    netIncome=96995000000, depreciationAndAmortization=11519000000,
    deferredIncomeTax=-224000000, stockBasedCompensation=10978000000,

    changeInWorkingCapital=-933000000, accountsReceivables=-409000000,
    inventory=1440000000, accountsPayables=1990000000, otherWorkingCapital=-2834000000,
    otherNonCashItems=0, netCashProvidedByOperatingActivities=110543000000,
    investmentsInPropertyPlantAndEquipment=-10959000000, acquisitionsNet=0,
    purchasesOfInvestments=-19794000000, salesMaturitiesOfInvestments=23746000000,
    otherInvestingActivities=122000000, netCashProvidedByInvestingActivities=-7885000000,
    netDebtIssuance=0, longTermNetDebtIssuance=0, shortTermNetDebtIssuance=0,
    netStockIssuance=0, netCommonStockIssuance=0, commonStockIssuance=0,
    commonStockRepurchased=-77550000000, netPreferredStockIssuance=0, netDividendsPaid=-15049000000,
    commonDividendsPaid=0, preferredDividendsPaid=0, otherFinancingActivities=-9332000000,
    netCashProvidedByFinancingActivities=-108456000000, effectOfForexChangesOnCash=-402000000,
    netChangeInCash=-6200000000, cashAtEndOfPeriod=29965000000,
    cashAtBeginningOfPeriod=36165000000, operatingCashFlow=110543000000,
    capitalExpenditure=10959000000, freeCashFlow=99584000000, incomeTaxesPaid=18490000000,
    interestPaid=4965000000
)
dummy_financials = FinancialData(
    id="1", companyId="1", year=2023, period="FY",
    data=FMPFinancialStatements(incomeStatement=dummy_income_statement, balanceSheet=dummy_balance_sheet, cashFlow=dummy_cash_flow),
    createdAt=datetime.now(), updatedAt=datetime.now()
)
dummy_analysis_result = AnalysisResult(
    id="1", companyId="1", templateId="1", score=85,
    insights=AnalysisInsights(summary="Strong buy.", strengths=["Cash flow"], weaknesses=[], opportunities=[], risks=[], recommendation="BUY"),
    metricScores=MetricScores(profitability=90, growth=80, balanceSheet=85, capitalAllocation=88, valuation=70, overall=85),
    createdAt=datetime.now(), updatedAt=datetime.now()
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
    return BulkAnalysisJob(id=job_id, status="COMPLETED", progress=1.0, createdAt=datetime.now(), updatedAt=datetime.now())


@router.post("/analysis/bulk", response_model=BulkAnalysisJob)
def post_bulk_analysis(request: BulkAnalysisRequest):
    return BulkAnalysisJob(id="new_job_id", status="PENDING", progress=0.0, createdAt=datetime.now(), updatedAt=datetime.now())


app.include_router(router)
