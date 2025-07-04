// Database models (matching Prisma schema)
export interface Company {
  id: string;
  name: string;
  ticker: string;
  sector?: string;
  industry?: string;
  createdAt: string;
  updatedAt: string;
}

export interface FinancialData {
  id: string;
  companyId: string;
  year: number;
  period: string; // "Q1", "Q2", "Q3", "Q4", "FY"
  type: string; // e.g., "income-statement", "balance-sheet-statement", "10-K", "10-Q"
  data: FMPFinancialStatements | Record<string, unknown>; // Can be financial statements OR SEC filing data
  createdAt: string;
  updatedAt: string;
}

export interface AnalysisTemplate {
  id: string;
  name: string;
  description?: string;
  sectors: string[];
  template: {
    weights: {
      profitability: number;
      growth: number;
      balanceSheet: number;
      capitalAllocation: number;
      valuation: number;
    };
  }; // JSON for prompt chain and scoring logic
  createdAt: string;
  updatedAt: string;
}

export interface AnalysisResult {
  id: string;
  companyId: string;
  templateId: string;
  jobId?: string;
  score: number;
  insights: AnalysisInsights;
  metricScores: MetricScores;
  createdAt: string;
  updatedAt: string;
}

export interface BulkAnalysisJob {
  id: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
  progress: number;
  createdAt: string;
  updatedAt: string;
}

// FMP Data Models (matching Python Pydantic models)
export interface FMPFinancialStatement {
  date: string;
  symbol: string;
  reportedCurrency: string;
  cik: string;
  filingDate: string;
  acceptedDate: string;
  calendarYear?: string;
  fiscalYear: string;
  period: string;
  link?: string;
  finalLink?: string;
}

export interface FMPIncomeStatement extends FMPFinancialStatement {
  revenue: number;
  costOfRevenue: number;
  grossProfit: number;
  researchAndDevelopmentExpenses: number;
  generalAndAdministrativeExpenses: number;
  sellingAndMarketingExpenses: number;
  sellingGeneralAndAdministrativeExpenses: number;
  otherExpenses: number;
  operatingExpenses: number;
  costAndExpenses: number;
  interestIncome: number;
  interestExpense: number;
  depreciationAndAmortization: number;
  ebitda: number;
  ebit: number;
  operatingIncome: number;
  totalOtherIncomeExpensesNet: number;
  incomeBeforeTax: number;
  incomeTaxExpense: number;
  netIncome: number;
  netIncomeFromContinuingOperations: number;
  netIncomeFromDiscontinuedOperations: number;
  otherAdjustmentsToNetIncome: number;
  bottomLineNetIncome: number;
  netIncomeDeductions: number;
  netInterestIncome: number;
  nonOperatingIncomeExcludingInterest: number;
  eps?: number;
  epsDiluted?: number;
  weightedAverageShsOut: number;
  weightedAverageShsOutDil: number;
}

export interface FMPBalanceSheetStatement extends FMPFinancialStatement {
  // Current Assets
  cashAndCashEquivalents: number;
  shortTermInvestments: number;
  cashAndShortTermInvestments: number;
  netReceivables: number;
  accountsReceivables: number;
  otherReceivables: number;
  inventory: number;
  prepaids: number;
  otherCurrentAssets: number;
  totalCurrentAssets: number;

  // Non-Current Assets
  propertyPlantEquipmentNet: number;
  goodwill: number;
  intangibleAssets: number;
  goodwillAndIntangibleAssets: number;
  longTermInvestments: number;
  taxAssets: number;
  otherNonCurrentAssets: number;
  totalNonCurrentAssets: number;
  otherAssets: number;
  totalAssets: number;

  // Current Liabilities
  totalPayables: number;
  accountPayables: number;
  otherPayables: number;
  accruedExpenses: number;
  shortTermDebt: number;
  capitalLeaseObligationsCurrent: number;
  taxPayables: number;
  deferredRevenue: number;
  otherCurrentLiabilities: number;
  totalCurrentLiabilities: number;

  // Non-Current Liabilities
  longTermDebt: number;
  capitalLeaseObligationsNonCurrent?: number;
  deferredRevenueNonCurrent: number;
  deferredTaxLiabilitiesNonCurrent: number;
  otherNonCurrentLiabilities: number;
  totalNonCurrentLiabilities: number;
  otherLiabilities: number;
  capitalLeaseObligations: number;
  totalLiabilities: number;

  // Shareholders' Equity
  treasuryStock: number;
  preferredStock: number;
  commonStock: number;
  retainedEarnings: number;
  additionalPaidInCapital: number;
  accumulatedOtherComprehensiveIncomeLoss: number;
  otherTotalStockholdersEquity: number;
  totalStockholdersEquity: number;
  totalEquity: number;
  minorityInterest: number;
  totalLiabilitiesAndTotalEquity: number;

  // Additional Metrics
  totalInvestments: number;
  totalDebt: number;
  netDebt: number;
}

export interface FMPCashFlowStatement extends FMPFinancialStatement {
  // Operating Activities
  netIncome: number;
  depreciationAndAmortization: number;
  deferredIncomeTax: number;
  stockBasedCompensation: number;
  changeInWorkingCapital: number;
  accountsReceivables: number;
  inventory: number;
  accountsPayables: number;
  otherWorkingCapital: number;
  otherNonCashItems: number;
  netCashProvidedByOperatingActivities: number;

  // Investing Activities
  investmentsInPropertyPlantAndEquipment: number;
  acquisitionsNet: number;
  purchasesOfInvestments: number;
  salesMaturitiesOfInvestments: number;
  otherInvestingActivities: number;
  netCashProvidedByInvestingActivities: number;

  // Financing Activities
  netDebtIssuance: number;
  longTermNetDebtIssuance: number;
  shortTermNetDebtIssuance: number;
  netStockIssuance: number;
  netCommonStockIssuance: number;
  commonStockIssuance: number;
  commonStockRepurchased: number;
  netPreferredStockIssuance: number;
  netDividendsPaid: number;
  commonDividendsPaid: number;
  preferredDividendsPaid: number;
  otherFinancingActivities: number;
  netCashProvidedByFinancingActivities: number;

  // Net Change in Cash
  effectOfForexChangesOnCash: number;
  netChangeInCash: number;
  cashAtEndOfPeriod: number;
  cashAtBeginningOfPeriod: number;

  // Summary Metrics
  operatingCashFlow: number;
  capitalExpenditure: number;
  freeCashFlow: number;
  incomeTaxesPaid: number;
  interestPaid: number;
}

// Grouped financial statements as they would be stored in FinancialData.data
export interface FMPFinancialStatements {
  incomeStatement: FMPIncomeStatement;
  balanceSheet: FMPBalanceSheetStatement;
  cashFlow: FMPCashFlowStatement;
}

// Analysis-related types
export interface AnalysisInsights {
  summary: string;
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  risks: string[];
  recommendation: 'BUY' | 'HOLD' | 'SELL';
}

export interface MetricScores {
  profitability: number;
  growth: number;
  balanceSheet: number;
  capitalAllocation: number;
  valuation: number;
  overall: number;
}

// API Response types
export interface ScreeningResult {
  companies: {
    company: Company;
    latestFinancials: FinancialData;
    analysis: AnalysisResult;
  }[];
  totalCount: number;
  filters: {
    sector?: string;
    minScore?: number;
    maxScore?: number;
    recommendation?: string;
  };
}

// Company details API response type
export interface CompanyDetailsResponse {
  company: Company;
  financialData: FinancialData[];
  latestFinancials: FinancialData | null;
  analysisResult: AnalysisResult | null;
}

// These types are specific subsets for the FinancialMetrics component.
// They use Pick to select only the necessary fields from the main types,
// avoiding re-declaration and potential conflicts.

export type FinancialMetricsIncomeStatement = Pick<
  FMPIncomeStatement,
  'revenue' | 'grossProfit' | 'operatingIncome' | 'netIncome' | 'eps' | 'date'
>;

export type FinancialMetricsBalanceSheetStatement = Pick<
  FMPBalanceSheetStatement,
  | 'totalAssets'
  | 'totalLiabilities'
  | 'totalEquity'
  | 'cashAndCashEquivalents'
  | 'totalDebt'
  | 'totalCurrentAssets'
  | 'totalCurrentLiabilities'
  | 'date'
>;

export type FinancialMetricsCashFlowStatement = Pick<
  FMPCashFlowStatement,
  'operatingCashFlow' | 'freeCashFlow' | 'capitalExpenditure'
>;

// This type represents the data structure required by the FinancialMetrics component,
// with optional statement fields.
export interface FinancialMetricsData {
  incomeStatement?: FinancialMetricsIncomeStatement;
  balanceSheet?: FinancialMetricsBalanceSheetStatement;
  cashFlow?: FinancialMetricsCashFlowStatement;
}

export interface CompanyWithAnalysis {
  id: string;
  name: string;
  ticker: string;
  sector?: string;
  industry?: string;
  score?: number;
  insights?: AnalysisInsights;
  createdAt: string;
  updatedAt: string;
}
