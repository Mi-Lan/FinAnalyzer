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
  const income = financials?.incomeStatement;
  const balance = financials?.balanceSheet;
  const cashFlow = financials?.cashFlow;

  // If no financial data is available, show a message
  if (!income && !balance && !cashFlow) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Financial Data Unavailable</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            No financial data is available for this period.
          </p>
        </CardContent>
      </Card>
    );
  }

  // Calculate key metrics with null safety
  const grossMargin =
    income?.revenue && income?.grossProfit
      ? income.grossProfit / income.revenue
      : 0;
  const operatingMargin =
    income?.revenue && income?.operatingIncome
      ? income.operatingIncome / income.revenue
      : 0;
  const netMargin =
    income?.revenue && income?.netIncome
      ? income.netIncome / income.revenue
      : 0;
  const currentRatio =
    balance?.totalCurrentAssets && balance?.totalCurrentLiabilities
      ? balance.totalCurrentAssets / balance.totalCurrentLiabilities
      : 0;
  const debtToEquity =
    balance?.totalDebt && balance?.totalEquity
      ? balance.totalDebt / balance.totalEquity
      : 0;
  const roe =
    income?.netIncome && balance?.totalEquity
      ? income.netIncome / balance.totalEquity
      : 0;
  const fcfMargin =
    income?.revenue && cashFlow?.freeCashFlow
      ? cashFlow.freeCashFlow / income.revenue
      : 0;

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {income && (
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
                  {income.revenue ? formatCurrency(income.revenue) : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Gross Profit</span>
                <span className="text-sm font-medium">
                  {income.grossProfit
                    ? `${formatCurrency(income.grossProfit)} (${formatPercent(
                        grossMargin
                      )})`
                    : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Operating Income</span>
                <span className="text-sm font-medium">
                  {income.operatingIncome
                    ? `${formatCurrency(
                        income.operatingIncome
                      )} (${formatPercent(operatingMargin)})`
                    : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Net Income</span>
                <span className="text-sm font-medium">
                  {income.netIncome
                    ? `${formatCurrency(income.netIncome)} (${formatPercent(
                        netMargin
                      )})`
                    : 'N/A'}
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
      )}

      {balance && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Balance Sheet</CardTitle>
            <p className="text-xs text-muted-foreground">
              As of {balance.date || income?.date || 'Latest'}
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm">Total Assets</span>
                <span className="text-sm font-medium">
                  {balance.totalAssets
                    ? formatCurrency(balance.totalAssets)
                    : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Total Liabilities</span>
                <span className="text-sm font-medium">
                  {balance.totalLiabilities
                    ? formatCurrency(balance.totalLiabilities)
                    : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Total Equity</span>
                <span className="text-sm font-medium">
                  {balance.totalEquity
                    ? formatCurrency(balance.totalEquity)
                    : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Current Ratio</span>
                <span className="text-sm font-medium">
                  {currentRatio > 0 ? currentRatio.toFixed(2) : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Debt/Equity</span>
                <span className="text-sm font-medium">
                  {debtToEquity > 0 ? debtToEquity.toFixed(2) : 'N/A'}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {(cashFlow || balance) && (
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
              {cashFlow?.operatingCashFlow != null && (
                <div className="flex justify-between">
                  <span className="text-sm">Operating Cash Flow</span>
                  <span className="text-sm font-medium">
                    {formatCurrency(cashFlow.operatingCashFlow)}
                  </span>
                </div>
              )}
              {cashFlow?.freeCashFlow != null && (
                <div className="flex justify-between">
                  <span className="text-sm">Free Cash Flow</span>
                  <span className="text-sm font-medium">
                    {formatCurrency(cashFlow.freeCashFlow)}
                    {fcfMargin > 0 && ` (${formatPercent(fcfMargin)})`}
                  </span>
                </div>
              )}
              {cashFlow?.capitalExpenditure != null && (
                <div className="flex justify-between">
                  <span className="text-sm">CapEx</span>
                  <span className="text-sm font-medium">
                    {formatCurrency(Math.abs(cashFlow.capitalExpenditure))}
                  </span>
                </div>
              )}
              {roe > 0 && (
                <div className="flex justify-between">
                  <span className="text-sm">ROE</span>
                  <span className="text-sm font-medium">
                    {formatPercent(roe)}
                  </span>
                </div>
              )}
              {balance?.cashAndCashEquivalents != null && (
                <div className="flex justify-between">
                  <span className="text-sm">Cash & Equivalents</span>
                  <span className="text-sm font-medium">
                    {formatCurrency(balance.cashAndCashEquivalents)}
                  </span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
