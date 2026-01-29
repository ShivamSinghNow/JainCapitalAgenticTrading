# Binance US Migration Guide

## Summary of Changes

The codebase has been updated to use **Binance US** instead of international Binance or testnet. This document explains what changed and important limitations.

---

## What Changed

### 1. Exchange Data Module (`exchange_utils.py`)

**Before**: Used international Binance API endpoints
- `https://api.binance.com` (spot)
- `https://fapi.binance.com` (futures)

**After**: Now uses Binance US API endpoints
- `https://api.binance.us/api/v3` (spot only)

---

## Important Limitations of Binance US

### ⚠️ Binance US Does NOT Support Futures Trading

Binance US is a **spot-only exchange**. This means the following features are **NOT available**:

1. ❌ **Funding Rates** - Requires futures/perpetual contracts
2. ❌ **Open Interest** - Requires futures/perpetual contracts
3. ❌ **Long/Short Ratios** - Requires futures/perpetual contracts

### ✅ What IS Available on Binance US

1. ✅ **Spot Order Book Data** - Bid/ask depth analysis
2. ✅ **Spot Kline/Candlestick Data** - Historical OHLCV
3. ✅ **Taker Buy/Sell Volume** - Market order flow analysis
4. ✅ **24h Ticker Statistics** - Price, volume, changes

---

## How We Handle Missing Features

### Funding Rates & Open Interest

**Solution**: Automatically fallback to **Bybit** for futures data

```python
# Now uses Bybit API when you call these functions
funding_rate = get_binance_funding_rate("BTCUSDT", limit=10)
# Returns: Funding rate data from Bybit with a note

open_interest = get_binance_open_interest("BTCUSDT")
# Returns: Open interest data from Bybit with a note
```

### Long/Short Ratios

**Solution**: Returns informational message with alternative data sources

```python
ls_ratio = get_binance_long_short_ratio("BTCUSDT")
# Returns: Message explaining where to get this data (Bybit, Coinglass, etc.)
```

### Order Book & Taker Volume

**Solution**: Uses Binance US spot API (fully functional)

```python
# These work perfectly with Binance US
orderbook = get_order_book_imbalance("BTCUSDT", depth=20)
volume = get_taker_buysell_volume("BTCUSDT", interval="1h", limit=24)
```

---

## API Endpoints Reference

### Binance US Spot API

All spot endpoints use: `https://api.binance.us/api/v3`

**Available Endpoints**:
- `/depth` - Order book
- `/klines` - Candlestick data
- `/ticker/24hr` - 24-hour statistics
- `/ticker/price` - Latest price
- `/ticker/bookTicker` - Best bid/ask

**NOT Available on Binance US**:
- Any `/fapi/*` endpoints (futures)
- Any `/dapi/*` endpoints (delivery futures)
- Funding rate endpoints
- Open interest endpoints
- Long/short ratio endpoints

### Alternative Exchange APIs (Used for Missing Data)

**Bybit** (for futures data):
- Funding rates: `https://api.bybit.com/v5/market/funding/history`
- Open interest: `https://api.bybit.com/v5/market/open-interest`
- Long/short ratio: `https://api.bybit.com/v5/market/account-ratio`

---

## Testing the Changes

Run the test script to verify everything works:

```bash
python test_crypto_data.py
```

**Expected Results**:
- ✅ Order book data: Works with Binance US
- ✅ Taker volume data: Works with Binance US
- ℹ️ Funding rates: Returns Bybit data with note
- ℹ️ Open interest: Returns Bybit data with note
- ℹ️ Long/short ratio: Returns informational message

---

## Migration Checklist

- [x] Updated spot endpoints to Binance US (`api.binance.us`)
- [x] Added fallback to Bybit for funding rates
- [x] Added fallback to Bybit for open interest
- [x] Added informational message for long/short ratios
- [x] Updated order book to use Binance US
- [x] Updated taker volume to use Binance US
- [x] Added clear notes in function outputs
- [x] Updated documentation

---

## Recommended Configuration

For optimal crypto trading data in the US:

### Multi-Exchange Strategy

1. **Binance US** - Spot trading and order flow
   - Order book analysis
   - Taker buy/sell volume
   - Spot price data

2. **Bybit** - Futures data (via fallback)
   - Funding rates
   - Open interest
   - Perpetual contract data

3. **CCXT Library** - Multi-exchange aggregation
   - Use `get_ccxt_funding_rates()` for cross-exchange comparison
   - Access 100+ exchanges with unified interface

### Example Usage

```python
from TradingAgents.tradingagents.dataflows.exchange_utils import (
    get_order_book_imbalance,      # Binance US
    get_taker_buysell_volume,      # Binance US
    get_binance_funding_rate,      # Bybit (automatic fallback)
    get_binance_open_interest,     # Bybit (automatic fallback)
    get_ccxt_funding_rates,        # Multi-exchange via CCXT
)

# Spot data from Binance US
orderbook = get_order_book_imbalance("BTCUSDT", depth=20)
volume = get_taker_buysell_volume("BTCUSDT", interval="1h")

# Futures data from Bybit (automatic)
funding = get_binance_funding_rate("BTCUSDT", limit=10)
oi = get_binance_open_interest("BTCUSDT")

# Multi-exchange comparison
multi_funding = get_ccxt_funding_rates("BTC/USDT", exchanges=['bybit', 'okx'])
```

---

## Why Binance US?

### Regulatory Compliance
- Fully compliant with US regulations
- Licensed to operate in most US states
- Proper KYC/AML procedures

### Limitations to Be Aware Of
- No futures/derivatives trading
- Smaller selection of cryptocurrencies vs international Binance
- Lower trading volume than international exchanges

### When to Use International Exchanges

Consider using international exchanges (via VPN or if outside US) for:
- Futures/derivatives trading
- More altcoins
- Advanced trading features
- Higher liquidity

---

## Troubleshooting

### Issue: "451 Client Error" from Binance

**Cause**: Geographic restrictions

**Solutions**:
1. Verify you're using Binance US endpoints (`api.binance.us`)
2. For futures data, the system automatically uses Bybit
3. If you're outside the US, you may need to use international Binance

### Issue: "Funding rate not available"

**Cause**: Binance US doesn't support futures

**Solution**: The code automatically uses Bybit. No action needed.

### Issue: "Symbol not found"

**Cause**: Symbol may not be listed on Binance US

**Solutions**:
1. Check available symbols on Binance US website
2. Use CCXT to access other exchanges
3. Some altcoins may only be on international Binance

---

## Additional Resources

- **Binance US API Docs**: https://docs.binance.us/
- **Bybit API Docs**: https://bybit-exchange.github.io/docs/v5/intro
- **CCXT Library**: https://github.com/ccxt/ccxt
- **Supported Symbols**: https://www.binance.us/en/trade-pro

---

## Support

For issues or questions:
1. Check Binance US API status: https://status.binance.us/
2. Review API documentation
3. Test with the provided test script: `python test_crypto_data.py`

---

**Last Updated**: January 2026
**Binance US API Version**: v3 (Spot)
**Alternative APIs**: Bybit v5
