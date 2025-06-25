import pytest
from typing import Dict, Any
from data_adapter.providers.fmp.enhanced_parser import EnhancedFMPParser
from data_adapter.providers.fmp.models import (
    IncomeStatement, BalanceSheetStatement, CashFlowStatement,
    SECFiling, TenKFiling, TenQFiling, CompanyProfile
)
from data_adapter.exceptions import ParserError


class TestEnhancedFMPParser:
    """Test suite for the EnhancedFMPParser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EnhancedFMPParser()
    
    def test_parse_income_statement_valid_data(self):
        """Test parsing valid income statement data."""
        data = [{
            "date": "2024-12-31",
            "symbol": "AAPL",
            "reportedCurrency": "USD",
            "cik": "0000320193",
            "filingDate": "2024-01-01",
            "acceptedDate": "2024-01-01 18:00:00",
            "fiscalYear": "2024",
            "period": "FY",
            "revenue": 394328000000,
            "costOfRevenue": 223546000000,
            "grossProfit": 170782000000,
            "netIncome": 97394000000,
            "eps": 6.11
        }]
        
        result = self.parser.parse("income-statement", data)
        
        assert len(result) == 1
        assert isinstance(result[0], IncomeStatement)
        assert result[0].symbol == "AAPL"
        assert result[0].revenue == 394328000000
        assert result[0].net_income == 97394000000
    
    def test_parse_with_missing_fields_recovery(self):
        """Test parsing with missing fields and automatic recovery."""
        data = [{
            "symbol": "AAPL",
            "fiscalYear": "2024",
            "period": "FY",
            "revenue": 394328000000,
            # Missing many required fields
        }]
        
        result = self.parser.parse("income-statement", data)
        
        # Should recover and create valid object with defaults
        assert len(result) == 1
        assert isinstance(result[0], IncomeStatement)
        assert result[0].symbol == "AAPL"
        assert result[0].revenue == 394328000000
        
        # Check parsing stats
        stats = self.parser.get_parsing_stats()
        assert stats["warnings"] > 0  # Should have warnings from recovery
    
    def test_parse_numeric_field_cleaning(self):
        """Test cleaning of numeric fields with various formats."""
        data = [{
            "symbol": "TEST",
            "fiscalYear": "2024",
            "period": "FY",
            "revenue": "1000000.50",  # String number
            "netIncome": "null",      # Null string
            "eps": None,              # None value
            "grossProfit": "-",       # Dash
            "operatingIncome": "N/A", # N/A
            "ebitda": 500000,         # Already numeric
        }]
        
        result = self.parser.parse("income-statement", data)
        
        assert len(result) == 1
        income_stmt = result[0]
        
        assert income_stmt.revenue == 1000000.50  # Converted from string
        assert income_stmt.net_income == 0.0      # Converted from "null"
        assert income_stmt.eps == 0.0             # Converted from None
        assert income_stmt.gross_profit == 0.0    # Converted from "-"
        assert income_stmt.ebitda == 500000       # Unchanged
    
    def test_parse_sec_filing_10k(self):
        """Test parsing 10-K SEC filing."""
        data = [{
            "symbol": "AAPL",
            "cik": "0000320193",
            "acceptedDate": "2024-01-01 18:00:00",
            "filingDate": "2024-01-01",
            "reportDate": "2023-12-31",
            "form": "10-K",
            "filingURL": "https://example.com/filing",
            "reportURL": "https://example.com/report",
            "type": "annual"
        }]
        
        result = self.parser.parse("sec_filings", data)
        
        assert len(result) == 1
        assert isinstance(result[0], TenKFiling)
        assert result[0].symbol == "AAPL"
        assert result[0].form == "10-K"
    
    def test_parse_sec_filing_10q(self):
        """Test parsing 10-Q SEC filing with quarter extraction."""
        data = [{
            "symbol": "AAPL", 
            "cik": "0000320193",
            "acceptedDate": "2024-01-01 18:00:00",
            "filingDate": "2024-01-01",
            "reportDate": "2024-03-31",
            "form": "10-Q",
            "filingURL": "https://example.com/filing",
            "reportURL": "https://example.com/report",
            "type": "quarterly",
            "period": "Q1"
        }]
        
        result = self.parser.parse("sec-filings", data)
        
        assert len(result) == 1
        assert isinstance(result[0], TenQFiling)
        assert result[0].form == "10-Q"
        assert result[0].quarter == 1  # Extracted from period
    
    def test_parse_company_profile(self):
        """Test parsing company profile data."""
        data = [{
            "symbol": "AAPL",
            "companyName": "Apple Inc.",
            "price": 150.00,
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "website": "https://apple.com",
            "description": "Apple Inc. designs, manufactures, and markets smartphones..."
        }]
        
        result = self.parser.parse("profile", data)
        
        assert len(result) == 1
        assert isinstance(result[0], CompanyProfile)
        assert result[0].symbol == "AAPL"
        assert result[0].company_name == "Apple Inc."
        assert result[0].price == 150.00
    
    def test_parse_date_normalization(self):
        """Test date field normalization."""
        data = [{
            "symbol": "TEST",
            "fiscalYear": "2024",
            "period": "FY",
            "date": "2024-12-31 00:00:00",  # Full datetime
            "filingDate": "2024-01-01",     # Already normalized
            "acceptedDate": "2023",          # Just year
        }]
        
        result = self.parser.parse("income-statement", data)
        
        assert len(result) == 1
        # Date normalization should have occurred during preprocessing
        assert "2024-12-31" in result[0].date
    
    def test_parse_invalid_endpoint(self):
        """Test handling of invalid endpoint."""
        data = [{"symbol": "TEST"}]
        
        with pytest.raises(ParserError, match="No parser model found"):
            self.parser.parse("invalid-endpoint", data)
    
    def test_parse_empty_data(self):
        """Test parsing empty data."""
        result = self.parser.parse("income-statement", [])
        assert result == []
        
        result = self.parser.parse("income-statement", None)
        assert result == []
    
    def test_parse_single_dict_input(self):
        """Test parsing single dictionary input (not wrapped in list)."""
        data = {
            "symbol": "AAPL",
            "fiscalYear": "2024",
            "period": "FY",
            "revenue": 1000000
        }
        
        result = self.parser.parse("income-statement", data)
        
        assert len(result) == 1
        assert isinstance(result[0], IncomeStatement)
        assert result[0].symbol == "AAPL"
    
    def test_fuzzy_endpoint_matching(self):
        """Test fuzzy endpoint matching for variations."""
        data = [{"symbol": "TEST", "fiscalYear": "2024", "period": "FY"}]
        
        # Test underscore vs dash variations
        result1 = self.parser.parse("income_statement", data)
        result2 = self.parser.parse("income-statement", data)
        
        assert len(result1) == 1
        assert len(result2) == 1
        assert type(result1[0]) == type(result2[0])
    
    def test_parsing_stats_tracking(self):
        """Test parsing statistics tracking."""
        self.parser.reset_stats()
        
        valid_data = [{"symbol": "AAPL", "fiscalYear": "2024", "period": "FY", "revenue": 1000}]
        invalid_data = [{"invalid": "data"}]  # Will cause validation error
        
        # Parse valid data
        self.parser.parse("income-statement", valid_data)
        
        # Parse invalid data (should trigger recovery)
        self.parser.parse("income-statement", invalid_data)
        
        stats = self.parser.get_parsing_stats()
        assert stats["total_processed"] == 2
        assert stats["successful"] >= 1
        # May have warnings from recovery attempts
    
    def test_field_name_normalization(self):
        """Test field name normalization for variations."""
        data = [{
            "symbol": "TEST",
            "fiscal_year": "2024",  # Underscore version
            "period": "FY",
            "company_name": "Test Company"  # Underscore version
        }]
        
        # This should work due to field name normalization
        result = self.parser.parse("profile", data)
        
        assert len(result) == 1
        assert isinstance(result[0], CompanyProfile)
        assert result[0].symbol == "TEST"


@pytest.fixture
def sample_income_statement_data():
    """Sample income statement data for testing."""
    return {
        "date": "2024-12-31",
        "symbol": "AAPL",
        "reportedCurrency": "USD",
        "cik": "0000320193",
        "filingDate": "2024-01-01",
        "acceptedDate": "2024-01-01 18:00:00",
        "fiscalYear": "2024",
        "period": "FY",
        "revenue": 394328000000,
        "costOfRevenue": 223546000000,
        "grossProfit": 170782000000,
        "netIncome": 97394000000,
        "eps": 6.11,
        "ebitda": 123456000000,
        "operatingIncome": 114301000000
    }


@pytest.fixture
def sample_sec_filing_data():
    """Sample SEC filing data for testing."""
    return {
        "symbol": "AAPL",
        "cik": "0000320193",
        "acceptedDate": "2024-01-01 18:00:00",
        "filingDate": "2024-01-01",
        "reportDate": "2023-12-31",
        "form": "10-K",
        "filingURL": "https://example.com/filing",
        "reportURL": "https://example.com/report",
        "type": "annual"
    } 