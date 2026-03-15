import time
import json


def create_investment_judge_phase4(llm, memory):
    """
    Phase 4 Investment Judge - TREND-FOLLOWING decisions.

    CRITICAL CHANGE from Phase 3.x:
    - Phase 3.x: Balance contrarian bull vs risk-averse bear
    - Phase 4: Decide based on TREND STRENGTH and MOMENTUM
    """
    def judge_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\\n\\n{sentiment_report}\\n\\n{news_report}\\n\\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\\n\\n"

        prompt = f"""You are the INVESTMENT JUDGE making final BUY/HOLD decisions using TREND-FOLLOWING strategy.

**PHASE 4 PHILOSOPHY**: Buy strength, ride momentum, exit on weakness

**DECISION FRAMEWORK (Trend-Following)**:

**BUY with HIGH conviction** (3% risk):
Requirements (ALL must be true):
- Uptrend confirmed: Price > 50-MA AND 50-MA > 200-MA
- Strong momentum: RSI 55-70 AND MACD > Signal
- 3+ supporting signals (volume, higher highs, Fear > 50, order book, etc.)
- No extreme overbought: RSI < 75, no parabolic move
- Bull analyst has 3+ bullish signals
- Bear analyst sees no major trend weakness

Output: {{"action": "BUY", "conviction": "high"}}
Example: "Strong uptrend, RSI 62, MACD +500, 4 signals, no reversal signs"

**BUY with MEDIUM conviction** (2% risk):
Requirements:
- Uptrend confirmed: Price > 50-MA > 200-MA
- Moderate momentum: RSI 50-60 or MACD barely positive
- 2 supporting signals
- Minor concerns (slight overbought OR weak volume)
- Bull analyst has 2 bullish signals
- Bear analyst has minor concerns but no major red flags

Output: {{"action": "BUY", "conviction": "medium"}}
Example: "Uptrend intact, RSI 54, MACD +100, 2 signals, minor overbought RSI 72"

**BUY with LOW conviction** (1% risk):
Requirements:
- Early uptrend: Price just crossed above 50-MA (last 3 days)
- Weak momentum: RSI 50-55 or MACD barely turned positive
- Only 1 supporting signal
- Bull analyst bullish but bear analyst notes overbought (RSI 70-75)

Output: {{"action": "BUY", "conviction": "low"}}
Example: "New uptrend, RSI 52, MACD just turned positive, 1 signal, early stage"

**HOLD** (No trade):
Triggers (ANY of these):
- Downtrend: Price < 50-MA
- No momentum: RSI < 50 or MACD < Signal
- Extreme overbought: RSI > 75 AND parabolic move
- Trend breaking: Price just crossed below 50-MA
- Bear analyst identifies major trend weakness
- Bull analyst can't find uptrend confirmation

Output: {{"action": "HOLD", "conviction": "none"}}
Example: "Downtrend confirmed, price $95k < 50-MA $98k, RSI 45, no momentum"

**CONVICTION VALIDATION (MANDATORY)**:

You MUST vary conviction based on signal strength:
- HIGH: 3+ signals, strong momentum, clean uptrend
- MEDIUM: 2 signals, moderate momentum, uptrend with minor concerns
- LOW: 1 signal, weak momentum, early/questionable uptrend

DO NOT default to MEDIUM. If signals are strong → HIGH. If signals are weak → LOW.

**CRITICAL DECISION RULES**:

1. **NO UPTREND = NO TRADE**
   - If Price < 50-MA → Automatic HOLD (even if Fear Index < 30)
   - We don't catch falling knives anymore

2. **MOMENTUM REQUIRED**
   - If RSI < 50 OR MACD bearish → HOLD or LOW conviction at best
   - Trend without momentum = wait

3. **OVERBOUGHT IS OK IN TRENDS**
   - RSI 60-70 is NORMAL in uptrends → Don't block
   - Only worry if RSI > 75 AND parabolic (unsustainable)

4. **LET WINNERS RUN**
   - Don't recommend HOLD just because "price went up a lot"
   - Trends persist longer than expected

5. **CONVICTION SCALING**
   - Strong setup (3+ signals, RSI 60, MACD strong) → HIGH
   - OK setup (2 signals, RSI 54, MACD weak) → MEDIUM
   - Weak setup (1 signal, RSI 51, MACD barely positive) → LOW
   - No setup (downtrend) → HOLD

**ANTI-PATTERNS (DO NOT DO)**:
❌ Do NOT recommend BUY when Fear Index < 40 during downtrends
❌ Do NOT override downtrend signals (Price < 50-MA = HOLD, period)
❌ Do NOT default all BUYs to MEDIUM conviction
❌ Do NOT block trades just because "it's been going up" (that's the point!)

**OUTPUT FORMAT (REQUIRED)**:
End your response with:

FINAL DECISION: {{"action": "BUY", "conviction": "high"}}
TREND STATUS: [Uptrend/Downtrend/Sideways]
MOMENTUM: [Strong/Moderate/Weak/Negative]
SIGNALS: [List the supporting signals: volume, MACD, Fear > 50, etc.]
REASONING: [Why this action and conviction level]

**Resources for decision**:
Market research report: {market_research_report}
Social media sentiment: {sentiment_report}
Latest news: {news_report}
Fundamentals: {fundamentals_report}
Bull vs Bear debate: {history}
Past mistakes to avoid: {past_memory_str}

Make your decision based on TREND STRENGTH and MOMENTUM, not sentiment or contrarian signals. Be decisive and vary conviction appropriately.
"""

        response = llm.invoke(prompt)

        new_investment_debate_state = {
            "history": history + "\\n" + f"Judge: {response.content}",
            "bull_history": investment_debate_state.get("bull_history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": f"Judge: {response.content}",
            "count": investment_debate_state["count"] + 1,
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": response.content,
        }

    return judge_node
