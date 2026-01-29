# Trading Agents Architecture - Complete Breakdown

## Overview

This is a **multi-agent trading system** built on **LangGraph** that uses a **shared state** pattern for agent communication. The system orchestrates multiple specialized AI agents that work together to analyze market data and make trading decisions through a structured workflow.

---

## Core Architecture Pattern: Shared State Communication

### How Agents Communicate

**All agents communicate through a shared `AgentState` object** that gets passed between nodes in the graph. This is NOT direct agent-to-agent messaging - instead:

1. **Each agent receives the full state** when it's invoked
2. **Each agent reads relevant parts** of the state (reports, debate history, etc.)
3. **Each agent updates specific fields** in the state and returns them
4. **LangGraph automatically merges** the returned updates into the shared state

### The Shared State Structure

The `AgentState` (from `agent_states.py`) contains:

```python
AgentState {
    # Core info
    company_of_interest: str
    trade_date: str
    messages: List[Message]  # LangGraph message history
    
    # Analyst Reports (updated by analysts)
    market_report: str
    sentiment_report: str  
    news_report: str
    fundamentals_report: str
    
    # Investment Debate State (updated by researchers)
    investment_debate_state: {
        bull_history: str      # Bull researcher's arguments
        bear_history: str       # Bear researcher's arguments
        history: str            # Combined debate history
        current_response: str   # Last response
        judge_decision: str     # Research manager's decision
        count: int              # Round counter
    }
    
    # Investment Plan
    investment_plan: str        # Research manager's plan
    trader_investment_plan: str # Trader's refined plan
    
    # Risk Debate State (updated by risk analysts)
    risk_debate_state: {
        risky_history: str
        safe_history: str
        neutral_history: str
        history: str
        latest_speaker: str     # Controls routing
        current_risky_response: str
        current_safe_response: str
        current_neutral_response: str
        judge_decision: str
        count: int
    }
    
    # Final Output
    final_trade_decision: str   # Risk manager's final decision
}
```

---

## Execution Flow: The Complete Pipeline

The system follows a **linear pipeline with conditional branching** for debates:

```
START
  ↓
┌─────────────────────────────────────────┐
│  PHASE 1: DATA COLLECTION (Analysts)   │
└─────────────────────────────────────────┘
  ↓
Market Analyst → Tools → Market Analyst → Clear Messages
  ↓
Social Analyst → Tools → Social Analyst → Clear Messages  
  ↓
News Analyst → Tools → News Analyst → Clear Messages
  ↓
Fundamentals Analyst → Tools → Fundamentals Analyst → Clear Messages
  ↓
┌─────────────────────────────────────────┐
│  PHASE 2: INVESTMENT DEBATE             │
└─────────────────────────────────────────┘
  ↓
Bull Researcher ←→ Bear Researcher (debate loop)
  ↓ (when max rounds reached)
Research Manager (judge)
  ↓
┌─────────────────────────────────────────┐
│  PHASE 3: TRADING DECISION              │
└─────────────────────────────────────────┘
  ↓
Trader (creates investment plan)
  ↓
┌─────────────────────────────────────────┐
│  PHASE 4: RISK ANALYSIS                  │
└─────────────────────────────────────────┘
  ↓
Risky Analyst → Safe Analyst → Neutral Analyst (round-robin debate)
  ↓ (when max rounds reached)
Risk Judge (final decision)
  ↓
END
```

---

## Detailed Agent Breakdown

### Phase 1: Analysts (Data Collection)

**Purpose**: Collect and analyze different types of market data

**How They Work**:
1. Each analyst receives the shared state
2. Extracts `company_of_interest` and `trade_date`
3. Uses **tools** (via ToolNode) to fetch data:
   - Market Analyst: `get_YFin_data`, `get_stockstats_indicators_report`
   - Social Analyst: `get_stock_news_openai`, `get_reddit_stock_info`
   - News Analyst: `get_google_news`, `get_finnhub_news`
   - Fundamentals Analyst: `get_fundamentals_openai`, `get_simfin_balance_sheet`, etc.
4. Analyzes the data and writes a report
5. Updates state: `{market_report: "...", messages: [result]}`

**Tool Calling Pattern**:
- Agent calls tools → conditional logic checks if `tool_calls` exist → routes to `tools_{analyst}` node → executes tools → returns to analyst → analyst processes results → conditional logic routes to "Msg Clear" node → clears messages → next analyst

**Example Flow**:
```
Market Analyst Node
  ↓ (has tool_calls)
Tools Market Node (executes get_YFin_data, get_stockstats_indicators_report)
  ↓
Market Analyst Node (processes tool results, writes report)
  ↓ (no more tool_calls)
Msg Clear Market Node (cleans up messages)
  ↓
Social Analyst Node
```

---

### Phase 2: Investment Debate (Researchers)

**Purpose**: Debate whether to invest, with opposing viewpoints

#### Bull Researcher
- **Reads**: All analyst reports, debate history, bear's last argument
- **Reads from memory**: Past similar situations (via `memory.get_memories()`)
- **Updates**: `investment_debate_state.bull_history`, `investment_debate_state.history`, `investment_debate_state.current_response`, `count++`
- **Role**: Advocate for buying/investing

#### Bear Researcher  
- **Reads**: All analyst reports, debate history, bull's last argument
- **Reads from memory**: Past similar situations
- **Updates**: `investment_debate_state.bear_history`, `investment_debate_state.history`, `investment_debate_state.current_response`, `count++`
- **Role**: Advocate for selling/not investing

#### Debate Loop Logic (Conditional Logic)
```python
def should_continue_debate(state):
    if count >= 2 * max_debate_rounds:
        return "Research Manager"  # End debate
    if current_response.startswith("Bull"):
        return "Bear Researcher"   # Bull just spoke, bear responds
    return "Bull Researcher"       # Bear just spoke, bull responds
```

**Pattern**: 
- Bull → Bear → Bull → Bear → ... (until max rounds)
- Then Research Manager is invoked

#### Research Manager (Judge)
- **Reads**: Complete debate history, all analyst reports
- **Reads from memory**: Past mistakes/lessons
- **Updates**: `investment_debate_state.judge_decision`, `investment_plan`
- **Role**: Synthesize the debate, make investment recommendation (Buy/Sell/Hold), create detailed plan

---

### Phase 3: Trader

**Purpose**: Translate the investment plan into a concrete trading decision

- **Reads**: `investment_plan`, all analyst reports
- **Reads from memory**: Past trading mistakes
- **Updates**: `trader_investment_plan`, `messages`
- **Role**: Refine the plan into actionable trading decision with "FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**"

---

### Phase 4: Risk Analysis (Risk Debators)

**Purpose**: Evaluate risk from multiple perspectives

#### Risky Analyst
- **Reads**: Trader's plan, all reports, safe/neutral responses
- **Updates**: `risk_debate_state.risky_history`, `risk_debate_state.history`, `latest_speaker="Risky"`, `count++`
- **Role**: Advocate for higher-risk, higher-reward strategies

#### Safe Analyst (Conservative)
- **Reads**: Trader's plan, all reports, risky/neutral responses  
- **Updates**: `risk_debate_state.safe_history`, `risk_debate_state.history`, `latest_speaker="Safe"`, `count++`
- **Role**: Advocate for conservative, risk-averse strategies

#### Neutral Analyst
- **Reads**: Trader's plan, all reports, risky/safe responses
- **Updates**: `risk_debate_state.neutral_history`, `risk_debate_state.history`, `latest_speaker="Neutral"`, `count++`
- **Role**: Provide balanced, moderate perspective

#### Risk Debate Loop Logic
```python
def should_continue_risk_analysis(state):
    if count >= 3 * max_risk_discuss_rounds:
        return "Risk Judge"
    if latest_speaker.startswith("Risky"):
        return "Safe Analyst"      # Risky → Safe
    if latest_speaker.startswith("Safe"):
        return "Neutral Analyst"   # Safe → Neutral  
    return "Risky Analyst"         # Neutral → Risky (or initial)
```

**Pattern**: Risky → Safe → Neutral → Risky → ... (round-robin)

#### Risk Manager (Judge)
- **Reads**: Complete risk debate history, trader's plan, all reports
- **Reads from memory**: Past risk management mistakes
- **Updates**: `risk_debate_state.judge_decision`, `final_trade_decision`
- **Role**: Final decision maker - Buy/Sell/Hold with risk-adjusted plan

---

## Key Communication Mechanisms

### 1. State Updates (Primary Method)

Each agent returns a dictionary with only the fields it updates:
```python
# Example: Bull Researcher
return {
    "investment_debate_state": new_investment_debate_state
}

# Example: Market Analyst  
return {
    "messages": [result],
    "market_report": report
}
```

LangGraph automatically merges these partial updates into the full state.

### 2. Conditional Routing

The `ConditionalLogic` class determines which node executes next based on state:
- **Tool calls**: Routes to tool nodes if agent requests tools
- **Debate rounds**: Routes based on debate count and last speaker
- **Message cleanup**: Routes to clear nodes after analysis

### 3. Memory System

Each agent type has its own `FinancialSituationMemory`:
- **Bull Memory**: Stores bull researcher's past decisions
- **Bear Memory**: Stores bear researcher's past decisions  
- **Trader Memory**: Stores trader's past decisions
- **Invest Judge Memory**: Stores research manager's past decisions
- **Risk Manager Memory**: Stores risk manager's past decisions

**How it works**:
- Agents call `memory.get_memories(curr_situation, n_matches=2)` to retrieve similar past situations
- These memories are injected into prompts to help agents learn from mistakes
- After execution, `reflect_and_remember()` can be called to update memories based on actual returns/losses

### 4. Tool Integration

Tools are organized into **ToolNodes** by category:
- `tools_market`: Market data tools
- `tools_social`: Social media tools
- `tools_news`: News tools
- `tools_fundamentals`: Fundamentals tools

When an agent makes tool calls, the conditional logic routes to the appropriate ToolNode, which executes the tools and returns results to the agent.

---

## Complete Execution Example

### Step-by-Step Flow for "BTC-USD" on "2024-12-30"

1. **Initialization** (`Propagator.create_initial_state()`):
   ```python
   {
       "messages": [("human", "BTC-USD")],
       "company_of_interest": "BTC-USD",
       "trade_date": "2024-12-30",
       "investment_debate_state": {...empty...},
       "risk_debate_state": {...empty...},
       "market_report": "",
       ...
   }
   ```

2. **Market Analyst**:
   - Reads: `company_of_interest="BTC-USD"`, `trade_date="2024-12-30"`
   - Calls tools: `get_YFin_data_online("BTC-USD", "2024-12-30")`
   - Analyzes data, writes report
   - Updates: `state["market_report"] = "BTC shows strong momentum..."`

3. **Social Analyst**:
   - Reads: `market_report` (from previous step)
   - Calls tools: `get_stock_news_openai("BTC-USD")`
   - Updates: `state["sentiment_report"] = "Social sentiment is bullish..."`

4. **News Analyst**:
   - Reads: `market_report`, `sentiment_report`
   - Calls tools: `get_google_news("BTC")`
   - Updates: `state["news_report"] = "Recent news indicates..."`

5. **Fundamentals Analyst**:
   - Reads: All previous reports
   - Calls tools: `get_fundamentals_openai("BTC-USD")`
   - Updates: `state["fundamentals_report"] = "Fundamental analysis shows..."`

6. **Bull Researcher**:
   - Reads: All 4 reports, empty debate history
   - Retrieves memories: Similar past situations
   - Updates: 
     ```python
     investment_debate_state = {
         "bull_history": "Bull Analyst: BTC shows strong growth potential...",
         "history": "Bull Analyst: BTC shows strong growth potential...",
         "current_response": "Bull Analyst: BTC shows strong growth potential...",
         "count": 1
     }
     ```

7. **Bear Researcher**:
   - Reads: All reports, bull's argument
   - Updates:
     ```python
     investment_debate_state = {
         "bear_history": "Bear Analyst: However, volatility concerns...",
         "history": "Bull Analyst: ...\nBear Analyst: However...",
         "current_response": "Bear Analyst: However...",
         "count": 2
     }
     ```

8. **Debate Continues** (if `count < max_debate_rounds * 2`):
   - Bull → Bear → Bull → Bear (back and forth)

9. **Research Manager**:
   - Reads: Complete debate history, all reports
   - Synthesizes: "After evaluating both sides, I recommend BUY..."
   - Updates:
     ```python
     investment_debate_state.judge_decision = "Recommend BUY..."
     investment_plan = "Detailed plan: Buy BTC at $65000, stop loss at $63700..."
     ```

10. **Trader**:
    - Reads: `investment_plan`, all reports
    - Refines: "FINAL TRANSACTION PROPOSAL: **BUY**"
    - Updates: `trader_investment_plan = "BUY with entry at $65000..."`

11. **Risky Analyst**:
    - Reads: Trader's plan, all reports
    - Updates: `risk_debate_state.risky_history = "Risky Analyst: The trader's plan is sound..."`, `latest_speaker="Risky"`

12. **Safe Analyst**:
    - Reads: Trader's plan, risky's argument
    - Updates: `risk_debate_state.safe_history = "Safe Analyst: However, we should be more conservative..."`, `latest_speaker="Safe"`

13. **Neutral Analyst**:
    - Reads: Trader's plan, risky's and safe's arguments
    - Updates: `risk_debate_state.neutral_history = "Neutral Analyst: A balanced approach..."`, `latest_speaker="Neutral"`

14. **Risk Debate Continues** (round-robin until max rounds)

15. **Risk Manager**:
    - Reads: Complete risk debate, trader's plan
    - Final decision: "FINAL TRANSACTION PROPOSAL: **BUY** with risk-adjusted position sizing..."
    - Updates: `final_trade_decision = "BUY at $65000, stop loss $63700, take profit $67000"`

16. **Signal Processing**:
    - Extracts core decision: `"BUY"` from the full decision text

17. **Output**:
    - Returns: `(final_state, "BUY")`
    - Saved to: `last_decision.json` and `eval_results/BTC-USD/.../full_states_log_2024-12-30.json`

---

## Key Design Patterns

### 1. **State-Based Communication**
- No direct agent-to-agent calls
- All communication through shared state
- Agents are stateless functions that transform state

### 2. **Conditional Routing**
- Graph flow controlled by state inspection
- Enables dynamic workflows (debates, tool loops)

### 3. **Memory-Augmented Agents**
- Each agent type has persistent memory
- Retrieves relevant past experiences
- Can reflect and learn from outcomes

### 4. **Tool Integration**
- Tools organized by domain (market, social, news, fundamentals)
- Agents call tools via LangGraph ToolNodes
- Conditional logic routes tool calls automatically

### 5. **Debate Pattern**
- Opposing viewpoints (Bull/Bear, Risky/Safe/Neutral)
- Round-based debates with max limits
- Judge agent synthesizes and decides

---

## How to Run the System

### Entry Point: `run_decision.py`

```python
from run_decision import decide

# Make a trading decision
decision = decide("BTC-USD", "2024-12-30")
```

### What Happens:

1. **Configuration**: Loads config, sets up LLMs, toolkits, memories
2. **Graph Creation**: `TradingAgentsGraph.__init__()` builds the LangGraph workflow
3. **State Initialization**: Creates initial state with company and date
4. **Graph Execution**: `graph.stream()` or `graph.invoke()` runs the workflow
5. **State Propagation**: State flows through nodes, each agent updates it
6. **Result Extraction**: Final decision extracted from `final_trade_decision`
7. **Persistence**: Results saved to JSON files

---

## Integration with Executor

The `executor.py` file can read `last_decision.json` and execute trades via 3Commas API:

```python
# Executor reads the decision
decision = {
    "action": "BUY",
    "entry": 65000.0,
    "stop_loss": 63700.0,
    "take_profit": 67000.0
}

# Executor places trade
place_from_decision(decision, quote="USDT", base="BTC", risk_usd=50.0)
```

---

## Summary

This is a **sophisticated multi-agent system** where:

1. **Agents don't directly talk** - they communicate through a shared state object
2. **Workflow is graph-based** - LangGraph orchestrates the flow
3. **Routing is conditional** - based on state (tool calls, debate rounds, etc.)
4. **Agents are specialized** - each has a specific role and expertise
5. **Memory is persistent** - agents learn from past decisions
6. **Tools are integrated** - agents can fetch real market data
7. **Decisions are debated** - multiple perspectives ensure thorough analysis

The system is designed to be **modular** (easy to add/remove analysts), **extensible** (new agents can be added), and **traceable** (all state is logged for analysis).



