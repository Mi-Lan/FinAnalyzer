from typing import Dict, List, Type

from data_adapter.exceptions import ParserError
from data_adapter.logging import get_logger
from data_adapter.abc import BaseParser
from data_adapter.providers.fmp.models import (
    BalanceSheetStatement,
    CashFlowStatement,
    FinancialStatement,
    IncomeStatement,
    SECFiling,
)

logger = get_logger(__name__)


class FMPParser(BaseParser):
    """
    Parses raw FMP API data into Pydantic models.
    """

    MODEL_MAP: Dict[str, Type[FinancialStatement]] = {
        "income-statement": IncomeStatement,
        "balance-sheet-statement": BalanceSheetStatement,
        "cash-flow-statement": CashFlowStatement,
        "sec-filings-search/symbol": SECFiling,
    }

    def parse(
        self, endpoint: str, data: List[Dict]
    ) -> List[FinancialStatement]:
        """
        Parse a list of FMP financial statement data into a list of Pydantic models.
        """
        model = self.MODEL_MAP.get(endpoint)
        if not model:
            logger.error(f"No FMP parser model found for endpoint: {endpoint}")
            raise ParserError(f"No FMP parser model found for endpoint: {endpoint}")

        return [model(**item) for item in data] 