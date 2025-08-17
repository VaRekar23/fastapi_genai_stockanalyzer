from crewai import Task


def build_tasks(
    data_explorer,
    news_info_explorer,
    analyst,
    fin_expert,
    stock: str,
):
    """Create tasks for a given stock and assigned agents."""
    # Task to gather comprehensive financial data and analysis
    get_company_financials = Task(
        description=(
            f"Get comprehensive financial analysis for stock: {stock}. Use the comprehensive analysis tool to get: "
            f"1) Fundamental metrics (revenue, profitability, cash flow, debt ratios) "
            f"2) Earnings quality analysis (accruals quality, persistence, predictability) "
            f"3) Technical indicators (RSI, MACD, momentum, relative strength) "
            f"4) Market sentiment (analyst ratings, price targets, volume analysis) "
            f"5) ESG and risk factors (environmental, social, governance, volatility) "
            f"6) Overall 0-100 score with detailed breakdown. "
            f"Return the comprehensive analysis and highlight key insights for decision making."
        ),
        expected_output=(
            f"Comprehensive financial analysis for {stock} including: fundamentals score, earnings quality score, "
            f"technical momentum score, sentiment score, risk assessment, and overall 0-100 rating. "
            f"Provide key insights and red flags for each category."
        ),
        agent=data_explorer,
    )

    # Task to gather company news
    get_company_news = Task(
        description=f"Get latest news and business information about company: {stock}",
        expected_output="Latest news and business information about the company. Provide a summary also.",
        agent=news_info_explorer,
    )

    # Task to analyze financial data and news with enhanced insights
    analyse = Task(
        description=(
            "Make thorough analysis based on comprehensive financial data and latest news. Include: "
            "1) Profitability analysis (net margin, EBITDA margin, ROE trends) "
            "2) Earnings quality assessment (reliability, persistence, cash flow quality) "
            "3) Technical momentum evaluation (RSI, MACD, price trends, relative strength) "
            "4) Market sentiment analysis (analyst consensus, price targets, volume patterns) "
            "5) Risk factor assessment (ESG scores, volatility, leverage, liquidity) "
            "6) Industry and competitive positioning "
            "7) Overall investment thesis based on the 0-100 comprehensive score. "
            "Use Indian units (lakh, crore) and explain the scoring methodology."
        ),
        expected_output=(
            "Comprehensive analysis of stock outlining financial health, earnings quality, technical momentum, "
            "market sentiment, risk factors, and competitive position. Include the overall 0-100 score breakdown "
            "and explain what each component means for investment decision making. "
            "Mention currency information and use Indian context (lakh/crore)."
        ),
        agent=analyst,
        context=[get_company_financials, get_company_news],
        output_file='Analysis.md',
    )

    # Task to provide enhanced financial advice
    advise = Task(
        description=(
            "Make a comprehensive investment recommendation based on: "
            "1) The detailed analysis provided "
            "2) The comprehensive 0-100 score and its breakdown "
            "3) Current stock price and technical indicators "
            "4) Risk-reward assessment "
            "5) Time horizon considerations "
            "6) Alternative investment options. "
            "Provide specific Buy/Hold/Sell recommendation with clear reasoning and risk warnings."
        ),
        expected_output=(
            "Detailed investment recommendation (Buy/Hold/Sell) with: "
            "1) Clear reasoning based on comprehensive analysis "
            "2) Risk assessment and warnings "
            "3) Price targets and time horizons "
            "4) Portfolio positioning advice "
            "5) Key factors that could change the recommendation. "
            "Response in Markdown format with structured sections."
        ),
        agent=fin_expert,
        context=[analyse],
        output_file='Recommendation.md',
    )

    return get_company_financials, get_company_news, analyse, advise