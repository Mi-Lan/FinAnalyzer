import { NextResponse } from 'next/server';
import { getMockCompanyData } from '@/lib/mockData';

export async function GET(
  request: Request,
  { params }: { params: { ticker: string } }
) {
  const { ticker } = params;
  const data = getMockCompanyData(ticker.toUpperCase());

  if (!data) {
    return NextResponse.json({ error: 'Company not found' }, { status: 404 });
  }

  return NextResponse.json(data);
}
