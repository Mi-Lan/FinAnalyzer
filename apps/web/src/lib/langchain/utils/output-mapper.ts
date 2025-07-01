import { v4 as uuidv4 } from 'uuid';
import { AnalysisResult } from '@/types/financial';
import { AnalysisChainOutput } from '../chains';

type MapperInput = {
  chainOutput: AnalysisChainOutput;
  companyId: string;
  templateId: string;
  jobId?: string;
};

export const mapChainOutputToAnalysisResult = ({
  chainOutput,
  companyId,
  templateId,
  jobId,
}: MapperInput): AnalysisResult => {
  const now = new Date().toISOString();
  return {
    id: uuidv4(),
    companyId,
    templateId,
    jobId,
    score: chainOutput.scores.overall,
    insights: chainOutput.insights,
    metricScores: chainOutput.scores,
    createdAt: now,
    updatedAt: now,
  };
};
