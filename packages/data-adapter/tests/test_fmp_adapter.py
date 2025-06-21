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
    
    # Test data structure and types without checking specific values
    statement = data[0]
    
    # Test that base fields exist and have correct types
    assert isinstance(statement.symbol, str) and len(statement.symbol) > 0
    assert isinstance(statement.date, str) and len(statement.date) > 0
    assert isinstance(statement.fiscal_year, str) and len(statement.fiscal_year) > 0
    assert isinstance(statement.period, str) and len(statement.period) > 0
    assert isinstance(statement.cik, str) and len(statement.cik) > 0
    assert isinstance(statement.filing_date, str) and len(statement.filing_date) > 0
    assert isinstance(statement.accepted_date, str) and len(statement.accepted_date) > 0
    assert isinstance(statement.reported_currency, str) and len(statement.reported_currency) > 0
    
    # Test key financial fields are present and numeric
    assert isinstance(statement.revenue, (int, float))
    assert isinstance(statement.operating_income, (int, float))
    assert isinstance(statement.net_income, (int, float))
    assert isinstance(statement.gross_profit, (int, float))
    assert isinstance(statement.ebitda, (int, float))
    assert isinstance(statement.eps, (int, float))
    assert isinstance(statement.epsdiluted, (int, float))
    assert isinstance(statement.cost_of_revenue, (int, float))
    assert isinstance(statement.research_and_development_expenses, (int, float))
    assert isinstance(statement.operating_expenses, (int, float))


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
    
    # Test data structure and types without checking specific values
    statement = data[0]
    
    # Test that base fields exist and have correct types
    assert isinstance(statement.symbol, str) and len(statement.symbol) > 0
    assert isinstance(statement.date, str) and len(statement.date) > 0
    assert isinstance(statement.fiscal_year, str) and len(statement.fiscal_year) > 0
    assert isinstance(statement.period, str) and len(statement.period) > 0
    assert isinstance(statement.cik, str) and len(statement.cik) > 0
    assert isinstance(statement.filing_date, str) and len(statement.filing_date) > 0
    assert isinstance(statement.accepted_date, str) and len(statement.accepted_date) > 0
    assert isinstance(statement.reported_currency, str) and len(statement.reported_currency) > 0
    
    # Test key balance sheet structure fields are present and numeric
    assert isinstance(statement.total_assets, (int, float))
    assert isinstance(statement.total_liabilities, (int, float))
    assert isinstance(statement.total_equity, (int, float))
    
    # Test current assets section
    assert isinstance(statement.cash_and_cash_equivalents, (int, float))
    assert isinstance(statement.total_current_assets, (int, float))
    assert isinstance(statement.inventory, (int, float))
    assert isinstance(statement.short_term_investments, (int, float))
    assert isinstance(statement.net_receivables, (int, float))
    
    # Test current liabilities section
    assert isinstance(statement.total_current_liabilities, (int, float))
    assert isinstance(statement.short_term_debt, (int, float))
    assert isinstance(statement.account_payables, (int, float))
    
    # Test equity section
    assert isinstance(statement.common_stock, (int, float))
    assert isinstance(statement.retained_earnings, (int, float))
    assert isinstance(statement.total_stockholders_equity, (int, float))
    
    # Test additional metrics
    assert isinstance(statement.total_debt, (int, float))
    assert isinstance(statement.net_debt, (int, float))
    
    # Verify balance sheet equation: Assets = Liabilities + Equity (business logic validation)
    assert abs(statement.total_assets - (statement.total_liabilities + statement.total_equity)) < 1000


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
    
    # Test data structure and types without checking specific values
    statement = data[0]
    
    # Test that base fields exist and have correct types
    assert isinstance(statement.symbol, str) and len(statement.symbol) > 0
    assert isinstance(statement.date, str) and len(statement.date) > 0
    assert isinstance(statement.fiscal_year, str) and len(statement.fiscal_year) > 0
    assert isinstance(statement.period, str) and len(statement.period) > 0
    assert isinstance(statement.cik, str) and len(statement.cik) > 0
    assert isinstance(statement.filing_date, str) and len(statement.filing_date) > 0
    assert isinstance(statement.accepted_date, str) and len(statement.accepted_date) > 0
    assert isinstance(statement.reported_currency, str) and len(statement.reported_currency) > 0
    
    # Test operating activities section
    assert isinstance(statement.net_income, (int, float))
    assert isinstance(statement.net_cash_provided_by_operating_activities, (int, float))
    assert isinstance(statement.depreciation_and_amortization, (int, float))
    assert isinstance(statement.change_in_working_capital, (int, float))
    assert isinstance(statement.stock_based_compensation, (int, float))
    
    # Test investing activities section
    assert isinstance(statement.net_cash_provided_by_investing_activities, (int, float))
    assert isinstance(statement.capital_expenditure, (int, float))
    assert isinstance(statement.investments_in_property_plant_and_equipment, (int, float))
    assert isinstance(statement.purchases_of_investments, (int, float))
    
    # Test financing activities section
    assert isinstance(statement.net_cash_provided_by_financing_activities, (int, float))
    assert isinstance(statement.net_dividends_paid, (int, float))
    assert isinstance(statement.common_stock_repurchased, (int, float))
    assert isinstance(statement.net_debt_issuance, (int, float))
    
    # Test summary metrics
    assert isinstance(statement.free_cash_flow, (int, float))
    assert isinstance(statement.operating_cash_flow, (int, float))
    assert isinstance(statement.net_change_in_cash, (int, float))
    assert isinstance(statement.cash_at_end_of_period, (int, float))
    assert isinstance(statement.cash_at_beginning_of_period, (int, float))
    
    # Verify cash flow logic: Beginning Cash + Net Change = Ending Cash (business logic validation)
    expected_ending_cash = statement.cash_at_beginning_of_period + statement.net_change_in_cash
    assert abs(statement.cash_at_end_of_period - expected_ending_cash) < 1000


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