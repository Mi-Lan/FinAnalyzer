from typing import Any, Dict, List, Optional, TYPE_CHECKING
from datetime import datetime, timezone
import re

from data_adapter.providers.fmp.adapter import FMPAdapter
from data_adapter.providers.fmp.models import FinancialStatement, IncomeStatement, BalanceSheetStatement, CashFlowStatement, SECFiling
from data_adapter.logging import get_logger

if TYPE_CHECKING:
    from data_adapter.database import DatabaseManager

logger = get_logger(__name__)


class StorageEnabledFMPAdapter(FMPAdapter):
    """
    Extended FMP adapter that adds database storage capabilities.
    """
    
    def __init__(self, client, settings, parser, database_manager: "DatabaseManager"):
        super().__init__(client, settings, parser)
        self.db_manager = database_manager
    
    def _extract_period_info(self, financial_statement: FinancialStatement) -> tuple[int, str]:
        """
        Extract year and period from a financial statement.
        Returns (year, period) tuple.
        """
        # Extract year from fiscal_year or calendar_year
        year = int(financial_statement.fiscal_year)
        
        # Determine period from the period field
        period = financial_statement.period.upper()
        
        # Normalize period names
        if period in ['FY', 'ANNUAL']:
            period = 'FY'
        elif period.startswith('Q'):
            period = period  # Keep Q1, Q2, Q3, Q4 as is
        else:
            # Try to parse from other formats
            period_mapping = {
                'Q1': 'Q1', 'Q2': 'Q2', 'Q3': 'Q3', 'Q4': 'Q4',
                'FIRST': 'Q1', 'SECOND': 'Q2', 'THIRD': 'Q3', 'FOURTH': 'Q4'
            }
            period = period_mapping.get(period, period)
        
        return year, period
    
    def _prepare_financial_data(self, statements: List[FinancialStatement]) -> Dict[str, Any]:
        """
        Prepare financial statements for storage in the database.
        Organizes statements by type and converts to dict format.
        """
        data = {
            "income_statements": [],
            "balance_sheets": [],
            "cash_flows": [],
            "metadata": {
                "stored_at": datetime.now(timezone.utc).isoformat(),
                "source": "fmp"
            }
        }
        
        for statement in statements:
            statement_dict = statement.model_dump(by_alias=True)
            
            if isinstance(statement, IncomeStatement):
                data["income_statements"].append(statement_dict)
            elif isinstance(statement, BalanceSheetStatement):
                data["balance_sheets"].append(statement_dict)
            elif isinstance(statement, CashFlowStatement):
                data["cash_flows"].append(statement_dict)
            else:
                # Generic financial statement - add to a general category
                if "general_statements" not in data:
                    data["general_statements"] = []
                data["general_statements"].append(statement_dict)
        
        return data
    
    async def fetch_and_store_data(
        self, 
        endpoint: str, 
        params: Dict[str, Any],
        company_name: str = None,
        sector: str = None,
        industry: str = None
    ) -> List[str]:
        """
        Fetch data from FMP API and store it in the database.
        Returns list of financial data IDs that were stored.
        """
        # Fetch data using the parent class method
        statements = await self.fetch_data(endpoint, params)
        
        if not statements:
            logger.warning(f"No data received from endpoint {endpoint} with params {params}")
            return []
        
        # Group statements by ticker, year, and period
        grouped_statements = {}
        
        for statement in statements:
            ticker = statement.symbol
            year, period = self._extract_period_info(statement)
            
            key = (ticker, year, period)
            if key not in grouped_statements:
                grouped_statements[key] = []
            grouped_statements[key].append(statement)
        
        stored_ids = []
        
        # Store each group in the database
        for (ticker, year, period), group_statements in grouped_statements.items():
            try:
                # Ensure company exists
                company_id = await self.db_manager.ensure_company_exists(
                    ticker=ticker,
                    name=company_name or group_statements[0].symbol,
                    sector=sector,
                    industry=industry
                )
                
                type_mapping = {
                    "income-statement": "Income Statement",
                    "balance-sheet-statement": "Balance Sheet",
                    "cash-flow-statement": "Cash Flow Statement",
                }
                human_readable_type = type_mapping.get(endpoint, endpoint)

                # Prepare financial data for storage
                financial_data_to_add = self._prepare_financial_data(group_statements)
                
                # Store the financial data
                financial_data_id = await self.db_manager.store_financial_data(
                    company_id=company_id,
                    year=year,
                    period=period,
                    type=human_readable_type,
                    financial_statements=financial_data_to_add,
                    merge=True  # Enable merging
                )
                
                stored_ids.append(financial_data_id)
                logger.info(f"Stored financial data for {ticker} {year} {period} (ID: {financial_data_id})")
                
            except Exception as e:
                logger.error(f"Failed to store financial data for {ticker} {year} {period}: {e}")
                continue
        
        return stored_ids
    
    async def fetch_and_store_company_financials(
        self,
        ticker: str,
        years: List[int] = None,
        periods: List[str] = None,
        company_name: str = None,
        sector: str = None,
        industry: str = None,
        max_data_points: int = None
    ) -> Dict[str, List[str]]:
        """
        Fetch and store comprehensive financial data for a company.
        Respects API limits by prioritizing recent years and essential data.
        Returns dict with endpoint names as keys and lists of stored data IDs as values.
        """
        if years is None:
            # Default to last 10 years for comprehensive analysis
            current_year = datetime.now().year
            years = list(range(current_year - 9, current_year + 1))
        
        if periods is None:
            periods = ['annual', 'quarter']  # Both annual and quarterly data
            
        if max_data_points is None:
            max_data_points = self.settings.max_data_points
        
        # Define endpoints first
        endpoints = ['income-statement', 'balance-sheet-statement', 'cash-flow-statement']
        
        # Estimate data points: 3 endpoints × periods × years
        # Annual: ~1 record per endpoint per year
        # Quarter: ~4 records per endpoint per year  
        estimated_annual = len(endpoints) * len([y for y in years]) * 1
        estimated_quarterly = len(endpoints) * len([y for y in years]) * 4
        total_estimated = estimated_annual + (estimated_quarterly if 'quarter' in periods else 0)
        
        logger.info(f"Estimated data points for {ticker}: {total_estimated} (limit: {max_data_points})")
        
        # Apply smart limits if we exceed the threshold
        if total_estimated > max_data_points:
            logger.warning(f"Estimated data points ({total_estimated}) exceeds limit ({max_data_points}). Applying prioritization.")
            # Prioritize: recent years first, annual data over quarterly
            years = self._prioritize_years(years, max_data_points)
            periods = self._prioritize_periods(periods, max_data_points, len(years))
        
        results = {}
        data_points_fetched = 0
        
        for endpoint in endpoints:
            results[endpoint] = []
            
            for period in periods:
                if data_points_fetched >= max_data_points:
                    logger.warning(f"Reached data point limit ({max_data_points}). Stopping fetch for {ticker}")
                    break
                    
                try:
                    params = {
                        'symbol': ticker,
                        'period': period
                    }
                    
                    stored_ids = await self.fetch_and_store_data(
                        endpoint=endpoint,
                        params=params,
                        company_name=company_name,
                        sector=sector,
                        industry=industry
                    )
                    
                    results[endpoint].extend(stored_ids)
                    
                    # Estimate data points fetched (this is approximate)
                    estimated_points = len(years) * (4 if period == 'quarter' else 1)
                    data_points_fetched += estimated_points
                    
                except Exception as e:
                    logger.error(f"Failed to fetch {endpoint} data for {ticker} ({period}): {e}")
                    continue
                    
            if data_points_fetched >= max_data_points:
                break
        
        logger.info(f"Fetched approximately {data_points_fetched} data points for {ticker}")
        return results
    
    def _prioritize_years(self, years: List[int], max_data_points: int) -> List[int]:
        """Prioritize recent years when hitting data limits."""
        # Sort years in descending order (most recent first)
        sorted_years = sorted(years, reverse=True)
        
        # Estimate how many years we can afford (conservative estimate)
        # Assume 3 endpoints × 2 periods × 5 records per period-year = 30 per year
        max_years = min(len(sorted_years), max_data_points // 30)
        max_years = max(1, max_years)  # Always fetch at least 1 year
        
        return sorted_years[:max_years]
    
    def _prioritize_periods(self, periods: List[str], max_data_points: int, num_years: int) -> List[str]:
        """Prioritize annual data over quarterly when hitting limits."""
        if 'annual' in periods and 'quarter' in periods:
            # Check if we can afford both
            # Estimate: 3 endpoints × num_years × (1 annual + 4 quarterly) = 15 per year
            estimated_both = 3 * num_years * 5
            if estimated_both > max_data_points:
                logger.info("Prioritizing annual data over quarterly due to data point limits")
                return ['annual']
        
        return periods
    
    async def fetch_and_store_sec_filings(
        self,
        ticker: str,
        from_date: str,
        to_date: str,
        company_name: str = None,
        sector: str = None,
        industry: str = None,
        max_filings: int = None
    ) -> List[str]:
        """
        Fetch SEC filings for a company within a date range and store them.
        Respects limits by prioritizing 10-K filings over other types.
        """
        if max_filings is None:
            # Reserve some capacity for SEC filings (about 10% of total limit)
            max_filings = max(50, self.settings.max_data_points // 10)
        
        params = {
            'symbol': ticker,
            'from': from_date,
            'to': to_date,
            'page': 0,
            'limit': 1500  # Request up to 1000 filings to get full 10-year history
        }
        
        # Fetch data using the parent class method
        filings = await self.fetch_data("sec-filings-search/symbol", params)
        
        if not filings:
            logger.warning(f"No SEC filings found for {ticker} from {from_date} to {to_date}")
            return []
        
        # Prioritize 10-K filings, then 10-Q, then others
        prioritized_filings = self._prioritize_sec_filings(filings, max_filings)
        
        if len(prioritized_filings) < len(filings):
            logger.info(f"Limited SEC filings for {ticker} from {len(filings)} to {len(prioritized_filings)} due to limits")
            
        # Ensure company exists
        company_id = await self.db_manager.ensure_company_exists(
            ticker=ticker,
            name=company_name or ticker,
            sector=sector,
            industry=industry
        )
        
        stored_ids = []
        for filing in prioritized_filings:
            if isinstance(filing, SECFiling):
                stored_id = await self.db_manager.store_sec_filing(company_id, filing)
                if stored_id:
                    stored_ids.append(stored_id)
        
        logger.info(f"Stored {len(stored_ids)} new SEC filings for {ticker}.")
        return stored_ids
    
    def _prioritize_sec_filings(self, filings: List[SECFiling], max_filings: int) -> List[SECFiling]:
        """
        Prioritize SEC filings by type and recency.
        Priority order: 10-K (annual) > 10-Q (quarterly) > others
        Within each type: most recent first
        """
        if len(filings) <= max_filings:
            return filings
        
        # Separate by filing type
        ten_k_filings = [f for f in filings if f.form == '10-K']
        ten_q_filings = [f for f in filings if f.form == '10-Q']
        other_filings = [f for f in filings if f.form not in ['10-K', '10-Q']]
        
        # Sort each group by filing date (most recent first)
        ten_k_filings.sort(key=lambda x: x.filing_date, reverse=True)
        ten_q_filings.sort(key=lambda x: x.filing_date, reverse=True)
        other_filings.sort(key=lambda x: x.filing_date, reverse=True)
        
        # Allocate filings based on priority
        selected_filings = []
        remaining_capacity = max_filings
        
        # First priority: 10-K filings (keep most important ones)
        if ten_k_filings and remaining_capacity > 0:
            ten_k_count = min(len(ten_k_filings), max(1, remaining_capacity // 2))  # At least 1, up to half capacity
            selected_filings.extend(ten_k_filings[:ten_k_count])
            remaining_capacity -= ten_k_count
        
        # Second priority: 10-Q filings
        if ten_q_filings and remaining_capacity > 0:
            ten_q_count = min(len(ten_q_filings), remaining_capacity // 2)  # Up to half remaining
            selected_filings.extend(ten_q_filings[:ten_q_count])
            remaining_capacity -= ten_q_count
        
        # Third priority: Other filings
        if other_filings and remaining_capacity > 0:
            selected_filings.extend(other_filings[:remaining_capacity])
        
        logger.info(f"Prioritized SEC filings: {len([f for f in selected_filings if f.form == '10-K'])} 10-K, "
                   f"{len([f for f in selected_filings if f.form == '10-Q'])} 10-Q, "
                   f"{len([f for f in selected_filings if f.form not in ['10-K', '10-Q']])} others")
        
        return selected_filings

    async def get_stored_company_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve stored financial data for a company from the database.
        """
        # Get company info
        company = await self.db_manager.get_company_by_ticker(ticker)
        if not company:
            return None
        
        # Get financial data
        financial_data = await self.db_manager.get_financial_data(company['id'])
        
        return {
            'company': company,
            'financial_data': financial_data
        } 