'use client';

import { useQuery } from '@tanstack/react-query';
import type {
  ScreeningResult,
  CompanyDetailsResponse,
  CompanyWithAnalysis,
} from '@/types/financial';

// Fetch all companies
export function useCompanies() {
  return useQuery({
    queryKey: ['companies'],
    queryFn: async () => {
      const response = await fetch('/api/companies');
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.error ||
            'Failed to fetch companies. Please try again later.'
        );
      }
      return response.json();
    },
    staleTime: 15 * 60 * 1000, // 15 minutes
    refetchInterval: 60 * 1000, // Refetch every 1 minute
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
    queryFn: async (): Promise<CompanyWithAnalysis[]> => {
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
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.error ||
            'Failed to fetch screening results. Please try again later.'
        );
      }

      return response.json();
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
}

// Fetch bulk analysis job status
export function useBulkAnalysisJob(jobId?: string) {
  return useQuery({
    queryKey: ['bulk-analysis', jobId],
    queryFn: async () => {
      const response = await fetch(`/api/analysis/bulk?jobId=${jobId}`);
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

export const useCompanyAnalysis = () => {
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const runAnalysis = useCallback(
    async (
      company: Company,
      financials: FMPFinancialStatements[],
      templateId: string
    ) => {
      setIsLoading(true);
      setError(null);
      setAnalysis(null);

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

        const analysisResult = await response.json();
        setAnalysis(analysisResult);
      } catch (err) {
        setError(err as Error);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { analysis, isLoading, error, runAnalysis };
};
