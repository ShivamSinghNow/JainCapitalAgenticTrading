# run_decision.py
from dotenv import load_dotenv
load_dotenv()  # loads your .env

import os, json
from datetime import datetime
from TradingAgents.tradingagents.graph.trading_graph import TradingAgentsGraph
from TradingAgents.tradingagents.default_config import DEFAULT_CONFIG

def decide(symbol: str = "BTC-USD", date: str | None = None):
    """
    Returns the agent team's trading decision for (symbol, date).
    date=None means "now" (live analysis) if the framework supports it.
    """

    # 1) Start from the framework defaults, then make it cheap/fast for MVP
    cfg = DEFAULT_CONFIG.copy()
    cfg.update({
        # Use small/cheap models first; you can override via env later
        "deep_think_llm": os.getenv("AGENT_DEEP_MODEL", "gpt-4o-mini"),
        "quick_think_llm": os.getenv("AGENT_QUICK_MODEL", "gpt-4o-mini"),

        # Keep debates short so you get quick output
        "max_debate_rounds": int(os.getenv("AGENT_MAX_DEBATE", "1")),

        # Allow HTTP data tools (news/prices/etc.) if the repo supports them
        "online_tools": True,
        
        # Fix data directory paths to use current working directory
        "data_dir": os.path.join(os.getcwd(), "data"),
        "data_cache_dir": os.path.join(os.getcwd(), "data_cache"),
    })

    # 2) Create necessary directories
    os.makedirs(cfg["data_cache_dir"], exist_ok=True)
    os.makedirs(cfg["data_dir"], exist_ok=True)

    # 3) Use a proper historical date if none provided (since system date is 2025)
    if date is None:
        date = "2024-12-30"  # Use a recent historical date

    # 4) Build the graph (this wires together Analysts → Researchers → Trader → Risk → Manager)
    ta = TradingAgentsGraph(debug=True, config=cfg)

    # 5) Run one full pass through the graph
    try:
        report, decision = ta.propagate(symbol, date)
    except Exception as e:
        print(f"Error during propagation: {e}")
        print("Trying with a different symbol...")
        # Fallback to a more common symbol
        report, decision = ta.propagate("AAPL", date)

    # 6) Show and persist the result so the executor can read it later
    print("\n=== TRADING DECISION ===")
    print(json.dumps(decision, indent=2, default=str))

    payload = {"symbol": symbol, "date": date, "decision": decision, "report": report}
    with open("last_decision.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)

    return decision

if __name__ == "__main__":
    # Try with BTC-USD and a proper historical date
    decide("BTC-USD", "2024-12-30")
