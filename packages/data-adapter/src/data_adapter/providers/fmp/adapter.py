from typing import Any, Dict, List

import httpx
from pydantic import ValidationError

from data_adapter.abc import DataSourceAdapter
from data_adapter.config import ProviderSettings
from data_adapter.exceptions import APIError, ParserError
from data_adapter.logging import get_logger
from data_adapter.providers.fmp.models import FinancialStatement
from data_adapter.providers.fmp.parser import FMPParser

logger = get_logger(__name__)


class FMPAdapter(DataSourceAdapter):
    """
    Data source adapter for the Financial Modeling Prep (FMP) API.
    """

    BASE_URL = "https://financialmodelingprep.com/stable"

    def __init__(self, client: httpx.AsyncClient, settings: ProviderSettings, parser: FMPParser):
        self.client = client
        self.settings = settings
        self.parser = parser

    async def fetch_data(
        self, endpoint: str, params: Dict[str, Any]
    ) -> List[FinancialStatement]:
        """
        Fetch and parse data from the FMP API using a pre-configured client.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        params_with_key = {**params, "apikey": self.settings.api_key}

        try:
            response = await self.client.get(url, params=params_with_key)
            response.raise_for_status()
            data = response.json()
            return self.parser.parse(endpoint, data) 
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.request.url} - {e}")
            raise APIError(f"API request failed with status {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {e.request.url} - {e}")
            raise APIError("API request failed") from e
        except ValidationError as e:
            logger.error(f"Data validation error for FMP endpoint {endpoint}: {e}")
            raise ParserError("Failed to parse or validate FMP API response") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred in FMPAdapter: {e}")
            raise 