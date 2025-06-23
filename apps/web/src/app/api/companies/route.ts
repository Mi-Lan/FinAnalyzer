import { NextResponse } from 'next/server';
import { mockCompanies } from '@/lib/mockData';

export async function GET() {
  return NextResponse.json({
    companies: mockCompanies,
    total: mockCompanies.length,
  });
}
