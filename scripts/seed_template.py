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

        # --- Seeding Logic with Upsert ---

        # 1. Check if a template with the correct ID ('tech_v1') already exists.
        result_by_id = connection.execute(
            text("SELECT id FROM \"AnalysisTemplate\" WHERE id = :id"),
            {"id": DEFAULT_TECH_TEMPLATE["id"]},
        ).first()

        if result_by_id:
            print(f"Template with ID '{DEFAULT_TECH_TEMPLATE['id']}' found. Updating it.")
            connection.execute(
                text("""
                    UPDATE "AnalysisTemplate" 
                    SET name = :name, description = :description, sectors = :sectors, template = :template, "updatedAt" = NOW()
                    WHERE id = :id
                """),
                {
                    "id": DEFAULT_TECH_TEMPLATE["id"],
                    "name": DEFAULT_TECH_TEMPLATE["name"],
                    "description": DEFAULT_TECH_TEMPLATE["description"],
                    "sectors": ["Technology"],
                    "template": json.dumps(DEFAULT_TECH_TEMPLATE),
                }
            )
            connection.commit()
            print("Template updated successfully.")
            return

        # 2. If no template with the correct ID, check if one exists with the same name.
        result_by_name = connection.execute(
            text("SELECT id FROM \"AnalysisTemplate\" WHERE name = :name"),
            {"name": DEFAULT_TECH_TEMPLATE["name"]},
        ).first()

        if result_by_name:
            old_id = result_by_name[0]
            print(f"Template with name '{DEFAULT_TECH_TEMPLATE['name']}' found with old ID '{old_id}'.")
            print(f"Updating it to the correct ID '{DEFAULT_TECH_TEMPLATE['id']}'.")
            
            # To avoid unique constraint on ID if 'tech_v1' somehow exists, delete it first
            connection.execute(text("DELETE FROM \"AnalysisTemplate\" WHERE id = :id"), {"id": DEFAULT_TECH_TEMPLATE["id"]})
            
            # Update the old record to the new ID and content
            connection.execute(
                text("""
                    UPDATE "AnalysisTemplate"
                    SET id = :new_id, name = :name, description = :description, sectors = :sectors, template = :template, "updatedAt" = NOW()
                    WHERE id = :old_id
                """),
                {
                    "new_id": DEFAULT_TECH_TEMPLATE["id"],
                    "name": DEFAULT_TECH_TEMPLATE["name"],
                    "description": DEFAULT_TECH_TEMPLATE["description"],
                    "sectors": ["Technology"],
                    "template": json.dumps(DEFAULT_TECH_TEMPLATE),
                    "old_id": old_id
                }
            )
            connection.commit()
            print("Template updated successfully to new ID.")
            return
            
        # 3. If no template exists by ID or name, insert a new one.
        print(f"No existing template found. Inserting new template '{DEFAULT_TECH_TEMPLATE['name']}' with ID '{DEFAULT_TECH_TEMPLATE['id']}'...")
        connection.execute(
            text("""
                INSERT INTO "AnalysisTemplate" (id, name, description, sectors, template, "createdAt", "updatedAt")
                VALUES (:id, :name, :description, :sectors, :template, NOW(), NOW())
            """),
            {
                "id": DEFAULT_TECH_TEMPLATE["id"],
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