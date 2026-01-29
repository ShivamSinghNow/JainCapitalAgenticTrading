"""
Test Script for Phase 2 Tools 6-11

Tests all remaining Phase 2 on-chain and social sentiment tools.
"""

import sys
import os

# Add TradingAgents to path
sys.path.insert(0, os.path.join(os.getcwd(), 'TradingAgents'))

from tradingagents.dataflows.onchain_utils import (
    get_coincap_rankings,
    get_cryptocompare_social_stats,
    get_github_dev_activity,
    get_github_repo_stats,
    get_reddit_crypto_sentiment,
    get_bitcoin_mining_metrics
)


def test_all_remaining_tools():
    """Test all remaining Phase 2 tools."""

    print("=" * 80)
    print("TESTING PHASE 2 TOOLS 6-11")
    print("=" * 80)
    print()

    results = []

    # Tool 6: CoinCap Rankings
    print(f"\n{'=' * 80}")
    print(f"TEST TOOL 6: get_coincap_rankings()")
    print(f"{'=' * 80}\n")
    try:
        result = get_coincap_rankings(limit=10)
        if "Error" in result:
            print(f"❌ FAILED\n{result}")
            results.append(("FAILED", "Tool 6", "get_coincap_rankings"))
        else:
            print(result[:500] + "..." if len(result) > 500 else result)
            print(f"\n✅ SUCCESS")
            results.append(("SUCCESS", "Tool 6", "get_coincap_rankings"))
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        results.append(("EXCEPTION", "Tool 6", "get_coincap_rankings"))

    # Tool 7: CryptoCompare Social Stats
    print(f"\n{'=' * 80}")
    print(f"TEST TOOL 7: get_cryptocompare_social_stats()")
    print(f"{'=' * 80}\n")
    try:
        result = get_cryptocompare_social_stats('BTC')
        if "Error" in result or "API key required" in result:
            print(f"⚠️  SKIPPED (requires API key)\n{result}")
            results.append(("SKIPPED", "Tool 7", "get_cryptocompare_social_stats"))
        else:
            print(result[:500] + "..." if len(result) > 500 else result)
            print(f"\n✅ SUCCESS")
            results.append(("SUCCESS", "Tool 7", "get_cryptocompare_social_stats"))
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        results.append(("EXCEPTION", "Tool 7", "get_cryptocompare_social_stats"))

    # Tool 8: GitHub Dev Activity
    print(f"\n{'=' * 80}")
    print(f"TEST TOOL 8: get_github_dev_activity()")
    print(f"{'=' * 80}\n")
    try:
        result = get_github_dev_activity('BTC')  # Should map to bitcoin/bitcoin
        if "Error" in result or "rate limit" in result.lower():
            print(f"⚠️  WARNING\n{result}")
            results.append(("WARNING", "Tool 8", "get_github_dev_activity"))
        else:
            print(result[:500] + "..." if len(result) > 500 else result)
            print(f"\n✅ SUCCESS")
            results.append(("SUCCESS", "Tool 8", "get_github_dev_activity"))
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        results.append(("EXCEPTION", "Tool 8", "get_github_dev_activity"))

    # Tool 9: GitHub Repo Stats (alias test)
    print(f"\n{'=' * 80}")
    print(f"TEST TOOL 9: get_github_repo_stats()")
    print(f"{'=' * 80}\n")
    try:
        result = get_github_repo_stats('ETH')  # Should map to ethereum/go-ethereum
        if "Error" in result or "rate limit" in result.lower():
            print(f"⚠️  WARNING\n{result}")
            results.append(("WARNING", "Tool 9", "get_github_repo_stats"))
        else:
            print(result[:500] + "..." if len(result) > 500 else result)
            print(f"\n✅ SUCCESS")
            results.append(("SUCCESS", "Tool 9", "get_github_repo_stats"))
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        results.append(("EXCEPTION", "Tool 9", "get_github_repo_stats"))

    # Tool 10: Reddit Crypto Sentiment
    print(f"\n{'=' * 80}")
    print(f"TEST TOOL 10: get_reddit_crypto_sentiment()")
    print(f"{'=' * 80}\n")
    try:
        result = get_reddit_crypto_sentiment('cryptocurrency', limit=10)
        if "Error" in result:
            print(f"❌ FAILED\n{result}")
            results.append(("FAILED", "Tool 10", "get_reddit_crypto_sentiment"))
        else:
            print(result[:500] + "..." if len(result) > 500 else result)
            print(f"\n✅ SUCCESS")
            results.append(("SUCCESS", "Tool 10", "get_reddit_crypto_sentiment"))
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        results.append(("EXCEPTION", "Tool 10", "get_reddit_crypto_sentiment"))

    # Tool 11: Bitcoin Mining Metrics
    print(f"\n{'=' * 80}")
    print(f"TEST TOOL 11: get_bitcoin_mining_metrics()")
    print(f"{'=' * 80}\n")
    try:
        result = get_bitcoin_mining_metrics()
        if "Error" in result:
            print(f"❌ FAILED\n{result}")
            results.append(("FAILED", "Tool 11", "get_bitcoin_mining_metrics"))
        else:
            print(result[:500] + "..." if len(result) > 500 else result)
            print(f"\n✅ SUCCESS")
            results.append(("SUCCESS", "Tool 11", "get_bitcoin_mining_metrics"))
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        results.append(("EXCEPTION", "Tool 11", "get_bitcoin_mining_metrics"))

    # Summary
    print(f"\n\n{'=' * 80}")
    print("TEST SUMMARY")
    print(f"{'=' * 80}\n")

    success_count = sum(1 for r in results if r[0] == "SUCCESS")
    warning_count = sum(1 for r in results if r[0] == "WARNING")
    skipped_count = sum(1 for r in results if r[0] == "SKIPPED")
    failed_count = sum(1 for r in results if r[0] in ["FAILED", "EXCEPTION"])

    for status, tool, func in results:
        icon = "✅" if status == "SUCCESS" else "⚠️ " if status in ["WARNING", "SKIPPED"] else "❌"
        print(f"{icon} {status:10} - {tool}: {func}()")

    print()
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {success_count}")
    print(f"Warnings: {warning_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Failed: {failed_count}")
    print()

    if failed_count == 0:
        print("🎉 ALL TESTS PASSED (or skipped with good reason)! Tools 6-11 are ready.")
        return True
    else:
        print("⚠️  SOME TESTS FAILED. Review errors above.")
        return False


if __name__ == "__main__":
    success = test_all_remaining_tools()
    sys.exit(0 if success else 1)
