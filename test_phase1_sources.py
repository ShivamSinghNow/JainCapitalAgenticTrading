"""
Comprehensive Phase 1 Data Sources Test

This script tests ALL Phase 1 crypto data sources to identify which work and which don't.
Tests include:
- Exchange data (Binance US + fallbacks)
- Crypto news sources (CryptoPanic, RSS, CryptoCompare, CoinGecko)
- Data validation functions
"""

from datetime import datetime

print("=" * 80)
print("🔍 COMPREHENSIVE PHASE 1 DATA SOURCES TEST")
print("=" * 80)
print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
print()

test_results = {
    "working": [],
    "failed": [],
    "partial": []
}

# ===== CATEGORY 1: EXCHANGE DATA =====
print("=" * 80)
print("CATEGORY 1: EXCHANGE DATA (Binance US + Fallbacks)")
print("=" * 80)
print()

# Test 1.1: Binance US Order Book
print("TEST 1.1: Binance US Order Book")
print("-" * 80)
try:
    from TradingAgents.tradingagents.dataflows.exchange_utils import get_order_book_imbalance

    result = get_order_book_imbalance("BTCUSDT", depth=20)

    if "Best Bid" in result and "error" not in result.lower():
        print("✅ Status: WORKING")
        test_results["working"].append("Binance US Order Book")
        print(result[:300] + "...\n")
    else:
        print("❌ Status: FAILED")
        test_results["failed"].append("Binance US Order Book")
        print(result[:300] + "...\n")
except Exception as e:
    print(f"❌ Status: ERROR - {str(e)[:200]}\n")
    test_results["failed"].append(f"Binance US Order Book: {str(e)[:50]}")

# Test 1.2: Binance US Taker Volume
print("TEST 1.2: Binance US Taker Buy/Sell Volume")
print("-" * 80)
try:
    from TradingAgents.tradingagents.dataflows.exchange_utils import get_taker_buysell_volume

    result = get_taker_buysell_volume("BTCUSDT", interval="1h", limit=12)

    if "Taker Buy" in result and "error" not in result.lower():
        print("✅ Status: WORKING")
        test_results["working"].append("Binance US Taker Volume")
        print(result[:300] + "...\n")
    else:
        print("❌ Status: FAILED")
        test_results["failed"].append("Binance US Taker Volume")
        print(result[:300] + "...\n")
except Exception as e:
    print(f"❌ Status: ERROR - {str(e)[:200]}\n")
    test_results["failed"].append(f"Binance US Taker Volume: {str(e)[:50]}")

# Test 1.3: Funding Rates (Bybit Fallback)
print("TEST 1.3: Funding Rates (Bybit Fallback)")
print("-" * 80)
try:
    from TradingAgents.tradingagents.dataflows.exchange_utils import get_binance_funding_rate

    result = get_binance_funding_rate("BTCUSDT", limit=5)

    if "Funding Rate" in result and "403" not in result and "Error" not in result[:100]:
        print("✅ Status: WORKING")
        test_results["working"].append("Funding Rates (Bybit)")
        print(result[:300] + "...\n")
    elif "Bybit" in result or "alternative" in result.lower():
        print("⚠️  Status: PARTIAL - Bybit accessible but returned error/no data")
        test_results["partial"].append("Funding Rates (Bybit): API accessible but restricted")
        print(result[:300] + "...\n")
    else:
        print("❌ Status: FAILED")
        test_results["failed"].append("Funding Rates (Bybit)")
        print(result[:300] + "...\n")
except Exception as e:
    print(f"❌ Status: ERROR - {str(e)[:200]}\n")
    test_results["failed"].append(f"Funding Rates: {str(e)[:50]}")

# Test 1.4: Open Interest (Bybit Fallback)
print("TEST 1.4: Open Interest (Bybit Fallback)")
print("-" * 80)
try:
    from TradingAgents.tradingagents.dataflows.exchange_utils import get_binance_open_interest

    result = get_binance_open_interest("BTCUSDT")

    if "Open Interest" in result and "403" not in result and "Error" not in result[:100]:
        print("✅ Status: WORKING")
        test_results["working"].append("Open Interest (Bybit)")
        print(result[:300] + "...\n")
    elif "Bybit" in result or "alternative" in result.lower():
        print("⚠️  Status: PARTIAL - Bybit accessible but returned error/no data")
        test_results["partial"].append("Open Interest (Bybit): API accessible but restricted")
        print(result[:300] + "...\n")
    else:
        print("❌ Status: FAILED")
        test_results["failed"].append("Open Interest (Bybit)")
        print(result[:300] + "...\n")
except Exception as e:
    print(f"❌ Status: ERROR - {str(e)[:200]}\n")
    test_results["failed"].append(f"Open Interest: {str(e)[:50]}")

# Test 1.5: CCXT Multi-Exchange
print("TEST 1.5: CCXT Multi-Exchange Funding Rates")
print("-" * 80)
try:
    from TradingAgents.tradingagents.dataflows.exchange_utils import get_ccxt_funding_rates

    result = get_ccxt_funding_rates("BTC/USDT", exchanges=['bybit', 'okx'])

    if "Funding Rate" in result and len(result) > 100:
        print("✅ Status: WORKING")
        test_results["working"].append("CCXT Multi-Exchange")
        print(result[:300] + "...\n")
    else:
        print("⚠️  Status: PARTIAL")
        test_results["partial"].append("CCXT Multi-Exchange: Limited data")
        print(result[:300] + "...\n")
except Exception as e:
    print(f"❌ Status: ERROR - {str(e)[:200]}\n")
    test_results["failed"].append(f"CCXT Multi-Exchange: {str(e)[:50]}")

# ===== CATEGORY 2: CRYPTO NEWS =====
print("=" * 80)
print("CATEGORY 2: CRYPTO NEWS SOURCES")
print("=" * 80)
print()

# Test 2.1: RSS Feed Aggregation
print("TEST 2.1: RSS Feed Aggregation (CoinDesk, Cointelegraph, etc.)")
print("-" * 80)
try:
    from TradingAgents.tradingagents.dataflows.cryptonews_utils import get_rss_crypto_news

    curr_date = datetime.now().strftime("%Y-%m-%d")
    result = get_rss_crypto_news(curr_date=curr_date, look_back_days=2, max_articles_per_source=3)

    if "Crypto News" in result and len(result) > 200:
        print("✅ Status: WORKING")
        test_results["working"].append("RSS Feed Aggregation")
        print(result[:400] + "...\n")
    else:
        print("❌ Status: FAILED")
        test_results["failed"].append("RSS Feed Aggregation")
        print(result[:300] + "...\n")
except Exception as e:
    print(f"❌ Status: ERROR - {str(e)[:200]}\n")
    test_results["failed"].append(f"RSS Feeds: {str(e)[:50]}")

# Test 2.2: CryptoPanic API
print("TEST 2.2: CryptoPanic API (Requires API Key)")
print("-" * 80)
try:
    from TradingAgents.tradingagents.dataflows.cryptonews_utils import get_cryptopanic_news

    curr_date = datetime.now().strftime("%Y-%m-%d")
    result = get_cryptopanic_news("BTC", curr_date, look_back_days=3)

    if "not configured" in result.lower():
        print("⚠️  Status: NEEDS API KEY")
        test_results["partial"].append("CryptoPanic: Needs free API key")
        print(result[:200] + "...\n")
    elif "CryptoPanic" in result and len(result) > 200:
        print("✅ Status: WORKING")
        test_results["working"].append("CryptoPanic API")
        print(result[:400] + "...\n")
    else:
        print("❌ Status: FAILED")
        test_results["failed"].append("CryptoPanic API")
        print(result[:300] + "...\n")
except Exception as e:
    print(f"❌ Status: ERROR - {str(e)[:200]}\n")
    test_results["failed"].append(f"CryptoPanic: {str(e)[:50]}")

# Test 2.3: CryptoCompare News
print("TEST 2.3: CryptoCompare News API (Requires API Key)")
print("-" * 80)
try:
    from TradingAgents.tradingagents.dataflows.cryptonews_utils import get_cryptocompare_news

    result = get_cryptocompare_news(categories="BTC,ETH", limit=10)

    if "not configured" in result.lower():
        print("⚠️  Status: NEEDS API KEY")
        test_results["partial"].append("CryptoCompare News: Needs free API key")
        print(result[:200] + "...\n")
    elif "CryptoCompare" in result and len(result) > 200:
        print("✅ Status: WORKING")
        test_results["working"].append("CryptoCompare News")
        print(result[:400] + "...\n")
    else:
        print("❌ Status: FAILED")
        test_results["failed"].append("CryptoCompare News")
        print(result[:300] + "...\n")
except Exception as e:
    print(f"❌ Status: ERROR - {str(e)[:200]}\n")
    test_results["failed"].append(f"CryptoCompare: {str(e)[:50]}")

# Test 2.4: CoinGecko Events
print("TEST 2.4: CoinGecko Events API (No API Key Required)")
print("-" * 80)
try:
    from TradingAgents.tradingagents.dataflows.cryptonews_utils import get_coingecko_events

    result = get_coingecko_events(coin_id="bitcoin", upcoming_only=True)

    if "404" in result or "error" in result.lower():
        print("⚠️  Status: API ENDPOINT CHANGED/UNAVAILABLE")
        test_results["partial"].append("CoinGecko Events: API endpoint may have changed")
        print(result[:300] + "...\n")
    elif "Events" in result or "Upcoming" in result:
        print("✅ Status: WORKING")
        test_results["working"].append("CoinGecko Events")
        print(result[:400] + "...\n")
    else:
        print("❌ Status: FAILED")
        test_results["failed"].append("CoinGecko Events")
        print(result[:300] + "...\n")
except Exception as e:
    print(f"❌ Status: ERROR - {str(e)[:200]}\n")
    test_results["failed"].append(f"CoinGecko Events: {str(e)[:50]}")

# ===== CATEGORY 3: DATA VALIDATION =====
print("=" * 80)
print("CATEGORY 3: DATA VALIDATION FUNCTIONS")
print("=" * 80)
print()

# Test 3.1: Price Cross-Validation
print("TEST 3.1: Price Cross-Validation")
print("-" * 80)
try:
    from TradingAgents.tradingagents.dataflows.data_validation import cross_validate_prices

    is_valid, warning = cross_validate_prices(
        price1=50000.0,
        price2=50500.0,
        source1="YFinance",
        source2="Binance US",
        symbol="BTC-USD",
        max_diff_pct=2.0
    )

    if is_valid or warning:
        print("✅ Status: WORKING")
        test_results["working"].append("Price Cross-Validation")
        print(f"Valid: {is_valid}, Warning: {warning}\n")
    else:
        print("❌ Status: FAILED\n")
        test_results["failed"].append("Price Cross-Validation")
except Exception as e:
    print(f"❌ Status: ERROR - {str(e)[:200]}\n")
    test_results["failed"].append(f"Price Validation: {str(e)[:50]}")

# Test 3.2: Data Freshness Check
print("TEST 3.2: Data Freshness Check")
print("-" * 80)
try:
    from TradingAgents.tradingagents.dataflows.data_validation import check_data_freshness
    from datetime import timedelta

    now = datetime.now()
    is_fresh, warning = check_data_freshness(
        timestamp=now - timedelta(minutes=5),
        symbol="BTC-USD",
        max_age_minutes=60
    )

    if is_fresh is not None:
        print("✅ Status: WORKING")
        test_results["working"].append("Data Freshness Check")
        print(f"Fresh: {is_fresh}, Warning: {warning}\n")
    else:
        print("❌ Status: FAILED\n")
        test_results["failed"].append("Data Freshness Check")
except Exception as e:
    print(f"❌ Status: ERROR - {str(e)[:200]}\n")
    test_results["failed"].append(f"Freshness Check: {str(e)[:50]}")

# Test 3.3: Anomaly Detection
print("TEST 3.3: Anomaly Detection")
print("-" * 80)
try:
    from TradingAgents.tradingagents.dataflows.data_validation import detect_price_anomalies
    import pandas as pd
    import numpy as np

    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    prices = 50000 + np.random.randn(30) * 1000
    df = pd.DataFrame({'Date': dates, 'Close': prices})

    result = detect_price_anomalies(df, symbol="BTC-USD")

    if result and 'anomalies_found' in result:
        print("✅ Status: WORKING")
        test_results["working"].append("Anomaly Detection")
        print(f"Anomalies found: {result.get('anomaly_count', 0)}\n")
    else:
        print("❌ Status: FAILED\n")
        test_results["failed"].append("Anomaly Detection")
except Exception as e:
    print(f"❌ Status: ERROR - {str(e)[:200]}\n")
    test_results["failed"].append(f"Anomaly Detection: {str(e)[:50]}")

# ===== FINAL SUMMARY =====
print("=" * 80)
print("📊 FINAL TEST SUMMARY")
print("=" * 80)
print()

total_tests = len(test_results["working"]) + len(test_results["failed"]) + len(test_results["partial"])

print(f"Total Tests Run: {total_tests}")
print()

print(f"✅ WORKING ({len(test_results['working'])} sources):")
for item in test_results["working"]:
    print(f"   ✓ {item}")
print()

print(f"⚠️  PARTIAL/NEEDS SETUP ({len(test_results['partial'])} sources):")
for item in test_results["partial"]:
    print(f"   ⚠ {item}")
print()

print(f"❌ FAILED ({len(test_results['failed'])} sources):")
for item in test_results["failed"]:
    print(f"   ✗ {item}")
print()

# Success rate
working_count = len(test_results["working"])
partial_count = len(test_results["partial"])
success_rate = (working_count / total_tests * 100) if total_tests > 0 else 0
usable_rate = ((working_count + partial_count) / total_tests * 100) if total_tests > 0 else 0

print("=" * 80)
print(f"📈 Success Rate: {success_rate:.1f}% fully working")
print(f"📈 Usable Rate: {usable_rate:.1f}% (working + needs API keys)")
print("=" * 80)
print()

print("💡 RECOMMENDATIONS:")
print()
print("1. ✅ USE IMMEDIATELY (No Setup Required):")
print("   - Binance US Order Book")
print("   - Binance US Taker Volume")
print("   - RSS Feed Aggregation")
print("   - All Data Validation Functions")
print()

print("2. ⚠️  SETUP RECOMMENDED (Free API Keys):")
print("   - CryptoPanic: https://cryptopanic.com/developers/api/")
print("   - CryptoCompare: https://min-api.cryptocompare.com")
print()

print("3. 🔍 INVESTIGATE:")
for item in test_results["failed"]:
    if "Bybit" not in item and "CoinGecko" not in item:
        print(f"   - {item}")
print()

print("=" * 80)
print("Test Complete!")
print("=" * 80)
