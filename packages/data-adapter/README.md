# Data Ingestion Adapter

This package provides a robust and extensible adapter for fetching financial data from various providers. It is designed with a plugin-based architecture that allows for easy addition of new data sources.

## Features

- **Async Support**: Uses `httpx` for non-blocking, asynchronous requests.
- **Caching**: Integrates with Redis to cache API responses and reduce redundant calls.
- **Rate Limiting**: Implements a token bucket algorithm with Redis for distributed rate limiting.
- **Data Parsing**: Uses Pydantic models for data validation and parsing.
- **Plugin Architecture**: Easily extensible to support new data providers.
- **Structured Logging**: Provides structured logging for monitoring and debugging.
- **Custom Exceptions**: Defines custom exceptions for specific error handling.

## Architecture

The adapter is built around a few key components:

- **`DataSourceAdapter`**: An abstract base class that defines the common interface for all data provider adapters.
- **`FMPAdapter`**: A concrete implementation of the `DataSourceAdapter` for the Financial Modeling Prep API.
- **`RateLimiter`**: A token bucket rate limiter implemented with Redis.
- **`Parser`**: A class that uses Pydantic models to parse and validate API responses.
- **`get_adapter` Factory**: A factory function that discovers and instantiates the correct adapter based on a configuration.

## Extending the Adapter

To add a new data provider, you need to:

1.  **Create a Provider Directory**: Create a new subdirectory inside `packages/data-adapter/src/data_adapter/providers/` for your new provider (e.g., `coolfinance/`).
2.  **Create an Adapter Class**: Inside your new directory, create an `adapter.py` file with a class that inherits from `DataSourceAdapter` and implements the `fetch_data` method.
3.  **Add Pydantic Models**: Create a `models.py` file in your provider's directory to define the Pydantic models for the data structures returned by the new provider's API.
4.  **Create a Parser Class**: Create a `parser.py` with a class that inherits from `BaseParser` and implements the `parse` method for your provider's data.
5.  **Register the New Provider**: In `factory.py`, import your new adapter and parser and add them to the `ADAPTER_REGISTRY`.
6.  **Add Configuration**: Update your root `.env` file with the necessary settings for the new provider (e.g., `DATA_PROVIDERS__COOLFINANCE__API_KEY=your_key`).

### Example: Adding a "CoolFinance" Provider

1.  **Directory Structure**:

    ```
    providers/
    └── coolfinance/
        ├── __init__.py
        ├── adapter.py
        ├── models.py
        └── parser.py
    ```

2.  **`providers/coolfinance/adapter.py`**:

    ```python
    class CoolFinanceAdapter(DataSourceAdapter):
        # ... implementation
    ```

3.  **`providers/coolfinance/models.py`**:

    ```python
    class CoolFinanceStatement(BaseModel):
        # ... implementation
    ```

4.  **`providers/coolfinance/parser.py`**:

    ```python
    class CoolFinanceParser(BaseParser):
        # ... implementation
    ```

5.  **Update `factory.py`**:

    ```python
    from .providers.coolfinance.adapter import CoolFinanceAdapter
    from .providers.coolfinance.parser import CoolFinanceParser

    ADAPTER_REGISTRY = {
        "fmp": (FMPAdapter, FMPParser),
        "coolfinance": (CoolFinanceAdapter, CoolFinanceParser),
    }
    ```

6.  **Update `.env`**:
    ```
    DATA_PROVIDERS__COOLFINANCE__API_KEY=your_coolfinance_key
    ```
