import { FMPFinancialStatements } from '@/types/financial';

// --- Type Definitions ---

export interface TransformedFinancialData {
  companyInfo: {
    symbol: string;
    currency: string;
  };
  historicalData: FinancialYearData[];
  latestMetrics: FinancialMetrics;
  yearlyMetrics: Record<string, FinancialMetrics>;
}

export interface FinancialYearData {
  year: number;
  revenue: number;
  netIncome: number;
  freeCashFlow: number;
  totalAssets: number;
  totalLiabilities: number;
  totalEquity: number;
}

export interface FinancialMetrics {
  // Profitability
  grossMargin: number | null;
  operatingMargin: number | null;
  netMargin: number | null;
  // Growth (Year-over-Year)
  revenueGrowth: number | null;
  netIncomeGrowth: number | null;
  freeCashFlowGrowth: number | null;
  // Balance Sheet Health
  currentRatio: number | null;
  debtToEquity: number | null;
  // Capital Allocation & Efficiency
  returnOnEquity: number | null;
  returnOnAssets: number | null;
  returnOnInvestedCapital: number | null;
  assetTurnover: number | null;
  // Cash Flow
  operatingCashFlowMargin: number | null;
  freeCashFlowMargin: number | null;
}

// --- Helper Functions ---

const calculateRatio = (
  numerator?: number | null,
  denominator?: number | null
): number | null => {
  if (
    numerator === undefined ||
    numerator === null ||
    denominator === undefined ||
    denominator === null ||
    denominator === 0
  ) {
    return null;
  }
  return numerator / denominator;
};

const calculateGrowth = (
  current?: number,
  previous?: number
): number | null => {
  if (
    current === undefined ||
    current === null ||
    previous === undefined ||
    previous === null ||
    previous === 0
  ) {
    return null;
  }
  return (current - previous) / Math.abs(previous);
};

const getFinancialsByYear = (
  financials: FMPFinancialStatements[]
): Record<string, FMPFinancialStatements> => {
  return financials.reduce((acc, financial) => {
    const year = financial.incomeStatement.fiscalYear;
    if (year) {
      acc[year] = financial;
    }
    return acc;
  }, {} as Record<string, FMPFinancialStatements>);
};

// --- Core Metric Calculation ---

const calculateMetricsForYear = (
  current: FMPFinancialStatements,
  previous?: FMPFinancialStatements
): FinancialMetrics => {
  const is = current.incomeStatement;
  const bs = current.balanceSheet;
  const cf = current.cashFlow;

  const previousIs = previous?.incomeStatement;
  const previousCf = previous?.cashFlow;

  // Profitability
  const grossMargin = calculateRatio(is?.grossProfit, is?.revenue);
  const operatingMargin = calculateRatio(is?.operatingIncome, is?.revenue);
  const netMargin = calculateRatio(is?.netIncome, is?.revenue);

  // Growth
  const revenueGrowth = calculateGrowth(is?.revenue, previousIs?.revenue);
  const netIncomeGrowth = calculateGrowth(is?.netIncome, previousIs?.netIncome);
  const freeCashFlowGrowth = calculateGrowth(
    cf?.freeCashFlow,
    previousCf?.freeCashFlow
  );

  // Balance Sheet
  const currentRatio = calculateRatio(
    bs?.totalCurrentAssets,
    bs?.totalCurrentLiabilities
  );
  const debtToEquity = calculateRatio(bs?.totalDebt, bs?.totalEquity);

  // Capital Allocation
  const returnOnEquity = calculateRatio(is?.netIncome, bs?.totalEquity);
  const returnOnAssets = calculateRatio(is?.netIncome, bs?.totalAssets);
  const investedCapital =
    bs?.totalDebt && bs?.totalEquity && bs?.cashAndCashEquivalents
      ? bs.totalDebt + bs.totalEquity - bs.cashAndCashEquivalents
      : null;
  const ebit =
    is?.operatingIncome && is?.interestExpense
      ? is.operatingIncome + is.interestExpense
      : null; // Simplified EBIT
  const returnOnInvestedCapital = calculateRatio(ebit, investedCapital);
  const assetTurnover = calculateRatio(is?.revenue, bs?.totalAssets);

  // Cash Flow
  const operatingCashFlowMargin = calculateRatio(
    cf?.operatingCashFlow,
    is?.revenue
  );
  const freeCashFlowMargin = calculateRatio(cf?.freeCashFlow, is?.revenue);

  return {
    grossMargin,
    operatingMargin,
    netMargin,
    revenueGrowth,
    netIncomeGrowth,
    freeCashFlowGrowth,
    currentRatio,
    debtToEquity,
    returnOnEquity,
    returnOnAssets,
    returnOnInvestedCapital,
    assetTurnover,
    operatingCashFlowMargin,
    freeCashFlowMargin,
  };
};

// --- Main Transformer Function ---

export const transformFinancialDataForPrompts = (
  financials: FMPFinancialStatements[]
): TransformedFinancialData => {
  if (financials.length === 0) {
    throw new Error('Financial data is empty. Cannot perform transformation.');
  }

  // Sort by year to ensure correct growth calculations
  const sortedFinancials = [...financials].sort(
    (a, b) =>
      parseInt(a.incomeStatement.fiscalYear, 10) -
      parseInt(b.incomeStatement.fiscalYear, 10)
  );

  const financialsByYear = getFinancialsByYear(sortedFinancials);
  const years = Object.keys(financialsByYear).sort();

  const yearlyMetrics: Record<string, FinancialMetrics> = {};
  const historicalData: FinancialYearData[] = [];

  for (let i = 0; i < years.length; i++) {
    const year = years[i];
    const currentFinancials = financialsByYear[year];
    const previousFinancials =
      i > 0 ? financialsByYear[years[i - 1]] : undefined;

    const metrics = calculateMetricsForYear(
      currentFinancials,
      previousFinancials
    );
    yearlyMetrics[year] = metrics;

    historicalData.push({
      year: parseInt(year, 10),
      revenue: currentFinancials.incomeStatement.revenue,
      netIncome: currentFinancials.incomeStatement.netIncome,
      freeCashFlow: currentFinancials.cashFlow.freeCashFlow,
      totalAssets: currentFinancials.balanceSheet.totalAssets,
      totalLiabilities: currentFinancials.balanceSheet.totalLiabilities,
      totalEquity: currentFinancials.balanceSheet.totalEquity,
    });
  }

  const latestYear = years[years.length - 1];
  const latestMetrics = yearlyMetrics[latestYear];

  const companyInfo = {
    symbol: sortedFinancials[0].incomeStatement.symbol,
    currency: sortedFinancials[0].incomeStatement.reportedCurrency,
  };

  return {
    companyInfo,
    historicalData,
    latestMetrics,
    yearlyMetrics,
  };
};
