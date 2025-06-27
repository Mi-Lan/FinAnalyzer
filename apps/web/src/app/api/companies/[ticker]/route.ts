import { NextResponse } from 'next/server';

// Mark the route dynamic so it always runs on demand
export const dynamic = 'force-dynamic';

const API_GATEWAY_URL =
  process.env.API_GATEWAY_URL || 'http://api-gateway:8000';
const API_KEY = process.env.API_KEY;

export async function GET(
  request: Request,
  { params }: { params: { ticker: string } }
) {
  const { ticker } = params;

  if (!API_KEY) {
    return NextResponse.json(
      { error: 'API key is not configured' },
      { status: 500 }
    );
  }

  try {
    const response = await fetch(`${API_GATEWAY_URL}/api/companies/${ticker}`, {
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || 'Failed to fetch from API Gateway' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching from API Gateway:', error);
    return NextResponse.json(
      { error: 'An internal error occurred' },
      { status: 500 }
    );
  }
}
