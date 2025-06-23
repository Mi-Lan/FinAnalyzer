import { NextResponse } from 'next/server';
import { mockBulkAnalysisJob } from '@/lib/mockData';

export async function GET() {
  // Simulate progress update
  const progress = Math.min(mockBulkAnalysisJob.progress + 0.05, 1.0);

  return NextResponse.json({
    ...mockBulkAnalysisJob,
    progress,
    status: progress >= 1.0 ? 'COMPLETED' : mockBulkAnalysisJob.status,
  });
}

export async function POST(request: Request) {
  const body = await request.json();
  const { tickers, templateId } = body;

  // Create a new bulk analysis job
  const newJob = {
    id: `job_${Date.now()}`,
    status: 'PENDING',
    progress: 0,
    tickerCount: tickers?.length || 0,
    templateId,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  return NextResponse.json(newJob, { status: 201 });
}
