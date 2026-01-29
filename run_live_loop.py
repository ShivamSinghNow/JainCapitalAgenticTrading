# run_live_loop.py
import time
from run_decision import decide
from executor import place_from_decision

SYMBOL_DECISION = "BTCUSDT"   # for the agent
SYMBOL_EXCHANGE = "BTC/USDT"  # for CCXT

while True:
    decision = decide(SYMBOL_DECISION, None)
    print("Decision:", decision)

    # Very thin translation layer if schema differs
    mapped = {
        "action": (decision.get("action") or "HOLD"),
        "entry": decision.get("entry"),
        "stop": decision.get("stop_loss") or decision.get("stop"),
        "take_profit": decision.get("take_profit") or decision.get("tp"),
    }

    if mapped["action"].upper() != "HOLD":
        place_from_decision(mapped, SYMBOL_EXCHANGE, risk_usd=25.0)
    else:
        print("No trade. Sleeping...")

    time.sleep(60 * 5)  # run every 5 minutes
