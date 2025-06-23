import { NextResponse } from 'next/server';
import { getMockCompanyData } from '@/lib/mockData';

// Mark the route dynamic so it always runs on demand
export const dynamic = 'force-dynamic';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ ticker: string }> }
) {
  // ✅ wait for the params object before using it
  const { ticker } = await params;

  const data = getMockCompanyData(ticker.toUpperCase());

  if (!data) {
    return NextResponse.json({ error: 'Company not found' }, { status: 404 });
  }

  return NextResponse.json(data);
}
