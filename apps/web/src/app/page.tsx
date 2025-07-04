'use client';

import { useState } from 'react';
import { useScreening } from '@/lib/api-hooks';
import { ScoreCard } from '@/components/score-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function DashboardPage() {
  const [filters] = useState({});

  const { data: screeningResult, isLoading, error } = useScreening(filters);

  if (isLoading) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">Loading financial data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center text-red-600">
          Error loading data: {error.message}
        </div>
      </div>
    );
  }

  // The API now returns a direct array of CompanyWithAnalysis
  const companies = screeningResult || [];

  // Filter companies that have analysis scores for top performers
  const companiesWithScores = companies.filter(
    (item) => typeof item.score === 'number'
  );

  const topPerformers = companiesWithScores
    .sort((a, b) => (b.score || 0) - (a.score || 0))
    .slice(0, 3);

  return (
    <div className="container mx-auto py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Financial Analysis Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          AI-powered financial analysis and stock screening
        </p>
      </div>

      {/* Top Performers */}
      <div>
        <h2 className="text-2xl font-semibold mb-4">Top Performers</h2>
        {topPerformers.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {topPerformers.map((item) => (
              <ScoreCard
                key={item.id}
                title={`${item.name} (${item.ticker})`}
                scores={{
                  overall: item.score || 0,
                  // The detailed metricScores are not available in the screening response,
                  // so we create a simplified structure for the ScoreCard.
                  profitability: item.score || 0,
                  growth: item.score || 0,
                  balanceSheet: item.score || 0,
                  capitalAllocation: item.score || 0,
                  valuation: item.score || 0,
                }}
                recommendation={item.insights?.recommendation}
              />
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="p-6">
              <p className="text-muted-foreground text-center">
                Analysis scores are not yet available. Companies are loaded but
                analysis is pending.
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* All Companies Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Companies ({companies.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Company</TableHead>
                <TableHead>Sector</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Recommendation</TableHead>
                <TableHead>Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {companies.map((company) => {
                return (
                  <TableRow key={company.id}>
                    <TableCell className="font-medium">
                      <div>
                        <div>{company.name}</div>
                        <div className="text-sm text-muted-foreground">
                          {company.ticker}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {company.sector || 'Unknown'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {typeof company.score === 'number' ? (
                        <div
                          className={`font-medium ${
                            company.score >= 80
                              ? 'text-green-600'
                              : company.score >= 60
                              ? 'text-yellow-600'
                              : 'text-red-600'
                          }`}
                        >
                          {company.score}
                        </div>
                      ) : (
                        <span className="text-muted-foreground">Pending</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {company.insights?.recommendation ? (
                        <Badge
                          variant={
                            company.insights.recommendation === 'BUY'
                              ? 'default'
                              : company.insights.recommendation === 'HOLD'
                              ? 'secondary'
                              : 'destructive'
                          }
                        >
                          {company.insights.recommendation}
                        </Badge>
                      ) : (
                        <span className="text-muted-foreground">Pending</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <Button asChild size="sm">
                        <Link href={`/company/${company.ticker}`}>
                          View Details
                        </Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
