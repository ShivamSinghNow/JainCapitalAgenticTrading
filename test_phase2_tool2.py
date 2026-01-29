"""
Test Script for Phase 2 Tool 2: get_coingecko_developer_activity()

This script tests the CoinGecko developer activity function with multiple coins.
"""

import sys
import os

# Add TradingAgents to path
sys.path.insert(0, os.path.join(os.getcwd(), 'TradingAgents'))

from tradingagents.dataflows.onchain_utils import get_coingecko_developer_activity


def test_developer_activity():
    """Test developer activity metrics for multiple coins."""

    print("=" * 80)
    print("TESTING PHASE 2 TOOL 2: get_coingecko_developer_activity()")
    print("=" * 80)
    print()

    test_cases = [
        ("bitcoin", "Bitcoin with coin ID 'bitcoin'"),
        ("ETH-USD", "Ethereum with ticker 'ETH-USD'"),
        ("SOLUSDT", "Solana with ticker 'SOLUSDT'"),
    ]

    results = []

    for coin_id, description in test_cases:
        print(f"\n{'=' * 80}")
        print(f"TEST: {description}")
        print(f"{'=' * 80}\n")

        try:
            result = get_coingecko_developer_activity(coin_id)

            # Check if result is valid
            if "No developer data available" in result:
                print(f"⚠️  WARNING - {description}: No developer data available")
                results.append(("WARNING", coin_id, description))
            elif "Error" in result or "not found" in result:
                print(f"❌ FAILED - {description}")
                print(f"   Error: {result}")
                results.append(("FAILED", coin_id, description))
            else:
                print(result)
                print(f"\n✅ SUCCESS - {description}")
                results.append(("SUCCESS", coin_id, description))

        except Exception as e:
            print(f"❌ EXCEPTION - {description}")
            print(f"   Error: {str(e)}")
            results.append(("EXCEPTION", coin_id, description))

    # Summary
    print(f"\n\n{'=' * 80}")
    print("TEST SUMMARY")
    print(f"{'=' * 80}\n")

    success_count = sum(1 for r in results if r[0] == "SUCCESS")
    warning_count = sum(1 for r in results if r[0] == "WARNING")
    failed_count = sum(1 for r in results if r[0] in ["FAILED", "EXCEPTION"])

    for status, coin_id, description in results:
        icon = "✅" if status == "SUCCESS" else "⚠️ " if status == "WARNING" else "❌"
        print(f"{icon} {status:10} - {description}")

    print()
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {success_count}")
    print(f"Warnings: {warning_count}")
    print(f"Failed: {failed_count}")
    print()

    if failed_count == 0:
        print("🎉 ALL TESTS PASSED! Tool 2 is ready.")
        return True
    else:
        print("⚠️  SOME TESTS FAILED. Review errors above.")
        return False


if __name__ == "__main__":
    success = test_developer_activity()
    sys.exit(0 if success else 1)
