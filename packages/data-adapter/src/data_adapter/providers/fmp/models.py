from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class FinancialStatement(BaseModel):
    """Base model for a financial statement entry."""
    model_config = ConfigDict(populate_by_name=True)

    date: str
    symbol: str
    reported_currency: str = Field(alias="reportedCurrency")
    cik: str
    filing_date: str = Field(alias="filingDate")
    accepted_date: str = Field(alias="acceptedDate")
    calendar_year: Optional[str] = Field(default=None, alias="calendarYear")
    fiscal_year: str = Field(alias="fiscalYear")
    period: str
    link: Optional[str] = None
    final_link: Optional[str] = Field(default=None, alias="finalLink")


class IncomeStatement(FinancialStatement):
    """Represents an entry in an income statement."""
    revenue: float
    cost_of_revenue: float = Field(alias="costOfRevenue")
    gross_profit: float = Field(alias="grossProfit")
    research_and_development_expenses: float = Field(alias="researchAndDevelopmentExpenses")
    general_and_administrative_expenses: float = Field(alias="generalAndAdministrativeExpenses")
    selling_and_marketing_expenses: float = Field(alias="sellingAndMarketingExpenses")
    selling_general_and_administrative_expenses: float = Field(alias="sellingGeneralAndAdministrativeExpenses")
    other_expenses: float = Field(alias="otherExpenses")
    operating_expenses: float = Field(alias="operatingExpenses")
    cost_and_expenses: float = Field(alias="costAndExpenses")
    interest_income: float = Field(alias="interestIncome")
    interest_expense: float = Field(alias="interestExpense")
    depreciation_and_amortization: float = Field(alias="depreciationAndAmortization")
    ebitda: float
    ebit: float
    operating_income: float = Field(alias="operatingIncome")
    total_other_income_expenses_net: float = Field(alias="totalOtherIncomeExpensesNet")
    income_before_tax: float = Field(alias="incomeBeforeTax")
    income_tax_expense: float = Field(alias="incomeTaxExpense")
    net_income: float = Field(alias="netIncome")
    net_income_from_continuing_operations: float = Field(alias="netIncomeFromContinuingOperations")
    net_income_from_discontinued_operations: float = Field(alias="netIncomeFromDiscontinuedOperations")
    other_adjustments_to_net_income: float = Field(alias="otherAdjustmentsToNetIncome")
    bottom_line_net_income: float = Field(alias="bottomLineNetIncome")
    net_income_deductions: int = Field(alias="netIncomeDeductions")
    net_interest_income: float = Field(alias="netInterestIncome")
    non_operating_income_excluding_interest: float = Field(alias="nonOperatingIncomeExcludingInterest")
    eps: float
    epsdiluted: float = Field(alias="epsDiluted")
    weighted_average_shs_out: int = Field(alias="weightedAverageShsOut")
    weighted_average_shs_out_dil: int = Field(alias="weightedAverageShsOutDil")


class BalanceSheetStatement(FinancialStatement):
    """Represents an entry in a balance sheet statement."""
    total_assets: float = Field(alias="totalAssets")
    total_liabilities: float = Field(alias="totalLiabilities")
    total_equity: float = Field(alias="totalEquity")
    cash_and_cash_equivalents: float = Field(alias="cashAndCashEquivalents")
    total_debt: float = Field(alias="totalDebt")


class CashFlowStatement(FinancialStatement):
    """Represents an entry in a cash flow statement."""
    net_cash_provided_by_operating_activities: float = Field(alias="netCashProvidedByOperatingActivities")
    net_cash_used_for_investing_activities: float = Field(alias="netCashUsedForInvestingActivities")
    net_cash_used_provided_by_financing_activities: float = Field(alias="netCashUsedProvidedByFinancingActivities")
    net_change_in_cash: float = Field(alias="netChangeInCash")