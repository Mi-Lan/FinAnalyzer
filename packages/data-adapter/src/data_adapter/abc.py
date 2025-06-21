from abc import ABC, abstractmethod
from typing import Any, Dict, List

from pydantic import BaseModel


class DataSourceAdapter(ABC):
    """
    Abstract base class for data source adapters.
    Defines the interface for fetching data from a financial data provider.
    """

    @abstractmethod
    async def fetch_data(self, endpoint: str, params: Dict[str, Any]) -> List[BaseModel]:
        """
        Fetch and parse data from the data source.
        """
        pass


class BaseParser(ABC):
    """
    Abstract base class for data parsers.
    """

    @abstractmethod
    def parse(self, endpoint: str, data: List[Dict]) -> List[BaseModel]:
        """
        Parse raw data into a list of Pydantic models.
        """
        pass 