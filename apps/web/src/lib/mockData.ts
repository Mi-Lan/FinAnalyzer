import type {
  Company,
  FinancialData,
  AnalysisTemplate,
  AnalysisResult,
  BulkAnalysisJob,
  FMPFinancialStatements,
  FMPIncomeStatement,
  FMPBalanceSheetStatement,
  FMPCashFlowStatement,
  CompanyDetailsResponse,
} from '@/types/financial';

// Mock companies data
export const mockCompanies: Company[] = [
  {
    id: '1',
    name: 'Apple Inc.',
    ticker: 'AAPL',
    sector: 'Technology',
    industry: 'Consumer Electronics',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },
  {
    id: '2',
    name: 'Microsoft Corporation',
    ticker: 'MSFT',
    sector: 'Technology',
    industry: 'Software',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },
  {
    id: '3',
    name: 'Tesla, Inc.',
    ticker: 'TSLA',
    sector: 'Consumer Cyclical',
    industry: 'Auto Manufacturers',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },
  {
    id: '4',
    name: 'Amazon.com, Inc.',
    ticker: 'AMZN',
    sector: 'Consumer Cyclical',
    industry: 'Internet Retail',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },
  {
    id: '5',
    name: 'NVIDIA Corporation',
    ticker: 'NVDA',
    sector: 'Technology',
    industry: 'Semiconductors',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },
];

// Mock analysis templates
export const mockAnalysisTemplates: AnalysisTemplate[] = [
  {
    id: 'template1',
    name: 'Technology Stock Analysis',
    description: 'Comprehensive analysis template for technology stocks',
    sectors: ['Technology'],
    template: {
      weights: {
        profitability: 0.25,
        growth: 0.3,
        balanceSheet: 0.2,
        capitalAllocation: 0.15,
        valuation: 0.1,
      },
    },
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },
];

// Mock bulk analysis job
export const mockBulkAnalysisJob: BulkAnalysisJob = {
  id: 'job_123456789',
  status: 'IN_PROGRESS',
  progress: 0.65,
  createdAt: '2024-01-01T00:00:00Z',
  updatedAt: '2024-01-01T00:00:00Z',
};

// Generate mock financial data for a company
export function generateMockFinancialData(
  companyId: string,
  ticker: string
): FinancialData[] {
  const currentYear = new Date().getFullYear();
  const periods = ['Q1', 'Q2', 'Q3', 'Q4'];

  return periods.map((period) => ({
    id: `${companyId}_${currentYear}_${period}`,
    companyId,
    year: currentYear,
    period,
    data: generateMockFinancialStatements(ticker, currentYear, period),
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  }));
}

// Generate mock financial statements
function generateMockFinancialStatements(
  ticker: string,
  year: number,
  period: string
): FMPFinancialStatements {
  // Base multipliers for different companies
  const multipliers: Record<string, number> = {
    AAPL: 100000000000, // $100B scale
    MSFT: 80000000000, // $80B scale
    TSLA: 30000000000, // $30B scale
    AMZN: 120000000000, // $120B scale
    NVDA: 25000000000, // $25B scale
  };

  const baseMultiplier = multipliers[ticker] || 10000000000; // $10B default

  const incomeStatement: FMPIncomeStatement = {
    date: `${year}-${
      period === 'Q1'
        ? '03'
        : period === 'Q2'
        ? '06'
        : period === 'Q3'
        ? '09'
        : '12'
    }-31`,
    symbol: ticker,
    reportedCurrency: 'USD',
    cik: '0000320193',
    filingDate: `${year}-${
      period === 'Q1'
        ? '04'
        : period === 'Q2'
        ? '07'
        : period === 'Q3'
        ? '10'
        : '01'
    }-15`,
    acceptedDate: `${year}-${
      period === 'Q1'
        ? '04'
        : period === 'Q2'
        ? '07'
        : period === 'Q3'
        ? '10'
        : '01'
    }-15T18:00:00.000Z`,
    calendarYear: year.toString(),
    fiscalYear: year.toString(),
    period,
    revenue: baseMultiplier * 0.4,
    costOfRevenue: baseMultiplier * 0.2,
    grossProfit: baseMultiplier * 0.2,
    researchAndDevelopmentExpenses: baseMultiplier * 0.05,
    generalAndAdministrativeExpenses: baseMultiplier * 0.02,
    sellingAndMarketingExpenses: baseMultiplier * 0.03,
    sellingGeneralAndAdministrativeExpenses: baseMultiplier * 0.05,
    otherExpenses: baseMultiplier * 0.01,
    operatingExpenses: baseMultiplier * 0.08,
    costAndExpenses: baseMultiplier * 0.28,
    interestIncome: baseMultiplier * 0.001,
    interestExpense: baseMultiplier * 0.002,
    depreciationAndAmortization: baseMultiplier * 0.01,
    ebitda: baseMultiplier * 0.15,
    ebit: baseMultiplier * 0.14,
    operatingIncome: baseMultiplier * 0.12,
    totalOtherIncomeExpensesNet: baseMultiplier * 0.001,
    incomeBeforeTax: baseMultiplier * 0.121,
    incomeTaxExpense: baseMultiplier * 0.021,
    netIncome: baseMultiplier * 0.1,
    netIncomeFromContinuingOperations: baseMultiplier * 0.1,
    netIncomeFromDiscontinuedOperations: 0,
    otherAdjustmentsToNetIncome: 0,
    bottomLineNetIncome: baseMultiplier * 0.1,
    netIncomeDeductions: 0,
    netInterestIncome: baseMultiplier * -0.001,
    nonOperatingIncomeExcludingInterest: baseMultiplier * 0.001,
    eps: 5.5,
    epsDiluted: 5.4,
    weightedAverageShsOut: 15000000000,
    weightedAverageShsOutDil: 15100000000,
  };

  const balanceSheet: FMPBalanceSheetStatement = {
    date: incomeStatement.date,
    symbol: ticker,
    reportedCurrency: 'USD',
    cik: incomeStatement.cik,
    filingDate: incomeStatement.filingDate,
    acceptedDate: incomeStatement.acceptedDate,
    calendarYear: incomeStatement.calendarYear,
    fiscalYear: incomeStatement.fiscalYear,
    period,
    cashAndCashEquivalents: baseMultiplier * 0.5,
    shortTermInvestments: baseMultiplier * 0.2,
    cashAndShortTermInvestments: baseMultiplier * 0.7,
    netReceivables: baseMultiplier * 0.1,
    accountsReceivables: baseMultiplier * 0.08,
    otherReceivables: baseMultiplier * 0.02,
    inventory: baseMultiplier * 0.05,
    prepaids: baseMultiplier * 0.01,
    otherCurrentAssets: baseMultiplier * 0.05,
    totalCurrentAssets: baseMultiplier * 0.91,
    propertyPlantEquipmentNet: baseMultiplier * 0.4,
    goodwill: baseMultiplier * 0.1,
    intangibleAssets: baseMultiplier * 0.05,
    goodwillAndIntangibleAssets: baseMultiplier * 0.15,
    longTermInvestments: baseMultiplier * 0.3,
    taxAssets: baseMultiplier * 0.02,
    otherNonCurrentAssets: baseMultiplier * 0.05,
    totalNonCurrentAssets: baseMultiplier * 0.92,
    otherAssets: baseMultiplier * 0.02,
    totalAssets: baseMultiplier * 1.85,
    totalPayables: baseMultiplier * 0.15,
    accountPayables: baseMultiplier * 0.1,
    otherPayables: baseMultiplier * 0.05,
    accruedExpenses: baseMultiplier * 0.05,
    shortTermDebt: baseMultiplier * 0.05,
    capitalLeaseObligationsCurrent: baseMultiplier * 0.01,
    taxPayables: baseMultiplier * 0.02,
    deferredRevenue: baseMultiplier * 0.03,
    otherCurrentLiabilities: baseMultiplier * 0.05,
    totalCurrentLiabilities: baseMultiplier * 0.36,
    longTermDebt: baseMultiplier * 0.2,
    capitalLeaseObligationsNonCurrent: baseMultiplier * 0.02,
    deferredRevenueNonCurrent: baseMultiplier * 0.05,
    deferredTaxLiabilitiesNonCurrent: baseMultiplier * 0.01,
    otherNonCurrentLiabilities: baseMultiplier * 0.05,
    totalNonCurrentLiabilities: baseMultiplier * 0.33,
    otherLiabilities: baseMultiplier * 0.02,
    capitalLeaseObligations: baseMultiplier * 0.03,
    totalLiabilities: baseMultiplier * 0.71,
    treasuryStock: -baseMultiplier * 0.1,
    preferredStock: 0,
    commonStock: baseMultiplier * 0.01,
    retainedEarnings: baseMultiplier * 0.8,
    additionalPaidInCapital: baseMultiplier * 0.2,
    accumulatedOtherComprehensiveIncomeLoss: baseMultiplier * 0.02,
    otherTotalStockholdersEquity: baseMultiplier * 0.01,
    totalStockholdersEquity: baseMultiplier * 1.14,
    totalEquity: baseMultiplier * 1.14,
    minorityInterest: 0,
    totalLiabilitiesAndTotalEquity: baseMultiplier * 1.85,
    totalInvestments: baseMultiplier * 0.5,
    totalDebt: baseMultiplier * 0.25,
    netDebt: -baseMultiplier * 0.25,
  };

  const cashFlow: FMPCashFlowStatement = {
    date: incomeStatement.date,
    symbol: ticker,
    reportedCurrency: 'USD',
    cik: incomeStatement.cik,
    filingDate: incomeStatement.filingDate,
    acceptedDate: incomeStatement.acceptedDate,
    calendarYear: incomeStatement.calendarYear,
    fiscalYear: incomeStatement.fiscalYear,
    period,
    netIncome: incomeStatement.netIncome,
    depreciationAndAmortization: baseMultiplier * 0.01,
    deferredIncomeTax: baseMultiplier * 0.001,
    stockBasedCompensation: baseMultiplier * 0.005,
    changeInWorkingCapital: baseMultiplier * 0.02,
    accountsReceivables: baseMultiplier * 0.01,
    inventory: baseMultiplier * 0.005,
    accountsPayables: baseMultiplier * 0.01,
    otherWorkingCapital: baseMultiplier * 0.005,
    otherNonCashItems: baseMultiplier * 0.001,
    netCashProvidedByOperatingActivities: baseMultiplier * 0.12,
    investmentsInPropertyPlantAndEquipment: -baseMultiplier * 0.03,
    acquisitionsNet: -baseMultiplier * 0.01,
    purchasesOfInvestments: -baseMultiplier * 0.1,
    salesMaturitiesOfInvestments: baseMultiplier * 0.08,
    otherInvestingActivities: baseMultiplier * 0.005,
    netCashProvidedByInvestingActivities: -baseMultiplier * 0.055,
    netDebtIssuance: baseMultiplier * 0.01,
    longTermNetDebtIssuance: baseMultiplier * 0.005,
    shortTermNetDebtIssuance: baseMultiplier * 0.005,
    netStockIssuance: -baseMultiplier * 0.02,
    netCommonStockIssuance: -baseMultiplier * 0.02,
    commonStockIssuance: 0,
    commonStockRepurchased: -baseMultiplier * 0.02,
    netPreferredStockIssuance: 0,
    netDividendsPaid: -baseMultiplier * 0.015,
    commonDividendsPaid: -baseMultiplier * 0.015,
    preferredDividendsPaid: 0,
    otherFinancingActivities: baseMultiplier * 0.001,
    netCashProvidedByFinancingActivities: -baseMultiplier * 0.039,
    effectOfForexChangesOnCash: baseMultiplier * 0.001,
    netChangeInCash: baseMultiplier * 0.027,
    cashAtEndOfPeriod: baseMultiplier * 0.5,
    cashAtBeginningOfPeriod: baseMultiplier * 0.473,
    operatingCashFlow: baseMultiplier * 0.12,
    capitalExpenditure: -baseMultiplier * 0.03,
    freeCashFlow: baseMultiplier * 0.09,
    incomeTaxesPaid: baseMultiplier * 0.018,
    interestPaid: baseMultiplier * 0.002,
  };

  return {
    incomeStatement,
    balanceSheet,
    cashFlow,
  };
}

// Generate mock analysis result
export function generateMockAnalysisResult(
  companyId: string,
  templateId: string,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  _financialData: FinancialData
): AnalysisResult {
  // Generate scores based on company
  const company = mockCompanies.find((c) => c.id === companyId);
  const baseScore =
    company?.ticker === 'AAPL'
      ? 85
      : company?.ticker === 'MSFT'
      ? 82
      : company?.ticker === 'NVDA'
      ? 88
      : company?.ticker === 'TSLA'
      ? 76
      : company?.ticker === 'AMZN'
      ? 79
      : 75;

  const variance = Math.random() * 10 - 5; // ±5 points variance
  const finalScore = Math.max(0, Math.min(100, baseScore + variance));

  const metricScores = {
    profitability: Math.round(finalScore + Math.random() * 10 - 5),
    growth: Math.round(finalScore + Math.random() * 10 - 5),
    balanceSheet: Math.round(finalScore + Math.random() * 10 - 5),
    capitalAllocation: Math.round(finalScore + Math.random() * 10 - 5),
    valuation: Math.round(finalScore + Math.random() * 10 - 5),
    overall: Math.round(finalScore),
  };

  const recommendation =
    finalScore >= 80 ? 'BUY' : finalScore >= 60 ? 'HOLD' : 'SELL';

  return {
    id: `analysis_${companyId}_${templateId}`,
    companyId,
    templateId,
    score: Math.round(finalScore),
    insights: {
      summary: `Based on our comprehensive analysis, ${company?.name} shows ${
        finalScore >= 80 ? 'strong' : finalScore >= 60 ? 'moderate' : 'weak'
      } financial performance across key metrics.`,
      strengths: [
        'Strong market position',
        'Healthy cash flow generation',
        'Innovative product portfolio',
      ],
      weaknesses: ['High valuation multiples', 'Competitive market pressure'],
      opportunities: [
        'Expanding into new markets',
        'Technology adoption trends',
      ],
      risks: ['Market volatility', 'Regulatory changes'],
      recommendation: recommendation as 'BUY' | 'HOLD' | 'SELL',
    },
    metricScores,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  };
}

// Get mock company data for a specific ticker
export function getMockCompanyData(
  ticker: string
): CompanyDetailsResponse | null {
  const company = mockCompanies.find((c) => c.ticker === ticker);
  if (!company) return null;

  const financialDataArray = generateMockFinancialData(company.id, ticker);
  const latestFinancials = financialDataArray[1]; // Q2 data
  const analysisResult = generateMockAnalysisResult(
    company.id,
    mockAnalysisTemplates[0].id,
    latestFinancials
  );

  return {
    company,
    financialData: financialDataArray,
    latestFinancials,
    analysisResult,
  };
}
