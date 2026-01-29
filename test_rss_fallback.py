"""
Test RSS Fallback for CryptoPanic News

This script tests the automatic RSS fallback mechanism when CryptoPanic API is blocked.
"""

from datetime import datetime

print("=" * 80)
print("🧪 Testing CryptoPanic with RSS Fallback")
print("=" * 80)
print()

# Test the CryptoPanic function (which now uses RSS fallback)
print("TEST: CryptoPanic News with Automatic RSS Fallback")
print("-" * 80)

try:
    from TradingAgents.tradingagents.dataflows.cryptonews_utils import get_cryptopanic_news

    curr_date = datetime.now().strftime("%Y-%m-%d")
    result = get_cryptopanic_news("BTC", curr_date, look_back_days=7)

    # Check if RSS fallback was used
    if "RSS" in result or "CoinDesk" in result or "Cointelegraph" in result:
        print("✅ Status: WORKING (Using RSS Fallback)")
        print()
        print("Sample Output (first 600 chars):")
        print(result[:600] + "...\n")
        print("✅ RSS fallback mechanism working correctly!")
    elif "CryptoPanic" in result and "404" not in result and "Error" not in result[:100]:
        print("✅ Status: WORKING (CryptoPanic API)")
        print()
        print("Sample Output (first 600 chars):")
        print(result[:600] + "...\n")
        print("✅ CryptoPanic API working!")
    else:
        print("⚠️  Status: UNEXPECTED RESPONSE")
        print(result[:400])

except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print()
print("=" * 80)
print("Test Complete!")
print("=" * 80)
print()
print("💡 RECOMMENDATION:")
print("   The get_cryptopanic_news() function now automatically uses RSS feeds")
print("   when the CryptoPanic API is blocked by Cloudflare. No action needed!")
print()
