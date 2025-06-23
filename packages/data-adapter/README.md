# Data Adapter Package

A Python-based data ingestion layer for the FinAnalyzer platform, providing standardized interfaces for financial data providers.

## Overview

The data adapter package implements a flexible, extensible architecture for integrating various financial data sources. It provides a common interface for data retrieval, validation, and transformation while supporting multiple providers through a plugin-based system.

## Architecture

### Core Components

- **Abstract Base Classes** (`abc.py`): Define interfaces for data providers
- **Provider Factory** (`factory.py`): Manages provider instantiation and configuration
- **Configuration Management** (`config.py`): Handles settings and API credentials
- **Rate Limiting** (`rate_limiter.py`): Implements request throttling and backoff
- **Transport Layer** (`transports.py`): HTTP client abstractions with retry logic

### Provider Implementation

The package currently supports:

- **Financial Modeling Prep (FMP)** API integration
- Extensible provider interface for additional data sources
- Standardized data models with Pydantic validation

## Installation

```bash
# From project root
cd packages/data-adapter

# Install in development mode
pip install -e .

# Or install dependencies only
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from data_adapter import create_provider
from data_adapter.config import Config

# Initialize configuration
config = Config()

# Create provider instance
provider = create_provider('fmp', config)

# Fetch company data
company_data = await provider.get_company_profile('AAPL')
financial_data = await provider.get_financial_statements('AAPL', period='quarterly')
```

### Configuration

Set up your API credentials:

```bash
# Environment variables
export FMP_API_KEY="your_fmp_api_key"
export FMP_BASE_URL="https://financialmodelingprep.com/api/v3"

# Or use .env file in project root
FMP_API_KEY=your_fmp_api_key
FMP_BASE_URL=https://financialmodelingprep.com/api/v3
```

### Error Handling

The adapter includes comprehensive error handling:

```python
from data_adapter.exceptions import DataAdapterError, RateLimitExceeded

try:
    data = await provider.get_company_profile('AAPL')
except RateLimitExceeded as e:
    print(f"Rate limit hit: {e.retry_after} seconds")
except DataAdapterError as e:
    print(f"Data adapter error: {e}")
```

## Data Models

All data is validated using Pydantic models:

```python
from data_adapter.providers.fmp.models import (
    CompanyProfile,
    FinancialStatements,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement
)

# Automatic validation and type conversion
profile: CompanyProfile = await provider.get_company_profile('AAPL')
print(f"Company: {profile.company_name}")
print(f"Market Cap: {profile.market_cap}")
```

## Testing

```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=data_adapter --cov-report=html

# Run specific test files
python -m pytest tests/test_fmp_adapter.py -v
```

## Development

### Adding New Providers

1. Create provider directory: `src/data_adapter/providers/new_provider/`
2. Implement the provider interface from `abc.py`
3. Define data models in `models.py`
4. Add provider to factory in `factory.py`
5. Write tests in `tests/test_new_provider.py`

### Provider Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from data_adapter.abc import BaseDataProvider

class NewProvider(BaseDataProvider):
    async def get_company_profile(self, symbol: str) -> CompanyProfile:
        """Fetch company profile data"""
        pass

    async def get_financial_statements(
        self,
        symbol: str,
        period: str = 'annual'
    ) -> FinancialStatements:
        """Fetch financial statements"""
        pass
```

## Configuration Options

| Environment Variable     | Description                     | Default                                    |
| ------------------------ | ------------------------------- | ------------------------------------------ |
| `FMP_API_KEY`            | Financial Modeling Prep API key | Required                                   |
| `FMP_BASE_URL`           | FMP API base URL                | `https://financialmodelingprep.com/api/v3` |
| `DATA_ADAPTER_LOG_LEVEL` | Logging level                   | `INFO`                                     |
| `RATE_LIMIT_REQUESTS`    | Max requests per minute         | `300`                                      |
| `REQUEST_TIMEOUT`        | Request timeout in seconds      | `30`                                       |

## Integration with FinAnalyzer

This package is designed to integrate seamlessly with the FinAnalyzer monorepo:

- **TypeScript Interop**: Data models designed for easy serialization to TypeScript
- **FastAPI Integration**: Compatible with FastAPI backend for API endpoints
- **Docker Support**: Included in multi-stage Docker builds
- **Shared Configuration**: Uses monorepo-wide environment configuration

## Performance Considerations

- **Rate Limiting**: Built-in request throttling to respect API limits
- **Caching**: Transport layer supports response caching
- **Async Operations**: Fully async for concurrent data fetching
- **Connection Pooling**: HTTP client reuses connections for efficiency

## Error Handling

The package provides structured error handling:

- `DataAdapterError`: Base exception class
- `ProviderNotFoundError`: Unknown provider requested
- `ConfigurationError`: Invalid configuration
- `RateLimitExceeded`: API rate limit hit
- `ValidationError`: Data validation failed

## Logging

Comprehensive logging for debugging and monitoring:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('data_adapter')

# Logs include:
# - API requests and responses
# - Rate limiting events
# - Data validation errors
# - Provider initialization
```

## License

This package is part of the FinAnalyzer project and is licensed under the MIT License.
