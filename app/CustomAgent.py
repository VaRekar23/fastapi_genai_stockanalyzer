import os
from datetime import datetime
from crewai import Agent
from app.SearchTool import search_tool
from app.CustomTool import (
    get_current_stock_price,
    get_company_info,
    get_income_statements,
    get_balance_sheet,
    get_cashflow_statements,
    get_fundamental_summary,
    analyze_earnings_quality,
    get_technical_indicators,
    get_market_sentiment,
    get_esg_risk_factors,
    get_comprehensive_analysis,
)
from dotenv import load_dotenv

Now = datetime.now()
Today = Now.strftime("%d-%b-%Y")
load_dotenv()

# OpenAI models - budget-friendly for reasoning
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def build_agents():
    """Create and return all agents. Uses OpenAI for reasoning tasks.

    Recommended models for budget-friendly reasoning:
    - gpt-4o-mini: Best balance of cost and reasoning (default)
    - gpt-4o: Better reasoning, slightly higher cost
    - gpt-3.5-turbo: Good reasoning, lowest cost
    """
    
    llm = None
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Check if API key is available
    if not api_key:
        error_msg = (
            "OPENAI_API_KEY environment variable not found. "
            "Please set your OpenAI API key in Render environment variables."
        )
        print(f"ERROR: {error_msg}")
        raise RuntimeError(error_msg)
    
    print(f"OpenAI API key found (length: {len(api_key)})")
    print(f"Using model: {OPENAI_MODEL}")
    
    # Use OpenAI (primary choice for reasoning)
    try:
        # Try the newer import first
        try:
            from langchain_openai import ChatOpenAI  # type: ignore
            print("Successfully imported langchain_openai.ChatOpenAI")
        except ImportError as ie:
            print(f"langchain_openai import failed: {ie}")
            try:
                from langchain.chat_models import ChatOpenAI  # type: ignore
                print("Successfully imported langchain.chat_models.ChatOpenAI")
            except ImportError as ie2:
                print(f"langchain.chat_models import also failed: {ie2}")
                raise ImportError("Could not import ChatOpenAI from either langchain_openai or langchain.chat_models")
        
        # Initialize the LLM with proper error handling
        try:
            # For OpenAI 0.28.x, use different initialization
            llm = ChatOpenAI(
                openai_api_key=api_key,
                temperature=0, 
                model_name=OPENAI_MODEL,
                max_retries=3,
                request_timeout=30
            )
            print(f"ChatOpenAI initialized successfully with {OPENAI_MODEL}")
            
            # Test the connection with a simple call
            try:
                test_response = llm.invoke("Hello")
                print("OpenAI connection test successful")
            except Exception as test_error:
                print(f"OpenAI connection test failed: {test_error}")
                # Continue anyway, test might fail but agents can still work
            
        except Exception as init_error:
            print(f"Failed to initialize ChatOpenAI: {init_error}")
            raise RuntimeError(f"Failed to initialize OpenAI client: {init_error}")
            
    except Exception as e:
        error_msg = f"Failed to set up OpenAI LLM: {str(e)}"
        print(f"ERROR: {error_msg}")
        raise RuntimeError(error_msg)
    
    print(f"LLM configured successfully: {type(llm).__name__}")
    print(f"LLM model: {getattr(llm, 'model_name', 'Unknown')}")
    print(f"LLM temperature: {getattr(llm, 'temperature', 'Not set')}")
    
    # Ensure LLM is properly configured to prevent CrewAI from overriding it
    if hasattr(llm, '_llm_type'):
        print(f"LLM type: {llm._llm_type}")

    news_info_explorer = Agent(
        role='News and Info Researcher',
        goal='Gather and provide the latest news and information about a company from the internet',
        llm=llm,
        verbose=True,
        backstory=(
            f"You are an expert researcher, who gathers detailed information about a company. "
            f"Always use exactly the user-provided stock symbol when referring to the company. "
            f"Never invent or use placeholder symbols like 'XYZ' or random examples. "
            f"If a tool returns no results for the provided symbol, you may try the NSE variant (symbol+'.NS'), "
            f"but continue to present the final result using the originally provided symbol. "
            f"Consider you are on: {Today}"
        ),
        tools=[search_tool],
        cache=True,
        max_iter=2,
    )

    data_explorer = Agent(
        role='Data Researcher',
        goal='Gather and provide financial data and company information about a stock',
        llm=llm,
        verbose=True,
        backstory=(
            f"You are an expert researcher who gathers detailed information about a company or stock. "
            f"Use exactly the stock symbol provided as input. Do not invent or switch to placeholder symbols like 'XYZ'. "
            f"If a tool returns empty results for the provided symbol, you may try a secondary attempt with the NSE variant (symbol+'.NS'). "
            f"In all outputs and reasoning, keep referring to the originally provided symbol. "
            f"Consider you are on: {Today}"
        ),
        tools=[
            get_company_info, 
            get_income_statements, 
            get_balance_sheet, 
            get_cashflow_statements,
            analyze_earnings_quality,
            get_technical_indicators,
            get_market_sentiment,
            get_esg_risk_factors,
            get_comprehensive_analysis
        ],
        cache=True,
        max_iter=2,
    )

    analyst = Agent(
        role='Data Analyst',
        goal='Consolidate financial data, stock information, and provide a summary',
        llm=llm,
        verbose=True,
        backstory=(
            f"You are an expert in analyzing financial data, stock/company-related current information, and making a comprehensive analysis. "
            f"Use Indian units for numbers (lakh, crore). Consider you are on: {Today}"
        ),
    )

    fin_expert = Agent(
        role='Financial Expert',
        goal='Considering financial analysis of a stock, make investment recommendations',
        llm=llm,
        verbose=True,
        tools=[get_current_stock_price],
        max_iter=2,
        backstory=(
            f"You are an expert financial advisor who provides investment recommendations based on the provided stock symbol. "
            f"Always use exactly the user-provided symbol; never invent placeholders like 'XYZ'. "
            f"If a tool returns no result with the provided symbol, you may try the NSE variant (symbol+'.NS'), "
            f"but present conclusions using the originally provided symbol. "
            f"Consider you are on: {Today}"
        ),
    )

    return data_explorer, news_info_explorer, analyst, fin_expert