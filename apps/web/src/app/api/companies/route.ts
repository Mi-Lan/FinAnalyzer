import { NextResponse } from 'next/server';

const API_GATEWAY_URL =
  process.env.API_GATEWAY_URL || 'http://api-gateway:8000';
const API_KEY = process.env.API_KEY;

export async function GET() {
  if (!API_KEY) {
    return NextResponse.json(
      { error: 'API key is not configured' },
      { status: 500 }
    );
  }

  try {
    const response = await fetch(`${API_GATEWAY_URL}/api/companies`, {
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      // For now, return empty list since backend doesn't implement this yet
      if (response.status === 501) {
        return NextResponse.json({
          companies: [],
          total: 0,
        });
      }

      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || 'Failed to fetch from API Gateway' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json({
      companies: data,
      total: data.length,
    });
  } catch (error) {
    console.error('Error fetching from API Gateway:', error);
    // Return empty list for now
    return NextResponse.json({
      companies: [],
      total: 0,
    });
  }
}
