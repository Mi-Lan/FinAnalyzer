import asyncio
import os
import pytest
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables from .env file
load_dotenv()

from data_adapter.factory import get_adapter
from data_adapter.config import ProviderSettings
from data_adapter.providers.fmp.storage_adapter import StorageEnabledFMPAdapter
from data_adapter.database import DatabaseManager

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

# --- Test Configuration ---
TEST_TICKER = "AAPL"
FMP_PROVIDER_NAME = "fmp"

# --- Helper Functions ---
def check_env_vars():
    """Check if necessary environment variables are set."""
    db_url = os.getenv("DATABASE_URL")
    fmp_api_key = os.getenv("FMP_API_KEY")
    if not db_url or not fmp_api_key:
        pytest.skip("Skipping integration test: DATABASE_URL and FMP_API_KEY must be set in .env file")
    return db_url, fmp_api_key

# --- Test Suite ---

class TestStorageIntegration:
    """
    Test suite for end-to-end data fetching and storage integration.
    """

    @pytest.fixture(scope="function")
    async def db_manager(self):
        """Fixture to provide a connected DatabaseManager instance."""
        db_url, _ = check_env_vars()
        manager = DatabaseManager(db_url)
        await manager.connect()
        yield manager
        await manager.disconnect()

    @pytest.fixture(scope="function")
    def storage_adapter(self) -> StorageEnabledFMPAdapter:
        """Fixture to provide a storage-enabled FMP adapter."""
        check_env_vars()
        # Set the API key in the settings for the factory
        from data_adapter.config import settings
        
        # Correctly create a ProviderSettings instance
        settings.data_providers[FMP_PROVIDER_NAME] = ProviderSettings(
            api_key=os.getenv("FMP_API_KEY")
        )
        
        adapter = get_adapter(FMP_PROVIDER_NAME, enable_storage=True, use_enhanced_parser=True)
        return adapter

    async def test_fetch_and_store_financials(self, storage_adapter: StorageEnabledFMPAdapter, db_manager: DatabaseManager):
        """
        Test fetching financial data from FMP and storing it in the database.
        """
        print(f"\n--- Testing fetch_and_store_company_financials for {TEST_TICKER} ---")
        
        # Action: Fetch and store data
        results = await storage_adapter.fetch_and_store_company_financials(
            ticker=TEST_TICKER,
            years=[2023], # Limit to one year for faster testing
            periods=['annual']
        )
        
        # Verification
        assert results is not None, "fetch_and_store should return results"
        assert "income-statement" in results
        assert "balance-sheet-statement" in results
        assert "cash-flow-statement" in results
        
        # Check that we have stored IDs
        assert len(results["income-statement"]) > 0, "Should have stored income statements"
        assert len(results["balance-sheet-statement"]) > 0, "Should have stored balance sheets"
        assert len(results["cash-flow-statement"]) > 0, "Should have stored cash flows"
        
        print(f"--- Successfully fetched and stored data for {TEST_TICKER} ---")

    async def test_get_stored_data(self, storage_adapter: StorageEnabledFMPAdapter, db_manager: DatabaseManager):
        """
        Test retrieving stored financial data from the database.
        """
        print(f"\n--- First, ensuring data is stored for {TEST_TICKER} ---")
        await storage_adapter.fetch_and_store_company_financials(
            ticker=TEST_TICKER,
            years=[2023],
            periods=['annual']
        )

        print(f"\n--- Testing get_stored_company_data for {TEST_TICKER} ---")

        # Action: Retrieve the stored data
        stored_data = await storage_adapter.get_stored_company_data(ticker=TEST_TICKER)

        # Verification
        assert stored_data is not None, "Should retrieve stored data"

        # Check company data
        company = stored_data.get("company")
        assert company is not None, "Company data should be present"
        assert company["ticker"] == TEST_TICKER

        # Check financial data
        financial_data = stored_data.get("financial_data")
        assert financial_data is not None and len(financial_data) > 0, "Financial data should be present"

        # Only check records with period == 'FY' (ignore SEC filings)
        fy_records = [r for r in financial_data if r.get("period") == "FY"]
        record_2023 = next((r for r in fy_records if r.get("year") == 2023), None)
        assert record_2023 is not None, "Should have a record for 2023 with period 'FY'"
        assert record_2023["period"] == "FY"

    async def test_fetch_and_store_sec_filings(self, storage_adapter: StorageEnabledFMPAdapter, db_manager: DatabaseManager):
        """
        Test fetching SEC filings and storing them in the database.
        """
        print(f"\n--- Testing fetch_and_store_sec_filings for {TEST_TICKER} ---")

        from_date = "2023-01-01"
        to_date = "2023-03-31"

        stored_ids = await storage_adapter.fetch_and_store_sec_filings(
            ticker=TEST_TICKER,
            from_date=from_date,
            to_date=to_date
        )

        # If no new filings were stored, check that filings exist in the DB for this period
        if not stored_ids:
            company = await db_manager.get_company_by_ticker(TEST_TICKER)
            assert company is not None, "Company should exist"
            filings = await db_manager.get_financial_data(company_id=company["id"])
            sec_filings = [f for f in filings if f["period"].startswith("FILING_")]
            assert len(sec_filings) > 0, "SEC filings should exist in the DB for this ticker and period"
        else:
            assert len(stored_ids) > 0, "Should have stored some SEC filings"

# To run this test:
# 1. Ensure you have a .env file in `packages/data-adapter` with:
#    DATABASE_URL=postgresql://user:password@localhost:5432/findb
#    FMP_API_KEY=your_fmp_api_key
# 2. Make sure your PostgreSQL container is running.
# 3. From the `packages/data-adapter` directory, run:
#    poetry run pytest tests/test_storage_integration.py -s -v 