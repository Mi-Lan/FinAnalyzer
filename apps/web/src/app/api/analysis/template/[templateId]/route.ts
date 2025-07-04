import { NextRequest, NextResponse } from 'next/server';
import { techSectorAnalysisChain } from '@/lib/langchain/chains/tech-sector';
import { transformFinancialDataForPrompts } from '@/lib/langchain/utils/data-transformer';
import { mapChainOutputToAnalysisResult } from '@/lib/langchain/utils/output-mapper';

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ templateId: string }> }
) {
  const { templateId } = await params;

  // Validate template ID
  if (templateId !== 'tech_v1') {
    return NextResponse.json(
      {
        error:
          'Template not found. Currently only "tech_v1" template is supported.',
      },
      { status: 404 }
    );
  }

  // Check for OpenAI API key
  if (!process.env.OPENAI_API_KEY) {
    return NextResponse.json(
      { error: 'OpenAI API key is not configured' },
      { status: 500 }
    );
  }

  try {
    const body = await req.json();
    const { financials, company } = body;

    if (!financials || !Array.isArray(financials) || financials.length === 0) {
      return NextResponse.json(
        { error: 'Financial data is required' },
        { status: 400 }
      );
    }

    if (!company?.ticker) {
      return NextResponse.json(
        { error: 'Company ticker is required' },
        { status: 400 }
      );
    }

    console.log(
      `🔍 Starting analysis for ${company.ticker} with ${financials.length} years of data`
    );

    // Transform financial data for the prompt chain
    const transformedData = transformFinancialDataForPrompts(financials);

    console.log(
      `📊 Transformed data for ${transformedData.companyInfo.symbol}`
    );

    // Run the analysis chain
    const chainResult = await techSectorAnalysisChain.invoke(transformedData);

    console.log(`✅ Analysis complete for ${company.ticker}`);

    // Map to the expected AnalysisResult format
    const result = mapChainOutputToAnalysisResult({
      chainOutput: chainResult,
      companyId: company.id,
      templateId,
    });

    // Save the result to the database via the API gateway
    const gatewayUrl = process.env.API_GATEWAY_URL || 'http://api-gateway:8000';
    await fetch(`${gatewayUrl}/api/analysis/save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': process.env.API_KEY || 'your-secret-api-key',
      },
      body: JSON.stringify(result),
    });

    // Return the result as a JSON response
    return NextResponse.json(result);
  } catch (error) {
    console.error('❌ Analysis failed:', error);

    let errorMessage = 'Failed to run analysis';
    if (error instanceof Error) {
      errorMessage = error.message;
    }

    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}
