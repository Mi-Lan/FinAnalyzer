import { NextRequest, NextResponse } from 'next/server';
import { techSectorAnalysisChain } from '@/lib/langchain/chains';
import { transformFinancialDataForPrompts } from '@/lib/langchain/utils/data-transformer';
import { FMPFinancialStatements, Company } from '@/types/financial';

export const runtime = 'edge';

export async function POST(
  req: NextRequest,
  { params }: { params: { templateId: string } }
) {
  const { templateId } = params;

  // For now, we only support the tech sector template
  if (templateId !== 'tech-default-v1') {
    return NextResponse.json(
      { error: `Template ${templateId} not found.` },
      { status: 404 }
    );
  }

  try {
    const body = await req.json();
    const {
      financials,
      company,
    }: { financials: FMPFinancialStatements[]; company: Company } = body;

    if (!financials || !company || financials.length === 0) {
      return NextResponse.json(
        { error: 'Missing or invalid financial data or company info' },
        { status: 400 }
      );
    }

    const transformedData = transformFinancialDataForPrompts(financials);

    const stream = await techSectorAnalysisChain.stream(transformedData);

    const readableStream = new ReadableStream({
      async start(controller) {
        for await (const chunk of stream) {
          controller.enqueue(`data: ${JSON.stringify(chunk)}\n\n`);
        }
        controller.close();
      },
    });

    return new Response(readableStream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive',
      },
    });
  } catch (e: unknown) {
    console.error(e);
    let error = 'Failed to run analysis';
    if (e instanceof Error) {
      error = e.message;
    }
    return NextResponse.json({ error }, { status: 500 });
  }
}
