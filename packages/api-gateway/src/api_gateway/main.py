from fastapi import FastAPI, APIRouter, Depends, HTTPException
from .security import get_api_key
from .models import CompanyDetailsResponse, Company, FinancialData
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import sys

# Add the data-adapter to the Python path
sys.path.append('/data-adapter/src')

from data_adapter.async_processor import AsyncProcessor

app = FastAPI()
router = APIRouter(prefix="/api", dependencies=[Depends(get_api_key)])

# Dependency to get the AsyncProcessor
async def get_processor():
    processor = AsyncProcessor()
    try:
        yield processor
    finally:
        # No explicit close needed for AsyncProcessor in this setup
        pass

def transform_company_data(db_company: Dict[str, Any]) -> Company:
    """Transform database company data to API model."""
    # Handle datetime objects that come from the database
    created_at = db_company.get('createdAt', db_company.get('created_at'))
    updated_at = db_company.get('updatedAt', db_company.get('updated_at'))
    
    # Convert datetime objects to ISO format strings if needed
    if isinstance(created_at, datetime):
        created_at = created_at
    elif isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)
    else:
        created_at = datetime.now()
        
    if isinstance(updated_at, datetime):
        updated_at = updated_at
    elif isinstance(updated_at, str):
        updated_at = datetime.fromisoformat(updated_at)
    else:
        updated_at = datetime.now()
    
    return Company(
        id=str(db_company['id']),
        name=db_company['name'],
        ticker=db_company['ticker'],
        sector=db_company.get('sector') or 'Unknown',
        industry=db_company.get('industry') or 'Unknown',
        createdAt=created_at,
        updatedAt=updated_at
    )


def transform_financial_data(db_financial: Dict[str, Any]) -> FinancialData:
    """Transform database financial data to API model."""
    # Handle datetime objects that come from the database
    created_at = db_financial.get('createdAt', db_financial.get('created_at'))
    updated_at = db_financial.get('updatedAt', db_financial.get('updated_at'))
    
    # Convert datetime objects to ISO format strings if needed
    if isinstance(created_at, datetime):
        created_at = created_at
    elif isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)
    else:
        created_at = datetime.now()
        
    if isinstance(updated_at, datetime):
        updated_at = updated_at
    elif isinstance(updated_at, str):
        updated_at = datetime.fromisoformat(updated_at)
    else:
        updated_at = datetime.now()
    
    # Get company_id with fallback
    company_id = db_financial.get('company_id', db_financial.get('companyId'))
    if company_id is None:
        company_id = db_financial.get('company', {}).get('id') if 'company' in db_financial else 'unknown'
    
    return FinancialData(
        id=str(db_financial['id']),
        companyId=str(company_id),
        year=db_financial['year'],
        period=db_financial['period'],
        type=db_financial['type'],
        data=db_financial['data'],
        createdAt=created_at,
        updatedAt=updated_at
    )

def assemble_latest_financials(financials: List[FinancialData]) -> Optional[FinancialData]:
    """
    Finds the latest annual statements and assembles them into a single
    FinancialData object with a structured 'data' payload.
    """
    if not financials:
        return None

    annual_financials = [f for f in financials if f.period == 'FY' and f.year is not None]
    if not annual_financials:
        return None  # Or could fall back to most recent of any type

    latest_year = max(f.year for f in annual_financials)

    # Helper to find the first statement list within a data blob
    def get_statement_from_list(data_blob, key):
        statement_list = data_blob.get(key, [])
        return statement_list[0] if statement_list and isinstance(statement_list, list) else None

    # Find the data blobs for the latest year
    income_data, balance_data, cash_flow_data = None, None, None
    parent_fd_for_metadata = None

    for f in annual_financials:
        if f.year == latest_year:
            parent_fd_for_metadata = f # Use one of the real entries for metadata
            if not income_data and f.data.get('income_statements'):
                income_data = get_statement_from_list(f.data, 'income_statements')
            if not balance_data and f.data.get('balance_sheets'):
                balance_data = get_statement_from_list(f.data, 'balance_sheets')
            if not cash_flow_data and f.data.get('cash_flows'):
                cash_flow_data = get_statement_from_list(f.data, 'cash_flows')

    if not (income_data or balance_data or cash_flow_data):
        return None

    # Assemble the final payload
    return FinancialData(
        id=parent_fd_for_metadata.id if parent_fd_for_metadata else "assembled",
        companyId=parent_fd_for_metadata.companyId if parent_fd_for_metadata else "unknown",
        year=latest_year,
        period='FY',
        type='assembled-financial-statements',  # Special type for assembled data
        createdAt=parent_fd_for_metadata.createdAt if parent_fd_for_metadata else datetime.now(),
        updatedAt=parent_fd_for_metadata.updatedAt if parent_fd_for_metadata else datetime.now(),
        data={
            "incomeStatement": income_data,
            "balanceSheet": balance_data,
            "cashFlow": cash_flow_data,
        }
    )

@router.get("/companies/{ticker}", response_model=CompanyDetailsResponse)
async def get_company_details(ticker: str, processor: AsyncProcessor = Depends(get_processor)):
    try:
        # Check for stored data first
        company_data = await processor.get_stored_data_for_tickers([ticker.upper()])

        # If no data exists, fetch and store it
        if not company_data or ticker.upper() not in company_data:
            current_year = datetime.now().year
            await processor.fetch_and_store_for_tickers(
                tickers=[ticker.upper()],
                years=[current_year, current_year - 1, current_year - 2], # Fetch last 3 years
                periods=['annual', 'quarter']
            )
            
            # Try to get the data again
            company_data = await processor.get_stored_data_for_tickers([ticker.upper()])
            
            if not company_data or ticker.upper() not in company_data:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Unable to fetch or find data for ticker {ticker}"
                )

        data = company_data[ticker.upper()]
        
        if not data.get('company'):
            raise HTTPException(status_code=404, detail=f"Company info for {ticker} not found in database.")

        # Transform data for the response
        company = transform_company_data(data['company'])
        financials = [transform_financial_data(fd) for fd in data.get('financial_data', [])]
        
        # Assemble the latest financials payload
        latest_financials_payload = assemble_latest_financials(financials)

        return CompanyDetailsResponse(
            company=company,
            financialData=financials,
            latestFinancials=latest_financials_payload,
            analysisResult=None  # AI analysis not yet implemented
        )
    except Exception as e:
        print(f"Error in get_company_details for {ticker}: {e}")
        # Re-raise as HTTPException to be handled by FastAPI
        raise HTTPException(status_code=500, detail=str(e))

def find_latest_annual_financials(financials: List[FinancialData]) -> Optional[FinancialData]:
    """Find the most recent annual ('FY') financial statement."""
    if not financials:
        return None
    
    annual_financials = [f for f in financials if f.period == 'FY' and f.year is not None]
    
    if not annual_financials:
        # If no annual data, fall back to the most recent of any type
        return max(financials, key=lambda f: f.year, default=None)
        
    # Find the one with the highest year
    return max(annual_financials, key=lambda f: f.year, default=None)


@router.get("/companies", response_model=List[Company])
async def get_companies():
    # This would need a proper implementation to list all companies from DB
    raise HTTPException(status_code=501, detail="Not implemented")


app.include_router(router)
