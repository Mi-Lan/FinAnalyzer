import pytest
import respx
from httpx import Response, AsyncClient

from data_adapter.config import ProviderSettings
from data_adapter.exceptions import APIError
from data_adapter.providers.fmp.adapter import FMPAdapter
from data_adapter.providers.fmp.models import IncomeStatement, BalanceSheetStatement, CashFlowStatement
from data_adapter.providers.fmp.parser import FMPParser

# Mock objects for testing
mock_provider_settings = ProviderSettings(api_key="test_key")
mock_parser = FMPParser()


@pytest.mark.asyncio
@respx.mock
async def test_fetch_data_success():
    """
    Test the successful fetching and parsing of data with the FMP adapter.
    """
    fmp_api_route = respx.get(
        "https://financialmodelingprep.com/stable/income-statement"
    ).mock(
        return_value=Response(
            200,
            json=[
                {
                    "date": "2024-09-28",
                    "symbol": "AAPL",
                    "reportedCurrency": "USD",
                    "cik": "0000320193",
                    "filingDate": "2024-11-01",
                    "acceptedDate": "2024-11-01 06:01:36",
                    "fiscalYear": "2024",
                    "period": "FY",
                    "revenue": 391035000000,
                    "costOfRevenue": 210352000000,
                    "grossProfit": 180683000000,
                    "researchAndDevelopmentExpenses": 31370000000,
                    "generalAndAdministrativeExpenses": 0,
                    "sellingAndMarketingExpenses": 0,
                    "sellingGeneralAndAdministrativeExpenses": 26097000000,
                    "otherExpenses": 0,
                    "operatingExpenses": 57467000000,
                    "costAndExpenses": 267819000000,
                    "netInterestIncome": 0,
                    "interestIncome": 0,
                    "interestExpense": 0,
                    "depreciationAndAmortization": 11445000000,
                    "ebitda": 134661000000,
                    "ebit": 123216000000,
                    "nonOperatingIncomeExcludingInterest": 0,
                    "operatingIncome": 123216000000,
                    "totalOtherIncomeExpensesNet": 269000000,
                    "incomeBeforeTax": 123485000000,
                    "incomeTaxExpense": 29749000000,
                    "netIncomeFromContinuingOperations": 93736000000,
                    "netIncomeFromDiscontinuedOperations": 0,
                    "otherAdjustmentsToNetIncome": 0,
                    "netIncome": 93736000000,
                    "netIncomeDeductions": 0,
                    "bottomLineNetIncome": 93736000000,
                    "eps": 6.11,
                    "epsDiluted": 6.08,
                    "weightedAverageShsOut": 15343783000,
                    "weightedAverageShsOutDil": 15408095000
                }
            ],
        )
    )

    async with AsyncClient() as client:
        adapter = FMPAdapter(client, mock_provider_settings, mock_parser)
        data = await adapter.fetch_data(
            "income-statement", {"symbol": "AAPL", "period": "annual"}
        )

    assert fmp_api_route.called
    assert len(data) == 1
    assert isinstance(data[0], IncomeStatement)
    assert data[0].symbol == "AAPL"
    assert data[0].revenue == 391035000000
    assert data[0].operating_income == 123216000000


@pytest.mark.asyncio
@respx.mock
async def test_fetch_balance_sheet_success():
    """
    Test the successful fetching and parsing of balance sheet data with the FMP adapter.
    """
    fmp_api_route = respx.get(
        "https://financialmodelingprep.com/stable/balance-sheet-statement"
    ).mock(
        return_value=Response(
            200,
            json=[
                {
                    "date": "2024-09-28",
                    "symbol": "AAPL",
                    "reportedCurrency": "USD",
                    "cik": "0000320193",
                    "filingDate": "2024-11-01",
                    "acceptedDate": "2024-11-01 06:01:36",
                    "fiscalYear": "2024",
                    "period": "FY",
                    "cashAndCashEquivalents": 29943000000,
                    "shortTermInvestments": 35228000000,
                    "cashAndShortTermInvestments": 65171000000,
                    "netReceivables": 66243000000,
                    "accountsReceivables": 33410000000,
                    "otherReceivables": 32833000000,
                    "inventory": 7286000000,
                    "prepaids": 0,
                    "otherCurrentAssets": 14287000000,
                    "totalCurrentAssets": 152987000000,
                    "propertyPlantEquipmentNet": 45680000000,
                    "goodwill": 0,
                    "intangibleAssets": 0,
                    "goodwillAndIntangibleAssets": 0,
                    "longTermInvestments": 91479000000,
                    "taxAssets": 19499000000,
                    "otherNonCurrentAssets": 55335000000,
                    "totalNonCurrentAssets": 211993000000,
                    "otherAssets": 0,
                    "totalAssets": 364980000000,
                    "totalPayables": 95561000000,
                    "accountPayables": 68960000000,
                    "otherPayables": 26601000000,
                    "accruedExpenses": 0,
                    "shortTermDebt": 20879000000,
                    "capitalLeaseObligationsCurrent": 1632000000,
                    "taxPayables": 26601000000,
                    "deferredRevenue": 8249000000,
                    "otherCurrentLiabilities": 50071000000,
                    "totalCurrentLiabilities": 176392000000,
                    "longTermDebt": 85750000000,
                    "deferredRevenueNonCurrent": 10798000000,
                    "deferredTaxLiabilitiesNonCurrent": 0,
                    "otherNonCurrentLiabilities": 35090000000,
                    "totalNonCurrentLiabilities": 131638000000,
                    "otherLiabilities": 0,
                    "capitalLeaseObligations": 12430000000,
                    "totalLiabilities": 308030000000,
                    "treasuryStock": 0,
                    "preferredStock": 0,
                    "commonStock": 83276000000,
                    "retainedEarnings": -19154000000,
                    "additionalPaidInCapital": 0,
                    "accumulatedOtherComprehensiveIncomeLoss": -7172000000,
                    "otherTotalStockholdersEquity": 0,
                    "totalStockholdersEquity": 56950000000,
                    "totalEquity": 56950000000,
                    "minorityInterest": 0,
                    "totalLiabilitiesAndTotalEquity": 364980000000,
                    "totalInvestments": 126707000000,
                    "totalDebt": 106629000000,
                    "netDebt": 76686000000
                }
            ],
        )
    )

    async with AsyncClient() as client:
        adapter = FMPAdapter(client, mock_provider_settings, mock_parser)
        data = await adapter.fetch_data(
            "balance-sheet-statement", {"symbol": "AAPL", "period": "annual"}
        )

    assert fmp_api_route.called
    assert len(data) == 1
    assert isinstance(data[0], BalanceSheetStatement)
    assert data[0].symbol == "AAPL"
    assert data[0].total_assets == 364980000000
    assert data[0].total_liabilities == 308030000000
    assert data[0].total_equity == 56950000000
    assert data[0].cash_and_cash_equivalents == 29943000000
    assert data[0].short_term_investments == 35228000000
    assert data[0].total_debt == 106629000000
    assert data[0].net_debt == 76686000000


@pytest.mark.asyncio
@respx.mock
async def test_fetch_cash_flow_success():
    """
    Test the successful fetching and parsing of cash flow data with the FMP adapter.
    """
    fmp_api_route = respx.get(
        "https://financialmodelingprep.com/stable/cash-flow-statement"
    ).mock(
        return_value=Response(
            200,
            json=[
                {
                    "date": "2024-09-28",
                    "symbol": "AAPL",
                    "reportedCurrency": "USD",
                    "cik": "0000320193",
                    "filingDate": "2024-11-01",
                    "acceptedDate": "2024-11-01 06:01:36",
                    "fiscalYear": "2024",
                    "period": "FY",
                    "netIncome": 93736000000,
                    "depreciationAndAmortization": 11445000000,
                    "deferredIncomeTax": 0,
                    "stockBasedCompensation": 11688000000,
                    "changeInWorkingCapital": 3651000000,
                    "accountsReceivables": -5144000000,
                    "inventory": -1046000000,
                    "accountsPayables": 6020000000,
                    "otherWorkingCapital": 3821000000,
                    "otherNonCashItems": -2266000000,
                    "netCashProvidedByOperatingActivities": 118254000000,
                    "investmentsInPropertyPlantAndEquipment": -9447000000,
                    "acquisitionsNet": 0,
                    "purchasesOfInvestments": -48656000000,
                    "salesMaturitiesOfInvestments": 62346000000,
                    "otherInvestingActivities": -1308000000,
                    "netCashProvidedByInvestingActivities": 2935000000,
                    "netDebtIssuance": -5998000000,
                    "longTermNetDebtIssuance": -9958000000,
                    "shortTermNetDebtIssuance": 3960000000,
                    "netStockIssuance": -94949000000,
                    "netCommonStockIssuance": -94949000000,
                    "commonStockIssuance": 0,
                    "commonStockRepurchased": -94949000000,
                    "netPreferredStockIssuance": 0,
                    "netDividendsPaid": -15234000000,
                    "commonDividendsPaid": -15234000000,
                    "preferredDividendsPaid": 0,
                    "otherFinancingActivities": -5802000000,
                    "netCashProvidedByFinancingActivities": -121983000000,
                    "effectOfForexChangesOnCash": 0,
                    "netChangeInCash": -794000000,
                    "cashAtEndOfPeriod": 29943000000,
                    "cashAtBeginningOfPeriod": 30737000000,
                    "operatingCashFlow": 118254000000,
                    "capitalExpenditure": -9447000000,
                    "freeCashFlow": 108807000000,
                    "incomeTaxesPaid": 26102000000,
                    "interestPaid": 0
                }
            ],
        )
    )

    async with AsyncClient() as client:
        adapter = FMPAdapter(client, mock_provider_settings, mock_parser)
        data = await adapter.fetch_data(
            "cash-flow-statement", {"symbol": "AAPL", "period": "annual"}
        )

    assert fmp_api_route.called
    assert len(data) == 1
    assert isinstance(data[0], CashFlowStatement)
    assert data[0].symbol == "AAPL"
    assert data[0].net_income == 93736000000
    assert data[0].net_cash_provided_by_operating_activities == 118254000000
    assert data[0].net_cash_provided_by_investing_activities == 2935000000
    assert data[0].net_cash_provided_by_financing_activities == -121983000000
    assert data[0].free_cash_flow == 108807000000
    assert data[0].capital_expenditure == -9447000000


@pytest.mark.asyncio
async def test_fetch_data_api_error():
    """
    Test that an APIError is raised when the FMP API returns an error.
    """
    @respx.mock
    async def test_call():
        respx.get("https://financialmodelingprep.com/stable/income-statement").mock(
            return_value=Response(500)
        )
        async with AsyncClient() as client:
            adapter = FMPAdapter(client, mock_provider_settings, mock_parser)
            with pytest.raises(APIError):
                await adapter.fetch_data(
                    "income-statement", {"symbol": "AAPL", "period": "annual"}
                )

    await test_call() 