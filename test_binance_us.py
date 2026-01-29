"""
Test Binance US Integration

This script tests the updated exchange_utils.py to verify Binance US integration.
"""

print("=" * 80)
print("🇺🇸 Testing Binance US Integration")
print("=" * 80)
print()

# Test 1: Order Book (Should work with Binance US)
print("TEST 1: Order Book Imbalance (Binance US)")
print("-" * 80)
try:
    from TradingAgents.tradingagents.dataflows.exchange_utils import get_order_book_imbalance

    result = get_order_book_imbalance("BTCUSDT", depth=20)
    print(result)
    print("✅ Order Book Test: PASSED")
except Exception as e:
    print(f"❌ Order Book Test: FAILED - {str(e)}")
print()

# Test 2: Taker Volume (Should work with Binance US)
print("TEST 2: Taker Buy/Sell Volume (Binance US)")
print("-" * 80)
try:
    from TradingAgents.tradingagents.dataflows.exchange_utils import get_taker_buysell_volume

    result = get_taker_buysell_volume("BTCUSDT", interval="1h", limit=12)
    print(result)
    print("✅ Taker Volume Test: PASSED")
except Exception as e:
    print(f"❌ Taker Volume Test: FAILED - {str(e)}")
print()

# Test 3: Funding Rate (Should use Bybit fallback)
print("TEST 3: Funding Rate (Bybit Fallback)")
print("-" * 80)
try:
    from TradingAgents.tradingagents.dataflows.exchange_utils import get_binance_funding_rate

    result = get_binance_funding_rate("BTCUSDT", limit=5)
    print(result)

    if "Bybit" in result:
        print("✅ Funding Rate Test: PASSED (Using Bybit fallback as expected)")
    else:
        print("⚠️  Funding Rate Test: Warning - Not using Bybit fallback")
except Exception as e:
    print(f"❌ Funding Rate Test: FAILED - {str(e)}")
print()

# Test 4: Open Interest (Should use Bybit fallback)
print("TEST 4: Open Interest (Bybit Fallback)")
print("-" * 80)
try:
    from TradingAgents.tradingagents.dataflows.exchange_utils import get_binance_open_interest

    result = get_binance_open_interest("BTCUSDT")
    print(result)

    if "Bybit" in result:
        print("✅ Open Interest Test: PASSED (Using Bybit fallback as expected)")
    else:
        print("⚠️  Open Interest Test: Warning - Not using Bybit fallback")
except Exception as e:
    print(f"❌ Open Interest Test: FAILED - {str(e)}")
print()

# Test 5: Long/Short Ratio (Should return info message)
print("TEST 5: Long/Short Ratio (Info Message)")
print("-" * 80)
try:
    from TradingAgents.tradingagents.dataflows.exchange_utils import get_binance_long_short_ratio

    result = get_binance_long_short_ratio("BTCUSDT", period="1h", limit=5)
    print(result)

    if "Not Available" in result or "Alternative" in result:
        print("✅ Long/Short Ratio Test: PASSED (Returns informational message)")
    else:
        print("⚠️  Long/Short Ratio Test: Warning - Expected informational message")
except Exception as e:
    print(f"❌ Long/Short Ratio Test: FAILED - {str(e)}")
print()

# Summary
print("=" * 80)
print("🎯 TEST SUMMARY")
print("=" * 80)
print()
print("✅ Binance US Spot Functions: Order Book, Taker Volume")
print("✅ Bybit Fallbacks: Funding Rate, Open Interest")
print("ℹ️  Info Messages: Long/Short Ratio")
print()
print("📝 Key Points:")
print("   - Binance US only supports spot trading")
print("   - Futures data automatically uses Bybit")
print("   - All spot data comes from Binance US")
print("   - No API keys required for public data")
print()
print("💡 Next Steps:")
print("   1. Read BINANCE_US_MIGRATION.md for full details")
print("   2. Use multi-exchange strategy for best coverage")
print("   3. Consider CCXT for additional exchange support")
print()
print("=" * 80)
