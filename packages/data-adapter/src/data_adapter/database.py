import asyncio
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import json
from datetime import datetime

import asyncpg
from databases import Database
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from data_adapter.config import ProviderSettings
from data_adapter.logging import get_logger
from data_adapter.models import Base, Company, FinancialData
from data_adapter.providers.fmp.models import FinancialStatement, SECFiling

logger = get_logger(__name__)


class DatabaseManager:
    """
    Manages database connections and operations for storing financial data.
    """
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        
        # Ensure the URL is compatible with asyncpg for SQLAlchemy
        if not database_url.startswith("postgresql+asyncpg://"):
            if database_url.startswith("postgresql://"):
                database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            else:
                raise ValueError("Invalid database URL format for asyncpg")
        
        self.database = Database(database_url)
        self.async_engine = create_async_engine(database_url, echo=False)
        self.async_session_maker = sessionmaker(
            self.async_engine, class_=AsyncSession, expire_on_commit=False
        )
        self._connected = False
    
    async def connect(self) -> None:
        """Connect to the database."""
        if not self._connected:
            await self.database.connect()
            self._connected = True
            logger.info("Database connection established")
    
    async def disconnect(self) -> None:
        """Disconnect from the database."""
        if self._connected:
            await self.database.disconnect()
            self._connected = False
            logger.info("Database connection closed")
    
    @asynccontextmanager
    async def get_session(self):
        """Get an async database session."""
        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def ensure_company_exists(self, ticker: str, name: str = None, sector: str = None, industry: str = None) -> str:
        """
        Ensure a company exists in the database, create if it doesn't.
        Returns the company ID.
        """
        async with self.get_session() as session:
            # Try to find existing company
            result = await session.execute(
                text('SELECT id FROM "Company" WHERE ticker = :ticker'),
                {"ticker": ticker}
            )
            company_row = result.fetchone()
            
            if company_row:
                return company_row[0]
            
            # Create new company
            company_id = str(__import__('uuid').uuid4())
            await session.execute(
                text(
                    'INSERT INTO "Company" (id, name, ticker, sector, industry, "createdAt", "updatedAt") '
                    'VALUES (:id, :name, :ticker, :sector, :industry, NOW(), NOW())'
                ),
                {
                    "id": company_id,
                    "name": name or ticker,
                    "ticker": ticker,
                    "sector": sector,
                    "industry": industry
                }
            )
            logger.info(f"Created new company: {ticker} (ID: {company_id})")
            return company_id
    
    async def store_financial_data(
        self, 
        company_id: str, 
        year: int, 
        period: str, 
        type: str,
        financial_statements: Dict[str, Any],
        merge: bool = False
    ) -> str:
        """
        Store financial data for a company.
        If merge is True, it merges the new financial_statements with existing data.
        Returns the financial data ID.
        """
        # Serialize the dictionary to a JSON string
        financial_statements_json = json.dumps(financial_statements)

        async with self.get_session() as session:
            # Check if data already exists
            result = await session.execute(
                text(
                    'SELECT id, data FROM "FinancialData" '
                    'WHERE "companyId" = :company_id AND year = :year AND period = :period AND type = :type'
                ),
                {"company_id": company_id, "year": year, "period": period, "type": type}
            )
            existing_row = result.fetchone()
            
            if existing_row and merge:
                # Merge new data with existing data
                existing_data = existing_row[1]
                if isinstance(existing_data, str):
                    existing_data = json.loads(existing_data)
                
                for key, value in financial_statements.items():
                    if key in existing_data and isinstance(existing_data[key], list):
                        existing_data[key].extend(value)
                    else:
                        existing_data[key] = value
                
                merged_data_json = json.dumps(existing_data)
                
                await session.execute(
                    text(
                        'UPDATE "FinancialData" SET data = :data, "updatedAt" = NOW() WHERE id = :id'
                    ),
                    {"id": existing_row[0], "data": merged_data_json}
                )
                logger.info(f"Merged and updated financial data for company {company_id}, {year} {period} {type}")
                return existing_row[0]
            elif existing_row:
                # Update existing data (overwrite)
                await session.execute(
                    text(
                        'UPDATE "FinancialData" SET data = :data, "updatedAt" = NOW() WHERE id = :id'
                    ),
                    {"id": existing_row[0], "data": financial_statements_json}
                )
                logger.info(f"Updated financial data for company {company_id}, {year} {period} {type}")
                return existing_row[0]
            else:
                # Insert new data
                financial_data_id = str(__import__('uuid').uuid4())
                await session.execute(
                    text(
                        'INSERT INTO "FinancialData" (id, "companyId", year, period, type, data, "createdAt", "updatedAt") '
                        'VALUES (:id, :company_id, :year, :period, :type, :data, NOW(), NOW())'
                    ),
                    {
                        "id": financial_data_id,
                        "company_id": company_id,
                        "year": year,
                        "period": period,
                        "type": type,
                        "data": financial_statements_json
                    }
                )
                logger.info(f"Stored new financial data for company {company_id}, {year} {period} {type}")
                return financial_data_id
    
    async def store_sec_filing(self, company_id: str, filing: SECFiling) -> Optional[str]:
        """
        Store a single SEC filing in the database.
        Each filing is stored as a unique record.
        """
        try:
            filing_date_str = filing.filing_date.split(" ")[0]
            filing_date = datetime.fromisoformat(filing_date_str)
            year = filing_date.year
            period = filing_date_str
            filing_type = filing.form

            async with self.get_session() as session:
                # Check if this specific filing already exists
                result = await session.execute(
                    text(
                        'SELECT id FROM "FinancialData" '
                        'WHERE "companyId" = :company_id AND period = :period AND type = :type'
                    ),
                    {"company_id": company_id, "period": period, "type": filing_type}
                )
                if result.fetchone():
                    logger.info(f"SEC filing {filing.form} from {filing.filing_date} already exists for company {company_id}.")
                    return None

                # Insert new filing data
                financial_data_id = str(__import__('uuid').uuid4())
                await session.execute(
                    text(
                        'INSERT INTO "FinancialData" (id, "companyId", year, period, type, data, "createdAt", "updatedAt") '
                        'VALUES (:id, :company_id, :year, :period, :type, :data, NOW(), NOW())'
                    ),
                    {
                        "id": financial_data_id,
                        "company_id": company_id,
                        "year": year,
                        "period": period,
                        "type": filing_type,
                        "data": filing.model_dump_json()
                    }
                )
                logger.info(f"Stored SEC filing {filing.form} from {filing.filing_date} for company {company_id}")
                return financial_data_id
        except Exception as e:
            logger.error(f"Failed to store SEC filing for company {company_id}: {e}")
            return None
    
    async def get_company_by_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get company information by ticker."""
        async with self.get_session() as session:
            result = await session.execute(
                text(
                    'SELECT id, name, ticker, sector, industry, "createdAt", "updatedAt" '
                    'FROM "Company" WHERE ticker = :ticker'
                ),
                {"ticker": ticker}
            )
            row = result.fetchone()
            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "ticker": row[2],
                    "sector": row[3],
                    "industry": row[4],
                    "createdAt": row[5],
                    "updatedAt": row[6]
                }
        return None
    
    async def get_financial_data(self, company_id: str, year: int = None, period: str = None) -> List[Dict[str, Any]]:
        """Get financial data for a company, optionally filtered by year and period."""
        query = 'SELECT id, year, period, type, data, "createdAt", "updatedAt" FROM "FinancialData" WHERE "companyId" = :company_id'
        params = {"company_id": company_id}
        
        if year is not None:
            query += " AND year = :year"
            params["year"] = year
            
        if period is not None:
            query += " AND period = :period"
            params["period"] = period
            
        query += " ORDER BY year DESC, period"
        
        async with self.get_session() as session:
            result = await session.execute(text(query), params)
            rows = result.fetchall()
            return [
                {
                    "id": row[0],
                    "year": row[1],
                    "period": row[2],
                    "type": row[3],
                    "data": row[4],
                    "createdAt": row[5],
                    "updatedAt": row[6]
                }
                for row in rows
            ] 