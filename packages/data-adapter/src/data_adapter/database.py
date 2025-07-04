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
    
    async def get_all_companies(self) -> List[Dict[str, Any]]:
        """Get all companies from the database, including their latest analysis result."""
        async with self.get_session() as session:
            # This query joins the Company table with the latest analysis result for each company
            query = text("""
                WITH LatestAnalysis AS (
                    SELECT 
                        "companyId",
                        score,
                        insights,
                        ROW_NUMBER() OVER(PARTITION BY "companyId" ORDER BY "createdAt" DESC) as rn
                    FROM "AnalysisResult"
                )
                SELECT 
                    c.id, 
                    c.name, 
                    c.ticker, 
                    c.sector, 
                    c.industry, 
                    c."createdAt", 
                    c."updatedAt",
                    la.score,
                    la.insights
                FROM "Company" c
                LEFT JOIN LatestAnalysis la ON c.id = la."companyId" AND la.rn = 1
                ORDER BY c.ticker
            """)
            
            result = await session.execute(query)
            rows = result.fetchall()
            
            companies = []
            for row in rows:
                company_data = {
                    "id": row[0],
                    "name": row[1],
                    "ticker": row[2],
                    "sector": row[3],
                    "industry": row[4],
                    "createdAt": row[5],
                    "updatedAt": row[6],
                    "score": row[7],
                    "insights": row[8],
                }
                # Deserialize insights JSON string if it exists
                if isinstance(company_data.get('insights'), str):
                    company_data['insights'] = json.loads(company_data['insights'])
                companies.append(company_data)
            
            return companies
    
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
    
    async def check_data_completeness(self, company_id: str, required_years: List[int]) -> Dict[str, Any]:
        """
        Check if we have complete financial data and SEC filings for a company.
        Returns a dict with completeness status and missing data information.
        """
        async with self.get_session() as session:
            current_year = datetime.now().year
            oldest_required_year = current_year - 9  # 10 years back
            
            # Check financial statements completeness
            financial_types = ['Income Statement', 'Balance Sheet', 'Cash Flow Statement']
            missing_financial_data = []
            
            for year in required_years:
                for financial_type in financial_types:
                    result = await session.execute(
                        text(
                            'SELECT COUNT(*) FROM "FinancialData" '
                            'WHERE "companyId" = :company_id AND year = :year AND type = :type AND period = :period'
                        ),
                        {"company_id": company_id, "year": year, "type": financial_type, "period": "FY"}
                    )
                    count = result.scalar()
                    if count == 0:
                        missing_financial_data.append(f"{financial_type} {year} FY")
            
            # Check for SEC 10-K filings - we need at least one 10-K that's at least 9 years old
            result = await session.execute(
                text(
                    'SELECT COUNT(*) FROM "FinancialData" '
                    'WHERE "companyId" = :company_id AND type = :type AND year <= :oldest_year'
                ),
                {"company_id": company_id, "type": "10-K", "oldest_year": oldest_required_year}
            )
            old_10k_count = result.scalar()
            
            # Check for recent SEC filings (last 2 years) to ensure we're up to date
            result = await session.execute(
                text(
                    'SELECT COUNT(*) FROM "FinancialData" '
                    'WHERE "companyId" = :company_id AND type IN (:type1, :type2) AND year >= :recent_year'
                ),
                {"company_id": company_id, "type1": "10-K", "type2": "10-Q", "recent_year": current_year - 1}
            )
            recent_filings_count = result.scalar()
            
            # Determine if data is complete
            has_complete_financials = len(missing_financial_data) == 0
            has_old_10k_filings = old_10k_count > 0
            has_recent_filings = recent_filings_count > 0
            
            is_complete = has_complete_financials and has_old_10k_filings and has_recent_filings
            
            return {
                "is_complete": is_complete,
                "has_complete_financials": has_complete_financials,
                "has_old_10k_filings": has_old_10k_filings,
                "has_recent_filings": has_recent_filings,
                "missing_financial_data": missing_financial_data,
                "old_10k_count": old_10k_count,
                "recent_filings_count": recent_filings_count,
                "oldest_required_year": oldest_required_year
            }
    
    async def get_latest_analysis_result(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest analysis result for a company."""
        query = text("""
            SELECT id, "companyId", "templateId", score, insights, "metricScores", "createdAt", "updatedAt"
            FROM "AnalysisResult"
            WHERE "companyId" = :company_id
            ORDER BY "createdAt" DESC
            LIMIT 1
        """)
        async with self.get_session() as session:
            result = await session.execute(query, {"company_id": company_id})
            row = result.fetchone()
            if row:
                data = dict(row._mapping)
                # Deserialize JSON strings back to Python dicts
                if isinstance(data.get('insights'), str):
                    data['insights'] = json.loads(data['insights'])
                if isinstance(data.get('metricScores'), str):
                    data['metricScores'] = json.loads(data['metricScores'])
                return data
        return None
    
    async def save_analysis_result(self, result_data: Dict[str, Any]):
        """Saves or updates an analysis result in the database."""
        async with self.get_session() as session:
            # Serialize insights and metricScores to JSON strings if they are dicts
            processed_data = result_data.copy()
            if isinstance(processed_data.get('insights'), dict):
                processed_data['insights'] = json.dumps(processed_data['insights'])
            if isinstance(processed_data.get('metricScores'), dict):
                processed_data['metricScores'] = json.dumps(processed_data['metricScores'])
            
            # Use a MERGE or ON CONFLICT statement to handle upsert
            stmt = text("""
                INSERT INTO "AnalysisResult" (id, "companyId", "templateId", score, insights, "metricScores", "createdAt", "updatedAt")
                VALUES (:id, :companyId, :templateId, :score, :insights, :metricScores, :createdAt, :updatedAt)
                ON CONFLICT (id) DO UPDATE SET
                    score = EXCLUDED.score,
                    insights = EXCLUDED.insights,
                    "metricScores" = EXCLUDED."metricScores",
                    "updatedAt" = EXCLUDED."updatedAt"
            """)
            await session.execute(stmt, processed_data)
            await session.commit() 