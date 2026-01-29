"""
Test script to verify Toolkit tools are properly accessible.
"""
import sys
sys.path.insert(0, 'TradingAgents')

from tradingagents.agents.utils.agent_utils import Toolkit

toolkit = Toolkit()

print("=" * 80)
print("TESTING TOOLKIT TOOL REGISTRATION")
print("=" * 80)
print()

# Test Market Analyst tools (online mode)
print("Market Analyst Tools (Online Mode):")
print("-" * 80)

tools_to_test = [
    'get_YFin_data_online',
    'get_stockstats_indicators_report_online',
    'get_order_book_imbalance',
    'get_taker_buysell_volume',
    'get_funding_rate',
    'get_open_interest',
    'cross_validate_prices',
    'get_fear_greed_index',
    'get_coincap_rankings',
]

for tool_name in tools_to_test:
    if hasattr(toolkit, tool_name):
        tool = getattr(toolkit, tool_name)
        # Check if it's decorated with @tool
        is_tool = hasattr(tool, 'name') and hasattr(tool, 'description')
        status = "✅ TOOL" if is_tool else "⚠️  METHOD"
        print(f"{status} - {tool_name}")
        if is_tool:
            print(f"        Name: {tool.name}")
    else:
        print(f"❌ MISSING - {tool_name}")

print()
print("=" * 80)
print("TESTING TOOL OBJECTS")
print("=" * 80)
print()

# Actually get the tool objects
tools = [
    toolkit.get_YFin_data_online,
    toolkit.get_stockstats_indicators_report_online,
    toolkit.get_order_book_imbalance,
    toolkit.get_taker_buysell_volume,
    toolkit.get_funding_rate,
    toolkit.get_open_interest,
    toolkit.cross_validate_prices,
    toolkit.get_fear_greed_index,
    toolkit.get_coincap_rankings,
]

print(f"Total tools in list: {len(tools)}")
print()

for i, tool in enumerate(tools, 1):
    print(f"{i}. {tool.name if hasattr(tool, 'name') else 'NO NAME'}")
    if hasattr(tool, 'description'):
        desc = tool.description.split('\n')[0][:60]
        print(f"   Description: {desc}...")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"All tools have 'name' attribute: {all(hasattr(t, 'name') for t in tools)}")
print(f"All tools have 'description' attribute: {all(hasattr(t, 'description') for t in tools)}")
