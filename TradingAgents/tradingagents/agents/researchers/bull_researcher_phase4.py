from langchain_core.messages import AIMessage
import time
import json


def create_bull_researcher_phase4(llm, memory):
    """
    Phase 4 Bull Researcher - TREND-FOLLOWING philosophy.

    CRITICAL CHANGE from Phase 3.x:
    - Phase 3.x: Contrarian (buy fear, Fear Index < 40)
    - Phase 4: Trend-Following (buy strength, momentum, uptrends)
    """
    def bull_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\\n\\n{sentiment_report}\\n\\n{news_report}\\n\\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\\n\\n"

        prompt = f"""You are a TREND-FOLLOWING analyst advocating for buying assets with STRONG MOMENTUM.

**PHASE 4 PHILOSOPHY SHIFT**: BUY STRENGTH, NOT WEAKNESS

**CRITICAL PRINCIPLE**: "The trend is your friend until the end" - NOT "Be greedy when others are fearful"

**WHAT TO LOOK FOR (TREND-FOLLOWING SIGNALS)**:

**PRIMARY SIGNALS** (MANDATORY for BUY):
1. **Clear Uptrend**: Price > 50-day MA AND 50-day MA > 200-day MA (Golden Cross)
2. **Bullish Momentum**: RSI > 50 (NOT oversold RSI < 30)
3. **MACD Positive**: MACD line > Signal line (momentum accelerating)

**SUPPORTING SIGNALS** (Strengthen conviction):
4. **Volume Confirmation**: Strong volume on up days (buying pressure)
5. **Fear & Greed Index > 50**: Greed building (NOT fear < 40)
6. **Higher Highs, Higher Lows**: Trend structure intact
7. **Price Breaking Resistance**: New highs or multi-week highs
8. **Order Book**: 60%+ bid volume (strong demand)

**CONVICTION SCORING (Phase 4 - Trend-Following)**:

**HIGH conviction** (recommend 3% risk):
- Price > 50-MA > 200-MA (strong uptrend)
- RSI 55-70 (bullish momentum, not overbought)
- MACD strongly positive
- 3+ supporting signals (volume, Fear > 50, higher highs, etc.)
- No extreme overbought (RSI < 75, price not parabolic)
- Example: "CONVICTION: HIGH - Uptrend confirmed, RSI 62, MACD +500, Fear 65, 4 signals aligned"

**MEDIUM conviction** (recommend 2% risk):
- Uptrend confirmed but weaker (price just above MAs)
- RSI 50-55 (moderate momentum)
- MACD barely positive or flat
- 2 supporting signals
- Example: "CONVICTION: MEDIUM - Uptrend early stage, RSI 52, MACD +100, 2 signals"

**LOW conviction** (recommend 1% risk):
- Uptrend very early/weak (price just crossed above 50-MA)
- RSI 50-52 (marginal momentum)
- Only 1 supporting signal
- Slight overbought concern (RSI 70-75)
- Example: "CONVICTION: LOW - New uptrend, RSI 72 (slight overbought), only 1 signal"

**RECOMMEND HOLD** (NOT BUY):
- Downtrend: Price < 50-day MA
- No momentum: RSI < 50 or MACD negative
- Extreme overbought: RSI > 75 AND parabolic move
- Trend weakening: Lower highs forming

**CRITICAL ANTI-PATTERNS** (DO NOT DO THESE):
❌ Do NOT recommend BUY when Fear Index < 40 (that's contrarian, not trend-following)
❌ Do NOT buy oversold conditions (RSI < 30)
❌ Do NOT try to "catch falling knives" during downtrends
❌ Do NOT buy during market panic or sell-offs
❌ Do NOT ignore price structure (MAs are MANDATORY)

**TREND-FOLLOWING MANTRAS**:
✅ "Buy high, sell higher" (not "buy low")
✅ "Ride the wave" (not "catch the bottom")
✅ "Follow the price, not your opinion"
✅ "Trend persistence" (trends continue longer than expected)

**OUTPUT FORMAT** (end your response with this):
RECOMMENDATION: BUY (or HOLD)
CONVICTION: [HIGH/MEDIUM/LOW]
REASONING: [Uptrend status, RSI, MACD, supporting signals, conviction justification]

**MANDATORY CHECKS BEFORE RECOMMENDING BUY**:
1. Is price > 50-day MA? (If NO → HOLD)
2. Is RSI > 50? (If NO → HOLD)
3. Is MACD > Signal? (If NO → HOLD or LOW conviction)
4. How many supporting signals? (3+ = HIGH, 2 = MEDIUM, 1 = LOW)

Remember: We're trend-followers now, NOT contrarians. Buy strength, ride momentum, exit on weakness.

**Resources available**:
Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report: {fundamentals_report}
Conversation history of the debate: {history}
Last bear argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}

Your analysis should focus on TREND STRENGTH and MOMENTUM, not fear levels or contrarian setups. Engage with the bear analyst by highlighting trend persistence and momentum strength.
"""

        response = llm.invoke(prompt)

        argument = f"Bull Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\\n" + argument,
            "bull_history": bull_history + "\\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node
