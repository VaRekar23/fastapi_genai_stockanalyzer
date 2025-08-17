from langchain.tools import tool
import json
import numpy as np
import pandas as pd
import yfinance as yf
import time
from datetime import datetime, timedelta


def safe_float(value):
    """Safely convert value to float, return None if conversion fails."""
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index."""
    try:
        if len(prices) < period + 1:
            return None
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = np.mean(gains[:period])
        avg_losses = np.mean(losses[:period])
        
        for i in range(period, len(prices)):
            avg_gains = (avg_gains * (period - 1) + gains[i]) / period
            avg_losses = (avg_losses * (period - 1) + losses[i]) / period
        
        if avg_losses == 0:
            return 100
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        return rsi
    except Exception:
        return None


def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD and signal line."""
    try:
        if len(prices) < slow:
            return None, None
        
        ema_fast = pd.Series(prices).ewm(span=fast).mean().iloc[-1]
        ema_slow = pd.Series(prices).ewm(span=slow).mean().iloc[-1]
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line (EMA of MACD)
        macd_values = []
        for i in range(len(prices) - slow + 1):
            ema_f = pd.Series(prices[i:i+slow]).ewm(span=fast).mean().iloc[-1]
            ema_s = pd.Series(prices[i:i+slow]).ewm(span=slow).mean().iloc[-1]
            macd_values.append(ema_f - ema_s)
        
        if len(macd_values) >= signal:
            signal_line = pd.Series(macd_values).ewm(span=signal).mean().iloc[-1]
        else:
            signal_line = None
            
        return macd_line, signal_line
    except Exception:
        return None, None


@tool("Get current stock price")
def get_current_stock_price(symbol: str) -> str:
    """Use this function to get the current stock price for a given symbol.

    Args:
        symbol (str): The stock symbol.

    Returns:
        str: The current stock price or error message.
    """
    try:
        time.sleep(0.2)
        # Try exact symbol first
        stock = yf.Ticker(symbol)
        current_price = stock.info.get("regularMarketPrice", stock.info.get("currentPrice"))
        if current_price is None and not symbol.endswith(".NS"):
            # Fallback: try NSE suffix
            alt = yf.Ticker(symbol + ".NS")
            current_price = alt.info.get("regularMarketPrice", alt.info.get("currentPrice"))
        if current_price is None:
            return f"Could not fetch current price for {symbol}"
        try:
            numeric_price = float(current_price)
            return f"{numeric_price:.2f}"
        except Exception:
            return str(current_price)
    except Exception as e:
        return f"Error fetching current price for {symbol}: {e}"


@tool
def get_company_info(symbol: str):
    """Use this function to get company information and current financial snapshot for a given stock symbol.

    Args:
        symbol (str): The stock symbol.

    Returns:
        JSON containing company profile and current financial snapshot.
    """
    try:
        # Try exact symbol, then NSE fallback
        ticker = yf.Ticker(symbol)
        company_info_full = ticker.info
        if (not company_info_full) and (not symbol.endswith(".NS")):
            company_info_full = yf.Ticker(symbol + ".NS").info
        if company_info_full is None:
            return f"Could not fetch company info for {symbol}"

        company_info_cleaned = {
            "Name": company_info_full.get("shortName"),
            "Symbol": company_info_full.get("symbol"),
            "Current Stock Price": f"{company_info_full.get('regularMarketPrice', company_info_full.get('currentPrice'))} {company_info_full.get('currency', 'USD')}",
            "Market Cap": f"{company_info_full.get('marketCap', company_info_full.get('enterpriseValue'))} {company_info_full.get('currency', 'USD')}",
            "Sector": company_info_full.get("sector"),
            "Industry": company_info_full.get("industry"),
            "City": company_info_full.get("city"),
            "Country": company_info_full.get("country"),
            "EPS": company_info_full.get("trailingEps"),
            "P/E Ratio": company_info_full.get("trailingPE"),
            "52 Week Low": company_info_full.get("fiftyTwoWeekLow"),
            "52 Week High": company_info_full.get("fiftyTwoWeekHigh"),
            "50 Day Average": company_info_full.get("fiftyDayAverage"),
            "200 Day Average": company_info_full.get("twoHundredDayAverage"),
            "Employees": company_info_full.get("fullTimeEmployees"),
            "Total Cash": company_info_full.get("totalCash"),
            "Free Cash flow": company_info_full.get("freeCashflow"),
            "Operating Cash flow": company_info_full.get("operatingCashflow"),
            "EBITDA": company_info_full.get("ebitda"),
            "Revenue Growth": company_info_full.get("revenueGrowth"),
            "Gross Margins": company_info_full.get("grossMargins"),
            "Ebitda Margins": company_info_full.get("ebitdaMargins"),
        }
        return json.dumps(company_info_cleaned, default=str)
    except Exception as e:
        return f"Error fetching company profile for {symbol}: {e}"


@tool
def get_income_statements(symbol: str):
    """Use this function to get income statements for a given stock symbol.

    Args:
        symbol (str): The stock symbol.

    Returns:
        JSON containing income statements or an empty dictionary.
    """
    try:
        # Try exact symbol, then NSE fallback
        stock = yf.Ticker(symbol)
        financials = getattr(stock, "financials", None)
        if (financials is None or getattr(financials, "empty", False)) and (not symbol.endswith(".NS")):
            stock = yf.Ticker(symbol + ".NS")
            financials = getattr(stock, "financials", None)
        if financials is None or getattr(financials, "empty", False):
            return json.dumps({})
        return financials.to_json(orient="index")
    except Exception as e:
        return f"Error fetching income statements for {symbol}: {e}"


@tool
def get_balance_sheet(symbol: str):
    """Get the latest balance sheet for a given stock symbol as JSON."""
    try:
        stock = yf.Ticker(symbol)
        balance = getattr(stock, "balance_sheet", None)
        if (balance is None or getattr(balance, "empty", False)) and (not symbol.endswith(".NS")):
            stock = yf.Ticker(symbol + ".NS")
            balance = getattr(stock, "balance_sheet", None)
        if balance is None or getattr(balance, "empty", False):
            return json.dumps({})
        return balance.to_json(orient="index")
    except Exception as e:
        return f"Error fetching balance sheet for {symbol}: {e}"


@tool
def get_cashflow_statements(symbol: str):
    """Get the latest cashflow statements for a given stock symbol as JSON."""
    try:
        stock = yf.Ticker(symbol)
        cashflow = getattr(stock, "cashflow", None)
        if (cashflow is None or getattr(cashflow, "empty", False)) and (not symbol.endswith(".NS")):
            stock = yf.Ticker(symbol + ".NS")
            cashflow = getattr(stock, "cashflow", None)
        if cashflow is None or getattr(cashflow, "empty", False):
            return json.dumps({})
        return cashflow.to_json(orient="index")
    except Exception as e:
        return f"Error fetching cashflow statements for {symbol}: {e}"


@tool("Analyze earnings quality and persistence")
def analyze_earnings_quality(symbol: str) -> str:
    """Analyze earnings quality, persistence, and cash flow reliability.
    
    Returns JSON with accruals quality, earnings persistence, and cash flow quality metrics.
    """
    try:
        # Get financial data
        stock = yf.Ticker(symbol)
        if not stock.info:
            stock = yf.Ticker(symbol + ".NS")
        
        financials = getattr(stock, "financials", None)
        cashflow = getattr(stock, "cashflow", None)
        
        if financials is None or getattr(financials, "empty", False):
            return json.dumps({"error": "No financial data available"})
        
        # Calculate earnings quality metrics
        net_income_series = []
        revenue_series = []
        ocf_series = []
        
        try:
            if "Net Income" in financials.index:
                net_income_series = [safe_float(x) for x in financials.loc["Net Income"] if safe_float(x) is not None]
            if "Total Revenue" in financials.index:
                revenue_series = [safe_float(x) for x in financials.loc["Total Revenue"] if safe_float(x) is not None]
            if cashflow is not None and not getattr(cashflow, "empty", False):
                if "Total Cash From Operating Activities" in cashflow.index:
                    ocf_series = [safe_float(x) for x in cashflow.loc["Total Cash From Operating Activities"] if safe_float(x) is not None]
        except Exception:
            pass
        
        # Earnings Quality Metrics
        accruals_quality = None
        earnings_persistence = None
        cash_flow_quality = None
        earnings_predictability = None
        
        if len(net_income_series) >= 3 and len(ocf_series) >= 3:
            # Accruals Quality = OCF / Net Income (higher is better)
            try:
                avg_ocf = np.mean(ocf_series[:3])
                avg_ni = np.mean(net_income_series[:3])
                if avg_ni != 0:
                    accruals_quality = avg_ocf / avg_ni
            except Exception:
                pass
        
        if len(net_income_series) >= 4:
            # Earnings Persistence (correlation of consecutive earnings)
            try:
                earnings_persistence = np.corrcoef(net_income_series[:-1], net_income_series[1:])[0, 1]
            except Exception:
                pass
            
            # Earnings Predictability (variance of earnings)
            try:
                earnings_predictability = 1 / (1 + np.std(net_income_series) / abs(np.mean(net_income_series))) if np.mean(net_income_series) != 0 else 0
            except Exception:
                pass
        
        if len(ocf_series) >= 1 and len(net_income_series) >= 1:
            # Cash Flow Quality
            try:
                ocf_latest = ocf_series[0]
                ni_latest = net_income_series[0]
                if ni_latest != 0:
                    cash_flow_quality = ocf_latest / ni_latest
            except Exception:
                pass
        
        result = {
            "symbol": symbol,
            "accruals_quality": accruals_quality,
            "earnings_persistence": earnings_persistence,
            "earnings_predictability": earnings_predictability,
            "cash_flow_quality": cash_flow_quality,
            "net_income_series": net_income_series[:5],  # Last 5 periods
            "ocf_series": ocf_series[:5],
            "revenue_series": revenue_series[:5]
        }
        
        return json.dumps(result, default=str)
    except Exception as e:
        return f"Error analyzing earnings quality for {symbol}: {e}"


@tool("Get technical momentum indicators")
def get_technical_indicators(symbol: str) -> str:
    """Calculate RSI, MACD, price momentum, and relative strength.
    
    Returns JSON with technical analysis scores and indicators.
    """
    try:
        stock = yf.Ticker(symbol)
        if not stock.info:
            stock = yf.Ticker(symbol + ".NS")
        
        # Get historical data
        hist = stock.history(period="1y")
        if hist.empty:
            return json.dumps({"error": "No historical data available"})
        
        prices = hist['Close'].values
        
        # Calculate technical indicators
        rsi = calculate_rsi(prices)
        macd_line, macd_signal = calculate_macd(prices)
        
        # Price momentum
        if len(prices) >= 63:  # 3 months (63 trading days)
            price_3m = (prices[0] - prices[62]) / prices[62] if prices[62] != 0 else 0
        else:
            price_3m = None
            
        if len(prices) >= 252:  # 12 months (252 trading days)
            price_12m = (prices[0] - prices[251]) / prices[251] if prices[251] != 0 else 0
        else:
            price_12m = None
        
        # Relative strength vs market (simplified)
        # In a real implementation, you'd compare to a market index
        relative_strength = None
        if price_12m is not None:
            # Assume market return of 10% annually for comparison
            market_return = 0.10
            relative_strength = price_12m - market_return
        
        # Technical scoring
        technical_score = 0
        reasons = []
        
        # RSI scoring
        if rsi is not None:
            if 30 <= rsi <= 70:  # Neutral zone
                technical_score += 10
                reasons.append("RSI in neutral zone (30-70)")
            elif rsi < 30:  # Oversold
                technical_score += 15
                reasons.append("RSI indicates oversold conditions")
            elif rsi > 70:  # Overbought
                technical_score += 5
                reasons.append("RSI indicates overbought conditions")
        
        # Momentum scoring
        if price_3m is not None and price_3m > 0:
            technical_score += 10
            reasons.append("Positive 3-month momentum")
        if price_12m is not None and price_12m > 0:
            technical_score += 10
            reasons.append("Positive 12-month momentum")
        
        # MACD scoring
        if macd_line is not None and macd_signal is not None:
            if macd_line > macd_signal:
                technical_score += 5
                reasons.append("MACD above signal line (bullish)")
        
        result = {
            "symbol": symbol,
            "rsi": rsi,
            "macd_line": macd_line,
            "macd_signal": macd_signal,
            "price_3m_momentum": price_3m,
            "price_12m_momentum": price_12m,
            "relative_strength": relative_strength,
            "technical_score": technical_score,
            "technical_reasons": reasons,
            "current_price": prices[0] if len(prices) > 0 else None,
            "price_change_1d": (prices[0] - prices[1]) / prices[1] if len(prices) > 1 and prices[1] != 0 else None
        }
        
        return json.dumps(result, default=str)
    except Exception as e:
        return f"Error calculating technical indicators for {symbol}: {e}"


@tool("Analyze market sentiment and insider activity")
def get_market_sentiment(symbol: str) -> str:
    """Get analyst ratings, insider trading, and market sentiment.
    
    Returns JSON with sentiment analysis and key metrics.
    """
    try:
        stock = yf.Ticker(symbol)
        if not stock.info:
            stock = yf.Ticker(symbol + ".NS")
        
        info = stock.info
        
        # Analyst recommendations
        analyst_recommendation = info.get("recommendationMean")
        analyst_rating = info.get("recommendationKey")
        number_of_analysts = info.get("numberOfAnalystOpinions")
        
        # Price targets
        target_high_price = info.get("targetHighPrice")
        target_low_price = info.get("targetLowPrice")
        target_median_price = info.get("targetMedianPrice")
        current_price = info.get("regularMarketPrice") or info.get("currentPrice")
        
        # Calculate sentiment score
        sentiment_score = 0
        reasons = []
        
        # Analyst rating scoring
        if analyst_recommendation is not None:
            if analyst_recommendation <= 2.0:  # Strong buy
                sentiment_score += 15
                reasons.append("Strong buy recommendation from analysts")
            elif analyst_recommendation <= 2.5:  # Buy
                sentiment_score += 10
                reasons.append("Buy recommendation from analysts")
            elif analyst_recommendation <= 3.0:  # Hold
                sentiment_score += 5
                reasons.append("Hold recommendation from analysts")
            elif analyst_recommendation > 3.5:  # Sell
                sentiment_score -= 5
                reasons.append("Sell recommendation from analysts")
        
        # Price target scoring
        if target_median_price is not None and current_price is not None:
            upside_potential = (target_median_price - current_price) / current_price
            if upside_potential > 0.20:  # 20%+ upside
                sentiment_score += 10
                reasons.append("High upside potential (>20%)")
            elif upside_potential > 0.10:  # 10-20% upside
                sentiment_score += 5
                reasons.append("Moderate upside potential (10-20%)")
            elif upside_potential < -0.10:  # 10%+ downside
                sentiment_score -= 5
                reasons.append("Downside risk (>10%)")
        
        # Volume and market activity
        avg_volume = info.get("averageVolume")
        volume = info.get("volume")
        if avg_volume and volume:
            volume_ratio = volume / avg_volume
            if volume_ratio > 1.5:
                sentiment_score += 5
                reasons.append("Above-average trading volume")
        
        result = {
            "symbol": symbol,
            "analyst_recommendation": analyst_recommendation,
            "analyst_rating": analyst_rating,
            "number_of_analysts": number_of_analysts,
            "target_high_price": target_high_price,
            "target_low_price": target_low_price,
            "target_median_price": target_median_price,
            "current_price": current_price,
            "upside_potential": (target_median_price - current_price) / current_price if target_median_price and current_price else None,
            "sentiment_score": sentiment_score,
            "sentiment_reasons": reasons,
            "volume_ratio": volume / avg_volume if volume and avg_volume else None
        }
        
        return json.dumps(result, default=str)
    except Exception as e:
        return f"Error analyzing market sentiment for {symbol}: {e}"


@tool("Get ESG scores and risk factors")
def get_esg_risk_factors(symbol: str) -> str:
    """Analyze environmental, social, governance, and risk factors.
    
    Returns JSON with ESG analysis and risk assessment.
    """
    try:
        stock = yf.Ticker(symbol)
        if not stock.info:
            stock = yf.Ticker(symbol + ".NS")
        
        info = stock.info
        
        # Basic risk metrics
        beta = info.get("beta")
        debt_to_equity = info.get("debtToEquity")
        current_ratio = info.get("currentRatio")
        quick_ratio = info.get("quickRatio")
        
        # ESG scoring (simplified - in real implementation, you'd use ESG data providers)
        esg_score = 0
        esg_reasons = []
        risk_score = 0
        risk_reasons = []
        
        # Environmental factors (simplified)
        sector = info.get("sector", "").lower()
        if "energy" in sector or "oil" in sector or "gas" in sector:
            esg_score -= 5
            esg_reasons.append("Energy sector - environmental concerns")
        elif "technology" in sector or "software" in sector:
            esg_score += 5
            esg_reasons.append("Technology sector - lower environmental impact")
        
        # Social factors
        employees = info.get("fullTimeEmployees")
        if employees and employees > 10000:
            esg_score += 3
            esg_reasons.append("Large employer - positive social impact")
        
        # Governance factors
        if info.get("auditRisk") is not None:
            audit_risk = info.get("auditRisk")
            if audit_risk < 0.1:
                esg_score += 5
                esg_reasons.append("Low audit risk - good governance")
            elif audit_risk > 0.3:
                esg_score -= 5
                esg_reasons.append("High audit risk - governance concerns")
        
        # Risk assessment
        if beta is not None:
            if beta > 1.5:
                risk_score += 10
                risk_reasons.append("High volatility (beta > 1.5)")
            elif beta < 0.8:
                risk_score -= 5
                risk_reasons.append("Low volatility (beta < 0.8)")
        
        if debt_to_equity is not None:
            if debt_to_equity > 1.0:
                risk_score += 10
                risk_reasons.append("High leverage (D/E > 1.0)")
            elif debt_to_equity < 0.3:
                risk_score -= 5
                risk_reasons.append("Low leverage (D/E < 0.3)")
        
        if current_ratio is not None:
            if current_ratio < 1.0:
                risk_score += 5
                risk_reasons.append("Low liquidity (current ratio < 1.0)")
            elif current_ratio > 2.0:
                risk_score -= 3
                risk_reasons.append("High liquidity (current ratio > 2.0)")
        
        result = {
            "symbol": symbol,
            "esg_score": esg_score,
            "esg_reasons": esg_reasons,
            "risk_score": risk_score,
            "risk_reasons": risk_reasons,
            "beta": beta,
            "debt_to_equity": debt_to_equity,
            "current_ratio": current_ratio,
            "quick_ratio": quick_ratio,
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "audit_risk": info.get("auditRisk"),
            "board_risk": info.get("boardRisk"),
            "compensation_risk": info.get("compensationRisk"),
            "shareholder_rights_risk": info.get("shareholderRightsRisk"),
            "overall_risk": info.get("overallRisk")
        }
        
        return json.dumps(result, default=str)
    except Exception as e:
        return f"Error analyzing ESG and risk factors for {symbol}: {e}"


@tool("Get comprehensive stock analysis with enhanced scoring")
def get_comprehensive_analysis(symbol: str) -> str:
    """Complete analysis with all factors: fundamentals, quality, momentum, sentiment, ESG.
    
    Returns comprehensive 0-100 score with detailed breakdown and analysis.
    """
    try:
        # Get all analysis components
        fundamental_summary = get_fundamental_summary(symbol)
        earnings_quality = analyze_earnings_quality(symbol)
        technical_indicators = get_technical_indicators(symbol)
        market_sentiment = get_market_sentiment(symbol)
        esg_risk = get_esg_risk_factors(symbol)
        
        # Parse results
        try:
            fundamental_data = json.loads(fundamental_summary) if isinstance(fundamental_summary, str) else fundamental_summary
            earnings_data = json.loads(earnings_quality) if isinstance(earnings_quality, str) else earnings_quality
            technical_data = json.loads(technical_indicators) if isinstance(technical_indicators, str) else technical_indicators
            sentiment_data = json.loads(market_sentiment) if isinstance(market_sentiment, str) else market_sentiment
            esg_data = json.loads(esg_risk) if isinstance(esg_risk, str) else esg_risk
        except Exception:
            return f"Error parsing analysis data for {symbol}"
        
        # Enhanced scoring system (0-100)
        total_score = 0
        score_breakdown = {}
        analysis_summary = []
        
        # 1. Core Fundamentals (25 points)
        fundamental_score = 0
        if isinstance(fundamental_data, dict):
            fundamental_score = fundamental_data.get("score", 0)
            # Scale to 25 points
            fundamental_score = min(25, fundamental_score * 0.25)
        
        total_score += fundamental_score
        score_breakdown["fundamentals"] = fundamental_score
        analysis_summary.append(f"Fundamentals: {fundamental_score:.1f}/25")
        
        # 2. Earnings Quality (25 points)
        earnings_score = 0
        if isinstance(earnings_data, dict) and "error" not in earnings_data:
            # Accruals quality (15 points)
            accruals_quality = earnings_data.get("accruals_quality")
            if accruals_quality is not None:
                if accruals_quality > 1.2:
                    earnings_score += 15
                    analysis_summary.append("Excellent accruals quality (OCF > 120% of NI)")
                elif accruals_quality > 0.8:
                    earnings_score += 10
                    analysis_summary.append("Good accruals quality (OCF > 80% of NI)")
                elif accruals_quality > 0.5:
                    earnings_score += 5
                    analysis_summary.append("Moderate accruals quality")
            
            # Earnings persistence (10 points)
            earnings_persistence = earnings_data.get("earnings_persistence")
            if earnings_persistence is not None:
                if earnings_persistence > 0.7:
                    earnings_score += 10
                    analysis_summary.append("High earnings persistence")
                elif earnings_persistence > 0.5:
                    earnings_score += 7
                    analysis_summary.append("Moderate earnings persistence")
                elif earnings_persistence > 0.3:
                    earnings_score += 3
                    analysis_summary.append("Low earnings persistence")
        
        total_score += earnings_score
        score_breakdown["earnings_quality"] = earnings_score
        analysis_summary.append(f"Earnings Quality: {earnings_score:.1f}/25")
        
        # 3. Market Factors (25 points)
        market_score = 0
        if isinstance(technical_data, dict) and "error" not in technical_data:
            technical_score = technical_data.get("technical_score", 0)
            # Scale to 15 points
            market_score += min(15, technical_score * 0.75)
        
        if isinstance(sentiment_data, dict) and "error" not in sentiment_data:
            sentiment_score = sentiment_data.get("sentiment_score", 0)
            # Scale to 10 points
            market_score += min(10, max(0, sentiment_score * 0.67))
        
        total_score += market_score
        score_breakdown["market_factors"] = market_score
        analysis_summary.append(f"Market Factors: {market_score:.1f}/25")
        
        # 4. Risk & Context (25 points)
        risk_score = 0
        if isinstance(esg_data, dict) and "error" not in esg_data:
            esg_score = esg_data.get("esg_score", 0)
            # Scale to 15 points
            risk_score += min(15, max(0, (esg_score + 10) * 0.75))  # Normalize to positive
            
            risk_penalty = esg_data.get("risk_score", 0)
            # Scale to 10 points
            risk_score += min(10, max(0, (10 - risk_penalty) * 0.5))
        
        total_score += risk_score
        score_breakdown["risk_context"] = risk_score
        analysis_summary.append(f"Risk & Context: {risk_score:.1f}/25")
        
        # Overall assessment
        if total_score >= 80:
            overall_assessment = "EXCELLENT - Strong buy candidate"
        elif total_score >= 65:
            overall_assessment = "GOOD - Buy recommendation"
        elif total_score >= 50:
            overall_assessment = "FAIR - Hold with monitoring"
        elif total_score >= 35:
            overall_assessment = "POOR - Consider selling"
        else:
            overall_assessment = "VERY POOR - Strong sell"
        
        result = {
            "symbol": symbol,
            "total_score": round(total_score, 1),
            "overall_assessment": overall_assessment,
            "score_breakdown": score_breakdown,
            "analysis_summary": analysis_summary,
            "fundamental_score": fundamental_score,
            "earnings_quality_score": earnings_score,
            "market_factors_score": market_score,
            "risk_context_score": risk_score,
            "detailed_analysis": {
                "fundamentals": fundamental_data,
                "earnings_quality": earnings_data,
                "technical_indicators": technical_data,
                "market_sentiment": sentiment_data,
                "esg_risk_factors": esg_data
            }
        }
        
        return json.dumps(result, default=str)
    except Exception as e:
        return f"Error in comprehensive analysis for {symbol}: {e}"


@tool("Get fundamental summary and score")
def get_fundamental_summary(symbol: str) -> str:
    """Compute key fundamentals, growth, and a simple score for the given symbol; returns JSON.

    The summary may include: debt_to_equity, net_margin, ebitda_margin, roe,
    revenue_cagr, fcf, ocf, pe, market_cap, current_price, and an overall score (0-100).
    """
    def safe_float(value):
        try:
            if value is None:
                return None
            return float(value)
        except Exception:
            return None

    def pick_latest_from_dataframe(df, row_name_candidates):
        try:
            if df is None or getattr(df, "empty", False):
                return None
            # yfinance financials/balance_sheet/cashflow have rows as index and columns as periods (latest first)
            for row_name in row_name_candidates:
                if row_name in df.index:
                    series = df.loc[row_name]
                    for val in series:  # iterate columns in order (latest first)
                        if val is not None:
                            return safe_float(val)
            return None
        except Exception:
            return None

    def get_row_series(df, row_name):
        try:
            if df is None or getattr(df, "empty", False) or row_name not in df.index:
                return None
            # Ensure numeric floats and reverse chronological if necessary
            series = df.loc[row_name]
            values = [safe_float(v) for v in series if v is not None]
            return values
        except Exception:
            return None

    try:
        # Try exact symbol, then NSE fallback
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
        fin = getattr(ticker, "financials", None)
        bal = getattr(ticker, "balance_sheet", None)
        cfs = getattr(ticker, "cashflow", None)
        if (not info) and (not symbol.endswith(".NS")):
            ticker = yf.Ticker(symbol + ".NS")
            info = ticker.info or {}
            fin = getattr(ticker, "financials", None)
            bal = getattr(ticker, "balance_sheet", None)
            cfs = getattr(ticker, "cashflow", None)

        # Pull latest values from statements
        total_debt = pick_latest_from_dataframe(bal, ["Total Debt", "Short Long Term Debt", "Long Term Debt"])
        total_equity = pick_latest_from_dataframe(bal, ["Total Stockholder Equity", "Total Equity Gross Minority Interest"])  # type: ignore
        total_assets = pick_latest_from_dataframe(bal, ["Total Assets"])  # for context
        total_liab = pick_latest_from_dataframe(bal, ["Total Liab", "Total Liabilities Net Minority Interest"])  # type: ignore

        revenue_series = get_row_series(fin, "Total Revenue")
        net_income_series = get_row_series(fin, "Net Income")
        ebitda_series = get_row_series(fin, "Ebitda")

        ocf_latest = pick_latest_from_dataframe(cfs, ["Total Cash From Operating Activities"]) or safe_float(info.get("operatingCashflow"))
        capex_latest = pick_latest_from_dataframe(cfs, ["Capital Expenditures"])  # usually negative
        fcf_latest = pick_latest_from_dataframe(cfs, ["Free Cash Flow"])  # not always present
        if fcf_latest is None and ocf_latest is not None and capex_latest is not None:
            fcf_latest = ocf_latest + capex_latest  # capex is negative, so add

        revenue_latest = revenue_series[0] if revenue_series and len(revenue_series) > 0 else None
        net_income_latest = net_income_series[0] if net_income_series and len(net_income_series) > 0 else None
        ebitda_latest = ebitda_series[0] if ebitda_series and len(ebitda_series) > 0 else None

        # Compute ratios
        debt_to_equity = None
        if total_debt is not None and total_equity is not None and total_equity != 0:
            debt_to_equity = total_debt / total_equity

        net_margin = None
        if net_income_latest is not None and revenue_latest not in (None, 0):
            net_margin = net_income_latest / revenue_latest

        ebitda_margin = None
        if ebitda_latest is not None and revenue_latest not in (None, 0):
            ebitda_margin = ebitda_latest / revenue_latest

        roe = None
        if net_income_latest is not None and total_equity not in (None, 0):
            roe = net_income_latest / total_equity

        # CAGR on revenue (use up to 4 periods if available)
        revenue_cagr = None
        if revenue_series and len(revenue_series) >= 3:
            try:
                latest = revenue_series[0]
                oldest = revenue_series[min(3, len(revenue_series) - 1)]
                periods = min(3, len(revenue_series) - 1)
                if oldest and oldest > 0 and latest:
                    revenue_cagr = (latest / oldest) ** (1 / periods) - 1
            except Exception:
                revenue_cagr = None

        # Market/valuation
        pe = safe_float(info.get("trailingPE"))
        market_cap = safe_float(info.get("marketCap") or info.get("enterpriseValue"))
        current_price = safe_float(info.get("regularMarketPrice") or info.get("currentPrice"))

        # Simple heuristic score (0-100)
        # Positive signals: revenue_cagr > 0, net_margin > 0.1, ebitda_margin > 0.15, roe > 0.15, fcf_latest > 0, debt_to_equity < 1.0
        score = 0
        reasons = []
        def add_points(condition, points, reason):
            nonlocal score
            if condition:
                score += points
                reasons.append(reason)

        add_points(revenue_cagr is not None and revenue_cagr > 0.0, 15, "Positive revenue CAGR")
        add_points(net_margin is not None and net_margin > 0.10, 15, "Healthy net margin > 10%")
        add_points(ebitda_margin is not None and ebitda_margin > 0.15, 10, "EBITDA margin > 15%")
        add_points(roe is not None and roe > 0.15, 15, "ROE > 15%")
        add_points(fcf_latest is not None and fcf_latest > 0, 15, "Positive free cash flow")
        add_points(debt_to_equity is not None and debt_to_equity < 1.0, 15, "Debt/Equity < 1")

        # Penalties
        if revenue_cagr is not None and revenue_cagr < 0:
            reasons.append("Negative revenue CAGR")
            score = max(0, score - 10)
        if net_margin is not None and net_margin < 0.05:
            reasons.append("Thin net margin < 5%")
            score = max(0, score - 10)
        if debt_to_equity is not None and debt_to_equity > 2.0:
            reasons.append("High leverage: D/E > 2")
            score = max(0, score - 10)

        result = {
            "symbol": symbol,
            "current_price": current_price,
            "market_cap": market_cap,
            "pe": pe,
            "debt_to_equity": debt_to_equity,
            "net_margin": net_margin,
            "ebitda_margin": ebitda_margin,
            "roe": roe,
            "revenue_cagr": revenue_cagr,
            "operating_cash_flow": ocf_latest,
            "free_cash_flow": fcf_latest,
            "total_assets": total_assets,
            "total_liabilities": total_liab,
            "score": score,
            "score_reasons": reasons,
        }
        return json.dumps(result, default=str)
    except Exception as e:
        return f"Error computing fundamental summary for {symbol}: {e}"