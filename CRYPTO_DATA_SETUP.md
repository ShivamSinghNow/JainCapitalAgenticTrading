# Crypto Data Collection Setup Guide

## 🎉 100% FREE Crypto Data Sources

This guide explains how to set up the new crypto-native data collection features. All data sources are **completely FREE** with generous limits suitable for trading applications.

---

## Quick Start

### 1. Install Required Dependencies

```bash
pip install ccxt feedparser requests pandas numpy
```

### 2. Configure API Keys (Optional but Recommended)

While some data sources work without API keys, getting free API keys provides better rate limits and more features.

#### Free API Keys to Get:

1. **CryptoPanic** (3000 requests/day)
   - Sign up: https://cryptopanic.com/developers/api/
   - Get your free API key
   - Add to environment: `export CRYPTOPANIC_API_KEY="your_key_here"`

2. **CryptoCompare** (100,000 calls/month)
   - Sign up: https://min-api.cryptocompare.com
   - Get your free API key
   - Add to environment: `export CRYPTOCOMPARE_API_KEY="your_key_here"`

3. **Reddit API** (Unlimited, OAuth2)
   - Create app: https://www.reddit.com/prefs/apps
   - Get client ID and secret
   - Add to environment:
     ```bash
     export REDDIT_CLIENT_ID="your_client_id"
     export REDDIT_CLIENT_SECRET="your_client_secret"`
     ```

4. **GitHub API** (5000 requests/hour)
   - Create token: https://github.com/settings/tokens
   - Add to environment: `export GITHUB_TOKEN="your_token_here"`

5. **Etherscan API** (5 calls/second)
   - Get key: https://etherscan.io/myapikey
   - Add to environment: `export ETHERSCAN_API_KEY="your_key_here"`

### 3. Set Environment Variables

Create a `.env` file in your project root:

```bash
# Crypto Data API Keys (All FREE!)
CRYPTOPANIC_API_KEY=your_key_here
CRYPTOCOMPARE_API_KEY=your_key_here
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
GITHUB_TOKEN=your_token_here
ETHERSCAN_API_KEY=your_key_here
```

Then load in your script:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## New Data Sources Available

### 📊 Exchange Data (100% FREE, No API Key Required)

#### Funding Rates
```python
from TradingAgents.tradingagents.dataflows.exchange_utils import get_binance_funding_rate

# Get funding rate history
funding_data = get_binance_funding_rate("BTCUSDT", limit=10)
print(funding_data)
```

**What it provides:**
- Current and historical funding rates
- Sentiment interpretation (bullish/bearish)
- Average funding rate trends

**Why it matters:**
- Positive funding = Longs pay shorts (bullish sentiment)
- Negative funding = Shorts pay longs (bearish sentiment)
- Extreme rates often precede reversals

#### Open Interest
```python
from TradingAgents.tradingagents.dataflows.exchange_utils import get_binance_open_interest

# Get current open interest
oi_data = get_binance_open_interest("BTCUSDT")
print(oi_data)
```

**What it provides:**
- Total outstanding contracts
- Timestamp of data

**Why it matters:**
- Rising OI + rising price = bullish (new longs)
- Rising OI + falling price = bearish (new shorts)
- Falling OI = liquidations or profit-taking

#### Long/Short Ratios
```python
from TradingAgents.tradingagents.dataflows.exchange_utils import get_binance_long_short_ratio

# Get top trader positioning
ratio_data = get_binance_long_short_ratio("BTCUSDT", period="1h", limit=10)
print(ratio_data)
```

**What it provides:**
- Ratio of long vs short positions
- Top trader sentiment
- Historical trends

**Why it matters:**
- Shows smart money positioning
- Extreme ratios indicate crowded trades
- Can be used as contrarian indicator

#### Order Book Analysis
```python
from TradingAgents.tradingagents.dataflows.exchange_utils import get_order_book_imbalance

# Analyze bid/ask pressure
orderbook_data = get_order_book_imbalance("BTCUSDT", depth=20)
print(orderbook_data)
```

**What it provides:**
- Bid/ask volume distribution
- Order book imbalance percentage
- Spread analysis

**Why it matters:**
- Shows short-term buy/sell pressure
- Helps identify support/resistance
- Indicates potential price direction

#### Taker Buy/Sell Volume
```python
from TradingAgents.tradingagents.dataflows.exchange_utils import get_taker_buysell_volume

# Analyze aggressive trading
volume_data = get_taker_buysell_volume("BTCUSDT", interval="1h", limit=24)
print(volume_data)
```

**What it provides:**
- Aggressive buy vs sell volume
- Market sentiment indicator
- Volume directionality

**Why it matters:**
- Taker buy > sell = Bullish momentum
- Taker sell > buy = Bearish momentum
- Sudden shifts signal trend changes

---

### 📰 Crypto News (FREE with API Keys)

#### CryptoPanic News (Aggregated + Sentiment)
```python
from TradingAgents.tradingagents.dataflows.cryptonews_utils import get_cryptopanic_news

# Get news with sentiment scoring
news = get_cryptopanic_news("BTC", curr_date="2024-12-30", look_back_days=7)
print(news)
```

**What it provides:**
- News from 5000+ crypto sources
- Positive/negative/neutral sentiment
- Importance filtering
- Engagement metrics

**Why it matters:**
- Aggregates all major crypto news
- Built-in sentiment analysis
- Filters noise from important news

#### RSS Feed Aggregation (100% FREE, No API Key)
```python
from TradingAgents.tradingagents.dataflows.cryptonews_utils import get_rss_crypto_news

# Get news from CoinDesk, Cointelegraph, Bitcoin Magazine, Decrypt
news = get_rss_crypto_news(curr_date="2024-12-30", look_back_days=7)
print(news)
```

**What it provides:**
- News from major publications
- No API key required
- Completely free

**Why it matters:**
- Reliable news sources
- No rate limits
- Always available

#### CryptoCompare News
```python
from TradingAgents.tradingagents.dataflows.cryptonews_utils import get_cryptocompare_news

# Get categorized crypto news
news = get_cryptocompare_news(categories="BTC,ETH,trading", limit=20)
print(news)
```

**What it provides:**
- Real-time crypto news
- Category filtering
- Source information

#### CoinGecko Events
```python
from TradingAgents.tradingagents.dataflows.cryptonews_utils import get_coingecko_events

# Get upcoming crypto events
events = get_coingecko_events(coin_id="bitcoin", upcoming_only=True)
print(events)
```

**What it provides:**
- Hard forks, airdrops, partnerships
- Conferences and mainnet launches
- Token unlocks

**Why it matters:**
- Plan around important events
- Anticipate volatility
- Identify catalysts

---

### ✅ Data Validation (100% FREE, No Dependencies)

#### Validate Price Data
```python
from TradingAgents.tradingagents.dataflows.data_validation import validate_price_data
import pandas as pd

# Validate OHLCV data
is_valid, issues = validate_price_data(df, symbol="BTC-USD")

if not is_valid:
    print("Data issues found:")
    for issue in issues:
        print(f"  - {issue}")
```

**Checks performed:**
- Missing values
- Negative/zero prices
- OHLC relationship validity
- Extreme price jumps
- Date ordering

#### Detect Anomalies
```python
from TradingAgents.tradingagents.dataflows.data_validation import detect_price_anomalies

# Find statistical outliers
anomalies = detect_price_anomalies(df, symbol="BTC-USD")

if anomalies['anomalies_found']:
    print(f"Found {anomalies['anomaly_count']} anomalies")
    for anomaly in anomalies['anomalies']:
        print(f"  - {anomaly['date']}: {anomaly['return']*100:.1f}% return")
```

#### Cross-Validate Sources
```python
from TradingAgents.tradingagents.dataflows.data_validation import cross_validate_prices

# Compare prices from different sources
is_valid, warning = cross_validate_prices(
    price1=50000.0,
    price2=50500.0,
    source1="YFinance",
    source2="Binance",
    symbol="BTC-USD",
    max_diff_pct=2.0
)

if not is_valid:
    print(warning)
```

---

## Usage Examples

### Example 1: Complete Market Analysis for BTC

```python
from TradingAgents.tradingagents.dataflows.exchange_utils import (
    get_binance_funding_rate,
    get_binance_open_interest,
    get_binance_long_short_ratio,
    get_taker_buysell_volume
)

symbol = "BTCUSDT"

# Get all exchange metrics
funding = get_binance_funding_rate(symbol, limit=5)
oi = get_binance_open_interest(symbol)
ls_ratio = get_binance_long_short_ratio(symbol, period="1h", limit=5)
volume = get_taker_buysell_volume(symbol, interval="1h", limit=12)

print("=== BTC Market Analysis ===")
print(funding)
print(oi)
print(ls_ratio)
print(volume)
```

### Example 2: Complete News Analysis for BTC

```python
from TradingAgents.tradingagents.dataflows.cryptonews_utils import (
    get_cryptopanic_news,
    get_rss_crypto_news,
    get_coingecko_events
)

curr_date = "2024-12-30"

# Get all news sources
cryptopanic = get_cryptopanic_news("BTC", curr_date, look_back_days=3)
rss_news = get_rss_crypto_news(curr_date, look_back_days=3)
events = get_coingecko_events(coin_id="bitcoin", upcoming_only=True)

print("=== BTC News Analysis ===")
print(cryptopanic)
print(rss_news)
print(events)
```

### Example 3: Data Validation Pipeline

```python
from TradingAgents.tradingagents.dataflows.data_validation import (
    generate_validation_report
)
import pandas as pd

# Load your price data
df = pd.read_csv("BTC-USD-data.csv")

# Generate comprehensive validation report
report = generate_validation_report(df, symbol="BTC-USD", source="YFinance")
print(report)
```

---

## Rate Limits & Best Practices

### API Rate Limits (All FREE Tiers):

| Service | Rate Limit | Cost |
|---------|-----------|------|
| Binance Public API | No limit | FREE |
| CCXT | Depends on exchange | FREE |
| CryptoPanic | 3000 req/day | FREE |
| CryptoCompare | 100k calls/month | FREE |
| RSS Feeds | No limit | FREE |
| CoinGecko | 10-50 calls/min | FREE |
| Reddit API | No limit (OAuth2) | FREE |
| GitHub API | 5000 req/hour | FREE |
| Etherscan | 5 calls/second | FREE |

### Best Practices:

1. **Use Caching**: Don't fetch the same data repeatedly
   - Funding rates: Cache for 15 minutes
   - News: Cache for 1 hour
   - Events: Cache for 24 hours

2. **Handle Failures Gracefully**: All functions use retry logic
   - 3 retries with exponential backoff
   - Returns error messages instead of crashing

3. **Validate Data**: Always validate critical data
   ```python
   from TradingAgents.tradingagents.dataflows.data_validation import validate_price_data

   is_valid, issues = validate_price_data(df, symbol)
   if not is_valid:
       # Handle invalid data
       pass
   ```

4. **Cross-Validate Prices**: Compare across sources
   ```python
   from TradingAgents.tradingagents.dataflows.data_validation import cross_validate_prices

   is_valid, warning = cross_validate_prices(price1, price2, "Source1", "Source2", symbol)
   ```

---

## Troubleshooting

### Issue: "CryptoPanic API key not configured" or CryptoPanic blocked by Cloudflare
**Solution**: No action needed! The `get_cryptopanic_news()` function automatically falls back to RSS feeds when the CryptoPanic API is unavailable. RSS feeds from CoinDesk, Cointelegraph, Bitcoin Magazine, and Decrypt provide reliable crypto news without any API key.

**Optional**: If you want to try the CryptoPanic API, get a free API key from https://cryptopanic.com/developers/api/ and set:
```bash
export CRYPTOPANIC_API_KEY="your_key_here"
```
Note: CryptoPanic API is currently blocked by Cloudflare protection for most users.

### Issue: "Error fetching funding rate for BTCUSDT"
**Solution**: Check symbol format. Use "BTCUSDT" (no slash) for Binance API.
```python
from TradingAgents.tradingagents.dataflows.exchange_utils import normalize_symbol_for_binance

symbol = normalize_symbol_for_binance("BTC-USD")  # Returns "BTCUSDT"
```

### Issue: RSS feed parsing fails
**Solution**: Install feedparser library:
```bash
pip install feedparser
```

### Issue: Rate limit exceeded
**Solution**: Implement caching or reduce request frequency. All functions support caching via config:
```python
config = {
    "cache_ttl": {
        "exchange_data": 900,  # 15 minutes
        "news_data": 3600,  # 1 hour
    }
}
```

---

## What's Next?

### Phase 2 (Coming Soon):
- On-chain metrics (CoinGecko, Blockchain.info, CryptoCompare)
- Social sentiment (Reddit, Fear & Greed Index, GitHub activity)

### Phase 3 (Future):
- DeFi protocol metrics (DefiLlama, Etherscan)
- Crypto-specific technical indicators

---

## Support

For issues or questions:
1. Check this documentation first
2. Review code examples in `/TradingAgents/tradingagents/dataflows/`
3. Open an issue on GitHub

---

## License

This project is open source and free for anyone to use. All data sources use free tiers or public APIs.

**Total Cost: $0.00/month** 🎉
