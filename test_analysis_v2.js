const testAnalysisWithTransformation = async () => {
  try {
    console.log('📥 Fetching AAPL company data...');
    const companyResponse = await fetch('http://localhost:3000/api/companies/AAPL');
    const companyData = await companyResponse.json();
    
    console.log(`📊 Found ${companyData.financialData.length} financial data records`);
    
    // Group financial data by year and extract the nested financial statements
    const groupedByYear = {};
    companyData.financialData.forEach((fd) => {
      if (['Income Statement', 'Balance Sheet', 'Cash Flow Statement'].includes(fd.type) && fd.data) {
        const year = fd.year.toString();
        const period = fd.period || 'FY';
        const key = `${year}-${period}`;
        
        if (!groupedByYear[key]) {
          groupedByYear[key] = { year, period };
        }
        
        if (fd.type === 'Income Statement') {
          groupedByYear[key].incomeStatement = fd.data;
        } else if (fd.type === 'Balance Sheet') {
          groupedByYear[key].balanceSheet = fd.data;
        } else if (fd.type === 'Cash Flow Statement') {
          groupedByYear[key].cashFlow = fd.data;
        }
      }
    });

    // Transform the data to the expected format
    const transformDatabaseDataToFMPFormat = (incomeData, balanceData, cashFlowData) => {
      const incomeStatement = incomeData?.income_statements?.[0] || {};
      const balanceSheet = balanceData?.balance_sheets?.[0] || {};
      const cashFlow = cashFlowData?.cash_flows?.[0] || {};

      return {
        incomeStatement: {
          symbol: incomeStatement.symbol || 'AAPL',
          fiscalYear: incomeStatement.calendarYear?.toString() || '2024',
          reportedCurrency: incomeStatement.reportedCurrency || 'USD',
          revenue: incomeStatement.revenue || 0,
          grossProfit: incomeStatement.grossProfit || (incomeStatement.revenue - incomeStatement.costOfRevenue) || 0,
          operatingIncome: incomeStatement.operatingIncome || incomeStatement.ebit || 0,
          netIncome: incomeStatement.netIncome || incomeStatement.bottomLineNetIncome || 0,
          interestExpense: incomeStatement.interestExpense || 0,
          costOfRevenue: incomeStatement.costOfRevenue || 0,
          eps: incomeStatement.eps || 0,
        },
        balanceSheet: {
          totalAssets: balanceSheet.totalAssets || 0,
          totalCurrentAssets: balanceSheet.totalCurrentAssets || 0,
          totalCurrentLiabilities: balanceSheet.totalCurrentLiabilities || 0,
          totalDebt: balanceSheet.totalDebt || 0,
          totalEquity: balanceSheet.totalStockholdersEquity || balanceSheet.totalEquity || 0,
          cashAndCashEquivalents: balanceSheet.cashAndCashEquivalents || 0,
        },
        cashFlow: {
          operatingCashFlow: cashFlow.operatingCashFlow || cashFlow.netCashProvidedByOperatingActivities || 0,
          freeCashFlow: cashFlow.freeCashFlow || 0,
        },
      };
    };

    // Convert to FMPFinancialStatements format
    const financialStatements = Object.values(groupedByYear)
      .filter((group) => group.incomeStatement && group.balanceSheet && group.cashFlow && group.period === 'FY')
      .map((group) => transformDatabaseDataToFMPFormat(
        group.incomeStatement,
        group.balanceSheet,
        group.cashFlow
      ))
      .sort((a, b) => parseInt(a.incomeStatement.fiscalYear) - parseInt(b.incomeStatement.fiscalYear));

    console.log(`🧮 Prepared ${financialStatements.length} years of complete financial statements`);
    
    if (financialStatements.length === 0) {
      console.error('❌ No complete financial statements found');
      return;
    }

    // Show a sample of the data
    console.log('📋 Sample financial data for', financialStatements[0].incomeStatement.fiscalYear + ':');
    console.log('  Revenue:', financialStatements[0].incomeStatement.revenue);
    console.log('  Net Income:', financialStatements[0].incomeStatement.netIncome);
    console.log('  Total Assets:', financialStatements[0].balanceSheet.totalAssets);
    console.log('  Operating Cash Flow:', financialStatements[0].cashFlow.operatingCashFlow);

    console.log('🤖 Starting AI analysis...');
    const analysisResponse = await fetch('http://localhost:3000/api/analysis/template/tech', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        company: companyData.company, 
        financials: financialStatements 
      }),
    });

    if (!analysisResponse.ok) {
      const error = await analysisResponse.json();
      console.error('❌ Analysis failed:', error);
      return;
    }

    const analysis = await analysisResponse.json();
    console.log('✅ Analysis completed successfully!');
    console.log('📈 Overall Score:', analysis.score);
    console.log('🎯 Recommendation:', analysis.insights.recommendation);
    console.log('💡 Summary:', analysis.insights.summary);
    console.log('🔢 Scores:', analysis.metricScores);
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
};

testAnalysisWithTransformation();
