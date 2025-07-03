import os
import json
import asyncio
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file at the project root
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")

# If running script locally (not in Docker), connect to localhost
# The Docker container name 'postgres' will not be resolvable.
if __name__ == "__main__":
    if "@postgres" in DATABASE_URL:
        print("Script is run locally, replacing host '@postgres' with '@localhost' in DATABASE_URL.")
        DATABASE_URL = DATABASE_URL.replace("@postgres", "@localhost")

# The template data that was previously hardcoded
DEFAULT_TECH_TEMPLATE = {
    "id": "tech_v1",
    "name": "Technology Sector Scoring Model V1",
    "description": "A standard scoring model for established technology companies.",
    "dimensions": [
        {
            "name": "Profitability",
            "weight": 0.25,
            "metrics": [
                {
                    "name": "gross_margin",
                    "weight": 0.4,
                    "higher_is_better": True,
                    "thresholds": [
                        {"value": 0.6, "score": 90},
                        {"value": 0.4, "score": 70},
                        {"value": 0.2, "score": 40},
                        {"value": 0.0, "score": 10},
                    ],
                },
                {
                    "name": "net_profit_margin",
                    "weight": 0.6,
                    "higher_is_better": True,
                    "thresholds": [
                        {"value": 0.20, "score": 95},
                        {"value": 0.10, "score": 75},
                        {"value": 0.05, "score": 50},
                        {"value": 0.0, "score": 20},
                    ],
                },
            ],
        },
        {
            "name": "Growth",
            "weight": 0.25,
            "metrics": [
                {
                    "name": "revenue_growth_qoq",
                    "weight": 0.7,
                    "higher_is_better": True,
                    "thresholds": [
                        {"value": 0.15, "score": 95},
                        {"value": 0.05, "score": 70},
                        {"value": 0.0, "score": 40},
                        {"value": -1.0, "score": 10},
                    ],
                },
                {
                    "name": "eps_growth_qoq",
                    "weight": 0.3,
                    "higher_is_better": True,
                    "thresholds": [
                        {"value": 0.15, "score": 90},
                        {"value": 0.05, "score": 70},
                        {"value": 0.0, "score": 40},
                        {"value": -1.0, "score": 10},
                    ],
                },
            ],
        },
        {
            "name": "Balance Sheet",
            "weight": 0.20,
            "metrics": [
                {
                    "name": "debt_to_equity",
                    "weight": 0.5,
                    "higher_is_better": False,
                    "thresholds": [
                        {"value": 0.2, "score": 90},
                        {"value": 0.5, "score": 70},
                        {"value": 1.0, "score": 40},
                        {"value": 2.0, "score": 10},
                    ],
                },
                {
                    "name": "current_ratio",
                    "weight": 0.5,
                    "higher_is_better": True,
                    "thresholds": [
                        {"value": 2.0, "score": 90},
                        {"value": 1.5, "score": 75},
                        {"value": 1.0, "score": 50},
                        {"value": 0.5, "score": 10},
                    ],
                },
            ],
        },
        {
            "name": "Capital Allocation",
            "weight": 0.15,
            "metrics": [
                {
                    "name": "return_on_equity",
                    "weight": 1.0,
                    "higher_is_better": True,
                    "thresholds": [
                        {"value": 0.25, "score": 95},
                        {"value": 0.15, "score": 75},
                        {"value": 0.10, "score": 50},
                        {"value": 0.0, "score": 20},
                    ],
                }
            ],
        },
        {
            "name": "Valuation",
            "weight": 0.15,
            "metrics": [
                {
                    "name": "pe_ratio",
                    "weight": 1.0,
                    "higher_is_better": False,
                    "thresholds": [
                        {"value": 15, "score": 90},
                        {"value": 25, "score": 70},
                        {"value": 40, "score": 40},
                        {"value": 60, "score": 10},
                    ],
                }
            ],
        },
    ],
}

def seed_template():
    """Connects to the database and seeds the default tech template."""
    print(f"Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        print("Connection successful.")
        
        # Check if table exists
        inspector = inspect(engine)
        if not inspector.has_table("AnalysisTemplate"):
            print("Error: 'AnalysisTemplate' table not found.")
            print("Please run migrations before seeding.")
            return

        # Check if the template already exists
        result = connection.execute(
            text("SELECT id FROM \"AnalysisTemplate\" WHERE name = :name"),
            {"name": DEFAULT_TECH_TEMPLATE["name"]},
        ).first()

        if result:
            print(f"Template '{DEFAULT_TECH_TEMPLATE['name']}' already exists. Skipping.")
            return

        print(f"Inserting template '{DEFAULT_TECH_TEMPLATE['name']}'...")
        
        # Insert new template
        connection.execute(
            text("""
                INSERT INTO "AnalysisTemplate" (id, name, description, sectors, template, "createdAt", "updatedAt")
                VALUES (:id, :name, :description, :sectors, :template, NOW(), NOW())
            """),
            {
                "id": f"seed_{os.urandom(4).hex()}", # Generate a unique enough ID
                "name": DEFAULT_TECH_TEMPLATE["name"],
                "description": DEFAULT_TECH_TEMPLATE["description"],
                "sectors": ["Technology"],
                "template": json.dumps(DEFAULT_TECH_TEMPLATE),
            }
        )
        connection.commit()
        print("Template inserted successfully.")

if __name__ == "__main__":
    seed_template() 