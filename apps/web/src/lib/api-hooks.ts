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
