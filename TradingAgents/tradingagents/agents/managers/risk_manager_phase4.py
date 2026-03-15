import time
import json


def create_risk_manager_phase4(llm, memory):
    """
    Phase 4 Risk Manager - TREND-FOLLOWING risk validation.

    CRITICAL CHANGE from Phase 3.x:
    - Phase 3.x: Validate contrarian setups (Fear < 40)
    - Phase 4: Validate trend strength and momentum
    """
    def risk_manager_node(state) -> dict:

        company_name = state["company_of_interest"]

        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["news_report"]
        sentiment_report = state["sentiment_report"]
        trader_plan = state["investment_plan"]

        curr_situation = f"{market_research_report}\\n\\n{sentiment_report}\\n\\n{news_report}\\n\\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\\n\\n"

        prompt = f"""You are the RISK MANAGER validating TREND-FOLLOWING trade decisions.

**PHASE 4 PHILOSOPHY**: Validate trend strength and momentum, NOT contrarian setups

**YOUR JOB**: Ensure the trade follows trend-following principles and conviction matches reality

**RISK VALIDATION FRAMEWORK (Phase 4)**:

**APPROVE AS-IS** (Green light):
Judge says BUY HIGH conviction AND:
- Uptrend confirmed (Price > 50-MA > 200-MA)
- Strong momentum (RSI 55-70, MACD strongly positive)
- 3+ supporting signals (volume, higher highs, Fear > 50, order book)
- No extreme overbought (RSI < 75)
→ Output: {{"action": "BUY", "conviction": "high"}}
→ State: "Conviction VALIDATED: Strong uptrend, RSI 62, MACD +500, 4 signals"

**APPROVE WITH DOWNGRADE**:
Judge says BUY HIGH conviction BUT:
- Only 2 signals (not 3+) → Downgrade to MEDIUM
- Moderate momentum (RSI 50-55) → Downgrade to MEDIUM
- Slight overbought (RSI 72-75) → Downgrade to LOW
→ Output: {{"action": "BUY", "conviction": "medium"}} or {{"action": "BUY", "conviction": "low"}}
→ State: "Conviction ADJUSTED: HIGH → MEDIUM because only 2 signals, not 3+"

**APPROVE WITH UPGRADE**:
Judge says BUY MEDIUM conviction BUT:
- Actually has strong uptrend + 3+ signals → Upgrade to HIGH
- Fear > 60 + strong MACD + volume → Upgrade to HIGH
→ Output: {{"action": "BUY", "conviction": "high"}}
→ State: "Conviction ADJUSTED: MEDIUM → HIGH because strong trend + 3 signals + momentum"

**MODIFY TO HOLD** (Override to HOLD):
Judge says BUY BUT:
- Downtrend exists (Price < 50-MA) → REJECT, force HOLD
- No momentum (RSI < 50 or MACD bearish) → REJECT, force HOLD
- Extreme overbought (RSI > 75 AND parabolic) → REJECT, force HOLD
- Trend just broke (crossed below 50-MA in last 3 days) → REJECT, force HOLD
→ Output: {{"action": "HOLD", "conviction": "none"}}
→ State: "REJECTED: Downtrend confirmed, price $95k < 50-MA $98k, cannot buy weakness"

**CONVICTION VALIDATION RULES (Phase 4)**:

**HIGH conviction checklist** (verify ALL of these):
1. Uptrend confirmed: Price > 50-MA > 200-MA ✓
2. Strong momentum: RSI 55-70 AND MACD > Signal ✓
3. 3+ supporting signals ✓
4. No extreme overbought: RSI < 75 ✓

If any missing → DOWNGRADE to MEDIUM or LOW

**MEDIUM conviction checklist** (verify 2-3 of these):
1. Uptrend confirmed ✓
2. Moderate momentum: RSI 50-60 or MACD barely positive ✓
3. 2 supporting signals ✓

If stronger → UPGRADE to HIGH. If weaker → DOWNGRADE to LOW

**LOW conviction checklist** (verify 1-2 of these):
1. Early uptrend (just crossed above 50-MA)
2. Weak momentum: RSI 50-55
3. Only 1 supporting signal

If stronger → UPGRADE to MEDIUM

**CRITICAL VALIDATION CHECKS**:

1. **Is there an uptrend?**
   - Check: Price > 50-MA > 200-MA
   - If NO → OVERRIDE to HOLD (no exceptions)

2. **Is there momentum?**
   - Check: RSI > 50 AND MACD > Signal
   - If NO → HOLD or maximum LOW conviction

3. **Is it extreme overbought?**
   - Check: RSI > 75 AND recent parabolic move
   - If YES → HOLD (unsustainable)

4. **How many signals support the trade?**
   - 3+ signals → Can be HIGH
   - 2 signals → Maximum MEDIUM
   - 1 signal → Maximum LOW
   - 0 signals → HOLD

**ANTI-PATTERNS (REJECT THESE)**:
❌ Judge says BUY during downtrend (Price < 50-MA) → REJECT to HOLD
❌ Judge says BUY with Fear < 30 (contrarian logic) → CHECK if uptrend exists, if not → HOLD
❌ Judge says HIGH conviction with only 1-2 signals → DOWNGRADE to MEDIUM/LOW
❌ Auto-defaulting to MEDIUM without validation → VARY conviction properly

**POSITION SIZE VALIDATION**:
- HIGH conviction → 3% risk (only if checklist fully passed)
- MEDIUM conviction → 2% risk
- LOW conviction → 1% risk

**OUTPUT FORMAT (REQUIRED)**:
End your response with:

FINAL DECISION: {{"action": "ACTION", "conviction": "LEVEL"}}
TREND VALIDATION: [Confirm uptrend status: Price vs 50-MA vs 200-MA]
MOMENTUM VALIDATION: [Confirm RSI > 50, MACD > Signal]
SIGNAL COUNT: [How many supporting signals: 0, 1, 2, 3+]
REASONING: [Why this conviction level is appropriate]

If ADJUSTED conviction, state: "Conviction ADJUSTED: [FROM] → [TO] because [specific reason]"
If REJECTED trade, state: "REJECTED: [specific violation of trend-following rules]"

**Trader's Plan to Evaluate**: {trader_plan}

**Analysts Debate History**: {history}

**Past Reflections**: {past_memory_str}

Your job: Validate that the trade follows trend-following principles (uptrend + momentum) and ensure conviction matches signal strength. Block trades that violate trend-following rules (downtrend, no momentum, extreme overbought).
"""

        response = llm.invoke(prompt)

        new_risk_debate_state = {
            "judge_decision": response.content,
            "history": risk_debate_state["history"],
            "risky_history": risk_debate_state["risky_history"],
            "safe_history": risk_debate_state["safe_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_risky_response": risk_debate_state["current_risky_response"],
            "current_safe_response": risk_debate_state["current_safe_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response.content,
        }

    return risk_manager_node
