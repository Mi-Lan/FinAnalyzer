'use client';

import { Suspense, use, useState } from 'react';
import { useCompanyDetails, useCompanyAnalysis } from '@/lib/api-hooks';
import { ScoreCard } from '@/components/score-card';
import { FinancialMetrics } from '@/components/financial-metrics';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { FMPFinancialStatements } from '@/types/financial';

function CompanyDetailContent({ ticker }: { ticker: string }) {
  const { data, isLoading, error } = useCompanyDetails(ticker);
  const {
    analysis,
    isLoading: analysisLoading,
    error: analysisError,
    runAnalysis,
  } = useCompanyAnalysis();
  const [filter, setFilter] = useState<'ALL' | '10-K' | '10-Q' | '8-K'>('ALL');

  if (isLoading || !data) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">Loading company details...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center text-red-600">
          {error?.message || 'Company not found'}
        </div>
      </div>
    );
  }

  const { company, latestFinancials, analysisResult, financialData } = data;

  // Mock analysis data if not available
  const mockAnalysis = {
    metricScores: {
      profitability: 0,
      growth: 0,
      balanceSheet: 0,
      capitalAllocation: 0,
      valuation: 0,
      overall: 0,
    },
    insights: {
      recommendation: undefined,
      summary: 'Financial analysis is not yet available for this company.',
      strengths: ['Data collection in progress'],
      weaknesses: ['Analysis pending'],
      opportunities: ['Full analysis coming soon'],
      risks: ['Please check back later'],
    },
  };

  // Use the real analysis if available, otherwise use existing analysis result, or fallback to mock
  const currentAnalysis = analysis || analysisResult || mockAnalysis;

  // Transform database financial data to FMPFinancialStatements format

  const transformDatabaseDataToFMPFormat = (
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    incomeData: any,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    balanceData: any,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    cashFlowData: any
  ): FMPFinancialStatements => {
    // Extract the actual financial statement data from the nested structure
    const incomeStatement = incomeData?.income_statements?.[0] || {};
    const balanceSheet = balanceData?.balance_sheets?.[0] || {};
    const cashFlow = cashFlowData?.cash_flows?.[0] || {};

    return {
      incomeStatement: {
        symbol: incomeStatement.symbol || ticker.toUpperCase(),
        fiscalYear: incomeStatement.calendarYear?.toString() || '2024',
        reportedCurrency: incomeStatement.reportedCurrency || 'USD',
        revenue: incomeStatement.revenue || 0,
        grossProfit:
          incomeStatement.grossProfit ||
          incomeStatement.revenue - incomeStatement.costOfRevenue ||
          0,
        operatingIncome:
          incomeStatement.operatingIncome || incomeStatement.ebit || 0,
        netIncome:
          incomeStatement.netIncome || incomeStatement.bottomLineNetIncome || 0,
        interestExpense: incomeStatement.interestExpense || 0,
        // Add other required fields with defaults
        costOfRevenue: incomeStatement.costOfRevenue || 0,
        researchAndDevelopmentExpenses:
          incomeStatement.researchAndDevelopmentExpenses || 0,
        generalAndAdministrativeExpenses:
          incomeStatement.generalAndAdministrativeExpenses || 0,
        sellingAndMarketingExpenses:
          incomeStatement.sellingAndMarketingExpenses || 0,
        otherExpenses: incomeStatement.otherExpenses || 0,
        operatingExpenses: incomeStatement.operatingExpenses || 0,
        costAndExpenses: incomeStatement.costAndExpenses || 0,
        interestIncome: incomeStatement.interestIncome || 0,
        totalOtherIncomeExpensesNet:
          incomeStatement.totalOtherIncomeExpensesNet || 0,
        incomeBeforeTax: incomeStatement.incomeBeforeTax || 0,
        incomeTaxExpense: incomeStatement.incomeTaxExpense || 0,
        eps: incomeStatement.eps || 0,
        epsDiluted: incomeStatement.epsDiluted || 0,
        weightedAverageShsOut: incomeStatement.weightedAverageShsOut || 0,
        weightedAverageShsOutDil: incomeStatement.weightedAverageShsOutDil || 0,
      } as any,
      balanceSheet: {
        totalAssets: balanceSheet.totalAssets || 0,
        totalCurrentAssets: balanceSheet.totalCurrentAssets || 0,
        totalCurrentLiabilities: balanceSheet.totalCurrentLiabilities || 0,
        totalDebt: balanceSheet.totalDebt || 0,
        totalEquity:
          balanceSheet.totalStockholdersEquity || balanceSheet.totalEquity || 0,
        totalLiabilities: balanceSheet.totalLiabilities || 0,
        cashAndCashEquivalents: balanceSheet.cashAndCashEquivalents || 0,
        // Add other fields with defaults as needed
        shortTermInvestments: balanceSheet.shortTermInvestments || 0,
        cashAndShortTermInvestments:
          balanceSheet.cashAndShortTermInvestments || 0,
        netReceivables: balanceSheet.netReceivables || 0,
        inventory: balanceSheet.inventory || 0,
        otherCurrentAssets: balanceSheet.otherCurrentAssets || 0,
        propertyPlantEquipmentNet: balanceSheet.propertyPlantEquipmentNet || 0,
        goodwill: balanceSheet.goodwill || 0,
        intangibleAssets: balanceSheet.intangibleAssets || 0,
        otherAssets: balanceSheet.otherAssets || 0,
        accountPayables: balanceSheet.accountPayables || 0,
        shortTermDebt: balanceSheet.shortTermDebt || 0,
        deferredRevenue: balanceSheet.deferredRevenue || 0,
        otherCurrentLiabilities: balanceSheet.otherCurrentLiabilities || 0,
        longTermDebt: balanceSheet.longTermDebt || 0,
        deferredRevenueNonCurrent: balanceSheet.deferredRevenueNonCurrent || 0,
        deferredTaxLiabilitiesNonCurrent:
          balanceSheet.deferredTaxLiabilitiesNonCurrent || 0,
        otherNonCurrentLiabilities:
          balanceSheet.otherNonCurrentLiabilities || 0,
        totalNonCurrentLiabilities:
          balanceSheet.totalNonCurrentLiabilities || 0,
        commonStock: balanceSheet.commonStock || 0,
        retainedEarnings: balanceSheet.retainedEarnings || 0,
        accumulatedOtherComprehensiveIncomeLoss:
          balanceSheet.accumulatedOtherComprehensiveIncomeLoss || 0,
        othertotalStockholdersEquity:
          balanceSheet.othertotalStockholdersEquity || 0,
        totalStockholdersEquity: balanceSheet.totalStockholdersEquity || 0,
        totalLiabilitiesAndStockholdersEquity:
          balanceSheet.totalLiabilitiesAndStockholdersEquity || 0,
        minorityInterest: balanceSheet.minorityInterest || 0,
        totalInvestments: balanceSheet.totalInvestments || 0,
        totalDebtAndCapitalLease: balanceSheet.totalDebtAndCapitalLease || 0,
        netDebt: balanceSheet.netDebt || 0,
      } as any,
      cashFlow: {
        operatingCashFlow:
          cashFlow.operatingCashFlow ||
          cashFlow.netCashProvidedByOperatingActivities ||
          0,
        freeCashFlow: cashFlow.freeCashFlow || 0,
        // Add other required fields with defaults
        netIncome: cashFlow.netIncome || 0,
        depreciationAndAmortization: cashFlow.depreciationAndAmortization || 0,
        deferredIncomeTax: cashFlow.deferredIncomeTax || 0,
        stockBasedCompensation: cashFlow.stockBasedCompensation || 0,
        changeInWorkingCapital: cashFlow.changeInWorkingCapital || 0,
        accountsReceivables: cashFlow.accountsReceivables || 0,
        inventory: cashFlow.inventory || 0,
        accountsPayables: cashFlow.accountsPayables || 0,
        otherWorkingCapital: cashFlow.otherWorkingCapital || 0,
        otherNonCashItems: cashFlow.otherNonCashItems || 0,
        investmentsInPropertyPlantAndEquipment:
          cashFlow.investmentsInPropertyPlantAndEquipment || 0,
        acquisitionsNet: cashFlow.acquisitionsNet || 0,
        purchasesOfInvestments: cashFlow.purchasesOfInvestments || 0,
        salesMaturitiesOfInvestments:
          cashFlow.salesMaturitiesOfInvestments || 0,
        otherInvestingActivites: cashFlow.otherInvestingActivites || 0,
        netCashUsedForInvestingActivites:
          cashFlow.netCashUsedForInvestingActivites || 0,
        debtRepayment: cashFlow.debtRepayment || 0,
        commonStockIssued: cashFlow.commonStockIssued || 0,
        commonStockRepurchased: cashFlow.commonStockRepurchased || 0,
        dividendsPaid: cashFlow.dividendsPaid || 0,
        otherFinancingActivites: cashFlow.otherFinancingActivites || 0,
        netCashUsedProvidedByFinancingActivities:
          cashFlow.netCashUsedProvidedByFinancingActivities || 0,
        effectOfForexChangesOnCash: cashFlow.effectOfForexChangesOnCash || 0,
        netChangeInCash: cashFlow.netChangeInCash || 0,
        cashAtEndOfPeriod: cashFlow.cashAtEndOfPeriod || 0,
        cashAtBeginningOfPeriod: cashFlow.cashAtBeginningOfPeriod || 0,
        operatingCashFlowOverNetIncome:
          cashFlow.operatingCashFlowOverNetIncome || 0,
        freeCashFlowOverNetIncome: cashFlow.freeCashFlowOverNetIncome || 0,
      } as any,
    } as FMPFinancialStatements;
  };

  // Prepare financial data for analysis
  const prepareFinancialDataForAnalysis = () => {
    // First, try to get assembled financial statements
    let financialStatements =
      financialData
        ?.filter(
          (fd) =>
            fd.type === 'assembled-financial-statements' &&
            typeof fd.data === 'object' &&
            fd.data !== null
        )
        .map((fd) => fd.data as FMPFinancialStatements)
        .sort(
          (a, b) =>
            parseInt(a.incomeStatement.fiscalYear) -
            parseInt(b.incomeStatement.fiscalYear)
        ) || [];

    // If no assembled statements, try to construct them from individual statements
    if (financialStatements.length === 0) {
      // Group by year and period
      const groupedByYear: Record<
        string,
        {
          year: string;
          period: string;
          incomeStatement?: unknown;
          balanceSheet?: unknown;
          cashFlow?: unknown;
        }
      > = {};

      financialData?.forEach((fd) => {
        if (
          ['Income Statement', 'Balance Sheet', 'Cash Flow Statement'].includes(
            fd.type
          ) &&
          fd.data
        ) {
          const year = fd.year.toString();
          const period = fd.period || 'FY';
          const key = `${year}-${period}`;

          if (!groupedByYear[key]) {
            groupedByYear[key] = { year, period };
          }

          if (fd.type === 'Income Statement') {
            groupedByYear[key].incomeStatement = fd.data;
          } else if (fd.type === 'Balance Sheet') {
            groupedByYear[key].balanceSheet = fd.data;
          } else if (fd.type === 'Cash Flow Statement') {
            groupedByYear[key].cashFlow = fd.data;
          }
        }
      });

      // Convert to FMPFinancialStatements format with proper data transformation
      financialStatements = Object.values(groupedByYear)
        .filter(
          (group) =>
            group.incomeStatement &&
            group.balanceSheet &&
            group.cashFlow &&
            group.period === 'FY'
        )
        .map((group) =>
          transformDatabaseDataToFMPFormat(
            group.incomeStatement,
            group.balanceSheet,
            group.cashFlow
          )
        )
        .sort(
          (a, b) =>
            parseInt(a.incomeStatement.fiscalYear) -
            parseInt(b.incomeStatement.fiscalYear)
        );
    }

    return financialStatements;
  };

  const handleRunAnalysis = async () => {
    const financialStatements = prepareFinancialDataForAnalysis();

    if (financialStatements.length === 0) {
      alert('No financial data available for analysis');
      return;
    }

    console.log(
      `Running analysis for ${company.ticker} with ${financialStatements.length} years of data`
    );
    await runAnalysis(company, financialStatements, 'tech_v1');
  };

  // **SIMPLIFIED: Data is now pre-filtered by the API Gateway**
  // financialData now contains only SEC filings and financial statements
  // This significantly reduces payload size and improves performance

  // SEC filing types (matching backend configuration)
  const secFilingTypes = new Set([
    '10-K',
    '10-Q',
    '8-K',
    '20-F',
    '6-K',
    'DEF 14A',
    'S-1',
    'S-3',
    'S-4',
    'SC 13G',
    'SC 13D',
  ]);

  const filings =
    financialData
      ?.filter((fd) => secFilingTypes.has(fd.type))
      .map((fd) => {
        // For SEC filings, the data structure is different
        let filingData;

        try {
          // SEC filing data is stored as JSON string, parse it
          filingData =
            typeof fd.data === 'string' ? JSON.parse(fd.data) : fd.data;
        } catch (e) {
          console.warn('Failed to parse filing data:', e);
          return null;
        }

        return {
          id: fd.id,
          type: fd.type, // This will be "10-K", "10-Q", "8-K", etc.
          date: filingData.filingDate || filingData.filing_date,
          link:
            filingData.finalLink ||
            filingData.final_link ||
            filingData.report_url ||
            filingData.filing_url ||
            filingData.link,
          year: fd.year,
          period: fd.period,
          formType: filingData.form || filingData.formType || fd.type,
        };
      })
      .filter(
        (filing): filing is NonNullable<typeof filing> => filing !== null
      ) || [];

  const filteredFilings = filings.filter((filing) => {
    if (filter === 'ALL') return true;
    return filing.type === filter;
  });

  const financialStatements = prepareFinancialDataForAnalysis();

  return (
    <div className="container mx-auto py-8 space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Button asChild variant="ghost" size="sm" className="mb-4">
            <Link href="/">← Back to Dashboard</Link>
          </Button>
          <h1 className="text-3xl font-bold">{company.name}</h1>
          <div className="flex items-center gap-4 mt-2">
            <Badge variant="outline">{company.ticker}</Badge>
            <span className="text-muted-foreground">
              {company.sector} • {company.industry}
            </span>
          </div>
        </div>
        <div className="flex flex-col gap-2">
          <Button
            onClick={handleRunAnalysis}
            disabled={analysisLoading || financialStatements.length === 0}
            className="min-w-[120px]"
          >
            {analysisLoading ? 'Analyzing...' : 'Run Analysis'}
          </Button>
          {financialStatements.length > 0 && (
            <span className="text-xs text-muted-foreground text-center">
              {financialStatements.length} years of data
            </span>
          )}
        </div>
      </div>

      {/* Analysis Error */}
      {analysisError && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive text-sm">
              Analysis Error: {analysisError.message}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Analysis Score */}
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <ScoreCard
            title={analysis ? 'AI Analysis Score' : 'Analysis Score'}
            scores={currentAnalysis.metricScores}
            recommendation={currentAnalysis.insights.recommendation}
          />
        </div>

        <div className="lg:col-span-2 space-y-4">
          {/* Insights */}
          <Card>
            <CardHeader>
              <CardTitle>
                Key Insights
                {analysis && (
                  <Badge variant="secondary" className="ml-2">
                    AI Generated
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-4">{currentAnalysis.insights.summary}</p>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <h4 className="font-semibold text-green-600 mb-2">
                    Strengths
                  </h4>
                  <ul className="list-disc list-inside space-y-1">
                    {currentAnalysis.insights.strengths.map(
                      (strength: string, i: number) => (
                        <li key={i} className="text-sm">
                          {strength}
                        </li>
                      )
                    )}
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-red-600 mb-2">
                    Weaknesses
                  </h4>
                  <ul className="list-disc list-inside space-y-1">
                    {currentAnalysis.insights.weaknesses.map(
                      (weakness: string, i: number) => (
                        <li key={i} className="text-sm">
                          {weakness}
                        </li>
                      )
                    )}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Opportunities & Risks */}
          <Card>
            <CardHeader>
              <CardTitle>Opportunities & Risks</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <h4 className="font-semibold text-blue-600 mb-2">
                    Opportunities
                  </h4>
                  <ul className="list-disc list-inside space-y-1">
                    {currentAnalysis.insights.opportunities.map(
                      (opportunity: string, i: number) => (
                        <li key={i} className="text-sm">
                          {opportunity}
                        </li>
                      )
                    )}
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-orange-600 mb-2">Risks</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {currentAnalysis.insights.risks.map(
                      (risk: string, i: number) => (
                        <li key={i} className="text-sm">
                          {risk}
                        </li>
                      )
                    )}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Financial Metrics */}
      {latestFinancials &&
        latestFinancials.data &&
        latestFinancials.type &&
        [
          'Income Statement',
          'income-statement',
          'balance-sheet-statement',
          'cash-flow-statement',
          'assembled-financial-statements',
        ].includes(latestFinancials.type) && (
          <div>
            <h2 className="text-2xl font-semibold mb-4">Financial Metrics</h2>
            <FinancialMetrics
              financials={latestFinancials.data as FMPFinancialStatements}
              period={latestFinancials.period}
              year={latestFinancials.year}
            />
          </div>
        )}

      {/* Historical Data */}
      <Card>
        <CardHeader>
          <CardTitle>Financial History</CardTitle>
        </CardHeader>
        <CardContent>
          {filings.length > 0 ? (
            <>
              <div className="flex gap-2 mb-4">
                <Button
                  variant={filter === 'ALL' ? 'secondary' : 'outline'}
                  size="sm"
                  onClick={() => setFilter('ALL')}
                >
                  All Filings
                </Button>
                <Button
                  variant={filter === '10-K' ? 'secondary' : 'outline'}
                  size="sm"
                  onClick={() => setFilter('10-K')}
                >
                  10-K
                </Button>
                <Button
                  variant={filter === '10-Q' ? 'secondary' : 'outline'}
                  size="sm"
                  onClick={() => setFilter('10-Q')}
                >
                  10-Q
                </Button>
              </div>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Type</TableHead>
                    <TableHead>Filing Date</TableHead>
                    <TableHead>Period</TableHead>
                    <TableHead className="text-right">Link</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredFilings.map((filing) => (
                    <TableRow key={filing.id}>
                      <TableCell>
                        <Badge variant="outline">{filing.type}</Badge>
                      </TableCell>
                      <TableCell>
                        {new Date(filing.date).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        {filing.year} {filing.period}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button asChild variant="link" size="sm">
                          <Link
                            href={filing.link || '#'}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            View Filing
                          </Link>
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              {filteredFilings.length === 0 && (
                <p className="text-muted-foreground text-center py-4">
                  No filings found for the selected filter.
                </p>
              )}
            </>
          ) : (
            <p className="text-muted-foreground">
              Historical financial filings are not yet available for this
              company.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function CompanyDetailPage({
  params,
}: {
  params: Promise<{ ticker: string }>;
}) {
  const resolvedParams = use(params);
  const { ticker } = resolvedParams;
  return (
    <Suspense
      fallback={
        <div className="container mx-auto py-8">
          <div className="text-center">Loading...</div>
        </div>
      }
    >
      <CompanyDetailContent ticker={ticker} />
    </Suspense>
  );
}
