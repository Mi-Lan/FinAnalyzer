import asyncio
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import json

import asyncpg
from databases import Database
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from data_adapter.config import ProviderSettings
from data_adapter.logging import get_logger
from data_adapter.models import Base, Company, FinancialData
from data_adapter.providers.fmp.models import FinancialStatement

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
                    'WHERE "companyId" = :company_id AND year = :year AND period = :period'
                ),
                {"company_id": company_id, "year": year, "period": period}
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
                logger.info(f"Merged and updated financial data for company {company_id}, {year} {period}")
                return existing_row[0]
            elif existing_row:
                # Update existing data (overwrite)
                await session.execute(
                    text(
                        'UPDATE "FinancialData" SET data = :data, "updatedAt" = NOW() WHERE id = :id'
                    ),
                    {"id": existing_row[0], "data": financial_statements_json}
                )
                logger.info(f"Updated financial data for company {company_id}, {year} {period}")
                return existing_row[0]
            else:
                # Insert new data
                financial_data_id = str(__import__('uuid').uuid4())
                await session.execute(
                    text(
                        'INSERT INTO "FinancialData" (id, "companyId", year, period, data, "createdAt", "updatedAt") '
                        'VALUES (:id, :company_id, :year, :period, :data, NOW(), NOW())'
                    ),
                    {
                        "id": financial_data_id,
                        "company_id": company_id,
                        "year": year,
                        "period": period,
                        "data": financial_statements_json
                    }
                )
                logger.info(f"Stored new financial data for company {company_id}, {year} {period}")
                return financial_data_id
    
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
        query = 'SELECT id, year, period, data, "createdAt", "updatedAt" FROM "FinancialData" WHERE "companyId" = :company_id'
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
                    "data": row[3],
                    "createdAt": row[4],
                    "updatedAt": row[5]
                }
                for row in rows
            ] 