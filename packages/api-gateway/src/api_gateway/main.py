from fastapi import FastAPI, APIRouter, Depends, HTTPException
from .security import get_api_key
from .models import CompanyDetailsResponse, Company, FinancialData
from typing import List
from data_adapter.async_processor import AsyncProcessor

app = FastAPI()
router = APIRouter(prefix="/api", dependencies=[Depends(get_api_key)])


@router.get("/companies/{ticker}", response_model=CompanyDetailsResponse)
async def get_company(ticker: str):
    """
    Retrieves detailed information for a specific company.
    If the company data is not in the database, it fetches from the provider and stores it.
    """
    processor = AsyncProcessor()
    try:
        # The data adapter now handles the get-or-create logic
        company_data = await processor.get_stored_data_for_tickers([ticker.upper()])

        if not company_data or ticker.upper() not in company_data:
            raise HTTPException(
                status_code=404,
                detail="Company not found after attempting to fetch.",
            )

        data = company_data[ticker.upper()]

        # The analysis part is not implemented, so we return None for it
        return CompanyDetailsResponse(
            company=data["company"],
            financialData=data["financial_data"],
            latestFinancials=data["financial_data"][0]
            if data["financial_data"]
            else None,
            analysisResult=None,
        )

    except Exception as e:
        print(f"Error processing ticker {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/companies", response_model=List[Company])
async def get_companies():
    # This would need a proper implementation to list all companies from DB
    raise HTTPException(status_code=501, detail="Not implemented")


app.include_router(router)
