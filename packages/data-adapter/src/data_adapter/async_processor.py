import asyncio
from typing import List, Dict, Any, Coroutine, Tuple

from data_adapter.factory import get_adapter
from data_adapter.providers.fmp.storage_adapter import StorageEnabledFMPAdapter
from data_adapter.logging import get_logger

logger = get_logger(__name__)

# --- Configuration ---
DEFAULT_CONCURRENCY_LIMIT = 10

class AsyncProcessor:
    """
    Handles asynchronous processing of data ingestion tasks.
    """
    def __init__(self, concurrency_limit: int = DEFAULT_CONCURRENCY_LIMIT):
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        # We no longer create a shared adapter here
    
    def _get_adapter(self) -> StorageEnabledFMPAdapter:
        """Creates a new instance of the storage adapter."""
        return get_adapter("fmp", enable_storage=True)

    async def _worker(self, coro_func, *args, **kwargs) -> Any:
        """
        A worker that creates a new adapter and executes a coroutine.
        """
        async with self.semaphore:
            # Create a new adapter for each task
            adapter = self._get_adapter()
            # The coroutine function should be a method of the adapter
            coro = coro_func(adapter, *args, **kwargs)
            return await coro

    async def run_tasks(self, tasks_with_params: List[Tuple[callable, List, Dict]]) -> List[Any]:
        """
        Run a list of tasks concurrently, where each task is defined by
        a function and its arguments.
        """
        tasks = [
            self._worker(func, *args, **kwargs) 
            for func, args, kwargs in tasks_with_params
        ]
        results = await asyncio.gather(*tasks)
        return results

    async def fetch_and_store_for_tickers(
        self,
        tickers: List[str],
        years: List[int] = None,
        periods: List[str] = None
    ) -> Dict[str, Dict[str, List[str]]]:
        """
        Fetch and store financial data for a list of tickers in parallel.
        """
        
        async def task_func(adapter, ticker, years, periods):
            return await adapter.fetch_and_store_company_financials(
                ticker=ticker, years=years, periods=periods
            )
            
        tasks_with_params = [
            (task_func, [ticker, years, periods], {}) for ticker in tickers
        ]
        
        logger.info(f"Starting parallel fetch for {len(tickers)} tickers.")
        
        results = await self.run_tasks(tasks_with_params)
        
        # Combine results into a dictionary keyed by ticker
        ticker_results = {ticker: result for ticker, result in zip(tickers, results)}
        
        logger.info(f"Completed parallel fetch for {len(tickers)} tickers.")
        return ticker_results

    async def get_stored_data_for_tickers(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve stored financial data for a list of tickers in parallel.
        """
        
        async def task_func(adapter, ticker):
            return await adapter.get_stored_company_data(ticker)

        tasks_with_params = [
            (task_func, [ticker], {}) for ticker in tickers
        ]
        
        logger.info(f"Starting parallel data retrieval for {len(tickers)} tickers.")
        
        results = await self.run_tasks(tasks_with_params)
        
        # Combine results into a dictionary keyed by ticker
        ticker_results = {ticker: result for ticker, result in zip(tickers, results)}
        
        logger.info(f"Completed parallel data retrieval for {len(tickers)} tickers.")
        return ticker_results

    async def fetch_and_store_sec_filings_for_tickers(
        self,
        tickers: List[str],
        from_date: str,
        to_date: str
    ) -> Dict[str, List[str]]:
        """
        Fetch and store SEC filings for a list of tickers in parallel.
        """
        
        async def task_func(adapter, ticker, from_date, to_date):
            return await adapter.fetch_and_store_sec_filings(
                ticker=ticker, from_date=from_date, to_date=to_date
            )
            
        tasks_with_params = [
            (task_func, [ticker, from_date, to_date], {}) for ticker in tickers
        ]
        
        logger.info(f"Starting parallel SEC filing fetch for {len(tickers)} tickers.")
        
        results = await self.run_tasks(tasks_with_params)
        
        # Combine results into a dictionary keyed by ticker
        ticker_results = {ticker: result for ticker, result in zip(tickers, results)}
        
        logger.info(f"Completed parallel SEC filing fetch for {len(tickers)} tickers.")
        return ticker_results

async def main():
    """
    Main function to demonstrate and test the AsyncProcessor.
    """
    processor = AsyncProcessor(concurrency_limit=5)
    
    # --- Example Usage ---
    test_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    
    # 1. Fetch and store data in parallel
    fetch_results = await processor.fetch_and_store_for_tickers(
        tickers=test_tickers,
        years=[2023],
        periods=['annual']
    )
    
    print("\\n--- Fetch and Store Results ---")
    for ticker, result in fetch_results.items():
        print(f"  {ticker}: {result}")
        
    # 2. Retrieve stored data in parallel
    stored_data = await processor.get_stored_data_for_tickers(test_tickers)
    
    print("\\n--- Retrieved Stored Data ---")
    for ticker, data in stored_data.items():
        if data:
            print(f"  {ticker}: Found {len(data.get('financial_data', []))} financial records.")
        else:
            print(f"  {ticker}: No data found.")

if __name__ == "__main__":
    # Ensure you have a .env file with DATABASE_URL and FMP_API_KEY
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(main()) 