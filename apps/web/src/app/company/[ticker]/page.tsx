'use client';

import { Suspense, use } from 'react';
import { useCompanyDetails } from '@/lib/api-hooks';
import { ScoreCard } from '@/components/score-card';
import { FinancialMetrics } from '@/components/financial-metrics';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

function CompanyDetailContent({ ticker }: { ticker: string }) {
  const { data, isLoading, error } = useCompanyDetails(ticker);

  if (isLoading) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">Loading company details...</div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center text-red-600">
          {error?.message || 'Company not found'}
        </div>
      </div>
    );
  }

  const { company, latestFinancials, analysisResult } = data;

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
            scores={analysisResult.metricScores}
            recommendation={analysisResult.insights.recommendation}
          />
        </div>

        <div className="lg:col-span-2 space-y-4">
          {/* Insights */}
          <Card>
            <CardHeader>
              <CardTitle>Key Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-4">{analysisResult.insights.summary}</p>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <h4 className="font-semibold text-green-600 mb-2">
                    Strengths
                  </h4>
                  <ul className="list-disc list-inside space-y-1">
                    {analysisResult.insights.strengths.map(
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
                    {analysisResult.insights.weaknesses.map(
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
                    {analysisResult.insights.opportunities.map(
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
                    {analysisResult.insights.risks.map(
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
      <div>
        <h2 className="text-2xl font-semibold mb-4">Financial Metrics</h2>
        <FinancialMetrics
          financials={latestFinancials.data}
          period={latestFinancials.period}
          year={latestFinancials.year}
        />
      </div>

      {/* Historical Data */}
      <Card>
        <CardHeader>
          <CardTitle>Financial History</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Latest data from {latestFinancials.period} {latestFinancials.year}.
            Historical trend analysis and multi-period comparisons will be
            available in the full version.
          </p>
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
  const { ticker } = use(params);
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
