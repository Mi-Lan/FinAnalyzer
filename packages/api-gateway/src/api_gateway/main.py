from fastapi import FastAPI, APIRouter, Depends, HTTPException
from .security import get_api_key
from .models import CompanyDetailsResponse, Company, FinancialData
from typing import List, Dict, Any
from datetime import datetime
import os
import sys

# Add the data-adapter to the Python path
sys.path.append('/data-adapter/src')

from data_adapter.async_processor import AsyncProcessor

app = FastAPI()
router = APIRouter(prefix="/api", dependencies=[Depends(get_api_key)])


def transform_company_data(db_company: Dict[str, Any]) -> Company:
    """Transform database company data to API model."""
    return Company(
        id=str(db_company['id']),
        name=db_company['name'],
        ticker=db_company['ticker'],
        sector=db_company.get('sector', 'Unknown'),
        industry=db_company.get('industry', 'Unknown'),
        createdAt=datetime.fromisoformat(db_company['created_at']),
        updatedAt=datetime.fromisoformat(db_company['updated_at'])
    )


def transform_financial_data(db_financial: Dict[str, Any]) -> FinancialData:
    """Transform database financial data to API model."""
    return FinancialData(
        id=str(db_financial['id']),
        companyId=str(db_financial['company_id']),
        year=db_financial['year'],
        period=db_financial['period'],
        data=db_financial['data'],
        createdAt=datetime.fromisoformat(db_financial['created_at']),
        updatedAt=datetime.fromisoformat(db_financial['updated_at'])
    )


@router.get("/companies/{ticker}", response_model=CompanyDetailsResponse)
async def get_company(ticker: str):
    """
    Retrieves detailed information for a specific company.
    If the company data is not in the database, it fetches from the provider and stores it.
    """
    processor = AsyncProcessor()
    
    try:
        # First, try to get stored data
        company_data = await processor.get_stored_data_for_tickers([ticker.upper()])
        
        # If no data exists, fetch and store it
        if not company_data or ticker.upper() not in company_data:
            # Fetch and store data for the current and previous year
            current_year = datetime.now().year
            await processor.fetch_and_store_for_tickers(
                tickers=[ticker.upper()],
                years=[current_year - 1, current_year],
                periods=['annual', 'quarter']
            )
            
            # Try to get the data again
            company_data = await processor.get_stored_data_for_tickers([ticker.upper()])
            
            if not company_data or ticker.upper() not in company_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Unable to fetch data for ticker {ticker}"
                )
        
        data = company_data[ticker.upper()]
        
        # Transform the data to match API models
        company = transform_company_data(data["company"])
        financial_data_list = [
            transform_financial_data(fd) for fd in data["financial_data"]
        ]
        
        # Get the latest financial data
        latest_financials = None
        if financial_data_list:
            # Sort by year and period to get the most recent
            sorted_financials = sorted(
                financial_data_list,
                key=lambda x: (x.year, x.period),
                reverse=True
            )
            latest_financials = sorted_financials[0]
        
        return CompanyDetailsResponse(
            company=company,
            financialData=financial_data_list,
            latestFinancials=latest_financials,
            analysisResult=None  # Analysis not implemented yet
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing ticker {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/companies", response_model=List[Company])
async def get_companies():
    # This would need a proper implementation to list all companies from DB
    raise HTTPException(status_code=501, detail="Not implemented")


app.include_router(router)
