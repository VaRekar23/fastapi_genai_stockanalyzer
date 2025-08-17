# 🚀 FastAPI GenAI Stock Analyzer

A sophisticated AI-powered stock analysis platform built with FastAPI and CrewAI, providing comprehensive stock analysis, intraday trading recommendations, and market insights.

## 🌟 Features

### 📊 **Comprehensive Stock Analysis** (`/stock/{symbol}`)
- **Fundamental Analysis**: Revenue, profitability, cash flow, debt ratios
- **Earnings Quality**: Accruals quality, persistence, predictability analysis
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages
- **Market Sentiment**: Analyst ratings, price targets, volume analysis
- **ESG & Risk Factors**: Environmental, social, governance, volatility assessment
- **AI-Powered Scoring**: 0-100 comprehensive rating system

### ⚡ **Intraday Trading Analysis** (`/intraday/{symbol}`)
- **Algorithmic Analysis**: Fast, rule-based entry/exit recommendations
- **Price Levels**: Entry, exit, and stop loss prices
- **Risk Assessment**: Risk-reward ratio calculations
- **Trading Strategy**: Position sizing and execution guidance

### 🤖 **AI Agent-Based Intraday** (`/intraday-agents/{symbol}`)
- **Expert AI Analysis**: CrewAI agents for intelligent market reasoning
- **Trading Decisions**: Clear BUY/SELL/HOLD recommendations
- **Exact Price Levels**: Specific entry, exit, and stop loss prices
- **Risk Management**: Comprehensive risk assessment and position sizing
- **Market Timing**: Optimal entry/exit timing during trading sessions

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python web framework)
- **AI Agents**: CrewAI (autonomous agent orchestration)
- **LLM Integration**: OpenAI GPT models (GPT-4o-mini, GPT-5-nano)
- **Data Sources**: yfinance (financial data), DuckDuckGo (web search)
- **Data Processing**: Pandas, NumPy
- **Deployment**: Uvicorn ASGI server

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/fastapi_genai_stockanalyzer.git
   cd fastapi_genai_stockanalyzer
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Edit .env with your API keys
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API**
   - **API Documentation**: http://localhost:8000/docs
   - **Alternative Docs**: http://localhost:8000/redoc
   - **Health Check**: http://localhost:8000/

## 📡 API Endpoints

### **Stock Analysis**
```
GET /stock/{symbol}
```
Comprehensive AI-powered stock analysis with detailed scoring and insights.

**Example**: `/stock/TCS` - Analyze Tata Consultancy Services

### **Algorithmic Intraday Analysis**
```
GET /intraday/{symbol}
```
Fast, rule-based intraday trading recommendations with price levels.

**Example**: `/intraday/RELIANCE` - Get intraday levels for Reliance Industries

### **AI Agent-Based Intraday Analysis**
```
GET /intraday-agents/{symbol}
```
Expert AI analysis with specific BUY/SELL/HOLD recommendations and exact price levels.

**Example**: `/intraday-agents/INFY` - Get AI-powered intraday trading strategy

### **Debug & Health**
```
GET /debug/openai
```
Verify OpenAI API key configuration and model access.

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Alternative LLM Providers (optional)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant

REPLICATE_API_TOKEN=your_replicate_token_here
REPLICATE_MODEL=meta/llama-3.1-70b-versatile

# Search API (optional)
TAVILY_API_KEY=your_tavily_api_key_here
```

### Model Selection

**OpenAI** (primary): Best reasoning capabilities

## 📊 Stock Analysis Components

### **Fundamental Analysis (25 points)**
- Revenue growth and profitability
- Cash flow analysis
- Debt-to-equity ratios
- Market capitalization trends
- Earnings per share (EPS) analysis

### **Earnings Quality (25 points)**
- Accruals quality (Operating Cash Flow vs Net Income)
- Earnings persistence and predictability
- Revenue recognition quality
- Working capital efficiency

### **Market Factors (25 points)**
- Technical indicators (RSI, MACD, Moving Averages)
- Price momentum and volatility
- Volume analysis and trends
- Support and resistance levels

### **Risk & Context (25 points)**
- ESG (Environmental, Social, Governance) scores
- Beta and market correlation
- Sector-specific risks
- Regulatory and compliance factors

## 🎯 Intraday Trading Strategy

### **Entry Criteria**
- RSI oversold/overbought conditions
- MACD signal crossovers
- Support/resistance breakouts
- Volume confirmation

### **Exit Strategy**
- Profit targets (1.5-2.5% for intraday)
- Time-based exits (2-4 hours maximum)
- Technical indicator reversals
- News-driven exits

### **Risk Management**
- Stop loss placement (0.8-1.5% risk)
- Position sizing (1-2% of portfolio)
- Risk-reward ratio minimum (1.5:1)
- Alternative scenario planning

## 🚀 Deployment

### **Development**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Production**
```bash
# Using Gunicorn (recommended for production)
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using Uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### **Docker Deployment**
```dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🧪 Testing

### **Manual Testing**
```bash
# Test stock analysis
curl "http://localhost:8000/stock/TCS"

# Test intraday analysis
curl "http://localhost:8000/intraday/RELIANCE"

# Test AI agent intraday
curl "http://localhost:8000/intraday-agents/INFY"
```

### **Automated Testing** (Future Enhancement)
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

## 📈 Performance Optimization

### **Current Optimizations**
- Agent `max_iter` limited to 2 to prevent infinite loops
- Caching enabled for agents
- Sequential processing for predictable execution
- Rate limiting and backoff for external APIs

### **Future Enhancements**
- Redis caching for API responses
- Async processing for multiple stock analysis
- Database storage for historical analysis
- WebSocket support for real-time updates

## 🔒 Security Considerations

- **API Keys**: Never commit `.env` files to version control
- **Rate Limiting**: Implemented for external API calls
- **Input Validation**: Stock symbols validated and sanitized
- **Error Handling**: Comprehensive error handling without exposing sensitive information

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### **Development Guidelines**
- Follow PEP 8 style guidelines
- Add type hints to function parameters
- Include docstrings for all functions
- Test your changes before submitting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**This software is for educational and research purposes only. It is not intended to provide financial advice or recommendations for actual trading. Always conduct your own research and consult with qualified financial advisors before making investment decisions.**

The authors and contributors are not responsible for any financial losses or decisions made based on the analysis provided by this software.

## 🆘 Support

### **Common Issues**

1. **Import Errors**: Ensure all dependencies are installed from `requirements.txt`
2. **API Key Issues**: Verify your `.env` file contains valid API keys
3. **Model Access**: Check if your OpenAI account has access to the specified model
4. **Rate Limits**: Implement backoff strategies for external API calls

### **Getting Help**
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the API docs at `/docs` endpoint

## 🎉 Acknowledgments

- **CrewAI**: For the amazing agent orchestration framework
- **FastAPI**: For the modern, fast web framework
- **OpenAI**: For providing powerful language models
- **yfinance**: For comprehensive financial data access

---

**Made with ❤️ for the AI and trading community**

*Star this repository if you find it helpful! ⭐*
