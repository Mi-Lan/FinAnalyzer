import pytest
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from data_adapter.async_processor import AsyncProcessor
from data_adapter.database import DatabaseManager

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

# --- Test Configuration ---
TEST_TICKERS = ["MSFT", "GOOGL", "META"]

# --- Helper Functions ---
def check_env_vars():
    """Check if necessary environment variables are set."""
    db_url = os.getenv("DATABASE_URL")
    fmp_api_key = os.getenv("FMP_API_KEY")
    if not db_url or not fmp_api_key:
        pytest.skip("Skipping integration test: DATABASE_URL and FMP_API_KEY must be set in .env file")

# --- Test Suite ---
class TestAsyncProcessor:
    """
    Test suite for the AsyncProcessor.
    """

    @pytest.fixture(scope="module")
    async def db_manager(self):
        """Fixture to provide a DatabaseManager instance for the module."""
        check_env_vars()
        db_url = os.getenv("DATABASE_URL")
        manager = DatabaseManager(db_url)
        await manager.connect()
        yield manager
        await manager.disconnect()

    @pytest.fixture(scope="module")
    def processor(self) -> AsyncProcessor:
        """Fixture to provide an AsyncProcessor instance."""
        check_env_vars()
        from data_adapter.config import settings
        from data_adapter.config import ProviderSettings
        settings.data_providers["fmp"] = ProviderSettings(api_key=os.getenv("FMP_API_KEY"))
        return AsyncProcessor(concurrency_limit=5)

    async def test_fetch_and_store_multiple_tickers(self, processor: AsyncProcessor, db_manager: DatabaseManager):
        """
        Test fetching and storing data for multiple tickers in parallel.
        """
        print(f"\\n--- Testing parallel fetch_and_store for tickers: {TEST_TICKERS} ---")
        
        # Action
        results = await processor.fetch_and_store_for_tickers(
            tickers=TEST_TICKERS,
            years=[2023],
            periods=['annual']
        )
        
        # Verification
        assert results is not None
        assert len(results) == len(TEST_TICKERS)
        
        for ticker in TEST_TICKERS:
            assert ticker in results
            assert "income-statement" in results[ticker]
            assert len(results[ticker]["income-statement"]) > 0
        
        print(f"--- Successfully fetched and stored data for {len(TEST_TICKERS)} tickers ---")

    async def test_get_stored_data_multiple_tickers(self, processor: AsyncProcessor, db_manager: DatabaseManager):
        """
        Test retrieving stored data for multiple tickers in parallel.
        """
        # First, ensure data is stored
        await self.test_fetch_and_store_multiple_tickers(processor, db_manager)

        print(f"\\n--- Testing parallel get_stored_data for tickers: {TEST_TICKERS} ---")
        
        # Action
        stored_data = await processor.get_stored_data_for_tickers(TEST_TICKERS)
        
        # Verification
        assert stored_data is not None
        assert len(stored_data) == len(TEST_TICKERS)
        
        for ticker in TEST_TICKERS:
            assert ticker in stored_data
            assert stored_data[ticker] is not None
            company_data = stored_data[ticker].get("company")
            financial_data = stored_data[ticker].get("financial_data")
            assert company_data["ticker"] == ticker
            assert financial_data is not None and len(financial_data) > 0

        print(f"--- Successfully retrieved data for {len(TEST_TICKERS)} tickers ---")

# To run this test:
# 1. Make sure your .env file is set up correctly.
# 2. From `packages/data-adapter`, run:
#    poetry run pytest tests/test_async_processor.py -s -v 