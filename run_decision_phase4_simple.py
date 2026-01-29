"""
Phase 4 Decision Runner - Simple version using existing infrastructure

Since modifying the agent graph is complex, this version uses the EXISTING agents
but the Phase 4 backtest script will apply trend-following FILTERS at the backtest level.

This is a pragmatic approach: agents still give recommendations, but backtest only
executes trades that meet trend-following criteria.
"""

from dotenv import load_dotenv
load_dotenv()

import os, json
from datetime import datetime
from TradingAgents.tradingagents.graph.trading_graph import TradingAgentsGraph
from TradingAgents.tradingagents.default_config import DEFAULT_CONFIG


def decide(company_ticker: str = "BTC-USD", decision_date: str | None = None, online_mode: bool = True):
    """
    Returns the agent team's trading decision.

    NOTE: This uses the EXISTING Phase 3.2 agents, but Phase 4 backtest will
    apply trend-following filters on top of their recommendations.

    Args:
        company_ticker: Trading symbol (renamed from symbol for compatibility)
        decision_date: Decision date (YYYY-MM-DD, renamed from date for compatibility)
        online_mode: Whether to use online data (not used here, for compatibility)

    Returns:
        dict with 'action' and 'conviction'
    """

    symbol = company_ticker
    date = decision_date

    # Start from defaults
    cfg = DEFAULT_CONFIG.copy()
    cfg.update({
        "deep_think_llm": os.getenv("AGENT_DEEP_MODEL", "gpt-4o-mini"),
        "quick_think_llm": os.getenv("AGENT_QUICK_MODEL", "gpt-4o-mini"),
        "max_debate_rounds": int(os.getenv("AGENT_MAX_DEBATE", "1")),
        "online_tools": True,
        "data_dir": os.path.join(os.getcwd(), "data"),
        "data_cache_dir": os.path.join(os.getcwd(), "data_cache"),
    })

    # Create directories
    os.makedirs(cfg["data_cache_dir"], exist_ok=True)
    os.makedirs(cfg["data_dir"], exist_ok=True)

    # Use provided date
    if date is None:
        date = "2024-12-30"

    # Build the graph (uses existing Phase 3.2 agents)
    ta = TradingAgentsGraph(debug=False, config=cfg)

    # Run decision
    try:
        report, decision = ta.propagate(symbol, date)
    except Exception as e:
        print(f"   Error during propagation: {e}")
        # Return HOLD on error
        return {"action": "HOLD", "conviction": "none"}

    # Ensure decision is a dict (sometimes it's a string)
    if isinstance(decision, str):
        # Try to parse JSON from string
        import re
        try:
            # Look for action and conviction in string
            action = "HOLD"
            conviction = "medium"

            if "BUY" in decision.upper():
                action = "BUY"
            elif "SELL" in decision.upper():
                action = "SELL"

            if "high" in decision.lower():
                conviction = "high"
            elif "low" in decision.lower():
                conviction = "low"

            decision = {"action": action, "conviction": conviction}
        except:
            decision = {"action": "HOLD", "conviction": "none"}

    # Ensure it has the required keys
    if not isinstance(decision, dict):
        decision = {"action": "HOLD", "conviction": "none"}

    if "action" not in decision:
        decision["action"] = "HOLD"
    if "conviction" not in decision:
        decision["conviction"] = "medium"

    # Return decision
    return decision


if __name__ == "__main__":
    result = decide("BTC-USD", "2024-11-08")
    print(f"\nDecision: {result}")
