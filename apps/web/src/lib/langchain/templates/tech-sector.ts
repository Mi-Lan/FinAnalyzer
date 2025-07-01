export interface SectorTemplate {
  id: string;
  name: string;
  description: string;
  weights: {
    profitability: number;
    growth: number;
    balanceSheet: number;
    capitalAllocation: number;
    valuation: number;
  };
  prompts: {
    profitability: string;
    growth: string;
    balanceSheet: string;
    capitalAllocation: string;
    valuation: string;
    insights: string;
  };
}

export const techSectorTemplate: SectorTemplate = {
  id: 'tech-default-v1',
  name: 'Tech Sector Analysis',
  description:
    'A default template for analyzing public technology companies, focusing on growth, profitability, and innovation.',
  weights: {
    growth: 0.3,
    profitability: 0.25,
    balanceSheet: 0.15,
    capitalAllocation: 0.2,
    valuation: 0.1,
  },
  prompts: {
    profitability: `
      Analyze the company's profitability as a technology firm, where high margins can indicate a strong competitive advantage (moat) or valuable intellectual property.
      
      Key Metrics:
      - Gross Margin: {grossMargin} (Indicates pricing power and production efficiency)
      - Operating Margin: {operatingMargin} (Shows efficiency of core business operations)
      - Net Margin: {netMargin} (Overall profitability after all expenses)
      - Operating Cash Flow Margin: {operatingCashFlowMargin} (Ability to generate cash from sales)
      - Free Cash Flow Margin: {freeCashFlowMargin} (Cash available after capital expenditures)

      Evaluation Criteria:
      - Benchmarks: Compare against typical SaaS / Tech hardware margins (e.g., Gross > 70%, Op > 20% for software; lower for hardware).
      - Trend Analysis: Are margins expanding, stable, or shrinking over the last 3-5 years? Expanding margins are a strong positive sign.
      - Quality: Is profitability driven by core operations or one-time events? Is it backed by strong cash flow?

      Output a numeric score from 1 to 100 for the PROFITABILITY dimension. The score should be an integer.
      The score should be based on a holistic view of the provided metrics, not a simple average.
      Format the output as a single integer. For example: 85
    `,
    growth: `
      Analyze the company's growth profile, which is critical for technology companies. Focus on sustainability, efficiency, and market opportunity.

      Key Metrics (Year-over-Year):
      - Revenue Growth: {revenueGrowth}
      - Net Income Growth: {netIncomeGrowth}
      - Free Cash Flow Growth: {freeCashFlowGrowth}

      Evaluation Criteria:
      - Rate of Growth: Is the company growing faster than the industry average? Is it maintaining a high growth rate (e.g., >20%)?
      - Sustainability: Is growth accelerating or decelerating? Is it organic or driven by acquisitions?
      - Quality of Growth: Is growth profitable? (i.e., is net income/FCF growing in line with or faster than revenue?). "Rule of 40" (Revenue Growth % + FCF Margin %) is a good indicator for SaaS.
      - Market Opportunity: Is the company in a large and growing Total Addressable Market (TAM)?

      Output a numeric score from 1 to 100 for the GROWTH dimension. The score should be an integer.
      The score should be based on a holistic view of the provided metrics, not a simple average.
      Format the output as a single integer. For example: 92
    `,
    balanceSheet: `
      Analyze the company's balance sheet to assess its financial stability and resilience, especially important for tech companies that may be reinvesting heavily or facing market volatility.

      Key Metrics:
      - Current Ratio: {currentRatio} (Liquidity to cover short-term liabilities. >1.5 is generally healthy)
      - Debt-to-Equity Ratio: {debtToEquity} (Leverage. Lower is generally better, especially for non-mature tech)

      Evaluation Criteria:
      - Liquidity: Does the company have enough cash and liquid assets to cover its short-term obligations?
      - Solvency: Is the company over-leveraged? High debt can be risky, especially if profitability is inconsistent.
      - Cash Position: Does the company have a strong net cash position (cash > debt)? This provides flexibility for R&D, acquisitions, or weathering downturns.
      - Intangibles: Note the value of Goodwill and Intangible Assets, which can be significant in tech.

      Output a numeric score from 1 to 100 for the BALANCE SHEET dimension. The score should be an integer.
      The score should be based on a holistic view of the provided metrics, not a simple average.
      Format the output as a single integer. For example: 78
    `,
    capitalAllocation: `
      Analyze how effectively the company's management is allocating capital to generate returns, a key indicator of management quality and long-term value creation.

      Key Metrics:
      - Return on Equity (ROE): {returnOnEquity} (Efficiency in generating profit from shareholder equity. >15% is strong)
      - Return on Assets (ROA): {returnOnAssets} (Efficiency in using assets to generate profit)
      - Return on Invested Capital (ROIC): {returnOnInvestedCapital} (Measures return on all capital invested. Should be > WACC)
      - Asset Turnover: {assetTurnover} (Efficiency in using assets to generate revenue)

      Evaluation Criteria:
      - Profitability of Investments: Are returns (ROE, ROIC) high and consistently above the company's cost of capital?
      - Reinvestment Strategy: Is the company reinvesting cash flow into high-return projects (R&D, strategic acquisitions) or returning capital to shareholders (buybacks, dividends)?
      - Efficiency: Is the company generating sufficient revenue from its asset base?

      Output a numeric score from 1 to 100 for the CAPITAL ALLOCATION dimension. The score should be an integer.
      The score should be based on a holistic view of the provided metrics, not a simple average.
      Format the output as a single integer. For example: 88
    `,
    valuation: `
      Analyze the company's current valuation to determine if its stock price is fair, overvalued, or undervalued, relative to its fundamentals and growth prospects.
      NOTE: This analysis is based on financial statement data and does not include live market data. The analysis should be based on reasoning about the company's performance relative to its sector.

      Key Considerations (based on provided financial data):
      - Historical Growth vs. Implied Expectations: Does the company's historical growth and profitability justify a high valuation multiple typical for tech stocks?
      - Profitability & Margins: High, stable margins can justify a premium valuation.
      - Competitive Advantage: Does the analysis of other dimensions suggest a strong moat that would warrant a higher valuation?
      - General Sentiment: Based on the overall financial health, would you consider this company to be in a position that typically commands a high market valuation?

      Instructions:
      Based on the financial strength and growth profile from the other dimensions, provide a qualitative assessment of whether the company's performance supports a premium, fair, or discounted valuation relative to the tech sector.
      Then, provide a numeric score from 1 to 100 for the VALUATION dimension, where a lower score suggests potential overvaluation risk and a higher score suggests the valuation may be reasonable or attractive.

      Output a numeric score from 1 to 100 for the VALUATION dimension. The score should be an integer.
      The score should be based on a holistic view of the company's performance, not a simple average.
      Format the output as a single integer. For example: 65
    `,
    insights: `
      Based on the comprehensive analysis of all financial dimensions (Profitability, Growth, Balance Sheet, Capital Allocation, and Valuation), synthesize the findings into a clear, actionable investment thesis.

      Inputs:
      - Company: {symbol}
      - Overall Score: {overallScore}
      - Profitability Analysis & Score: {profitabilityAnalysis}
      - Growth Analysis & Score: {growthAnalysis}
      - Balance Sheet Analysis & Score: {balanceSheetAnalysis}
      - Capital Allocation Analysis & Score: {capitalAllocationAnalysis}
      - Valuation Analysis & Score: {valuationAnalysis}

      Instructions:
      1.  **Summary:** Provide a 2-3 sentence executive summary of the investment thesis.
      2.  **Strengths:** List 2-3 key strengths of the company based on the analysis.
      3.  **Weaknesses:** List 2-3 key weaknesses or areas of concern.
      4.  **Opportunities:** Identify 1-2 potential opportunities for the company.
      5.  **Risks:** Identify 1-2 key risks to the investment thesis.
      6.  **Recommendation:** Provide a final investment recommendation: BUY, HOLD, or SELL.

      Output a JSON object with the following structure:
      {
        "summary": "...",
        "strengths": ["...", "..."],
        "weaknesses": ["...", "..."],
        "opportunities": ["...", "..."],
        "risks": ["...", "..."],
        "recommendation": "BUY" | "HOLD" | "SELL"
      }
    `,
  },
};
