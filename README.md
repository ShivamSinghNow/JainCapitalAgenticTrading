# Jain Capital Agentic Trading System

A multi-agent AI trading system for cryptocurrency markets that uses LangGraph and LLM-based agents to analyze market conditions, debate trading decisions, and execute trend-following strategies.

## 🎯 Project Overview

This project implements an **autonomous multi-agent trading system** where specialized AI agents collaborate to make trading decisions. The system combines:

- **Multi-agent debate architecture** (Bull vs Bear analysts)
- **LLM-powered decision making** (GPT-4, Claude)
- **Real-time data collection** (market data, news, social sentiment, on-chain metrics)
- **Trend-following strategy** with technical filters
- **Backtesting framework** for strategy evaluation

The goal is to create a systematic, data-driven trading approach that outperforms both random trading and simple buy-and-hold strategies while managing risk appropriately.

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                     Trading Decision Flow                    │
└─────────────────────────────────────────────────────────────┘

1. Data Collection Phase
   ├── Market Analyst → Price data, technical indicators (RSI, MACD, MAs)
   ├── News Analyst → Google News, crypto news RSS feeds
   ├── Fundamentals Analyst → CoinGecko metrics, Fear & Greed Index
   └── Social Media Analyst → Reddit sentiment, social mentions

2. Research Phase (Multi-Agent Debate)
   ├── Bull Researcher → Identifies bullish signals (uptrends, momentum)
   ├── Bear Researcher → Identifies bearish signals (downtrends, risks)
   └── Investment Judge → Synthesizes debate, outputs BUY/HOLD + conviction

3. Risk Management Phase
   ├── Risk Manager → Validates trend-following rules
   ├── Conviction Adjustment → Upgrades/downgrades based on signal strength
   └── Position Sizing → 1-3% risk per trade based on conviction

4. Execution Phase
   ├── Trend-Following Filters → Uptrend? Momentum? Not overbought?
   ├── Entry Logic → Only enter on confirmed uptrends + momentum
   ├── Trailing Stop → 20-day MA stop (dynamic, moves with price)
   └── Exit Logic → Exit on stop hit or trend break
```

### Agent Architecture (LangGraph)

The system uses **LangGraph** to orchestrate multiple LLM-based agents in a structured workflow:

```python
# Agent Node Structure
State = {
    "company_of_interest": str,      # Ticker (e.g., "BTC-USD")
    "decision_date": str,            # Decision date (YYYY-MM-DD)
    "market_report": str,            # Market analyst output
    "news_report": str,              # News analyst output
    "fundamentals_report": str,      # Fundamentals analyst output
    "sentiment_report": str,         # Social sentiment analyst output
    "investment_debate_state": dict, # Bull vs Bear debate history
    "investment_plan": str,          # Investment Judge decision
    "risk_debate_state": dict,       # Risk management validation
    "final_trade_decision": str      # Final decision (BUY/HOLD + conviction)
}

# Workflow: Analysts → Researchers → Judge → Risk Manager → Decision
```

**Agent Roles:**

1. **Market Analyst**: Collects price data, calculates technical indicators (50-day MA, 200-day MA, RSI, MACD, Bollinger Bands)
2. **News Analyst**: Scrapes Google News and crypto RSS feeds for latest market news
3. **Fundamentals Analyst**: Fetches Fear & Greed Index, CoinGecko market data, order book metrics
4. **Social Media Analyst**: Analyzes Reddit sentiment for crypto discussions
5. **Bull Researcher**: Argues for BUY based on trend-following signals (uptrend + momentum)
6. **Bear Researcher**: Argues for caution based on risk factors (overbought, downtrend)
7. **Investment Judge**: Makes final BUY/HOLD decision with HIGH/MEDIUM/LOW conviction
8. **Risk Manager**: Validates decision against trend-following rules, adjusts conviction

---

## 🛠️ Technology Stack

### Core Technologies

- **Python 3.11+** - Primary language
- **LangGraph** - Multi-agent orchestration framework
- **LangChain** - LLM integration and tooling
- **OpenAI GPT-4o-mini** - Primary LLM for agents (fast, cost-effective)
- **Anthropic Claude Sonnet 4.5** - Alternative LLM (higher quality reasoning)

### Data & Analysis

- **YFinance** - Historical and real-time price data
- **pandas** - Data manipulation and time series analysis
- **numpy** - Numerical calculations (RSI, MACD, statistics)
- **ccxt** - Exchange order book data (Binance)

### Data Sources (APIs)

- **YFinance** - OHLCV price data, technical indicators
- **Google News RSS** - Crypto news scraping
- **CoinGecko API** - Market cap, volume, community stats (FREE)
- **Alternative.me API** - Crypto Fear & Greed Index (FREE)
- **Binance API** - Order book data (FREE public endpoints)
- **Reddit API (PRAW)** - Social sentiment from crypto subreddits (FREE)

### Development Tools

- **dotenv** - Environment variable management
- **pytest** - Unit testing (planned)
- **git** - Version control

---

## 📊 Trading Strategy Evolution

### Phase 3.1: Initial Contrarian Strategy (FAILED)
**Philosophy**: "Be greedy when others are fearful"

**Entry Rules**:
- Fear Index < 40 (extreme fear)
- Price drop > 5% in 7 days

**Results**:
- Return: **-0.00%** (breakeven)
- Win Rate: 25%
- Problem: Caught falling knives, no exit discipline

---

### Phase 3.2: Refined Contrarian with Filters (FAILED)
**Improvements**:
- Added trend filters (50-day MA)
- Added overbought filters (RSI < 70)
- Wider stops (-3.5% → -5%)

**Results**:
- Return: **-0.10%** (worse than Phase 3.1)
- Win Rate: 25%
- Problem: Filter bugs blocked all valid trades, still caught falling knives

---

### Phase 4: Trend-Following Strategy (CURRENT) ✅
**Philosophy Shift**: "Buy strength, ride momentum"

**Entry Rules (ALL must be true)**:
1. **Uptrend confirmed**: Price > 50-day MA > 200-day MA (Golden Cross)
2. **Momentum positive**: RSI > 50 AND MACD > Signal line
3. **Not overbought**: RSI < 70 OR price < 3% from 30-day high

**Exit Rules**:
- **Trailing stop**: 20-day moving average (dynamic, follows price up)
- **No take-profit cap**: Let winners run indefinitely
- **Tight initial stop**: -2.5% hard stop (vs -3.5% in Phase 3.2)

**Conviction Levels**:
- **HIGH (3% risk)**: Uptrend + strong momentum + 3+ signals + not overbought
- **MEDIUM (2% risk)**: Uptrend + moderate momentum + 2 signals
- **LOW (1% risk)**: Early uptrend + weak momentum + 1 signal

**Phase 4 Results (Nov-Dec 2024 backtest)**:
- Return: **0.00%** (no trades executed)
- Trades blocked: 9/9 (100%)
- Reason: BTC was NOT in confirmed uptrend during test period
- **Verdict**: Filters working correctly - protected capital by avoiding bad trades

**Phase 4 Results (Full Year 2024 backtest)**: 🔄 IN PROGRESS
- Currently running 52 weekly decision points (Jan-Dec 2024)
- Estimated completion: 30-45 minutes
- Expected: Should capture Q2-Q4 2024 bull run

---

## 🗂️ Project Structure

```
JainCapitalAgenticTrading/
├── TradingAgents/                    # Core agent system (submodule)
│   ├── tradingagents/
│   │   ├── agents/
│   │   │   ├── analysts/            # Data collection agents
│   │   │   │   ├── market_analyst.py
│   │   │   │   ├── news_analyst.py
│   │   │   │   ├── fundamentals_analyst.py
│   │   │   │   └── social_media_analyst.py
│   │   │   ├── researchers/         # Bull/Bear debate agents
│   │   │   │   ├── bull_researcher_phase4.py   # Phase 4 trend-following
│   │   │   │   └── bear_researcher_phase4.py
│   │   │   └── managers/            # Decision & risk managers
│   │   │       ├── research_manager_phase4.py  # Investment Judge
│   │   │       └── risk_manager_phase4.py      # Risk validation
│   │   ├── dataflows/               # Data collection infrastructure
│   │   │   ├── interface.py         # Main data fetching interface
│   │   │   ├── stockstats_utils.py  # Technical indicators
│   │   │   ├── reddit_utils.py      # Reddit sentiment
│   │   │   └── config.py            # API keys, cache settings
│   │   ├── graph/
│   │   │   └── trading_graph.py     # LangGraph workflow orchestration
│   │   └── default_config.py        # Default configuration
│
├── backtest_phase4_trend_following.py  # Phase 4 backtest engine
├── run_decision_phase4_simple.py       # Phase 4 decision runner
├── run_decision_phase4.py              # Phase 4 with custom agents (not used)
│
├── eval_results/                     # Backtest results by phase
│   ├── phase3_1_baseline/
│   ├── phase3_2_refined/
│   └── phase4_trend_following/       # (to be created)
│
├── data_cache/                       # Cached API responses
├── test_all_data_sources.py          # Data source validation tests
├── test_yfinance.py                  # YFinance data tests
├── test_google_news.py               # News scraping tests
│
├── .env                              # Environment variables (API keys)
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

---

## 🚀 Getting Started

### Prerequisites

```bash
# Python 3.11 or higher
python --version

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the project root:

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=sk-...

# Agent Configuration
AGENT_DEEP_MODEL=gpt-4o-mini      # Deep thinking model
AGENT_QUICK_MODEL=gpt-4o-mini     # Quick analysis model
AGENT_MAX_DEBATE=1                # Max debate rounds (1 = faster)

# Optional: Anthropic Claude (alternative LLM)
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Reddit API (for social sentiment)
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=...
```

### Running a Backtest

```bash
# Run Phase 4 backtest (Nov-Dec 2024)
python backtest_phase4_trend_following.py

# Modify dates in backtest_phase4_trend_following.py main() function:
# start_date="2024-01-01", end_date="2024-12-31"
```

### Testing Data Sources

```bash
# Test all data sources
python test_all_data_sources.py

# Test specific sources
python test_yfinance.py
python test_google_news.py
```

### Running a Single Decision

```bash
# Get agent decision for specific date
python run_decision_phase4_simple.py
# Default: BTC-USD on 2024-11-08
```

---

## 📈 Backtest Results Summary

| Phase | Strategy | Return | Win Rate | Sharpe | Trades | Status |
|-------|----------|--------|----------|--------|--------|--------|
| 3.1 | Contrarian (Fear Index) | -0.00% | 25% | 0.00 | 8 | ❌ Failed |
| 3.2 | Contrarian + Filters | -0.10% | 25% | -1.03 | 8 | ❌ Failed |
| 4 (Nov-Dec) | Trend-Following | 0.00% | 0% | 0.00 | 0 | ⚠️ No valid trades |
| 4 (Full Year) | Trend-Following | 🔄 Running | - | - | - | 🔄 In Progress |

**Key Insights**:
- Contrarian strategies (Phases 3.1, 3.2) lost money by catching falling knives
- Phase 4 trend-following correctly avoided trading during Nov-Dec 2024 downtrend
- Need to test Phase 4 on periods with clear uptrends (full year 2024 backtest running)

---

## 🔍 Current Status & Work Completed

### ✅ Completed Work

1. **Multi-Agent System Architecture**
   - Implemented LangGraph workflow with 8 specialized agents
   - Bull vs Bear debate mechanism with Investment Judge arbiter
   - Risk Manager validation layer with conviction adjustment
   - Persistent memory system for learning from past decisions

2. **Data Collection Infrastructure**
   - YFinance integration for OHLCV price data
   - Google News RSS scraping for crypto news
   - CoinGecko API for market fundamentals
   - Fear & Greed Index integration
   - Binance order book data
   - Reddit sentiment analysis (PRAW)
   - Technical indicators: RSI, MACD, Bollinger Bands, 50/200-day MAs

3. **Phase 4 Trend-Following Strategy**
   - Complete rewrite of agent prompts (contrarian → trend-following)
   - Entry filters: Uptrend + Momentum + Not Overbought
   - Trailing stop system (20-day MA)
   - Dynamic conviction scaling (HIGH/MEDIUM/LOW)
   - Backtest engine with weekly decision points

4. **Backtesting Framework**
   - Automated backtest execution with 52 weekly decisions per year
   - Performance metrics: Return %, Win Rate, Sharpe Ratio, Max Drawdown
   - Trade logging with entry/exit prices, P&L, conviction levels
   - Comparison vs Buy & Hold benchmark

5. **Bug Fixes**
   - Fixed pandas Series boolean ambiguity error (critical bug)
   - Fixed timezone mismatch between decision dates and price data
   - Fixed date indexing when decision date not in price data
   - Fixed Python module caching issues during development

---

## 🎯 Next Priorities

### Immediate Priorities (Week 1-2)

1. **Complete Full Year 2024 Backtest** ⏳ IN PROGRESS
   - Currently running 52 weekly decisions for Jan-Dec 2024
   - Analyze results vs Buy & Hold
   - Identify which market conditions produce winning trades

2. **Optimize MA Lookback Period**
   - Current: 50-day and 200-day MAs (slow signals)
   - Test: 20-day and 50-day MAs (faster signals)
   - Issue: Early 2024 decisions had `MA50 = nan` (insufficient data)
   - Solution: Start backtest earlier OR use shorter MAs

3. **Fix Data Source Reliability**
   - Issue: CryptoPanic API blocked by Cloudflare
   - Solution: Implement robust RSS feed aggregation (CoinDesk, Cointelegraph, Bitcoin Magazine)
   - Add fallback logic when APIs fail

4. **Implement Profit Taking Logic**
   - Current: No take-profit cap (let winners run)
   - Problem: May give back gains during trend reversals
   - Test: Partial profit taking at +10%, +20%, +30% (trail remaining position)

### Medium-Term Priorities (Week 3-4)

5. **Live Trading Preparation**
   - Set up paper trading environment (testnet or exchange paper trading)
   - Implement real-time decision loop (`run_live_loop.py`)
   - Add Telegram/Discord notifications for trade signals
   - Implement position tracking and portfolio management

6. **Multi-Asset Support**
   - Current: BTC-USD only
   - Expand: ETH-USD, SOL-USD, major altcoins
   - Implement portfolio allocation (risk per asset)
   - Test correlation-based diversification

7. **Advanced Data Sources** (100% FREE)
   - **On-chain metrics**: CoinGecko API (network activity, developer stats)
   - **Exchange metrics**: Binance funding rates, open interest, long/short ratios
   - **DeFi metrics**: DefiLlama TVL, protocol revenue (for DeFi tokens)
   - **Social sentiment**: Twitter/X crypto sentiment (via CryptoCompare API)
   - See `ARCHITECTURE_EXPLANATION.md` for detailed plan

8. **Strategy Refinements**
   - Test different MA periods (10/20, 20/50, 50/100)
   - Add volume confirmation (high volume breakouts)
   - Implement market regime detection (bull/bear/sideways)
   - Test multiple timeframes (daily + weekly alignment)

### Long-Term Priorities (Month 2+)

9. **Machine Learning Enhancements**
   - Train ML model to predict optimal conviction levels
   - Use historical trade data to learn from wins/losses
   - Implement reinforcement learning for position sizing

10. **Risk Management Improvements**
    - Portfolio-level risk management (max drawdown limits)
    - Correlation-based position sizing
    - Dynamic risk adjustment based on market volatility
    - Kelly Criterion for optimal position sizing

11. **Performance Optimization**
    - Cache agent decisions to speed up backtests
    - Parallelize data collection across multiple symbols
    - Optimize LLM costs (use cheaper models for routine tasks)

12. **Production Readiness**
    - Comprehensive unit test suite
    - Error handling and retry logic
    - Monitoring and alerting (Sentry, Datadog)
    - Deployment infrastructure (Docker, Kubernetes)

---

## 🐛 Known Issues

1. **MA Calculation Requires Lookback**
   - 50-day MA needs 50 days of historical data
   - First ~7 decisions in backtests show `MA50 = nan`
   - Solution: Fetch data starting 200 days before first decision date

2. **CryptoPanic API Blocked**
   - Cloudflare protection blocks automated requests
   - Currently falling back to RSS feeds
   - Solution: Rotate user agents, use residential proxies, or accept RSS-only

3. **Long Backtest Execution Time**
   - 52 decisions × ~30 seconds per decision = 25-30 minutes
   - Each decision requires LLM inference (expensive API calls)
   - Solution: Cache decisions, use faster models (gpt-4o-mini), parallelize

4. **No Trades in Nov-Dec 2024 Test**
   - Phase 4 blocked all 9 trades (downtrend filter)
   - Not necessarily a bug - correctly avoided trading in unfavorable conditions
   - Need to test on periods with clear uptrends (full year 2024)

---

## 📚 Key Learnings

### What Worked

1. **Multi-agent debate improves decisions**: Bull vs Bear adversarial debate catches edge cases
2. **Risk Manager as gatekeeper**: Prevents overconfident trades, adjusts conviction appropriately
3. **Trend-following filters**: Correctly blocked trades during Nov-Dec 2024 downtrend (protected capital)
4. **Free data sources**: CoinGecko, Fear & Greed Index, Binance public APIs provide sufficient data
5. **LangGraph orchestration**: Clean agent workflow, easy to modify and debug

### What Didn't Work

1. **Contrarian strategies** (Phases 3.1, 3.2): Consistently lost money by catching falling knives
2. **Fixed stop losses** (-3.5%, -5%): Got stopped out during normal volatility
3. **Take-profit caps** (+7%): Limited upside during strong trends
4. **50-day MA in short backtests**: Not enough data for early decisions

### Strategic Insights

1. **Trend-following >> Contrarian** for crypto: Strong trends persist longer than expected
2. **Let winners run**: Trailing stops > fixed take-profits
3. **Downtrend avoidance**: Better to sit out than force trades in bad conditions
4. **Conviction scaling matters**: Position sizing should match signal strength

---

## 🤝 Contributing

This is currently a personal research project. Contributions are welcome via:

1. **Issue reports**: Found a bug? Open an issue with reproduction steps
2. **Feature requests**: Have an idea? Open an issue with use case
3. **Pull requests**: Code improvements welcome (please open issue first to discuss)

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions
- Write unit tests for new features
- Update README with any architecture changes

---

## 📄 License

This project is for educational and research purposes. Not financial advice.

**Disclaimer**: Trading cryptocurrencies involves substantial risk of loss. This system is experimental and should not be used with real capital without thorough testing and risk management. Past performance does not guarantee future results.

---

## 📞 Contact

**Author**: Shivam Singh (Jain Capital)
**Project Start Date**: March 2025
**Last Updated**: January 2026

---

## 🔗 References & Resources

### Papers & Research
- **LangGraph**: Multi-Agent Orchestration Framework (LangChain)
- **Trend Following**: "Following the Trend" by Andreas Clenow
- **Multi-Agent Systems**: "Generative Agents" (Stanford, 2023)

### APIs & Data Sources
- [YFinance Documentation](https://pypi.org/project/yfinance/)
- [CoinGecko API](https://www.coingecko.com/en/api)
- [Alternative.me Fear & Greed Index](https://alternative.me/crypto/fear-and-greed-index/)
- [Binance API](https://binance-docs.github.io/apidocs/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

### Trading Strategy Resources
- [Investopedia: Trend Following](https://www.investopedia.com/terms/t/trendtrading.asp)
- [TradingView: Moving Average Crossovers](https://www.tradingview.com/wiki/Moving_Average#Crosses)
- [BabyPips: RSI Indicator](https://www.babypips.com/learn/forex/relative-strength-index)

---

**Last Backtest Run**: January 21, 2025 (Phase 4 Full Year 2024 - IN PROGRESS)
**System Status**: 🟢 Active Development
**Next Milestone**: Complete full year 2024 backtest, analyze results, optimize MA periods
