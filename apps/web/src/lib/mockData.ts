import {
  AnalysisResult,
  BulkAnalysisJob,
  AnalysisTemplate,
  MetricScores,
  AnalysisInsights,
} from '@/types/financial';

// Mock analysis templates for future implementation
export const mockAnalysisTemplates: AnalysisTemplate[] = [
  {
    id: '1',
    name: 'Technology Sector Analysis',
    description: 'Comprehensive analysis for technology companies',
    sectors: ['Technology'],
    template: {
      weights: {
        profitability: 0.2,
        growth: 0.3,
        balanceSheet: 0.2,
        capitalAllocation: 0.2,
        valuation: 0.1,
      },
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

// Mock bulk analysis job for UI development
export const mockBulkAnalysisJob: BulkAnalysisJob = {
  id: 'job_123',
  status: 'IN_PROGRESS',
  progress: 0.45,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};

// Helper to generate mock analysis result
export function generateMockAnalysisResult(
  companyId: string,
  templateId: string
): AnalysisResult {
  // Generate random but consistent scores based on company ID
  const seed = companyId.charCodeAt(0);
  const baseScore = 60 + (seed % 30);

  const metricScores: MetricScores = {
    profitability: baseScore + (seed % 10),
    growth: baseScore + ((seed * 2) % 10),
    balanceSheet: baseScore + ((seed * 3) % 10),
    capitalAllocation: baseScore + ((seed * 4) % 10),
    valuation: baseScore - ((seed * 5) % 10),
    overall: baseScore,
  };

  const insights: AnalysisInsights = {
    summary:
      'This is a placeholder analysis summary until AI analysis is implemented.',
    strengths: ['Strong market position', 'Solid financials'],
    weaknesses: ['High valuation', 'Competitive pressure'],
    opportunities: ['Market expansion', 'New product lines'],
    risks: ['Economic downturn', 'Regulatory changes'],
    recommendation: baseScore >= 80 ? 'BUY' : baseScore >= 60 ? 'HOLD' : 'SELL',
  };

  return {
    id: `analysis_${companyId}`,
    companyId,
    templateId,
    score: baseScore,
    insights,
    metricScores,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
}
