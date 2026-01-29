"""
Test Script for Phase 2 Tool 5: get_fear_greed_index()

This script tests the Fear & Greed Index function.
"""

import sys
import os

# Add TradingAgents to path
sys.path.insert(0, os.path.join(os.getcwd(), 'TradingAgents'))

from tradingagents.dataflows.onchain_utils import get_fear_greed_index


def test_fear_greed():
    """Test Fear & Greed Index."""

    print("=" * 80)
    print("TESTING PHASE 2 TOOL 5: get_fear_greed_index()")
    print("=" * 80)
    print()

    print(f"\n{'=' * 80}")
    print(f"TEST: Crypto Fear & Greed Index from Alternative.me")
    print(f"{'=' * 80}\n")

    try:
        result = get_fear_greed_index()

        # Check if result is valid
        if "Error" in result or "No Fear & Greed Index data available" in result:
            print(f"❌ FAILED - Fear & Greed Index")
            print(f"   Error: {result}")
            success = False
        else:
            print(result)
            print(f"\n✅ SUCCESS - Fear & Greed Index")
            success = True

    except Exception as e:
        print(f"❌ EXCEPTION - Fear & Greed Index")
        print(f"   Error: {str(e)}")
        success = False

    # Summary
    print(f"\n\n{'=' * 80}")
    print("TEST SUMMARY")
    print(f"{'=' * 80}\n")

    if success:
        print("✅ SUCCESS - Fear & Greed Index")
        print()
        print("🎉 TEST PASSED! Tool 5 is ready.")
        return True
    else:
        print("❌ FAILED - Fear & Greed Index")
        print()
        print("⚠️  TEST FAILED. Review errors above.")
        return False


if __name__ == "__main__":
    success = test_fear_greed()
    sys.exit(0 if success else 1)
