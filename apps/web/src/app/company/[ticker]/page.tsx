'use client';

import { Suspense, use, useState } from 'react';
import { useCompanyDetails } from '@/lib/api-hooks';
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

function CompanyDetailContent({ ticker }: { ticker: string }) {
  const { data, isLoading, error } = useCompanyDetails(ticker);
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

  const analysis = analysisResult || mockAnalysis;

  // Filter out financial statements and show only actual SEC filings
  const filings =
    financialData
      ?.filter((fd) => {
        // Exclude financial statement types and only include SEC filing types
        const financialStatementTypes = [
          'Income Statement',
          'Balance Sheet',
          'Cash Flow Statement',
          'income-statement',
          'balance-sheet-statement',
          'cash-flow-statement',
        ];
        return !financialStatementTypes.includes(fd.type);
      })
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
      </div>

      {/* Analysis Score */}
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <ScoreCard
            title="Analysis Score"
            scores={analysis.metricScores}
            recommendation={analysis.insights.recommendation}
          />
        </div>

        <div className="lg:col-span-2 space-y-4">
          {/* Insights */}
          <Card>
            <CardHeader>
              <CardTitle>Key Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-4">{analysis.insights.summary}</p>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <h4 className="font-semibold text-green-600 mb-2">
                    Strengths
                  </h4>
                  <ul className="list-disc list-inside space-y-1">
                    {analysis.insights.strengths.map(
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
                    {analysis.insights.weaknesses.map(
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
                    {analysis.insights.opportunities.map(
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
                    {analysis.insights.risks.map((risk: string, i: number) => (
                      <li key={i} className="text-sm">
                        {risk}
                      </li>
                    ))}
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
              financials={latestFinancials.data as any}
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
