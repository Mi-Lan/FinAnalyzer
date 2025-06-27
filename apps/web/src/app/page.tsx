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
  const [filters] = useState({
    minScore: 60,
  });

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

  const topPerformers = screeningResult?.companies
    .sort((a, b) => b.analysis.score - a.analysis.score)
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
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {topPerformers?.map((item) => (
            <ScoreCard
              key={item.company.id}
              title={`${item.company.name} (${item.company.ticker})`}
              scores={item.analysis.metricScores}
              recommendation={item.analysis.insights.recommendation}
            />
          ))}
        </div>
      </div>

      {/* All Companies Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Companies</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Company</TableHead>
                <TableHead>Sector</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Recommendation</TableHead>
                <TableHead>Latest Financials</TableHead>
                <TableHead>Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {screeningResult?.companies.map((item) => (
                <TableRow key={item.company.id}>
                  <TableCell className="font-medium">
                    <div>
                      <div>{item.company.name}</div>
                      <div className="text-sm text-muted-foreground">
                        {item.company.ticker}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>{item.company.sector}</TableCell>
                  <TableCell>
                    <div
                      className={`font-medium ${
                        item.analysis.score >= 80
                          ? 'text-green-600'
                          : item.analysis.score >= 60
                          ? 'text-yellow-600'
                          : 'text-red-600'
                      }`}
                    >
                      {item.analysis.score}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        item.analysis.insights.recommendation === 'BUY'
                          ? 'default'
                          : item.analysis.insights.recommendation === 'HOLD'
                          ? 'secondary'
                          : 'destructive'
                      }
                    >
                      {item.analysis.insights.recommendation}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {item.latestFinancials ? (
                      `${item.latestFinancials.period} ${item.latestFinancials.year}`
                    ) : (
                      <span className="text-muted-foreground">N/A</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <Button asChild size="sm">
                      <Link href={`/company/${item.company.ticker}`}>
                        View Details
                      </Link>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
