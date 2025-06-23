# API Gateway

This package contains the FastAPI application that serves as the main backend gateway for the FinAnalyzer frontend.

## Overview

The API Gateway is responsible for:

- Providing a secure and unified entry point for all frontend requests.
- Authenticating incoming requests using an API key.
- Routing requests to the appropriate downstream services (coming soon).
- Validating incoming and outgoing data structures using Pydantic models.

## Getting Started

### Prerequisites

- Python 3.11+
- Poetry for dependency management

### Installation

1.  **Navigate to the package directory:**

    ```bash
    cd packages/api-gateway
    ```

2.  **Install dependencies:**

    ```bash
    poetry install
    ```

3.  **Set up environment variables:**

    Create a `.env` file in this directory (`packages/api-gateway/.env`). For local development, you can also add this to the root `.env` file of the monorepo.

    Add the following line:

    ```
    API_KEY="your-secret-key"
    ```

    Replace `"your-secret-key"` with a secure, random string.

### Running the Service

To run the API gateway locally, use the following command from within the `packages/api-gateway` directory:

```bash
poetry run uvicorn api_gateway.main:app --reload
```

The service will be available at `http://127.0.0.1:8000`.

## API Endpoints

All endpoints are prefixed with `/api` and require an API key for authentication.

### Authentication

You must provide your API key in the `X-API-Key` header for all requests.

### Endpoints

- `GET /companies`: Returns a list of companies.
- `GET /companies/{ticker}`: Returns detailed information for a specific company.
- `GET /analysis/screen`: Allows for filtering and screening of companies.
- `POST /analysis/bulk`: Submits a list of tickers for bulk analysis.
- `GET /analysis/bulk/{job_id}`: Retrieves the status of a bulk analysis job.

## Testing

To run the integration tests, use the following command from within the `packages/api-gateway` directory:

```bash
poetry run pytest
```
