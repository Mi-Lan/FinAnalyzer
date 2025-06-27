import { NextResponse } from 'next/server';
import {
  generateMockAnalysisResult,
  mockAnalysisTemplates,
} from '@/lib/mockData';
import { ScreeningResult } from '@/types/financial';

const API_GATEWAY_URL =
  process.env.API_GATEWAY_URL || 'http://api-gateway:8000';
const API_KEY = process.env.API_KEY;

// List of known tickers to use for demo purposes
const DEMO_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA'];

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);

  const sector = searchParams.get('sector');
  const minScore = searchParams.get('minScore');
  const maxScore = searchParams.get('maxScore');
  const recommendation = searchParams.get('recommendation');

  if (!API_KEY) {
    return NextResponse.json(
      { error: 'API key is not configured' },
      { status: 500 }
    );
  }

  const screeningResults = [];

  // Fetch real data for demo tickers
  for (const ticker of DEMO_TICKERS) {
    try {
      const response = await fetch(
        `${API_GATEWAY_URL}/api/companies/${ticker}`,
        {
          headers: {
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.ok) {
        const data = await response.json();

        // Generate mock analysis for the real company data
        const analysisResult = generateMockAnalysisResult(
          data.company.id,
          mockAnalysisTemplates[0].id
        );

        // Apply sector filter
        if (sector && data.company.sector !== sector) {
          continue;
        }

        screeningResults.push({
          company: data.company,
          latestFinancials: data.latestFinancials,
          analysis: analysisResult,
        });
      }
    } catch (error) {
      console.error(`Error fetching ${ticker}:`, error);
      // Continue with other tickers
    }
  }

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
