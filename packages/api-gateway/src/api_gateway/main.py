from fastapi import FastAPI, APIRouter, Depends, HTTPException
from .security import get_api_key
# from .models import CompanyDetailsResponse, Company, FinancialData
# from typing import List, Dict, Any, Optional
# from datetime import datetime
# import os
# import sys
# import logging

from .routes import scoring as scoring_router

# logger = logging.getLogger(__name__)

# Add the data-adapter to the Python path
# sys.path.append('/data-adapter/src')

# Temporarily commented out for scoring module testing
# from data_adapter.async_processor import AsyncProcessor

# **NEW: Configuration for data filtering**
# FINANCIAL_DATA_FILTER_CONFIG = {
#     # Financial statement types we want to include
#     "financial_statement_types": {
#         'Income Statement',
#         'income-statement', 
#         'Balance Sheet',
#         'balance-sheet-statement',
#         'Cash Flow Statement', 
#         'cash-flow-statement',
#         'assembled-financial-statements'  # Our custom assembled type
#     },
#     
#     # SEC filing types we want to include
#     "sec_filing_types": {
#         '10-K',     # Annual report
#         '10-Q',     # Quarterly report  
#         '8-K',      # Current report
#         '20-F',     # Annual report for foreign companies
#         '6-K',      # Report of foreign private issuer
#         'DEF 14A',  # Proxy statement
#         'S-1',      # Registration statement
#         'S-3',      # Registration statement
#         'S-4',      # Registration statement
#         'SC 13G',   # Beneficial ownership report
#         'SC 13D'    # Beneficial ownership report
#     }
# }

app = FastAPI(title="Financial Analysis API", description="API for financial scoring and analysis")
router = APIRouter(prefix="/api", dependencies=[Depends(get_api_key)])

# Temporarily commented out data adapter functionality
# # Dependency to get the AsyncProcessor
# async def get_processor():
#     processor = AsyncProcessor()
#     try:
#         yield processor
#     finally:
#         # No explicit close needed for AsyncProcessor in this setup
#         pass

# def transform_company_data(db_company: Dict[str, Any]) -> Company:
#     """Transform database company data to API model."""
#     # Handle datetime objects that come from the database
#     created_at = db_company.get('createdAt', db_company.get('created_at'))
#     updated_at = db_company.get('updatedAt', db_company.get('updated_at'))
#     
#     # Convert datetime objects to ISO format strings if needed
#     if isinstance(created_at, datetime):
#         created_at = created_at
#     elif isinstance(created_at, str):
#         created_at = datetime.fromisoformat(created_at)
#     else:
#         created_at = datetime.now()
#         
#     if isinstance(updated_at, datetime):
#         updated_at = updated_at
#     elif isinstance(updated_at, str):
#         updated_at = datetime.fromisoformat(updated_at)
#     else:
#         updated_at = datetime.now()
#     
#     return Company(
#         id=str(db_company['id']),
#         name=db_company['name'],
#         ticker=db_company['ticker'],
#         sector=db_company.get('sector') or 'Unknown',
#         industry=db_company.get('industry') or 'Unknown',
#         createdAt=created_at,
#         updatedAt=updated_at
#     )


# def transform_financial_data(db_financial: Dict[str, Any]) -> FinancialData:
#     """Transform database financial data to API model."""
#     # Handle datetime objects that come from the database
#     created_at = db_financial.get('createdAt', db_financial.get('created_at'))
#     updated_at = db_financial.get('updatedAt', db_financial.get('updated_at'))
#     
#     # Convert datetime objects to ISO format strings if needed
#     if isinstance(created_at, datetime):
#         created_at = created_at
#     elif isinstance(created_at, str):
#         created_at = datetime.fromisoformat(created_at)
#     else:
#         created_at = datetime.now()
#         
#     if isinstance(updated_at, datetime):
#         updated_at = updated_at
#     elif isinstance(updated_at, str):
#         updated_at = datetime.fromisoformat(updated_at)
#     else:
#         updated_at = datetime.now()
#     
#     # Get company_id with fallback
#     company_id = db_financial.get('company_id', db_financial.get('companyId'))
#     if company_id is None:
#         company_id = db_financial.get('company', {}).get('id') if 'company' in db_financial else 'unknown'
#     
#     return FinancialData(
#         id=str(db_financial['id']),
#         companyId=str(company_id),
#         year=db_financial['year'],
#         period=db_financial['period'],
#         type=db_financial['type'],
#         data=db_financial['data'],
#         createdAt=created_at,
#         updatedAt=updated_at
#     )

# def assemble_latest_financials(financials: List[FinancialData]) -> Optional[FinancialData]:
#     """
#     Finds the latest annual statements and assembles them into a single
#     FinancialData object with a structured 'data' payload.
#     """
#     if not financials:
#         return None

#     annual_financials = [f for f in financials if f.period == 'FY' and f.year is not None]
#     if not annual_financials:
#         return None  # Or could fall back to most recent of any type

#     latest_year = max(f.year for f in annual_financials)

#     # Helper to find the first statement list within a data blob
#     def get_statement_from_list(data_blob, key):
#         statement_list = data_blob.get(key, [])
#         return statement_list[0] if statement_list and isinstance(statement_list, list) else None

#     # Find the data blobs for the latest year
#     income_data, balance_data, cash_flow_data = None, None, None
#     parent_fd_for_metadata = None

#     for f in annual_financials:
#         if f.year == latest_year:
#             parent_fd_for_metadata = f # Use one of the real entries for metadata
#             if not income_data and f.data.get('income_statements'):
#                 income_data = get_statement_from_list(f.data, 'income_statements')
#             if not balance_data and f.data.get('balance_sheets'):
#                 balance_data = get_statement_from_list(f.data, 'balance_sheets')
#             if not cash_flow_data and f.data.get('cash_flows'):
#                 cash_flow_data = get_statement_from_list(f.data, 'cash_flows')

#     if not (income_data or balance_data or cash_flow_data):
#         return None

#     # Assemble the final payload
#     return FinancialData(
#         id=parent_fd_for_metadata.id if parent_fd_for_metadata else "assembled",
#         companyId=parent_fd_for_metadata.companyId if parent_fd_for_metadata else "unknown",
#         year=latest_year,
#         period='FY',
#         type='assembled-financial-statements',  # Special type for assembled data
#         createdAt=parent_fd_for_metadata.createdAt if parent_fd_for_metadata else datetime.now(),
#         updatedAt=parent_fd_for_metadata.updatedAt if parent_fd_for_metadata else datetime.now(),
#         data={
#             "incomeStatement": income_data,
#             "balanceSheet": balance_data,
#             "cashFlow": cash_flow_data,
#         }
#     )

# def filter_relevant_financial_data(financials: List[FinancialData]) -> Dict[str, List[FinancialData]]:
#     """
#     Filter and categorize financial data into statements and SEC filings.
#     Returns only the data types needed for the company detail page.
#     """
#     # Use configuration for maintainability
#     financial_statement_types = FINANCIAL_DATA_FILTER_CONFIG["financial_statement_types"]
#     sec_filing_types = FINANCIAL_DATA_FILTER_CONFIG["sec_filing_types"]
#     
#     # Separate and filter the data
#     financial_statements = []
#     sec_filings = []
#     filtered_out_count = 0
#     
#     for fd in financials:
#         if fd.type in financial_statement_types:
#             financial_statements.append(fd)
#         elif fd.type in sec_filing_types:
#             sec_filings.append(fd)
#         else:
#             # Track what we're filtering out for monitoring
#             filtered_out_count += 1
#     
#     # Log filtering performance for monitoring
#     total_input = len(financials)
#     total_output = len(financial_statements) + len(sec_filings)
#     
#     logger.info(f"Financial data filtering: {total_input} → {total_output} records "
#                f"({len(financial_statements)} statements, {len(sec_filings)} filings, "
#                f"{filtered_out_count} filtered out)")
#     
#     return {
#         'financial_statements': financial_statements,
#         'sec_filings': sec_filings
#     }

# @router.get("/companies/{ticker}", response_model=CompanyDetailsResponse)
# async def get_company_details(ticker: str, processor: AsyncProcessor = Depends(get_processor)):
#     try:
#         current_year = datetime.now().year
#         years_to_fetch = list(range(current_year - 9, current_year + 1))  # Last 10 years
#         
#         # Check data completeness first
#         completeness_check = await processor.check_data_completeness_for_tickers(
#             [ticker.upper()], 
#             years_to_fetch
#         )
#         
#         ticker_upper = ticker.upper()
#         completeness = completeness_check.get(ticker_upper, {"is_complete": False})
#         
#         # If data is not complete, fetch missing data
#         if not completeness.get("is_complete", False):
#             logger.info(f"Data incomplete for {ticker}. Status: financials={completeness.get('has_complete_financials')}, old_10k={completeness.get('has_old_10k_filings')}, recent_filings={completeness.get('has_recent_filings')}, missing={completeness.get('missing_financial_data', [])}")
#             
#             # Fetch financial statements if missing or incomplete
#             if not completeness.get("has_complete_financials", False):
#                 logger.info(f"Fetching financial statements for {ticker}")
#                 await processor.fetch_and_store_for_tickers(
#                     tickers=[ticker_upper],
#                     years=years_to_fetch,
#                     periods=['annual', 'quarter'],
#                     max_data_points=1500  # Enforce API limit
#                 )
#             
#             # Fetch SEC filings if missing old 10-K filings or recent filings
#             if not completeness.get("has_old_10k_filings", False) or not completeness.get("has_recent_filings", False):
#                 logger.info(f"Fetching SEC filings for {ticker} (old 10-K: {completeness.get('has_old_10k_filings')}, recent: {completeness.get('has_recent_filings')})")
#                 try:
#                     from_date = f"{current_year - 9}-01-01"
#                     to_date = f"{current_year}-12-31"
#                     await processor.fetch_and_store_sec_filings_for_tickers(
#                         tickers=[ticker_upper],
#                         from_date=from_date,
#                         to_date=to_date,
#                         max_filings_per_ticker=150  # Reasonable limit for SEC filings
#                     )
#                 except Exception as e:
#                     logger.warning(f"Failed to fetch SEC filings for {ticker}: {e}")
#                     # Continue without SEC filings if they fail
#         else:
#             logger.info(f"Data already complete for {ticker} - using cached data")
#         
#         # Get the (now hopefully complete) data
#         company_data = await processor.get_stored_data_for_tickers([ticker_upper])
#         
#         if not company_data or ticker_upper not in company_data:
#             raise HTTPException(
#                 status_code=404, 
#                 detail=f"Unable to fetch or find data for ticker {ticker}"
#             )

#         data = company_data[ticker_upper]
#         
#         if not data.get('company'):
#             raise HTTPException(status_code=404, detail=f"Company info for {ticker} not found in database.")

#         # Transform data for the response
#         company = transform_company_data(data['company'])
#         all_financials = [transform_financial_data(fd) for fd in data.get('financial_data', [])]
#         
#         # **NEW: Filter the financial data to only include what we need**
#         filtered_data = filter_relevant_financial_data(all_financials)
#         
#         # Combine filtered financial statements and SEC filings
#         relevant_financials = filtered_data['financial_statements'] + filtered_data['sec_filings']
#         
#         # Assemble the latest financials payload from financial statements only
#         latest_financials_payload = assemble_latest_financials(filtered_data['financial_statements'])

#         return CompanyDetailsResponse(
#             company=company,
#             financialData=relevant_financials,  # Now contains only relevant data
#             latestFinancials=latest_financials_payload,
#             analysisResult=None  # AI analysis not yet implemented
#         )
#     except Exception as e:
#         print(f"Error in get_company_details for {ticker}: {e}")
#         # Re-raise as HTTPException to be handled by FastAPI
#         raise HTTPException(status_code=500, detail=str(e))

# def find_latest_annual_financials(financials: List[FinancialData]) -> Optional[FinancialData]:
#     """Find the most recent annual ('FY') financial statement."""
#     if not financials:
#         return None
#     
#     annual_financials = [f for f in financials if f.period == 'FY' and f.year is not None]
#     
#     if not annual_financials:
#         # If no annual data, fall back to the most recent of any type
#         return max(financials, key=lambda f: f.year, default=None)
#         
#     # Find the one with the highest year
#     return max(annual_financials, key=lambda f: f.year, default=None)


# @router.get("/companies", response_model=List[Company])
# async def get_companies():
#     # This would need a proper implementation to list all companies from DB
#     raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "message": "API Gateway is running"}

# Include the main router (currently just health check)
app.include_router(router)

# Include the scoring router
app.include_router(
    scoring_router.router,
    prefix="/api/scoring",
    tags=["Scoring"],
    dependencies=[Depends(get_api_key)]
)
