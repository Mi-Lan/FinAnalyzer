# Data Adapter Package

A Python-based data ingestion layer for the FinAnalyzer platform, providing standardized interfaces for financial data providers, with integrated support for data persistence and asynchronous processing.

## Overview

The data adapter package implements a flexible, extensible architecture for integrating various financial data sources. It provides a common interface for data retrieval, parsing, validation, and transformation. The package now includes a **storage layer** to persist financial data in a PostgreSQL database and an **async processor** for handling high-throughput, concurrent data ingestion tasks.

## Architecture

### Core Components

- **Abstract Base Classes** (`abc.py`): Define interfaces for data providers and parsers.
- **Provider Factory** (`factory.py`): Manages provider instantiation for both standard and storage-enabled adapters.
- **Configuration Management** (`config.py`): Handles settings for providers and the database connection.
- **Database Manager** (`database.py`): Manages asynchronous database connections, sessions, and CRUD operations using SQLAlchemy and `asyncpg`.
- **Async Processor** (`async_processor.py`): Orchestrates concurrent data ingestion and retrieval tasks with configurable concurrency limits.
- **Enhanced Parser** (`enhanced_parser.py`): A robust parsing engine with data cleaning, validation, error recovery, and support for multiple data formats.
- **Transport & Rate Limiting**: The underlying transport layer (`transports.py`, `rate_limiter.py`) handles caching (Redis) and API rate limiting.

### Provider Implementation

The package currently supports:

- **Financial Modeling Prep (FMP)** API integration.
- A `StorageEnabledFMPAdapter` that extends the base adapter with database persistence logic.
- Standardized data models with Pydantic for API data and SQLAlchemy for database schema.

## Installation

```bash
# Navigate to the package directory from the project root
cd packages/data-adapter

# Install all dependencies using Poetry
poetry install
```

## Usage

The factory function `get_adapter` can create two types of adapters: a standard, stateless adapter or a storage-enabled one.

### Basic Usage (Stateless)

This adapter fetches data from the API without interacting with the database.

```python
from data_adapter import get_adapter

# Create a standard FMP adapter instance
fmp_adapter = get_adapter("fmp")

# Fetch data directly from the API
income_statements = await fmp_adapter.fetch_data(
    "income-statement",
    {"symbol": "AAPL", "period": "annual"}
)
print(f"Fetched {len(income_statements)} income statements for AAPL.")
```

### Storage-Enabled Usage

This adapter fetches data and persists it to the PostgreSQL database.

```python
from data_adapter import get_adapter

# Create a storage-enabled FMP adapter instance
storage_adapter = get_adapter("fmp", enable_storage=True)

# Fetch financial statements for a company and store them
# This single call fetches income statements, balance sheets, and cash flows
# and merges them into a single record per fiscal period in the database.
results = await storage_adapter.fetch_and_store_company_financials(
    ticker="AAPL",
    years=[2023],
    periods=['annual']
)
print("Stored data results:", results)

# Retrieve the consolidated data from the database
stored_data = await storage_adapter.get_stored_company_data("AAPL")
print(f"Retrieved {len(stored_data['financial_data'])} records for AAPL from the database.")
```

### Asynchronous Batch Processing

The `AsyncProcessor` is designed for high-throughput operations on multiple tickers.

```python
import asyncio
from data_adapter.async_processor import AsyncProcessor

async def main():
    # Initialize the processor with a concurrency limit of 5
    processor = AsyncProcessor(concurrency_limit=5)

    tickers = ["AAPL", "MSFT", "GOOGL"]

    # Fetch and store data for multiple tickers in parallel
    await processor.fetch_and_store_for_tickers(
        tickers=tickers,
        years=[2023],
        periods=['annual']
    )

    # Retrieve all stored data in parallel
    all_data = await processor.get_stored_data_for_tickers(tickers)
    for ticker, data in all_data.items():
        print(f"Data retrieved for {ticker}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

Set up your API credentials and database URL in a `.env` file in the `packages/data-adapter` directory.

```bash
# .env file content
FMP_API_KEY=your_fmp_api_key
DATABASE_URL=postgresql://user:password@localhost:5432/findb
```

| Environment Variable | Description                     | Default                           |
| :------------------- | :------------------------------ | :-------------------------------- |
| `FMP_API_KEY`        | Financial Modeling Prep API key | **Required**                      |
| `DATABASE_URL`       | PostgreSQL connection URL       | **Required for storage features** |
| `REDIS_HOST`         | Redis host for caching          | `localhost`                       |
| `REDIS_PORT`         | Redis port for caching          | `6379`                            |

## Data Models

- **Pydantic Models** (`providers/fmp/models.py`): Used for validating and structuring the raw data from the FMP API.
- **SQLAlchemy Models** (`models.py`): Define the database schema, mirroring the structure in `packages/database/prisma/schema.prisma`.

## Database & Storage

The adapter's storage functionality is built around a `DatabaseManager` that handles all database interactions.

- **Asynchronous Operations**: Uses `asyncpg` and `SQLAlchemy`'s asyncio extension for non-blocking database calls.
- **Data Merging**: When storing data, the system performs an "upsert." If a record for a company's fiscal period already exists, the new financial statements are merged into the existing JSONB `data` field, ensuring a complete, consolidated record.
- **JSONB Storage**: Financial statement data is stored in a single `JSONB` column, allowing for flexibility while still being queryable.

## Testing

```bash
# Run all tests
poetry run pytest tests/

# Run specific integration tests (requires Docker services to be running)
poetry run pytest tests/test_storage_integration.py -s -v
poetry run pytest tests/test_async_processor.py -s -v
```

## Development

### Adding New Providers

The process remains the same, with the option to also create a storage-enabled version of your new adapter.

1.  Create provider directory: `src/data_adapter/providers/new_provider/`.
2.  Implement the `DataSourceAdapter` interface from `abc.py`.
3.  Define Pydantic models in `models.py`.
4.  Add the provider to `ADAPTER_REGISTRY` in `factory.py`.
5.  **(Optional)** Create a `StorageEnabledNewProviderAdapter` that inherits from your base adapter and implements storage logic. Add it to the `STORAGE_ADAPTER_REGISTRY`.
6.  Write tests in `tests/test_new_provider.py`.

## Error Handling

The package provides structured error handling for API, database, and parsing operations.

- `DataAdapterError`: Base exception class.
- `ConfigurationError`: Invalid or missing configuration.
- `APIError`: An error related to an external API call.
- `ParserError`: Failure during data parsing or validation.

## License

This package is part of the FinAnalyzer project and is licensed under the MIT License.
