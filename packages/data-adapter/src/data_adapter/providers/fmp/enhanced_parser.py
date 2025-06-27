from typing import Dict, List, Type, Any, Optional, Union
from datetime import datetime
import re

from pydantic import ValidationError, BaseModel
from data_adapter.exceptions import ParserError
from data_adapter.logging import get_logger
from data_adapter.abc import BaseParser
from data_adapter.providers.fmp.models import (
    BalanceSheetStatement,
    CashFlowStatement,
    CompanyProfile,
    FinancialStatement,
    IncomeStatement,
    SECFiling,
    TenKFiling,
    TenQFiling,
)

logger = get_logger(__name__)


class EnhancedFMPParser(BaseParser):
    """
    Enhanced parser for FMP API data with robust error handling,
    data transformation, and support for multiple data types.
    """

    MODEL_MAP: Dict[str, Type[BaseModel]] = {
        # Financial statements
        "income-statement": IncomeStatement,
        "balance-sheet-statement": BalanceSheetStatement,
        "cash-flow-statement": CashFlowStatement,
        
        # SEC filings
        "sec_filings": SECFiling,
        "sec-filings": SECFiling,
        "sec-filings-search/symbol": SECFiling,
        
        # Company profile
        "profile": CompanyProfile,
        "company-profile": CompanyProfile,
    }

    def __init__(self):
        super().__init__()
        self.parsing_stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "warnings": 0
        }

    def parse(self, endpoint: str, data: Union[List[Dict], Dict]) -> List[BaseModel]:
        """
        Enhanced parse method with error handling and data transformation.
        
        Args:
            endpoint: The API endpoint name
            data: Raw data from the API (list or single dict)
            
        Returns:
            List of parsed Pydantic models
        """
        if not data:
            logger.warning(f"No data provided for endpoint: {endpoint}")
            return []

        # Normalize data to list format
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            raise ParserError(f"Invalid data format for endpoint {endpoint}: expected list or dict")

        model_class = self._get_model_class(endpoint)
        parsed_items = []
        
        self.parsing_stats["total_processed"] += len(data)
        
        for i, item in enumerate(data):
            try:
                # Pre-process the data
                processed_item = self._preprocess_item(endpoint, item)
                
                # Handle special cases for different data types
                if endpoint in ['sec_filings', 'sec-filings']:
                    parsed_item = self._parse_sec_filing(processed_item)
                else:
                    # Standard parsing
                    parsed_item = model_class(**processed_item)
                
                parsed_items.append(parsed_item)
                self.parsing_stats["successful"] += 1
                
            except ValidationError as e:
                self.parsing_stats["failed"] += 1
                logger.error(f"Validation error for item {i} in {endpoint}: {e}")
                
                # Try to recover with relaxed validation
                try:
                    recovered_item = self._attempt_recovery(endpoint, item, e)
                    if recovered_item:
                        parsed_items.append(recovered_item)
                        self.parsing_stats["warnings"] += 1
                        logger.warning(f"Recovered item {i} in {endpoint} with missing/invalid fields")
                except Exception as recovery_error:
                    logger.error(f"Failed to recover item {i} in {endpoint}: {recovery_error}")
                    continue
                    
            except Exception as e:
                self.parsing_stats["failed"] += 1
                logger.error(f"Unexpected error parsing item {i} in {endpoint}: {e}")
                continue

        logger.info(f"Parsed {len(parsed_items)}/{len(data)} items from {endpoint}")
        return parsed_items

    def _get_model_class(self, endpoint: str) -> Type[BaseModel]:
        """Get the appropriate model class for an endpoint."""
        model_class = self.MODEL_MAP.get(endpoint)
        if not model_class:
            # Try to find a match with fuzzy matching
            endpoint_normalized = endpoint.lower().replace('_', '-')
            for key, model in self.MODEL_MAP.items():
                if key.lower().replace('_', '-') == endpoint_normalized:
                    return model
            
            raise ParserError(f"No parser model found for endpoint: {endpoint}")
        return model_class

    def _preprocess_item(self, endpoint: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess raw data before validation.
        Handles common data transformation and cleaning tasks.
        """
        if not isinstance(item, dict):
            raise ParserError(f"Expected dict for preprocessing, got {type(item)}")

        processed = item.copy()
        
        # Common preprocessing steps
        processed = self._clean_numeric_fields(processed)
        processed = self._normalize_date_fields(processed)
        processed = self._handle_missing_fields(endpoint, processed)
        processed = self._normalize_field_names(processed)
        
        # Only apply numeric cleaning to financial statement data
        if endpoint in ["income-statement", "balance-sheet-statement", "cash-flow-statement"]:
            processed = self._clean_numeric_fields(processed)

        return processed

    def _clean_numeric_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize numeric fields."""
        # More specific list of numeric fields
        numeric_fields = [
            'revenue', 'netIncome', 'eps', 'grossProfit', 'totalAssets',
            'totalLiabilities', 'totalEquity', 'operatingCashFlow', 'freeCashFlow',
            # Add other known numeric fields from your models here
        ]

        for key, value in data.items():
            # Only process fields that are known to be numeric or look like numbers
            if key in numeric_fields:
                if isinstance(value, str):
                    if value.lower() in ['null', 'none', 'n/a', 'na', '-', '']:
                        data[key] = 0.0
                    elif value.replace('.', '').replace('-', '').replace('+', '').isdigit():
                        try:
                            data[key] = float(value)
                        except ValueError:
                            logger.warning(f"Could not convert '{value}' to float for field '{key}'")
                            data[key] = 0.0
                elif value is None:
                    data[key] = 0.0
        
        return data

    def _normalize_date_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize date fields to consistent format."""
        date_fields = [
            'date', 'filingDate', 'acceptedDate', 'reportDate', 'calendarYear',
            'filing_date', 'accepted_date', 'report_date', 'calendar_year'
        ]
        
        for field in date_fields:
            if field in data and data[field]:
                try:
                    # Try to parse and reformat date
                    if isinstance(data[field], str):
                        # Handle various date formats
                        date_str = data[field].strip()
                        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                            # Already in YYYY-MM-DD format
                            pass
                        elif re.match(r'\d{4}', date_str) and len(date_str) == 4:
                            # Just year, leave as is
                            pass
                        else:
                            # Try to parse and reformat
                            try:
                                parsed_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                                data[field] = parsed_date.strftime('%Y-%m-%d')
                            except ValueError:
                                # If parsing fails, leave as is
                                pass
                except Exception as e:
                    logger.warning(f"Could not normalize date field '{field}': {e}")
        
        return data

    def _handle_missing_fields(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle missing fields by providing default values."""
        
        # Default values for different endpoint types
        defaults = {
            "income-statement": {
                "revenue": 0.0,
                "netIncome": 0.0,
                "eps": 0.0,
                "grossProfit": 0.0,
            },
            "balance-sheet-statement": {
                "totalAssets": 0.0,
                "totalLiabilities": 0.0,
                "totalEquity": 0.0,
            },
            "cash-flow-statement": {
                "netIncome": 0.0,
                "operatingCashFlow": 0.0,
                "freeCashFlow": 0.0,
            }
        }
        
        endpoint_defaults = defaults.get(endpoint, {})
        for field, default_value in endpoint_defaults.items():
            if field not in data or data[field] is None:
                data[field] = default_value
                
        return data

    def _normalize_field_names(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize field names to handle variations."""
        field_mappings = {
            # SEC filings endpoint mappings
            'filingDate': 'filing_date',
            'acceptedDate': 'accepted_date',
            'formType': 'form',
            'link': 'filing_url',
            'finalLink': 'report_url',
            # Common variations
            'company_name': 'companyName',
            'fiscal_year': 'fiscalYear',
            'filing_url': 'filingURL',
            'report_url': 'reportURL',
            'accepted_date': 'acceptedDate',
            'filing_date': 'filingDate',
            'report_date': 'reportDate',
        }
        normalized_data = {}
        for key, value in data.items():
            normalized_key = field_mappings.get(key, key)
            # For SEC filings, ensure all fields are strings
            if normalized_key in ['symbol', 'cik', 'filing_date', 'accepted_date', 'form', 'filing_url', 'report_url'] and value is not None:
                normalized_data[normalized_key] = str(value)
            else:
                normalized_data[normalized_key] = value
        return normalized_data

    def _parse_sec_filing(self, data: Dict[str, Any]) -> SECFiling:
        """Special handling for SEC filing data."""
        
        # Determine if this is a 10-K or 10-Q based on the form field
        form = data.get('form', '').upper()
        
        if form == '10-K':
            return TenKFiling(**data)
        elif form == '10-Q':
            # Ensure quarter field is present for 10-Q
            if 'quarter' not in data:
                # Try to extract quarter from period or reportDate
                period = data.get('period', '')
                if 'Q1' in period.upper():
                    data['quarter'] = 1
                elif 'Q2' in period.upper():
                    data['quarter'] = 2
                elif 'Q3' in period.upper():
                    data['quarter'] = 3
                elif 'Q4' in period.upper():
                    data['quarter'] = 4
                else:
                    data['quarter'] = 1  # Default
            return TenQFiling(**data)
        else:
            # Generic SEC filing
            return SECFiling(**data)

    def _attempt_recovery(self, endpoint: str, original_data: Dict[str, Any], error: ValidationError) -> Optional[BaseModel]:
        """
        Attempt to recover from validation errors by using more lenient parsing.
        """
        try:
            # Create a copy with required fields filled with defaults
            recovery_data = original_data.copy()
            
            # Extract missing field information from the error
            missing_fields = []
            for error_detail in error.errors():
                if error_detail['type'] == 'missing':
                    missing_fields.append(error_detail['loc'][0])
            
            # Fill missing required fields with sensible defaults
            for field in missing_fields:
                if field in ['symbol', 'ticker']:
                    recovery_data[field] = 'UNKNOWN'
                elif field in ['cik']:
                    recovery_data[field] = '0000000000'
                elif field in ['fiscalYear']:
                    recovery_data[field] = '2024'
                elif field in ['period']:
                    recovery_data[field] = 'FY'
                elif 'date' in field.lower():
                    recovery_data[field] = '2024-01-01'
                elif field in ['form']:
                    recovery_data[field] = 'UNKNOWN'
                elif 'url' in field.lower():
                    recovery_data[field] = 'https://example.com'
                elif field == 'type':
                    recovery_data[field] = 'filing'
                else:
                    # For numeric fields, use 0
                    recovery_data[field] = 0.0
            
            # Try parsing again
            model_class = self._get_model_class(endpoint)
            processed_data = self._preprocess_item(endpoint, recovery_data)
            
            if endpoint in ['sec_filings', 'sec-filings']:
                return self._parse_sec_filing(processed_data)
            else:
                return model_class(**processed_data)
                
        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")
            return None

    def get_parsing_stats(self) -> Dict[str, int]:
        """Get parsing statistics."""
        return self.parsing_stats.copy()

    def reset_stats(self) -> None:
        """Reset parsing statistics."""
        self.parsing_stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "warnings": 0
        } 