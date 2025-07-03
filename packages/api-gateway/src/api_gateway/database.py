import os
from databases import Database
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, JSON

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/db")

database = Database(DATABASE_URL)

metadata = MetaData()

analysis_templates = Table(
    "AnalysisTemplate",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String, unique=True, index=True),
    Column("template", JSON),
    # Add other columns if needed for queries, but we only need name and template for now
)

async def connect_db():
    await database.connect()

async def disconnect_db():
    await database.disconnect()

async def fetch_template_by_name(name: str):
    """Fetches a single analysis template by its unique name."""
    query = analysis_templates.select().where(analysis_templates.c.name == name)
    result = await database.fetch_one(query)
    return result

async def fetch_all_template_names():
    """Fetches the names of all available analysis templates."""
    query = analysis_templates.select().with_only_columns(analysis_templates.c.name)
    results = await database.fetch_all(query)
    return [row['name'] for row in results] 