import { NextResponse } from 'next/server';
import {
  mockCompanies,
  generateMockFinancialData,
  generateMockAnalysisResult,
  mockAnalysisTemplates,
} from '@/lib/mockData';
import { ScreeningResult } from '@/types/financial';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);

  const sector = searchParams.get('sector');
  const minScore = searchParams.get('minScore');
  const maxScore = searchParams.get('maxScore');
  const recommendation = searchParams.get('recommendation');

  // Filter companies based on criteria
  let filteredCompanies = [...mockCompanies];

  if (sector) {
    filteredCompanies = filteredCompanies.filter((c) => c.sector === sector);
  }

  // Generate analysis results for filtered companies
  const screeningResults = filteredCompanies.map((company) => {
    const financialData = generateMockFinancialData(company.id, company.ticker);
    const latestFinancials =
      financialData.find(
        (fd) => fd.period === 'Q2' && fd.year === new Date().getFullYear()
      ) || financialData[0];
    const analysisResult = generateMockAnalysisResult(
      company.id,
      mockAnalysisTemplates[0].id,
      latestFinancials
    );

    return {
      company,
      latestFinancials,
      analysis: analysisResult,
    };
  });

  // Apply score and recommendation filters
  let filteredResults = screeningResults;

  if (minScore) {
    filteredResults = filteredResults.filter(
      (r) => r.analysis.score >= parseFloat(minScore)
    );
  }

  if (maxScore) {
    filteredResults = filteredResults.filter(
      (r) => r.analysis.score <= parseFloat(maxScore)
    );
  }

  if (recommendation) {
    filteredResults = filteredResults.filter(
      (r) =>
        r.analysis.insights.recommendation.toLowerCase() ===
        recommendation.toLowerCase()
    );
  }

  const result: ScreeningResult = {
    companies: filteredResults,
    totalCount: filteredResults.length,
    filters: {
      sector: sector || undefined,
      minScore: minScore ? parseFloat(minScore) : undefined,
      maxScore: maxScore ? parseFloat(maxScore) : undefined,
      recommendation: recommendation || undefined,
    },
  };

  return NextResponse.json(result);
}
