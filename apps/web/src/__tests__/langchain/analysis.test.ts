/** @jest-environment node */

import { transformFinancialDataForPrompts } from '@/lib/langchain/utils/data-transformer';
import { mapChainOutputToAnalysisResult } from '@/lib/langchain/utils/output-mapper';
import { mockFinancials, mockCompany } from './mock-data';
import { techSectorAnalysisChain } from '@/lib/langchain/chains';

// Mock the entire chain, not the underlying model
jest.mock('@/lib/langchain/chains', () => ({
  techSectorAnalysisChain: {
    invoke: jest.fn().mockResolvedValue({
      scores: {
        profitability: 85,
        growth: 92,
        balanceSheet: 78,
        capitalAllocation: 88,
        valuation: 65,
        overall: 83,
      },
      insights: {
        summary: 'A strong growth story with solid profitability.',
        strengths: ['High revenue growth', 'Expanding margins'],
        weaknesses: ['High valuation', 'Dependence on key products'],
        opportunities: ['International expansion'],
        risks: ['Increased competition'],
        recommendation: 'BUY',
      },
    }),
  },
}));

describe('LangChain Analysis Integration Test', () => {
  it('should process financial data, call the analysis chain, and map the result', async () => {
    // 1. Test the data transformer
    const transformedData = transformFinancialDataForPrompts(mockFinancials);

    expect(transformedData).toBeDefined();
    expect(transformedData.latestMetrics.grossMargin).toBeCloseTo(0.6667);

    // 2. Invoke the (mocked) analysis chain
    const chainResult = await techSectorAnalysisChain.invoke(transformedData);

    // Verify the mock was called correctly
    expect(techSectorAnalysisChain.invoke).toHaveBeenCalledWith(
      transformedData
    );
    expect(chainResult.scores.overall).toBe(83);
    expect(chainResult.insights.recommendation).toBe('BUY');

    // 3. Test the output mapper
    const finalResult = mapChainOutputToAnalysisResult({
      chainOutput: chainResult,
      companyId: mockCompany.id,
      templateId: 'tech-default-v1',
    });

    expect(finalResult).toHaveProperty('id');
    expect(finalResult.companyId).toBe(mockCompany.id);
    expect(finalResult.score).toBe(83);
    expect(finalResult.insights.summary).toBe(
      'A strong growth story with solid profitability.'
    );
  });
});
