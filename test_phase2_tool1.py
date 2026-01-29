"""
Test Phase 2 - Tool 1: CoinGecko Market Metrics
"""

from TradingAgents.tradingagents.dataflows.onchain_utils import get_coingecko_market_metrics

print("=" * 80)
print("🧪 Testing Phase 2 - Tool 1: CoinGecko Market Metrics")
print("=" * 80)
print()

# Test 1: Bitcoin with coin ID
print("TEST 1: Bitcoin (using coin ID 'bitcoin')")
print("-" * 80)
result = get_coingecko_market_metrics("bitcoin")
if "Market Cap" in result and "error" not in result.lower():
    print("✅ SUCCESS")
    print(result[:500] + "...\n")
else:
    print("❌ FAILED")
    print(result[:300] + "\n")

# Test 2: Ethereum with ticker
print("TEST 2: Ethereum (using ticker 'ETH-USD')")
print("-" * 80)
result = get_coingecko_market_metrics("ETH-USD")
if "Market Cap" in result and "error" not in result.lower():
    print("✅ SUCCESS")
    print(result[:500] + "...\n")
else:
    print("❌ FAILED")
    print(result[:300] + "\n")

# Test 3: Solana with ticker
print("TEST 3: Solana (using ticker 'SOLUSDT')")
print("-" * 80)
result = get_coingecko_market_metrics("SOLUSDT")
if "Market Cap" in result and "error" not in result.lower():
    print("✅ SUCCESS")
    print(result[:500] + "...\n")
else:
    print("❌ FAILED")
    print(result[:300] + "\n")

print("=" * 80)
print("✅ Tool 1 Testing Complete!")
print("=" * 80)
