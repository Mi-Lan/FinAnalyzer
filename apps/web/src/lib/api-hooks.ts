'use client';

import { useQuery } from '@tanstack/react-query';
import type {
  ScreeningResult,
  CompanyDetailsResponse,
} from '@/types/financial';

// Fetch all companies
export function useCompanies() {
  return useQuery({
    queryKey: ['companies'],
    queryFn: async () => {
      const response = await fetch('/api/companies');
      if (!response.ok) throw new Error('Failed to fetch companies');
      return response.json();
    },
    staleTime: 15 * 60 * 1000, // 15 minutes
  });
}

// Fetch company details with financials and analysis
export function useCompanyDetails(ticker: string) {
  return useQuery({
    queryKey: ['company', ticker],
    queryFn: async (): Promise<CompanyDetailsResponse> => {
      const response = await fetch(`/api/companies/${ticker}`);
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Company not found');
        }
        throw new Error('Failed to fetch company details');
      }
      return response.json();
    },
    enabled: !!ticker,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Screen companies with filters
export function useScreening(filters: {
  sector?: string;
  minScore?: number;
  maxScore?: number;
  recommendation?: string;
}) {
  return useQuery({
    queryKey: ['screening', filters],
    queryFn: async (): Promise<ScreeningResult> => {
      const params = new URLSearchParams();

      if (filters.sector) params.append('sector', filters.sector);
      if (filters.minScore !== undefined)
        params.append('minScore', filters.minScore.toString());
      if (filters.maxScore !== undefined)
        params.append('maxScore', filters.maxScore.toString());
      if (filters.recommendation)
        params.append('recommendation', filters.recommendation);

      const response = await fetch(`/api/analysis/screen?${params.toString()}`);

      if (!response.ok) {
        throw new Error('Failed to fetch screening results');
      }

      return response.json();
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Fetch bulk analysis job status
export function useBulkAnalysisJob(jobId?: string) {
  return useQuery({
    queryKey: ['bulk-analysis', jobId],
    queryFn: async () => {
      const response = await fetch('/api/analysis/bulk');
      if (!response.ok) throw new Error('Failed to fetch bulk analysis status');
      return response.json();
    },
    enabled: !!jobId,
    refetchInterval: 2000, // Poll every 2 seconds
    staleTime: 0, // Always refetch
  });
}

// --- Custom Hook for Streaming Company Analysis ---

import { useState, useCallback } from 'react';
import {
  AnalysisResult,
  FMPFinancialStatements,
  Company,
} from '@/types/financial';
import { AnalysisChainOutput } from './langchain/chains';
import { mapChainOutputToAnalysisResult } from './langchain/utils/output-mapper';

export const useCompanyAnalysis = () => {
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [progress, setProgress] = useState<AnalysisChainOutput | null>(null);

  const runAnalysis = useCallback(
    async (
      company: Company,
      financials: FMPFinancialStatements[],
      templateId: string
    ) => {
      setIsLoading(true);
      setError(null);
      setAnalysis(null);
      setProgress(null);

      try {
        const response = await fetch(`/api/analysis/template/${templateId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ company, financials }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Analysis failed');
        }

        if (!response.body) throw new Error('Response body is null');

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let lastResult: AnalysisChainOutput | null = null;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const jsonString = line.substring(6);
              if (jsonString) {
                try {
                  const parsedChunk = JSON.parse(
                    jsonString
                  ) as AnalysisChainOutput;
                  lastResult = parsedChunk;
                  setProgress(parsedChunk); // Update progress with the latest chunk
                } catch {
                  console.error('Failed to parse stream chunk:', jsonString);
                }
              }
            }
          }
        }

        if (lastResult) {
          const finalResult = mapChainOutputToAnalysisResult({
            chainOutput: lastResult,
            companyId: company.id,
            templateId,
          });
          setAnalysis(finalResult);
        } else {
          throw new Error('Stream ended without a final result.');
        }
      } catch (err) {
        setError(err as Error);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { analysis, progress, isLoading, error, runAnalysis };
};
