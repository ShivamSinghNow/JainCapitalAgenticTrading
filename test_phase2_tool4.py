"""
Test Script for Phase 2 Tool 4: get_bitcoin_network_metrics()

This script tests the Blockchain.info Bitcoin network metrics function.
"""

import sys
import os

# Add TradingAgents to path
sys.path.insert(0, os.path.join(os.getcwd(), 'TradingAgents'))

from tradingagents.dataflows.onchain_utils import get_bitcoin_network_metrics


def test_bitcoin_network():
    """Test Bitcoin network metrics."""

    print("=" * 80)
    print("TESTING PHASE 2 TOOL 4: get_bitcoin_network_metrics()")
    print("=" * 80)
    print()

    print(f"\n{'=' * 80}")
    print(f"TEST: Bitcoin Network Metrics from Blockchain.info")
    print(f"{'=' * 80}\n")

    try:
        result = get_bitcoin_network_metrics()

        # Check if result is valid
        if "Error" in result:
            print(f"❌ FAILED - Bitcoin network metrics")
            print(f"   Error: {result}")
            success = False
        else:
            print(result)
            print(f"\n✅ SUCCESS - Bitcoin network metrics")
            success = True

    except Exception as e:
        print(f"❌ EXCEPTION - Bitcoin network metrics")
        print(f"   Error: {str(e)}")
        success = False

    # Summary
    print(f"\n\n{'=' * 80}")
    print("TEST SUMMARY")
    print(f"{'=' * 80}\n")

    if success:
        print("✅ SUCCESS - Bitcoin network metrics")
        print()
        print("🎉 TEST PASSED! Tool 4 is ready.")
        return True
    else:
        print("❌ FAILED - Bitcoin network metrics")
        print()
        print("⚠️  TEST FAILED. Review errors above.")
        return False


if __name__ == "__main__":
    success = test_bitcoin_network()
    sys.exit(0 if success else 1)
