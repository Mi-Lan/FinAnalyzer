import { z } from 'zod';
import { ChatOpenAI } from '@langchain/openai';
import { ChatPromptTemplate, PromptTemplate } from '@langchain/core/prompts';
import { RunnableSequence } from '@langchain/core/runnables';

import { techSectorTemplate } from '../templates';
import {
  FinancialMetrics,
  TransformedFinancialData,
} from '../utils/data-transformer';
import { AnalysisInsights, MetricScores } from '@/types/financial';

// --- Zod Schemas for Validation and Output Parsing ---

const ScoreOutputSchema = z.object({
  score: z
    .number()
    .int()
    .min(1)
    .max(100)
    .describe('The numeric score from 1 to 100 for the dimension.'),
});

const InsightsOutputSchema = z.object({
  summary: z
    .string()
    .describe('A 2-3 sentence executive summary of the investment thesis.'),
  strengths: z.array(z.string()).describe('2-3 key strengths of the company.'),
  weaknesses: z
    .array(z.string())
    .describe('2-3 key weaknesses or areas of concern.'),
  opportunities: z
    .array(z.string())
    .describe('1-2 potential opportunities for the company.'),
  risks: z
    .array(z.string())
    .describe('1-2 key risks to the investment thesis.'),
  recommendation: z
    .enum(['BUY', 'HOLD', 'SELL'])
    .describe('A final investment recommendation.'),
});

// --- Model Initialization ---

const model = new ChatOpenAI({
  model: 'gpt-4o-mini',
  temperature: 0.2,
});

// --- Reusable Analysis Sub-Chain ---

const createDimensionChain = (promptTemplate: string) => {
  const prompt = PromptTemplate.fromTemplate(promptTemplate);
  return prompt.pipe(model.withStructuredOutput(ScoreOutputSchema));
};

// --- Chain Components ---

const formatMetrics = (metrics: FinancialMetrics): Record<string, string> => {
  const format = (
    value: number | null,
    unit: 'percent' | 'ratio' = 'percent'
  ) => {
    if (value === null || value === undefined) return 'N/A';
    if (unit === 'percent') return `${(value * 100).toFixed(1)}%`;
    return value.toFixed(2);
  };
  return {
    grossMargin: format(metrics.grossMargin),
    operatingMargin: format(metrics.operatingMargin),
    netMargin: format(metrics.netMargin),
    revenueGrowth: format(metrics.revenueGrowth),
    netIncomeGrowth: format(metrics.netIncomeGrowth),
    freeCashFlowGrowth: format(metrics.freeCashFlowGrowth),
    currentRatio: format(metrics.currentRatio, 'ratio'),
    debtToEquity: format(metrics.debtToEquity, 'ratio'),
    returnOnEquity: format(metrics.returnOnEquity),
    returnOnAssets: format(metrics.returnOnAssets),
    returnOnInvestedCapital: format(metrics.returnOnInvestedCapital),
    assetTurnover: format(metrics.assetTurnover, 'ratio'),
    operatingCashFlowMargin: format(metrics.operatingCashFlowMargin),
    freeCashFlowMargin: format(metrics.freeCashFlowMargin),
  };
};

const parallelDimensionAnalysis = RunnableSequence.from([
  (input: TransformedFinancialData) => ({
    ...input,
    ...formatMetrics(input.latestMetrics),
  }),
  {
    profitability: createDimensionChain(
      techSectorTemplate.prompts.profitability
    ),
    growth: createDimensionChain(techSectorTemplate.prompts.growth),
    balanceSheet: createDimensionChain(techSectorTemplate.prompts.balanceSheet),
    capitalAllocation: createDimensionChain(
      techSectorTemplate.prompts.capitalAllocation
    ),
    valuation: createDimensionChain(techSectorTemplate.prompts.valuation),
  },
]);

type DimensionScores = {
  profitability: { score: number };
  growth: { score: number };
  balanceSheet: { score: number };
  capitalAllocation: { score: number };
  valuation: { score: number };
};

const calculateOverallScore = (result: DimensionScores): MetricScores => {
  const { weights } = techSectorTemplate;
  const overall =
    result.profitability.score * weights.profitability +
    result.growth.score * weights.growth +
    result.balanceSheet.score * weights.balanceSheet +
    result.capitalAllocation.score * weights.capitalAllocation +
    result.valuation.score * weights.valuation;

  return {
    profitability: result.profitability.score,
    growth: result.growth.score,
    balanceSheet: result.balanceSheet.score,
    capitalAllocation: result.capitalAllocation.score,
    valuation: result.valuation.score,
    overall: Math.round(overall),
  };
};

const insightsChain = RunnableSequence.from([
  (input: {
    scores: MetricScores;
    dimensions: DimensionScores;
    companyInfo: TransformedFinancialData['companyInfo'];
  }) => ({
    symbol: input.companyInfo.symbol,
    overallScore: input.scores.overall,
    profitabilityAnalysis: JSON.stringify(input.dimensions.profitability),
    growthAnalysis: JSON.stringify(input.dimensions.growth),
    balanceSheetAnalysis: JSON.stringify(input.dimensions.balanceSheet),
    capitalAllocationAnalysis: JSON.stringify(
      input.dimensions.capitalAllocation
    ),
    valuationAnalysis: JSON.stringify(input.dimensions.valuation),
  }),
  ChatPromptTemplate.fromTemplate(techSectorTemplate.prompts.insights),
  model.withStructuredOutput(InsightsOutputSchema),
]);

// --- Main Analysis Chain ---

export const techSectorAnalysisChain = RunnableSequence.from([
  {
    dimensions: parallelDimensionAnalysis,
    companyInfo: (input: TransformedFinancialData) => input.companyInfo,
  },
  {
    scores: ({ dimensions }) => calculateOverallScore(dimensions),
    dimensions: ({ dimensions }) => dimensions,
    companyInfo: ({ companyInfo }) => companyInfo,
  },
  {
    insights: insightsChain,
    scores: ({ scores }) => scores,
  },
]);

export type AnalysisChainOutput = {
  scores: MetricScores;
  insights: AnalysisInsights;
};
