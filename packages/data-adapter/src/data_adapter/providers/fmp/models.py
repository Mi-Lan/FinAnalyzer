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
    # Current Assets
    cash_and_cash_equivalents: float = Field(alias="cashAndCashEquivalents")
    short_term_investments: float = Field(alias="shortTermInvestments")
    cash_and_short_term_investments: float = Field(alias="cashAndShortTermInvestments")
    net_receivables: float = Field(alias="netReceivables")
    accounts_receivables: float = Field(alias="accountsReceivables")
    other_receivables: float = Field(alias="otherReceivables")
    inventory: float = Field(alias="inventory")
    prepaids: float = Field(alias="prepaids")
    other_current_assets: float = Field(alias="otherCurrentAssets")
    total_current_assets: float = Field(alias="totalCurrentAssets")
    
    # Non-Current Assets
    property_plant_equipment_net: float = Field(alias="propertyPlantEquipmentNet")
    goodwill: float = Field(alias="goodwill")
    intangible_assets: float = Field(alias="intangibleAssets")
    goodwill_and_intangible_assets: float = Field(alias="goodwillAndIntangibleAssets")
    long_term_investments: float = Field(alias="longTermInvestments")
    tax_assets: float = Field(alias="taxAssets")
    other_non_current_assets: float = Field(alias="otherNonCurrentAssets")
    total_non_current_assets: float = Field(alias="totalNonCurrentAssets")
    other_assets: float = Field(alias="otherAssets")
    total_assets: float = Field(alias="totalAssets")
    
    # Current Liabilities
    total_payables: float = Field(alias="totalPayables")
    account_payables: float = Field(alias="accountPayables")
    other_payables: float = Field(alias="otherPayables")
    accrued_expenses: float = Field(alias="accruedExpenses")
    short_term_debt: float = Field(alias="shortTermDebt")
    capital_lease_obligations_current: float = Field(alias="capitalLeaseObligationsCurrent")
    tax_payables: float = Field(alias="taxPayables")
    deferred_revenue: float = Field(alias="deferredRevenue")
    other_current_liabilities: float = Field(alias="otherCurrentLiabilities")
    total_current_liabilities: float = Field(alias="totalCurrentLiabilities")
    
    # Non-Current Liabilities
    long_term_debt: float = Field(alias="longTermDebt")
    capital_lease_obligations_non_current: Optional[float] = Field(default=None, alias="capitalLeaseObligationsNonCurrent")
    deferred_revenue_non_current: float = Field(alias="deferredRevenueNonCurrent")
    deferred_tax_liabilities_non_current: float = Field(alias="deferredTaxLiabilitiesNonCurrent")
    other_non_current_liabilities: float = Field(alias="otherNonCurrentLiabilities")
    total_non_current_liabilities: float = Field(alias="totalNonCurrentLiabilities")
    other_liabilities: float = Field(alias="otherLiabilities")
    capital_lease_obligations: float = Field(alias="capitalLeaseObligations")
    total_liabilities: float = Field(alias="totalLiabilities")
    
    # Shareholders' Equity
    treasury_stock: float = Field(alias="treasuryStock")
    preferred_stock: float = Field(alias="preferredStock")
    common_stock: float = Field(alias="commonStock")
    retained_earnings: float = Field(alias="retainedEarnings")
    additional_paid_in_capital: float = Field(alias="additionalPaidInCapital")
    accumulated_other_comprehensive_income_loss: float = Field(alias="accumulatedOtherComprehensiveIncomeLoss")
    other_total_stockholders_equity: float = Field(alias="otherTotalStockholdersEquity")
    total_stockholders_equity: float = Field(alias="totalStockholdersEquity")
    total_equity: float = Field(alias="totalEquity")
    minority_interest: float = Field(alias="minorityInterest")
    total_liabilities_and_total_equity: float = Field(alias="totalLiabilitiesAndTotalEquity")
    
    # Additional Metrics
    total_investments: float = Field(alias="totalInvestments")
    total_debt: float = Field(alias="totalDebt")
    net_debt: float = Field(alias="netDebt")


class CashFlowStatement(FinancialStatement):
    """Represents an entry in a cash flow statement."""
    # Operating Activities
    net_income: float = Field(alias="netIncome")
    depreciation_and_amortization: float = Field(alias="depreciationAndAmortization")
    deferred_income_tax: float = Field(alias="deferredIncomeTax")
    stock_based_compensation: float = Field(alias="stockBasedCompensation")
    change_in_working_capital: float = Field(alias="changeInWorkingCapital")
    accounts_receivables: float = Field(alias="accountsReceivables")
    inventory: float = Field(alias="inventory")
    accounts_payables: float = Field(alias="accountsPayables")
    other_working_capital: float = Field(alias="otherWorkingCapital")
    other_non_cash_items: float = Field(alias="otherNonCashItems")
    net_cash_provided_by_operating_activities: float = Field(alias="netCashProvidedByOperatingActivities")
    
    # Investing Activities
    investments_in_property_plant_and_equipment: float = Field(alias="investmentsInPropertyPlantAndEquipment")
    acquisitions_net: float = Field(alias="acquisitionsNet")
    purchases_of_investments: float = Field(alias="purchasesOfInvestments")
    sales_maturities_of_investments: float = Field(alias="salesMaturitiesOfInvestments")
    other_investing_activities: float = Field(alias="otherInvestingActivities")
    net_cash_provided_by_investing_activities: float = Field(alias="netCashProvidedByInvestingActivities")
    
    # Financing Activities
    net_debt_issuance: float = Field(alias="netDebtIssuance")
    long_term_net_debt_issuance: float = Field(alias="longTermNetDebtIssuance")
    short_term_net_debt_issuance: float = Field(alias="shortTermNetDebtIssuance")
    net_stock_issuance: float = Field(alias="netStockIssuance")
    net_common_stock_issuance: float = Field(alias="netCommonStockIssuance")
    common_stock_issuance: float = Field(alias="commonStockIssuance")
    common_stock_repurchased: float = Field(alias="commonStockRepurchased")
    net_preferred_stock_issuance: float = Field(alias="netPreferredStockIssuance")
    net_dividends_paid: float = Field(alias="netDividendsPaid")
    common_dividends_paid: float = Field(alias="commonDividendsPaid")
    preferred_dividends_paid: float = Field(alias="preferredDividendsPaid")
    other_financing_activities: float = Field(alias="otherFinancingActivities")
    net_cash_provided_by_financing_activities: float = Field(alias="netCashProvidedByFinancingActivities")
    
    # Net Change in Cash
    effect_of_forex_changes_on_cash: float = Field(alias="effectOfForexChangesOnCash")
    net_change_in_cash: float = Field(alias="netChangeInCash")
    cash_at_end_of_period: float = Field(alias="cashAtEndOfPeriod")
    cash_at_beginning_of_period: float = Field(alias="cashAtBeginningOfPeriod")
    
    # Summary Metrics
    operating_cash_flow: float = Field(alias="operatingCashFlow")
    capital_expenditure: float = Field(alias="capitalExpenditure")
    free_cash_flow: float = Field(alias="freeCashFlow")
    income_taxes_paid: float = Field(alias="incomeTaxesPaid")
    interest_paid: float = Field(alias="interestPaid")


class SECFiling(BaseModel):
    """Base model for SEC filing information."""
    model_config = ConfigDict(populate_by_name=True)

    symbol: str
    cik: str
    accepted_date: str = Field(alias="acceptedDate")
    filing_date: str = Field(alias="filingDate")
    report_date: str = Field(alias="reportDate")
    form: str  # 10-K, 10-Q, etc.
    filing_url: str = Field(alias="filingURL")
    report_url: str = Field(alias="reportURL")
    type: str
    size: Optional[int] = None
    period: Optional[str] = None
    fiscal_year: Optional[str] = Field(default=None, alias="fiscalYear")
    quarter: Optional[int] = None


class TenKFiling(SECFiling):
    """Represents a 10-K annual filing."""
    form: str = Field(default="10-K")


class TenQFiling(SECFiling):
    """Represents a 10-Q quarterly filing.""" 
    form: str = Field(default="10-Q")
    quarter: int


class CompanyProfile(BaseModel):
    """Company profile information from FMP."""
    model_config = ConfigDict(populate_by_name=True)
    
    symbol: str
    company_name: str = Field(alias="companyName")
    price: Optional[float] = None
    beta: Optional[float] = None
    vol_avg: Optional[int] = Field(default=None, alias="volAvg")
    mkt_cap: Optional[int] = Field(default=None, alias="mktCap")
    last_div: Optional[float] = Field(default=None, alias="lastDiv")
    range: Optional[str] = None
    changes: Optional[float] = None
    changes_percentage: Optional[str] = Field(default=None, alias="changesPercentage")
    exchange: Optional[str] = None
    exchange_short_name: Optional[str] = Field(default=None, alias="exchangeShortName")
    industry: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    ceo: Optional[str] = None
    sector: Optional[str] = None
    country: Optional[str] = None
    full_time_employees: Optional[str] = Field(default=None, alias="fullTimeEmployees")
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    dcf_diff: Optional[float] = Field(default=None, alias="dcfDiff")
    dcf: Optional[float] = None
    image: Optional[str] = None
    ipo_date: Optional[str] = Field(default=None, alias="ipoDate")
    default_image: Optional[bool] = Field(default=None, alias="defaultImage")
    is_etf: Optional[bool] = Field(default=None, alias="isEtf")
    is_actively_trading: Optional[bool] = Field(default=None, alias="isActivelyTrading")
    is_adr: Optional[bool] = Field(default=None, alias="isAdr")
    is_fund: Optional[bool] = Field(default=None, alias="isFund")