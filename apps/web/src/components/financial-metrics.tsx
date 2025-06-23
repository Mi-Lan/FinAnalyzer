import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FMPFinancialStatements } from '@/types/financial';

interface FinancialMetricsProps {
  financials: FMPFinancialStatements;
  period: string;
  year: number;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value);
}

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function FinancialMetrics({
  financials,
  period,
  year,
}: FinancialMetricsProps) {
  const income = financials.incomeStatement;
  const balance = financials.balanceSheet;
  const cashFlow = financials.cashFlow;

  // Calculate key metrics
  const grossMargin = income.revenue ? income.grossProfit / income.revenue : 0;
  const operatingMargin = income.revenue
    ? income.operatingIncome / income.revenue
    : 0;
  const netMargin = income.revenue ? income.netIncome / income.revenue : 0;
  const currentRatio =
    balance.totalCurrentAssets / balance.totalCurrentLiabilities;
  const debtToEquity = balance.totalDebt / balance.totalEquity;
  const roe = income.netIncome / balance.totalEquity;
  const fcfMargin = income.revenue ? cashFlow.freeCashFlow / income.revenue : 0;

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">
            Income Statement
          </CardTitle>
          <p className="text-xs text-muted-foreground">
            {period} {year}
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm">Revenue</span>
              <span className="text-sm font-medium">
                {formatCurrency(income.revenue)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Gross Profit</span>
              <span className="text-sm font-medium">
                {formatCurrency(income.grossProfit)} (
                {formatPercent(grossMargin)})
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Operating Income</span>
              <span className="text-sm font-medium">
                {formatCurrency(income.operatingIncome)} (
                {formatPercent(operatingMargin)})
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Net Income</span>
              <span className="text-sm font-medium">
                {formatCurrency(income.netIncome)} ({formatPercent(netMargin)})
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">EPS</span>
              <span className="text-sm font-medium">
                {income.eps != null ? `$${income.eps.toFixed(2)}` : 'N/A'}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Balance Sheet</CardTitle>
          <p className="text-xs text-muted-foreground">As of {income.date}</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm">Total Assets</span>
              <span className="text-sm font-medium">
                {formatCurrency(balance.totalAssets)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Total Liabilities</span>
              <span className="text-sm font-medium">
                {formatCurrency(balance.totalLiabilities)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Total Equity</span>
              <span className="text-sm font-medium">
                {formatCurrency(balance.totalEquity)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Current Ratio</span>
              <span className="text-sm font-medium">
                {currentRatio.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Debt/Equity</span>
              <span className="text-sm font-medium">
                {debtToEquity.toFixed(2)}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">
            Cash Flow & Returns
          </CardTitle>
          <p className="text-xs text-muted-foreground">
            {period} {year}
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm">Operating Cash Flow</span>
              <span className="text-sm font-medium">
                {formatCurrency(cashFlow.operatingCashFlow)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Free Cash Flow</span>
              <span className="text-sm font-medium">
                {formatCurrency(cashFlow.freeCashFlow)} (
                {formatPercent(fcfMargin)})
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">CapEx</span>
              <span className="text-sm font-medium">
                {formatCurrency(Math.abs(cashFlow.capitalExpenditure))}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">ROE</span>
              <span className="text-sm font-medium">{formatPercent(roe)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Cash & Equivalents</span>
              <span className="text-sm font-medium">
                {formatCurrency(balance.cashAndCashEquivalents)}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
