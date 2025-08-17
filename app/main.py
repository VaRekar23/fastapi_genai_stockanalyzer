from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from crewai import Crew, Process, Task
from datetime import datetime
import logging
import os
import sys
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Import after logging setup
from app.CustomTask import build_tasks
from app.CustomAgent import build_agents
from app.CustomTool import (
    get_current_stock_price,
    get_company_info,
    get_technical_indicators,
    get_market_sentiment
)
import json
import re

# Create FastAPI app with metadata
app = FastAPI(
    title="FastAPI GenAI Stock Analyzer",
    description="AI-powered stock analysis platform with comprehensive analysis, intraday trading recommendations, and market insights",
    version="1.0.0",
    contact={
        "name": "Stock Analyzer Team",
        "url": "https://github.com/yourusername/fastapi_genai_stockanalyzer",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Add CORS middleware for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.now().isoformat()
        }
    )

# Callback function to print a timestamp
def timestamp(Input):
    logger.info(f"Step completed at: {datetime.now()}")

# Initialize agents globally with detailed error logging
try:
    logger.info("Attempting to initialize agents...")
    
    # Check required environment variables
    required_env_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        logger.error("Please set these variables in your Render dashboard under Environment Variables")
        agents = None
    else:
        logger.info(f"Found required environment variables")
        logger.info(f"OpenAI Model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")
        
        agents = build_agents()
        logger.info("✅ Agents initialized successfully")
        
except Exception as e:
    logger.error(f"❌ Failed to initialize agents: {str(e)}")
    logger.error(f"Error type: {type(e).__name__}")
    import traceback
    logger.error(f"Full traceback: {traceback.format_exc()}")
    agents = None

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "FastAPI GenAI Stock Analyzer is running! 🚀",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "stock_analysis": "/stock/{symbol}",
            "intraday_analysis": "/intraday/{symbol}",
            "intraday_agents": "/intraday-agents/{symbol}",
            "health_check": "/health",
            "api_docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Check if agents are available
        agent_status = "healthy" if agents else "unhealthy"
        
        # Check environment variables
        env_status = {
            "openai_key": bool(os.getenv("OPENAI_API_KEY")),
            "openai_model": os.getenv("OPENAI_MODEL", "not_set"),
            "app_env": os.getenv("APP_ENV", "development")
        }
        
        return {
            "status": "healthy" if agent_status == "healthy" else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "components": {
                "agents": agent_status,
                "environment": env_status
            },
            "uptime": "running"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/debug/openai")
def debug_openai():
    """Debug endpoint to verify OpenAI configuration"""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "not_set")
        
        return {
            "openai_configured": bool(api_key),
            "api_key_length": len(api_key) if api_key else 0,
            "model": model,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Debug error: {e}")

@app.get("/stock/{stock}")
def get_post(stock: str):
    """Comprehensive stock analysis using AI agents"""
    if not agents:
        raise HTTPException(status_code=503, detail="Agents not initialized. Please check server logs.")
    
    try:
        logger.info(f"Starting comprehensive stock analysis for: {stock}")
        
        # Validate stock symbol
        if not stock or len(stock.strip()) == 0:
            raise HTTPException(status_code=400, detail="Stock symbol cannot be empty")
        
        stock = stock.strip().upper()
        
        # Build agents and tasks per request to inject stock symbol into task descriptions
        data_explorer, news_info_explorer, analyst, fin_expert = agents
        get_company_financials, get_company_news, analyse, advise = build_tasks(
            data_explorer, news_info_explorer, analyst, fin_expert, stock
        )

        crew = Crew(
            agents=[data_explorer, news_info_explorer, analyst, fin_expert],
            tasks=[get_company_financials, get_company_news, analyse, advise],
            verbose=True,
            process=Process.sequential,
            step_callback=timestamp,
        )

        logger.info(f"Executing crew analysis for stock: {stock}")
        result = crew.kickoff()
        
        logger.info(f"Analysis completed for {stock}")
        return {
            "stock_symbol": stock,
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_type": "Comprehensive Stock Analysis",
            "result": str(result),
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Error in stock analysis for {stock}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to analyze stock {stock}: {str(e)}"
        )

@app.get("/intraday/{stock}")
def get_intraday_analysis(stock: str):
    """Intraday trading analysis endpoint that provides entry, exit, and stop loss values."""
    try:
        logger.info(f"Starting algorithmic intraday analysis for stock: {stock}")
        
        # Validate stock symbol
        if not stock or len(stock.strip()) == 0:
            raise HTTPException(status_code=400, detail="Stock symbol cannot be empty")
        
        stock = stock.strip().upper()
        
        # Get current stock price and basic info
        current_price_info = get_current_stock_price(stock)
        company_info = get_company_info(stock)
        technical_data = get_technical_indicators(stock)
        sentiment_data = get_market_sentiment(stock)
        
        # Parse the data (handle JSON strings)
        try:
            current_price_data = json.loads(current_price_info) if isinstance(current_price_info, str) else current_price_info
            technical_analysis = json.loads(technical_data) if isinstance(technical_data, str) else technical_data
            sentiment_analysis = json.loads(sentiment_data) if isinstance(sentiment_data, str) else sentiment_data
        except:
            current_price_data = current_price_info
            technical_analysis = technical_data
            sentiment_analysis = sentiment_data
        
        # Extract current price
        current_price = None
        if isinstance(current_price_data, dict):
            current_price = current_price_data.get('current_price')
        elif isinstance(current_price_data, str):
            # Try to extract price from string
            price_match = re.search(r'₹(\d+(?:\.\d+)?)', current_price_data)
            if price_match:
                current_price = float(price_match.group(1))
        
        if not current_price:
            raise HTTPException(status_code=400, detail="Could not determine current stock price")
        
        # Calculate intraday levels based on technical analysis
        entry_price = current_price
        exit_price = current_price
        stop_loss = current_price
        
        # Technical analysis based calculations
        if isinstance(technical_analysis, dict) and 'error' not in technical_analysis:
            rsi = technical_analysis.get('rsi')
            macd_signal = technical_analysis.get('macd_signal')
            price_momentum_3m = technical_analysis.get('price_momentum_3m', 0)
            price_momentum_12m = technical_analysis.get('price_momentum_12m', 0)
            
            # RSI-based entry/exit logic
            if rsi is not None:
                if rsi < 30:  # Oversold - potential buy
                    entry_price = current_price * 0.995  # Slightly below current
                    exit_price = current_price * 1.02   # 2% target
                    stop_loss = current_price * 0.985   # 1.5% stop loss
                elif rsi > 70:  # Overbought - potential sell
                    entry_price = current_price * 1.005  # Slightly above current
                    exit_price = current_price * 0.98   # 2% target
                    stop_loss = current_price * 1.015   # 1.5% stop loss
                else:  # Neutral - range trading
                    entry_price = current_price * 0.998  # Very close to current
                    exit_price = current_price * 1.015  # 1.5% target
                    stop_loss = current_price * 0.99    # 1% stop loss
            
            # Momentum-based adjustments
            if price_momentum_3m > 0.05:  # Strong upward momentum
                entry_price = min(entry_price, current_price * 0.997)
                exit_price = max(exit_price, current_price * 1.025)
            elif price_momentum_3m < -0.05:  # Strong downward momentum
                entry_price = max(entry_price, current_price * 1.003)
                exit_price = min(exit_price, current_price * 0.975)
        
        # Sentiment-based adjustments
        if isinstance(sentiment_analysis, dict) and 'error' not in sentiment_analysis:
            sentiment_score = sentiment_analysis.get('sentiment_score', 0)
            if sentiment_score > 0.6:  # Positive sentiment
                exit_price = max(exit_price, current_price * 1.02)
            elif sentiment_score < 0.4:  # Negative sentiment
                stop_loss = min(stop_loss, current_price * 0.99)
        
        # Round prices to 2 decimal places
        entry_price = round(entry_price, 2)
        exit_price = round(exit_price, 2)
        stop_loss = round(stop_loss, 2)
        
        # Calculate risk-reward ratio
        risk = abs(entry_price - stop_loss)
        reward = abs(exit_price - entry_price)
        risk_reward_ratio = round(reward / risk, 2) if risk > 0 else 0
        
        # Generate trading recommendation
        if risk_reward_ratio >= 2:
            recommendation = "STRONG BUY - Excellent risk-reward ratio"
        elif risk_reward_ratio >= 1.5:
            recommendation = "BUY - Good risk-reward ratio"
        elif risk_reward_ratio >= 1:
            recommendation = "HOLD - Moderate risk-reward ratio"
        else:
            recommendation = "AVOID - Poor risk-reward ratio"
        
        # Create comprehensive intraday analysis
        intraday_analysis = {
            "stock_symbol": stock,
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_type": "Algorithmic Intraday Analysis",
            "current_price": round(current_price, 2),
            "intraday_levels": {
                "entry_price": entry_price,
                "exit_price": exit_price,
                "stop_loss": stop_loss
            },
            "risk_analysis": {
                "risk_amount": round(risk, 2),
                "reward_amount": round(reward, 2),
                "risk_reward_ratio": risk_reward_ratio,
                "recommendation": recommendation
            },
            "technical_indicators": technical_analysis if isinstance(technical_analysis, dict) else "Not available",
            "market_sentiment": sentiment_analysis if isinstance(sentiment_analysis, dict) else "Not available",
            "trading_strategy": {
                "entry_strategy": f"Enter at ₹{entry_price} (slightly {'below' if entry_price < current_price else 'above'} current price)",
                "exit_strategy": f"Target exit at ₹{exit_price} for {'profit' if exit_price > entry_price else 'loss'}",
                "stop_loss_strategy": f"Set stop loss at ₹{stop_loss} to limit downside risk",
                "position_size": "Consider position sizing based on your risk tolerance (1-2% of portfolio per trade)"
            },
            "disclaimer": "This analysis is for educational purposes only. Always do your own research and consider consulting a financial advisor before making trading decisions."
        }
        
        logger.info(f"Intraday analysis completed for {stock}")
        return intraday_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in intraday analysis for {stock}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to analyze {stock} for intraday trading: {str(e)}"
        )

@app.get("/intraday-agents/{stock}")
def get_intraday_agents_analysis(stock: str):
    """Intraday trading analysis using CrewAI agents for expert AI reasoning with specific buy/sell/hold recommendations."""
    if not agents:
        raise HTTPException(status_code=503, detail="Agents not initialized. Please check server logs.")
    
    try:
        logger.info(f"Starting agent-based intraday analysis for stock: {stock}")
        
        # Validate stock symbol
        if not stock or len(stock.strip()) == 0:
            raise HTTPException(status_code=400, detail="Stock symbol cannot be empty")
        
        stock = stock.strip().upper()
        
        # Build agents for this specific request
        data_explorer, news_info_explorer, analyst, fin_expert = agents
        
        # Create specialized intraday tasks focused on actionable trading decisions
        from crewai import Task
        
        # Task 1: Gather current market data and technical indicators
        gather_market_data = Task(
            description=(
                f"Analyze the current market data for {stock} and provide specific technical analysis: "
                f"1) Current stock price (exact value) "
                f"2) RSI value and interpretation (oversold/overbought/neutral) "
                f"3) MACD signal and trend direction "
                f"4) Support and resistance levels (exact price values) "
                f"5) Volume analysis and price momentum "
                f"6) Key moving averages (20, 50, 200 day) "
                f"Focus on data that directly impacts intraday trading decisions. "
                f"Provide exact numerical values for all technical indicators."
            ),
            expected_output=(
                f"Detailed technical analysis for {stock} with exact numerical values for RSI, MACD, "
                f"support/resistance levels, and moving averages. All values should be specific numbers."
            ),
            agent=data_explorer,
        )
        
        # Task 2: Research market sentiment and news
        research_market_sentiment = Task(
            description=(
                f"Research current market sentiment and news for {stock} that could affect intraday trading: "
                f"1) Latest company news and announcements (last 24 hours) "
                f"2) Market sentiment indicators (positive/negative/neutral) "
                f"3) Sector-specific developments affecting {stock} "
                f"4) Any breaking news that could cause intraday price movement "
                f"5) Analyst recommendations and price targets "
                f"6) Institutional buying/selling activity "
                f"Focus on information that could impact today's trading session and price movement."
            ),
            expected_output=(
                f"Current market sentiment analysis for {stock} with relevant news, analyst views, "
                f"and factors that could cause intraday price volatility or trend changes."
            ),
            agent=news_info_explorer,
        )
        
        # Task 3: Analyze intraday trading opportunities and provide specific recommendations
        analyze_intraday_opportunities = Task(
            description=(
                f"Based on the market data and sentiment for {stock}, provide SPECIFIC intraday trading recommendations: "
                f"1) TRADING DECISION: Should we BUY, SELL, or HOLD {stock} for intraday? "
                f"2) ENTRY PRICE: At what exact price should we enter the trade? "
                f"3) EXIT PRICE: What should be our profit target (exact price)? "
                f"4) STOP LOSS: What should be our stop loss level (exact price)? "
                f"5) RISK-REWARD RATIO: Calculate the exact risk-reward ratio "
                f"6) TRADING TIMEFRAME: How long should we hold this intraday position? "
                f"7) POSITION SIZING: What percentage of capital should be allocated? "
                f"8) KEY RISKS: What are the main risks for this intraday trade? "
                f"Use Indian units (lakh, crore) and provide EXACT price levels. "
                f"Format your response with clear sections: TRADING DECISION, PRICE LEVELS, RISK ANALYSIS, STRATEGY."
            ),
            expected_output=(
                f"Specific intraday trading recommendation for {stock} with exact entry, exit, and stop loss prices. "
                f"Clear BUY/SELL/HOLD decision with actionable price levels and risk management strategy."
            ),
            agent=analyst,
        )
        
        # Task 4: Generate final trading strategy and execution plan
        generate_trading_recommendations = Task(
            description=(
                f"Based on the intraday analysis for {stock}, provide a FINAL EXECUTION PLAN: "
                f"1) CONFIRM TRADING DECISION: BUY/SELL/HOLD with reasoning "
                f"2) EXACT PRICE LEVELS: Entry, Exit, Stop Loss (specific numbers) "
                f"3) EXECUTION STRATEGY: How to enter the trade (market order, limit order, etc.) "
                f"4) RISK MANAGEMENT: Stop loss placement and position sizing "
                f"5) PROFIT BOOKING: When and how to book profits "
                f"6) MARKET TIMING: Best time to enter/exit during the trading session "
                f"7) ALTERNATIVE SCENARIOS: What if the trade goes against us? "
                f"8) SUCCESS PROBABILITY: Percentage chance of this trade being profitable "
                f"Provide a clear, actionable trading plan that an intraday trader can execute immediately."
            ),
            expected_output=(
                f"Final execution plan for intraday trading {stock} with exact price levels, "
                f"execution strategy, risk management, and alternative scenarios. "
                f"This should be immediately actionable for intraday traders."
            ),
            agent=fin_expert,
        )
        
        # Create crew for intraday analysis
        intraday_crew = Crew(
            agents=[data_explorer, news_info_explorer, analyst, fin_expert],
            tasks=[gather_market_data, research_market_sentiment, analyze_intraday_opportunities, generate_trading_recommendations],
            verbose=True,
            process=Process.sequential,
            step_callback=timestamp,
        )
        
        # Execute the intraday analysis
        logger.info(f"Executing agent-based intraday analysis for {stock}")
        result = intraday_crew.kickoff()
        
        # Format the result for better readability
        try:
            formatted_result = {
                "stock_symbol": stock,
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_type": "Agent-Based Intraday Trading Recommendation",
                "crew_result": str(result),
                "endpoint": f"/intraday-agents/{stock}",
                "note": "This analysis provides specific BUY/SELL/HOLD recommendations with exact entry, exit, and stop loss prices for intraday trading.",
                "expected_output_format": {
                    "trading_decision": "BUY/SELL/HOLD",
                    "price_levels": {
                        "entry_price": "₹X.XX",
                        "exit_price": "₹X.XX", 
                        "stop_loss": "₹X.XX"
                    },
                    "risk_analysis": "Risk-reward ratio and position sizing",
                    "execution_strategy": "How to execute the trade"
                }
            }
            
            logger.info(f"Agent-based intraday analysis completed for {stock}")
            return formatted_result
            
        except Exception as format_error:
            logger.error(f"Error formatting result: {format_error}")
            return {"Result": str(result)}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in agent-based intraday analysis for {stock}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to perform agent-based intraday analysis for {stock}: {str(e)}"
        )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("🚀 FastAPI GenAI Stock Analyzer starting up...")
    logger.info(f"Environment: {os.getenv('APP_ENV', 'development')}")
    logger.info(f"Log Level: {os.getenv('LOG_LEVEL', 'INFO')}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 FastAPI GenAI Stock Analyzer shutting down...")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=port,
        reload=os.getenv("APP_ENV", "development") == "development",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )