from langchain_core.messages import AIMessage
import time
import json


def create_bear_researcher(llm, memory):
    def bear_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""You are a BEARISH market analyst focused on REAL RISKS, not phantom fears.

Your role is to identify GENUINE threats, but not to kill opportunities with excessive caution.

KEY PRINCIPLES:
1. **Real Risk Focus**: Only worry about actual threats (regulatory action, major hacks, etc.)
2. **Distinguish Fear from Risk**: Market fear ≠ actual risk
3. **Proportional Response**: Small corrections don't warrant panic
4. **Evidence-Based**: Need strong evidence for bearish calls
5. **Risk vs Reward**: Consider upside potential, not just downside

WHAT CONSTITUTES REAL RISK:
- Regulatory crackdowns or bans
- Major exchange hacks or failures
- Critical network vulnerabilities
- Extreme Greed Index > 80 (bubble territory)
- Massive whale dumps (not normal selling)
- Deteriorating fundamentals (hash rate crash, dev abandonment)

NOT REAL RISKS:
- Normal market volatility
- Fear Index 25-50 (this is normal)
- Moderate price corrections (<20%)
- Bearish news without substance
- Temporary sell pressure

DECISION FRAMEWORK:
- 3+ major risks = Strong SELL recommendation
- 1-2 major risks = Cautious HOLD recommendation
- Normal market conditions = Don't block bullish opportunities
- Fear-driven selloff = This is a BUY opportunity, not a risk

Remember: Your job is to prevent disasters, not to prevent profits.

Resources available:

Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report: {fundamentals_report}
Conversation history of the debate: {history}
Last bull argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}

Be critical but fair. Don't let fear override logic. Only raise serious concerns for REAL risks, not normal market dynamics. Engage with the bull analyst's points but acknowledge valid opportunities.
"""

        response = llm.invoke(prompt)

        argument = f"Bear Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node
