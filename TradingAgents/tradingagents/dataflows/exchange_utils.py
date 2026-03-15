"""
Exchange Data Utilities - FREE Crypto Exchange Metrics

This module provides access to crypto exchange data using completely free APIs:
- Binance US Public API (no authentication required)
- CCXT library (open source, multi-exchange support)
- Bybit/OKX Public APIs (no authentication required)

All functions use FREE public endpoints - no API keys needed!

Note: Binance US does not support futures/derivatives trading, so funding rates,
open interest, and long/short ratios are not available. These functions will
return appropriate messages or use alternative exchanges.
"""

from typing import Annotated, Dict, List, Optional
import requests
from datetime import datetime, timedelta
import ccxt
import pandas as pd
from .utils import retry_on_failure
from .config import get_config

# Binance US API endpoints (spot trading only)
BINANCE_US_SPOT_API = "https://api.binance.us/api/v3"

# For futures data, we'll use alternative exchanges or return informative messages
# since Binance US doesn't support futures trading


# ===== BINANCE FUNDING RATE FUNCTIONS =====

@retry_on_failure(max_retries=3, delay=2)
def get_binance_funding_rate(
    symbol: Annotated[str, "Trading pair symbol (e.g., 'BTCUSDT', 'ETHUSDT')"],
    limit: Annotated[int, "Number of historical funding rate records to fetch"] = 10,
) -> str:
    """
    Get current and historical funding rates (using alternative exchanges).

    NOTE: Binance US does not support futures/derivatives trading.
    This function uses Bybit as an alternative source for funding rate data.

    Funding rates are a critical indicator for crypto trading:
    - Positive funding rate: Longs pay shorts (bullish sentiment)
    - Negative funding rate: Shorts pay longs (bearish sentiment)
    - High positive rates often precede corrections
    - High negative rates often precede rallies

    Args:
        symbol: Trading pair (e.g., 'BTCUSDT', 'ETHUSDT')
        limit: Number of historical records (default 10)

    Returns:
        Formatted string with funding rate history and analysis
    """
    # Use Bybit for funding rates since Binance US doesn't support futures
    try:
        url = "https://api.bybit.com/v5/market/funding/history"
        # Bybit uses different symbol format
        bybit_symbol = symbol.replace("USDT", "")  # BTC for BTCUSDT
        params = {"category": "linear", "symbol": symbol, "limit": limit}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('retCode') != 0:
            return f"Bybit API error for {symbol}: {data.get('retMsg', 'Unknown error')}"

        results = data.get('result', {}).get('list', [])

        if not results:
            return f"No funding rate data available for {symbol} on Bybit"

        # Format the data
        result_str = f"## Funding Rate History for {symbol} (via Bybit):\n\n"
        result_str += f"_Note: Using Bybit data since Binance US doesn't support futures trading_\n\n"

        for record in results[:limit]:  # Limit results
            timestamp = datetime.fromtimestamp(int(record['fundingRateTimestamp']) / 1000)
            rate = float(record['fundingRate']) * 100  # Convert to percentage

            # Interpret the funding rate
            if rate > 0.05:
                sentiment = "VERY BULLISH (high long demand)"
            elif rate > 0.01:
                sentiment = "Bullish (longs paying shorts)"
            elif rate > -0.01:
                sentiment = "Neutral"
            elif rate > -0.05:
                sentiment = "Bearish (shorts paying longs)"
            else:
                sentiment = "VERY BEARISH (high short demand)"

            result_str += f"**{timestamp.strftime('%Y-%m-%d %H:%M')}**: {rate:.4f}% - {sentiment}\n"

        # Calculate average funding rate
        avg_rate = sum(float(r['fundingRate']) for r in results[:limit]) / len(results[:limit]) * 100

        result_str += f"\n**Average Funding Rate**: {avg_rate:.4f}%\n"
        result_str += "\n### Interpretation:\n"
        result_str += "- Funding rates show the cost of holding perpetual futures positions\n"
        result_str += "- Positive rates indicate bullish sentiment (longs outnumber shorts)\n"
        result_str += "- Negative rates indicate bearish sentiment (shorts outnumber longs)\n"
        result_str += "- Extreme rates (>0.1% or <-0.1%) often precede reversals\n"

        return result_str

    except Exception as e:
        return f"Error fetching funding rate for {symbol} from Bybit: {str(e)}\n\nNote: Binance US doesn't support futures trading. Consider using Bybit, OKX, or international exchanges for funding rate data."


@retry_on_failure(max_retries=3, delay=2)
def get_binance_open_interest(
    symbol: Annotated[str, "Trading pair symbol (e.g., 'BTCUSDT', 'ETHUSDT')"],
) -> str:
    """
    Get current open interest (using alternative exchanges).

    NOTE: Binance US does not support futures/derivatives trading.
    This function uses Bybit as an alternative source for open interest data.

    Open Interest (OI) represents the total number of outstanding contracts:
    - Rising OI + rising price = bullish (new money entering longs)
    - Rising OI + falling price = bearish (new money entering shorts)
    - Falling OI + rising price = short squeeze
    - Falling OI + falling price = long liquidations

    Args:
        symbol: Trading pair (e.g., 'BTCUSDT', 'ETHUSDT')

    Returns:
        Formatted string with open interest data and analysis
    """
    # Use Bybit for open interest since Binance US doesn't support futures
    url = "https://api.bybit.com/v5/market/open-interest"
    params = {"category": "linear", "symbol": symbol, "intervalTime": "1h"}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('retCode') != 0:
            return f"Bybit API error for {symbol}: {data.get('retMsg', 'Unknown error')}\n\nNote: Binance US doesn't support futures trading."

        results = data.get('result', {}).get('list', [])

        if not results:
            return f"No open interest data available for {symbol} on Bybit\n\nNote: Binance US doesn't support futures trading."

        latest = results[0]
        oi = float(latest['openInterest'])
        timestamp = datetime.fromtimestamp(int(latest['timestamp']) / 1000)

        result_str = f"## Open Interest for {symbol} (via Bybit):\n\n"
        result_str += f"_Note: Using Bybit data since Binance US doesn't support futures trading_\n\n"
        result_str += f"**Open Interest**: {oi:,.2f} contracts\n"
        result_str += f"**Timestamp**: {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        result_str += "\n### Interpretation:\n"
        result_str += "- High OI indicates active market participation and liquidity\n"
        result_str += "- Sudden OI drops often indicate large liquidations\n"
        result_str += "- Compare OI changes with price movement for directional bias\n"
        result_str += "- Rising OI with price = new positions opening\n"
        result_str += "- Falling OI with price = positions closing (take profit or liquidations)\n"

        return result_str

    except Exception as e:
        return f"Error fetching open interest for {symbol} from Bybit: {str(e)}\n\nNote: Binance US doesn't support futures trading. Consider using Bybit, OKX, or international exchanges."


@retry_on_failure(max_retries=3, delay=2)
def get_binance_long_short_ratio(
    symbol: Annotated[str, "Trading pair symbol (e.g., 'BTCUSDT', 'ETHUSDT')"],
    period: Annotated[str, "Time period: '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d'"] = "1h",
    limit: Annotated[int, "Number of historical records"] = 10,
) -> str:
    """
    Get long/short ratio (using alternative exchanges).

    NOTE: Binance US does not support futures/derivatives trading.
    This function returns a message directing users to alternative data sources.

    This shows the ratio of long vs short positions held by top traders:
    - Ratio > 1: More accounts are long than short (bullish)
    - Ratio < 1: More accounts are short than long (bearish)
    - Extreme ratios can indicate potential reversals (contrarian indicator)

    Args:
        symbol: Trading pair (e.g., 'BTCUSDT', 'ETHUSDT')
        period: Time period for aggregation
        limit: Number of historical records

    Returns:
        Formatted string with long/short ratio history and analysis or informational message
    """
    return f"""## Long/Short Ratio Data Not Available for {symbol}

**Note**: Binance US does not support futures/derivatives trading, which means long/short ratio data is not available through Binance US.

### Alternative Data Sources:

1. **Bybit** - Offers long/short ratio data via their API
   - API: https://api.bybit.com/v5/market/account-ratio

2. **Coinglass** - Aggregates long/short data from multiple exchanges
   - Website: https://www.coinglass.com/LongShortRatio

3. **TradingView** - Charts long/short ratios from various sources

4. **Use CCXT Function**: Try `get_ccxt_funding_rates()` which supports multiple exchanges

### Recommendation:
Consider using international exchanges (Bybit, OKX, Binance International) for derivatives data while using Binance US for spot trading only.
"""


# ===== ORDER BOOK ANALYSIS =====

@retry_on_failure(max_retries=3, delay=2)
def get_order_book_imbalance(
    symbol: Annotated[str, "Trading pair symbol (e.g., 'BTCUSDT', 'ETHUSDT')"],
    depth: Annotated[int, "Order book depth to analyze"] = 20,
) -> str:
    """
    Analyze order book bid/ask imbalance from Binance US.

    Order book imbalance can indicate short-term price pressure:
    - Bid imbalance > 60%: Strong buy pressure, likely to move up
    - Bid imbalance < 40%: Strong sell pressure, likely to move down
    - Balanced (40-60%): Neutral, price discovery mode

    Args:
        symbol: Trading pair (e.g., 'BTCUSDT', 'ETHUSDT')
        depth: Number of order book levels to analyze

    Returns:
        Formatted string with order book analysis
    """
    url = f"{BINANCE_US_SPOT_API}/depth"
    params = {"symbol": symbol, "limit": depth}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Calculate total bid and ask volumes
        total_bid_volume = sum(float(bid[1]) for bid in data['bids'])
        total_ask_volume = sum(float(ask[1]) for ask in data['asks'])
        total_volume = total_bid_volume + total_ask_volume

        bid_percentage = (total_bid_volume / total_volume) * 100 if total_volume > 0 else 0
        ask_percentage = (total_ask_volume / total_volume) * 100 if total_volume > 0 else 0

        # Best bid/ask
        best_bid = float(data['bids'][0][0]) if data['bids'] else 0
        best_ask = float(data['asks'][0][0]) if data['asks'] else 0
        spread = best_ask - best_bid
        spread_pct = (spread / best_bid * 100) if best_bid > 0 else 0

        result_str = f"## Order Book Analysis for {symbol} (Top {depth} levels - Binance US):\n\n"
        result_str += f"**Best Bid**: ${best_bid:,.2f}\n"
        result_str += f"**Best Ask**: ${best_ask:,.2f}\n"
        result_str += f"**Spread**: ${spread:,.2f} ({spread_pct:.4f}%)\n\n"
        result_str += f"**Total Bid Volume**: {total_bid_volume:,.4f} ({bid_percentage:.2f}%)\n"
        result_str += f"**Total Ask Volume**: {total_ask_volume:,.4f} ({ask_percentage:.2f}%)\n\n"

        # Interpret imbalance
        if bid_percentage > 60:
            pressure = "STRONG BUY PRESSURE - More bids than asks, upward pressure likely"
        elif bid_percentage > 55:
            pressure = "Moderate buy pressure - Slightly more bids than asks"
        elif bid_percentage > 45:
            pressure = "Balanced - Price discovery mode, no clear directional pressure"
        elif bid_percentage > 40:
            pressure = "Moderate sell pressure - Slightly more asks than bids"
        else:
            pressure = "STRONG SELL PRESSURE - More asks than bids, downward pressure likely"

        result_str += f"**Order Book Imbalance**: {pressure}\n"
        result_str += "\n### Interpretation:\n"
        result_str += "- Order book imbalance shows short-term supply/demand dynamics\n"
        result_str += "- Large imbalances can indicate potential price movement direction\n"
        result_str += "- Note: Can change rapidly and doesn't account for hidden/iceberg orders\n"
        result_str += "- Best used in combination with other indicators\n"

        return result_str

    except Exception as e:
        return f"Error analyzing order book for {symbol}: {str(e)}"


# ===== TAKER BUY/SELL VOLUME =====

@retry_on_failure(max_retries=3, delay=2)
def get_taker_buysell_volume(
    symbol: Annotated[str, "Trading pair symbol (e.g., 'BTCUSDT', 'ETHUSDT')"],
    interval: Annotated[str, "Kline interval: '1m', '5m', '15m', '30m', '1h', '4h', '1d'"] = "1h",
    limit: Annotated[int, "Number of periods to analyze"] = 24,
) -> str:
    """
    Analyze taker buy vs sell volume from Binance US.

    Taker buy/sell ratio shows aggressive market orders:
    - High taker buy volume: Aggressive buying (bullish)
    - High taker sell volume: Aggressive selling (bearish)
    - Ratio > 1: More aggressive buying than selling
    - Ratio < 1: More aggressive selling than buying

    Args:
        symbol: Trading pair (e.g., 'BTCUSDT', 'ETHUSDT')
        interval: Time interval for analysis
        limit: Number of periods

    Returns:
        Formatted string with taker buy/sell analysis
    """
    url = f"{BINANCE_US_SPOT_API}/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        result_str = f"## Taker Buy/Sell Volume for {symbol} ({interval} intervals - Binance US):\n\n"

        total_taker_buy = 0
        total_taker_sell = 0

        # Analyze recent periods (last 5)
        for kline in data[-5:]:
            timestamp = datetime.fromtimestamp(int(kline[0]) / 1000)
            volume = float(kline[5])
            taker_buy_volume = float(kline[9])
            taker_sell_volume = volume - taker_buy_volume

            buy_pct = (taker_buy_volume / volume * 100) if volume > 0 else 0
            sell_pct = (taker_sell_volume / volume * 100) if volume > 0 else 0

            result_str += f"**{timestamp.strftime('%Y-%m-%d %H:%M')}**: Buy={buy_pct:.1f}%, Sell={sell_pct:.1f}%"

            if buy_pct > 55:
                result_str += " - Aggressive buying\n"
            elif sell_pct > 55:
                result_str += " - Aggressive selling\n"
            else:
                result_str += " - Balanced\n"

            total_taker_buy += taker_buy_volume
            total_taker_sell += taker_sell_volume

        # Overall statistics
        total_volume = total_taker_buy + total_taker_sell
        overall_buy_pct = (total_taker_buy / total_volume * 100) if total_volume > 0 else 0
        overall_sell_pct = (total_taker_sell / total_volume * 100) if total_volume > 0 else 0

        result_str += f"\n**Overall Taker Buy**: {overall_buy_pct:.2f}%\n"
        result_str += f"**Overall Taker Sell**: {overall_sell_pct:.2f}%\n"

        if overall_buy_pct > 55:
            sentiment = "BULLISH - Dominant aggressive buying"
        elif overall_sell_pct > 55:
            sentiment = "BEARISH - Dominant aggressive selling"
        else:
            sentiment = "NEUTRAL - Balanced buying and selling"

        result_str += f"\n**Market Sentiment**: {sentiment}\n"
        result_str += "\n### Interpretation:\n"
        result_str += "- Taker buy volume represents market orders to buy (more aggressive)\n"
        result_str += "- Taker sell volume represents market orders to sell (more aggressive)\n"
        result_str += "- Higher taker buy % indicates bullish momentum\n"
        result_str += "- Higher taker sell % indicates bearish momentum\n"
        result_str += "- Sudden shifts can signal trend changes\n"

        return result_str

    except Exception as e:
        return f"Error analyzing taker volume for {symbol}: {str(e)}"


# ===== CCXT MULTI-EXCHANGE AGGREGATION =====

def get_ccxt_funding_rates(
    symbol: Annotated[str, "Trading pair in CCXT format (e.g., 'BTC/USDT', 'ETH/USDT')"],
    exchanges: Annotated[List[str], "List of exchange names"] = None,
) -> str:
    """
    Get funding rates from multiple exchanges using CCXT.

    Compares funding rates across exchanges to identify discrepancies
    that might indicate arbitrage opportunities or market sentiment shifts.

    Args:
        symbol: Trading pair in CCXT format (e.g., 'BTC/USDT')
        exchanges: List of exchanges to check (default: ['binance', 'bybit', 'okx'])

    Returns:
        Formatted string with multi-exchange funding rate comparison
    """
    if exchanges is None:
        exchanges = ['binance', 'bybit', 'okx']

    result_str = f"## Multi-Exchange Funding Rates for {symbol}:\n\n"

    funding_rates = {}

    for exchange_name in exchanges:
        try:
            exchange_class = getattr(ccxt, exchange_name)
            exchange = exchange_class()

            # Fetch funding rate
            if hasattr(exchange, 'fetch_funding_rate'):
                funding_rate_data = exchange.fetch_funding_rate(symbol)
                rate = funding_rate_data.get('fundingRate', None)

                if rate is not None:
                    funding_rates[exchange_name] = float(rate) * 100
                    timestamp = funding_rate_data.get('timestamp', None)
                    dt = datetime.fromtimestamp(timestamp / 1000) if timestamp else datetime.now()

                    result_str += f"**{exchange_name.capitalize()}**: {float(rate) * 100:.4f}% (updated: {dt.strftime('%H:%M UTC')})\n"

        except Exception as e:
            result_str += f"**{exchange_name.capitalize()}**: Unable to fetch - {str(e)[:50]}\n"

    if funding_rates:
        avg_rate = sum(funding_rates.values()) / len(funding_rates)
        max_exchange = max(funding_rates, key=funding_rates.get)
        min_exchange = min(funding_rates, key=funding_rates.get)
        spread = funding_rates[max_exchange] - funding_rates[min_exchange]

        result_str += f"\n**Average Funding Rate**: {avg_rate:.4f}%\n"
        result_str += f"**Highest**: {max_exchange.capitalize()} ({funding_rates[max_exchange]:.4f}%)\n"
        result_str += f"**Lowest**: {min_exchange.capitalize()} ({funding_rates[min_exchange]:.4f}%)\n"
        result_str += f"**Spread**: {spread:.4f}%\n"

        result_str += "\n### Interpretation:\n"
        result_str += "- Funding rate convergence across exchanges indicates market consensus\n"
        result_str += "- Large spreads may indicate arbitrage opportunities\n"
        result_str += "- Consistent positive/negative rates show directional bias\n"

    return result_str


# ===== HELPER FUNCTIONS =====

def normalize_symbol_for_binance(symbol: str) -> str:
    """
    Normalize symbol format for Binance API.

    Examples:
        'BTC-USD' -> 'BTCUSDT'
        'BTC/USDT' -> 'BTCUSDT'
        'BTCUSDT' -> 'BTCUSDT'
    """
    symbol = symbol.upper().replace('-', '').replace('/', '').replace('_', '')

    # Handle common conversions
    if symbol.endswith('USD') and not symbol.endswith('USDT'):
        symbol = symbol[:-3] + 'USDT'

    return symbol


def normalize_symbol_for_ccxt(symbol: str) -> str:
    """
    Normalize symbol format for CCXT.

    Examples:
        'BTCUSDT' -> 'BTC/USDT'
        'BTC-USD' -> 'BTC/USD'
        'BTC/USDT' -> 'BTC/USDT'
    """
    symbol = symbol.upper()

    if '/' in symbol:
        return symbol

    # Try to split common patterns
    if 'USDT' in symbol:
        base = symbol.replace('USDT', '')
        return f"{base}/USDT"
    elif 'USD' in symbol:
        base = symbol.replace('USD', '')
        return f"{base}/USD"
    elif 'BTC' in symbol and symbol != 'BTC':
        # Altcoin/BTC pairs
        base = symbol.replace('BTC', '')
        return f"{base}/BTC"

    return symbol
