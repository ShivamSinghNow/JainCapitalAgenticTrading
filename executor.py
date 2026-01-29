# executor.py
from __future__ import annotations

import os, time, json, hmac, hashlib
import requests
from typing import Any, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

API_KEY   = os.getenv("THREECOMMAS_API_KEY", "")
API_SECRET= os.getenv("THREECOMMAS_API_SECRET", "")
ACCOUNT_ID= os.getenv("THREECOMMAS_ACCOUNT_ID", "")
USE_PAPER = os.getenv("THREECOMMAS_PAPER", "1") in ("1", "true", "True")

BASE_URL  = "https://api.3commas.io"  # prod API host

def _sign(payload: str) -> str:
    """
    3Commas HMAC-SHA256 signature over `uri?query + body` (concatenated).
    The result is a lowercase hex digest.
    Docs: developers.3commas.io → Signing a Request Using HMAC SHA256
    """
    return hmac.new(
        API_SECRET.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

def _headers(signature: str, json_body: bool = False) -> Dict[str, str]:
    hdrs = {
        "Apikey": API_KEY,
        "Signature": signature,
    }
    if json_body:
        hdrs["Content-Type"] = "application/json"
    return hdrs

def _req(method: str, path: str, params: Optional[Dict[str, Any]] = None,
         json_data: Optional[Dict[str, Any]] = None) -> requests.Response:
    """
    Minimal helper that computes the correct signature payload for 3Commas.

    Signature payload = path + ("?" + querystring if any) + (raw body if any)
    """
    params = params or {}
    json_data = json_data or {}

    # Build querystring (stable order)
    from urllib.parse import urlencode
    qs = urlencode(params, doseq=True)
    url = f"{BASE_URL}{path}"
    payload_for_sig = f"{path}"
    if qs:
        url += f"?{qs}"
        payload_for_sig += f"?{qs}"

    body_str = ""
    data = None
    json_mode = False

    if json_data:
        body_str = json.dumps(json_data, separators=(",", ":"))
        payload_for_sig += body_str
        data = body_str
        json_mode = True

    sig = _sign(payload_for_sig)
    hdr = _headers(sig, json_body=json_mode)

    if method.upper() == "GET":
        return requests.get(url, headers=hdr, timeout=30)
    elif method.upper() == "POST":
        if json_mode:
            return requests.post(url, headers=hdr, data=data, timeout=30)
        else:
            return requests.post(url, headers=hdr, data=params, timeout=30)
    else:
        raise ValueError(f"Unsupported method: {method}")

def ensure_paper_mode():
    """
    Optional: switch to paper mode (Demo account) via API.
    Equivalent to toggling Demo in the UI.
    Endpoint: POST /public/api/ver1/users/change_mode  (SIGNED)
    """
    if not USE_PAPER:
        return
    path = "/public/api/ver1/users/change_mode"
    params = {"mode": "paper"}
    # For HMAC payload when sending body form-encoded, 3Commas examples still sign with '?mode=paper'
    resp = _req("POST", path, params=params)
    if resp.status_code != 200:
        print("Warn: change_mode failed:", resp.status_code, resp.text)

def create_smart_trade(pair: str, side: str, units: float,
                       tp_price: Optional[float] = None,
                       sl_price: Optional[float] = None,
                       leverage: Optional[int] = None) -> Dict[str, Any]:
    """
    Creates a Simple Buy/Sell SmartTrade at market.
    - pair: 3Commas pair like 'USDT_BTC' (buying BTC with USDT)  <-- verify for your exchange
    - side: 'buy' or 'sell'
    - units: asset amount (e.g., BTC amount for buy)
    - tp_price / sl_price: absolute price levels (optional)
    """
    path = "/public/api/v2/smart_trades"

    payload: Dict[str, Any] = {
        "account_id": int(ACCOUNT_ID),
        "pair": pair,
        "instant": True,              # Simple Buy/Sell
        "position": {
            "type": side,             # 'buy' or 'sell'
            "units": {"value": str(units)},
            "order_type": "market",
        },
    }

    if leverage:
        payload["leverage"] = {"enabled": True, "type": "custom", "value": str(leverage)}

    # Optional Take Profit
    if tp_price:
        payload["take_profit"] = {
            "enabled": True,
            "steps": [{
                "order_type": "limit",
                "volume": 100,           # 100% close at TP
                "price": {"type": "last", "value": float(tp_price)},
            }],
        }

    # Optional Stop Loss
    if sl_price:
        payload["stop_loss"] = {
            "enabled": True,
            "order_type": "market",
            "price": {"value": float(sl_price)},
            # You can use conditional {price:{type:'last', value:...}} if you prefer
        }

    # Compute signature over path + body, send JSON body
    resp = _req("POST", path, json_data=payload)
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"SmartTrade create failed [{resp.status_code}]: {resp.text}")
    return resp.json()

def place_from_decision(decision: Dict[str, Any],
                        quote: str = "USDT",
                        base: str = "BTC",
                        risk_usd: float = 50.0) -> Optional[Dict[str, Any]]:
    """
    Map your agent's decision to a 3Commas SmartTrade.

    decision: {
      "action": "BUY" | "SELL" | "HOLD",
      "entry": 65000.0,                     # target (optional for market)
      "stop" or "stop_loss": 63700.0,       # optional
      "take_profit" or "tp": 67000.0        # optional
    }
    """
    action = (decision.get("action") or "HOLD").upper()
    if action == "HOLD":
        print("Executor: HOLD — no action taken.")
        return None

    # Basic position sizing by risk (fallback if stop is present)
    entry = float(decision.get("entry") or 0.0)
    stop  = float(decision.get("stop_loss") or decision.get("stop") or 0.0)
    tp    = decision.get("take_profit") or decision.get("tp")
    tp    = float(tp) if tp else None

    # Compute units (amount of BASE to buy/sell). If we have stop, use risk model.
    if entry > 0 and stop > 0 and entry != stop:
        one_unit_risk = abs(entry - stop)
        # Convert risk_usd to "units" via price difference. This is a rough calc for spot.
        units = max(risk_usd / one_unit_risk, 0.0001)
    else:
        # If no stop or entry, just buy a small fixed notional at market: notional / last_price
        # You can query 3Commas market data to fetch last price; here we assume entry ~ current
        px = entry if entry > 0 else 1.0
        units = max(risk_usd / px, 0.0001)

    side = "buy" if action == "BUY" else "sell"

    # Pair format in 3Commas is typically QUOTE_BASE (e.g., USDT_BTC)
    pair = f"{quote}_{base}"

    ensure_paper_mode()
    print(f"Creating SmartTrade: {pair} {side} units={units:.8f} tp={tp} sl={stop if stop>0 else None}")
    trade = create_smart_trade(pair=pair, side=side, units=units,
                               tp_price=tp, sl_price=(stop if stop > 0 else None))
    print("SmartTrade created:", json.dumps(trade, indent=2))
    return trade

if __name__ == "__main__":
    # Example manual test
    sample = {"action": "BUY", "entry": 65000, "stop": 63700, "take_profit": 67000}
    place_from_decision(sample, quote="USDT", base="BTC", risk_usd=25.0)
