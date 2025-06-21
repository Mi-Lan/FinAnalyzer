import pytest
import respx
from httpx import Response, AsyncClient

from data_adapter.config import ProviderSettings
from data_adapter.exceptions import APIError
from data_adapter.providers.fmp.adapter import FMPAdapter
from data_adapter.providers.fmp.models import IncomeStatement
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