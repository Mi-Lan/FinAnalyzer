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
        industry: str = None
    ) -> Dict[str, List[str]]:
        """
        Fetch and store comprehensive financial data for a company.
        Returns dict with endpoint names as keys and lists of stored data IDs as values.
        """
        if years is None:
            years = [2023, 2024]  # Default to recent years
        
        if periods is None:
            periods = ['annual', 'quarter']  # Both annual and quarterly data
        
        results = {}
        endpoints = ['income-statement', 'balance-sheet-statement', 'cash-flow-statement']
        
        for endpoint in endpoints:
            results[endpoint] = []
            
            for period in periods:
                try:
                    params = {
                        'symbol': ticker,
                        'period': period
                    }
                    
                    # Add year filtering if quarterly data
                    if period == 'quarter' and years:
                        # For quarterly data, we might need to filter by years
                        # FMP returns all quarters, so we'll filter after fetching
                        pass
                    
                    stored_ids = await self.fetch_and_store_data(
                        endpoint=endpoint,
                        params=params,
                        company_name=company_name,
                        sector=sector,
                        industry=industry
                    )
                    
                    results[endpoint].extend(stored_ids)
                    
                except Exception as e:
                    logger.error(f"Failed to fetch {endpoint} data for {ticker} ({period}): {e}")
                    continue
        
        return results
    
    async def fetch_and_store_sec_filings(
        self,
        ticker: str,
        from_date: str,
        to_date: str,
        company_name: str = None,
        sector: str = None,
        industry: str = None
    ) -> List[str]:
        """
        Fetch SEC filings for a company within a date range and store them.
        """
        params = {
            'symbol': ticker,
            'from': from_date,
            'to': to_date
        }
        
        # Fetch data using the parent class method
        filings = await self.fetch_data("sec-filings-search/symbol", params)
        
        if not filings:
            logger.warning(f"No SEC filings found for {ticker} from {from_date} to {to_date}")
            return []
            
        # Ensure company exists
        company_id = await self.db_manager.ensure_company_exists(
            ticker=ticker,
            name=company_name or ticker,
            sector=sector,
            industry=industry
        )
        
        stored_ids = []
        for filing in filings:
            if isinstance(filing, SECFiling):
                stored_id = await self.db_manager.store_sec_filing(company_id, filing)
                if stored_id:
                    stored_ids.append(stored_id)
        
        logger.info(f"Stored {len(stored_ids)} new SEC filings for {ticker}.")
        return stored_ids

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