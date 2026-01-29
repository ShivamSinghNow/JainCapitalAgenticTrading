"""
Phase 4 Decision Runner - Uses Trend-Following Agent Prompts

This script replaces the contrarian agents (Phase 3.x) with trend-following agents.
"""

import os
import sys

# Add TradingAgents to path
sys.path.insert(0, "TradingAgents")

from tradingagents.agents.researchers.bull_researcher_phase4 import create_bull_researcher_phase4
from tradingagents.agents.researchers.bear_researcher_phase4 import create_bear_researcher_phase4
from tradingagents.agents.managers.research_manager_phase4 import create_investment_judge_phase4
from tradingagents.agents.managers.risk_manager_phase4 import create_risk_manager_phase4

# Use existing infrastructure
from tradingagents.workflows.multi_agent_workflow import create_workflow
from tradingagents.agents.analysts import (
    create_market_analyst,
    create_news_analyst,
    create_fundamentals_analyst,
    create_social_media_analyst,
)
from langchain_anthropic import ChatAnthropic
from tradingagents.workflows.memory import create_memory
import json


def decide(company_ticker: str, decision_date: str, online_mode: bool = True):
    """
    Run Phase 4 trend-following decision system.

    Args:
        company_ticker: Asset ticker (e.g., 'BTC-USD')
        decision_date: Date for decision (YYYY-MM-DD)
        online_mode: Whether to fetch live data

    Returns:
        dict with 'action' and 'conviction'
    """

    # Initialize LLM
    llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.7)

    # Create memory
    memory = create_memory()

    # Create Phase 4 agents (trend-following)
    print("   Initializing Phase 4 Trend-Following Agents...")
    bull_researcher = create_bull_researcher_phase4(llm, memory)
    bear_researcher = create_bear_researcher_phase4(llm, memory)
    investment_judge = create_investment_judge_phase4(llm, memory)
    risk_manager = create_risk_manager_phase4(llm, memory)

    # Use existing data collection analysts
    market_analyst = create_market_analyst(llm)
    news_analyst = create_news_analyst(llm)
    fundamentals_analyst = create_fundamentals_analyst(llm)
    social_media_analyst = create_social_media_analyst(llm)

    # Create workflow with Phase 4 agents
    workflow = create_workflow(
        market_analyst=market_analyst,
        news_analyst=news_analyst,
        fundamentals_analyst=fundamentals_analyst,
        social_media_analyst=social_media_analyst,
        bull_researcher=bull_researcher,
        bear_researcher=bear_researcher,
        investment_judge=investment_judge,
        risk_manager=risk_manager,
        memory=memory,
    )

    # Initial state
    initial_state = {
        "company_of_interest": company_ticker,
        "decision_date": decision_date,
        "online_mode": online_mode,
        "investment_debate_state": {
            "history": "",
            "bull_history": "",
            "bear_history": "",
            "current_response": "",
            "count": 0,
        },
        "risk_debate_state": {
            "history": "",
            "risky_history": "",
            "safe_history": "",
            "neutral_history": "",
            "latest_speaker": "",
            "current_risky_response": "",
            "current_safe_response": "",
            "current_neutral_response": "",
            "count": 0,
        },
    }

    # Run workflow
    print("   Running decision workflow...")
    final_state = workflow.invoke(initial_state)

    # Extract decision
    final_decision_text = final_state.get("final_trade_decision", "")

    # Parse decision (extract JSON from text)
    decision = {"action": "HOLD", "conviction": "none"}

    try:
        # Look for JSON pattern in text
        import re
        json_match = re.search(r'\{[^{}]*"action"[^{}]*"conviction"[^{}]*\}', final_decision_text)
        if json_match:
            decision_json = json.loads(json_match.group())
            decision["action"] = decision_json.get("action", "HOLD").upper()
            decision["conviction"] = decision_json.get("conviction", "none").lower()
        else:
            # Fallback: parse from text
            if "BUY" in final_decision_text.upper():
                decision["action"] = "BUY"
                if "high" in final_decision_text.lower():
                    decision["conviction"] = "high"
                elif "low" in final_decision_text.lower():
                    decision["conviction"] = "low"
                else:
                    decision["conviction"] = "medium"
            else:
                decision["action"] = "HOLD"
                decision["conviction"] = "none"
    except Exception as e:
        print(f"   Warning: Could not parse decision: {e}")
        print(f"   Using fallback: HOLD")

    return decision


if __name__ == "__main__":
    # Test the Phase 4 decision system
    result = decide(
        company_ticker="BTC-USD",
        decision_date="2024-11-08",
        online_mode=True
    )
    print(f"\nFinal Decision: {result}")
