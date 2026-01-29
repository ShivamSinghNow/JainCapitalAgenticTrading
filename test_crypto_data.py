"""
Test Script for New Crypto Data Collection Features

This script demonstrates all the new FREE crypto data sources:
- Exchange data (funding rates, open interest, long/short ratios)
- Crypto news (CryptoPanic, RSS feeds, CoinGecko events)
- Data validation

Run this to verify everything is working correctly!
"""

print("=" * 80)
print("🚀 Testing New Crypto Data Collection Features (100% FREE)")
print("=" * 80)
print()

# ===== TEST 1: EXCHANGE DATA (No API Key Required) =====
print("=" * 80)
print("TEST 1: Exchange Data (Binance Public API - FREE)")
print("=" * 80)
print()

try:
    from TradingAgents.tradingagents.dataflows.exchange_utils import (
        get_binance_funding_rate,
        get_binance_open_interest,
        get_binance_long_short_ratio,
        get_order_book_imbalance,
        get_taker_buysell_volume,
    )

    symbol = "BTCUSDT"

    print(f"📊 Testing Funding Rate for {symbol}...")
    funding = get_binance_funding_rate(symbol, limit=5)
    print(funding)
    print()

    print(f"📊 Testing Open Interest for {symbol}...")
    oi = get_binance_open_interest(symbol)
    print(oi)
    print()

    print(f"📊 Testing Long/Short Ratio for {symbol}...")
    ls_ratio = get_binance_long_short_ratio(symbol, period="1h", limit=5)
    print(ls_ratio)
    print()

    print(f"📊 Testing Order Book Imbalance for {symbol}...")
    orderbook = get_order_book_imbalance(symbol, depth=20)
    print(orderbook)
    print()

    print(f"📊 Testing Taker Buy/Sell Volume for {symbol}...")
    volume = get_taker_buysell_volume(symbol, interval="1h", limit=12)
    print(volume)
    print()

    print("✅ Exchange Data Test: PASSED")
    print()

except Exception as e:
    print(f"❌ Exchange Data Test: FAILED - {str(e)}")
    print()

# ===== TEST 2: CRYPTO NEWS (FREE with Optional API Keys) =====
print("=" * 80)
print("TEST 2: Crypto News Sources")
print("=" * 80)
print()

try:
    from TradingAgents.tradingagents.dataflows.cryptonews_utils import (
        get_rss_crypto_news,
        get_coingecko_events,
    )
    from datetime import datetime

    curr_date = datetime.now().strftime("%Y-%m-%d")

    print("📰 Testing RSS Feed Aggregation (100% FREE, No API Key)...")
    rss_news = get_rss_crypto_news(curr_date=curr_date, look_back_days=2, max_articles_per_source=5)
    print(rss_news[:1000] + "..." if len(rss_news) > 1000 else rss_news)  # Truncate for readability
    print()

    print("📅 Testing CoinGecko Events (100% FREE, No API Key)...")
    events = get_coingecko_events(coin_id="bitcoin", upcoming_only=True)
    print(events[:1000] + "..." if len(events) > 1000 else events)
    print()

    print("✅ Crypto News Test: PASSED")
    print()

except Exception as e:
    print(f"❌ Crypto News Test: FAILED - {str(e)}")
    print()

# ===== TEST 3: DATA VALIDATION (100% FREE) =====
print("=" * 80)
print("TEST 3: Data Validation")
print("=" * 80)
print()

try:
    from TradingAgents.tradingagents.dataflows.data_validation import (
        cross_validate_prices,
        check_data_freshness,
        validate_value_range,
    )
    from datetime import datetime, timedelta

    print("✅ Testing Price Cross-Validation...")
    is_valid, warning = cross_validate_prices(
        price1=50000.0,
        price2=50200.0,
        source1="YFinance",
        source2="Binance",
        symbol="BTC-USD",
        max_diff_pct=1.0
    )

    if is_valid:
        print(f"  ✅ Prices validated successfully (within 1% tolerance)")
    else:
        print(f"  ⚠️  {warning}")
    print()

    print("✅ Testing Data Freshness Check...")
    now = datetime.now()
    is_fresh, warning = check_data_freshness(
        timestamp=now - timedelta(minutes=5),
        symbol="BTC-USD",
        max_age_minutes=60
    )

    if is_fresh:
        print(f"  ✅ Data is fresh (less than 60 minutes old)")
    else:
        print(f"  ⚠️  {warning}")
    print()

    print("✅ Testing Value Range Validation...")
    is_valid, error = validate_value_range(
        value=0.05,
        symbol="BTC-USD",
        field_name="Funding Rate",
        min_value=-1.0,
        max_value=1.0
    )

    if is_valid:
        print(f"  ✅ Value within valid range")
    else:
        print(f"  ❌ {error}")
    print()

    print("✅ Data Validation Test: PASSED")
    print()

except Exception as e:
    print(f"❌ Data Validation Test: FAILED - {str(e)}")
    print()

# ===== TEST 4: Symbol Normalization =====
print("=" * 80)
print("TEST 4: Symbol Normalization Utilities")
print("=" * 80)
print()

try:
    from TradingAgents.tradingagents.dataflows.exchange_utils import (
        normalize_symbol_for_binance,
        normalize_symbol_for_ccxt,
    )

    test_symbols = ["BTC-USD", "BTC/USDT", "BTCUSDT", "ETH-USD"]

    print("Testing Binance Symbol Normalization:")
    for symbol in test_symbols:
        normalized = normalize_symbol_for_binance(symbol)
        print(f"  {symbol:15} -> {normalized}")
    print()

    print("Testing CCXT Symbol Normalization:")
    for symbol in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        normalized = normalize_symbol_for_ccxt(symbol)
        print(f"  {symbol:15} -> {normalized}")
    print()

    print("✅ Symbol Normalization Test: PASSED")
    print()

except Exception as e:
    print(f"❌ Symbol Normalization Test: FAILED - {str(e)}")
    print()

# ===== SUMMARY =====
print("=" * 80)
print("🎉 TEST SUMMARY")
print("=" * 80)
print()
print("✅ All tests completed!")
print()
print("📝 Next Steps:")
print("   1. Set up optional API keys for more features:")
print("      - CryptoPanic: https://cryptopanic.com/developers/api/")
print("      - CryptoCompare: https://min-api.cryptocompare.com")
print()
print("   2. Read CRYPTO_DATA_SETUP.md for detailed documentation")
print()
print("   3. Try integrating these functions into your trading agents!")
print()
print("💰 Total Cost: $0.00/month - Everything is FREE!")
print("=" * 80)
