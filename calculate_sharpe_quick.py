"""
Quick Sharpe Ratio Calculator

This script calculates Sharpe ratio and other metrics from existing trading decisions
or by running a quick backtest with minimal agent calls.
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf


def calculate_sharpe_from_returns(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    Calculate annualized Sharpe ratio from returns.

    Args:
        returns: Series of daily returns
        risk_free_rate: Annual risk-free rate (default 2%)

    Returns:
        Annualized Sharpe ratio
    """
    if len(returns) == 0 or returns.std() == 0:
        return 0.0

    # Calculate excess returns
    daily_rf_rate = (1 + risk_free_rate) ** (1 / 252) - 1
    excess_returns = returns - daily_rf_rate

    # Annualize
    sharpe = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)

    return sharpe


def simple_strategy_backtest(symbol: str = "BTC-USD", days: int = 30):
    """
    Quick strategy backtest using simple buy-and-hold with the agent's recommended entry/exit.

    Args:
        symbol: Trading symbol
        days: Number of days to backtest

    Returns:
        Performance metrics including Sharpe ratio
    """
    print("=" * 80)
    print("📊 QUICK SHARPE RATIO CALCULATION")
    print("=" * 80)
    print(f"Symbol: {symbol}")
    print(f"Lookback Period: {days} days")
    print("=" * 80)
    print()

    # Get price data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    print(f"📥 Downloading price data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")

    try:
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)
    except Exception as e:
        print(f"❌ Error downloading data: {e}")
        return None

    if data.empty:
        print(f"❌ No data available for {symbol}")
        return None

    print(f"✅ Downloaded {len(data)} days of data")
    print()

    # Calculate daily returns
    data['Returns'] = data['Close'].pct_change()

    # Strategy 1: Buy & Hold
    buy_hold_return = float((data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100)
    buy_hold_sharpe = calculate_sharpe_from_returns(data['Returns'].dropna())

    # Strategy 2: Simple Moving Average Crossover (as proxy for agent strategy)
    # This simulates a basic trend-following strategy similar to what agents might do
    data['SMA_10'] = data['Close'].rolling(window=10).mean()
    data['SMA_30'] = data['Close'].rolling(window=30).mean()
    data['Signal'] = 0
    data.loc[data['SMA_10'] > data['SMA_30'], 'Signal'] = 1  # Buy signal
    data.loc[data['SMA_10'] <= data['SMA_30'], 'Signal'] = -1  # Sell signal

    # Calculate strategy returns
    data['Strategy_Returns'] = data['Signal'].shift(1) * data['Returns']
    strategy_return = float((data['Strategy_Returns'].sum()) * 100)
    strategy_sharpe = calculate_sharpe_from_returns(data['Strategy_Returns'].dropna())

    # Calculate max drawdown
    data['Cumulative'] = (1 + data['Returns']).cumprod()
    data['Cumulative_Max'] = data['Cumulative'].cummax()
    data['Drawdown'] = (data['Cumulative'] - data['Cumulative_Max']) / data['Cumulative_Max']
    max_drawdown = float(data['Drawdown'].min() * 100)

    data['Strategy_Cumulative'] = (1 + data['Strategy_Returns']).cumprod()
    data['Strategy_Cumulative_Max'] = data['Strategy_Cumulative'].cummax()
    data['Strategy_Drawdown'] = (data['Strategy_Cumulative'] - data['Strategy_Cumulative_Max']) / data['Strategy_Cumulative_Max']
    strategy_max_drawdown = float(data['Strategy_Drawdown'].min() * 100)

    # Volatility (annualized)
    volatility = float(data['Returns'].std() * np.sqrt(252) * 100)
    strategy_volatility = float(data['Strategy_Returns'].std() * np.sqrt(252) * 100)

    # Print results
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 25 + "PERFORMANCE METRICS" + " " * 34 + "║")
    print("╠" + "═" * 78 + "╣")
    print(f"║  Symbol: {symbol:30}                                     ║")
    print(f"║  Period: {len(data)} days                                                        ║")
    print("╠" + "═" * 78 + "╣")
    print()
    print("  BUY & HOLD STRATEGY:")
    print(f"  ├─ Total Return:       {buy_hold_return:>10.2f}%")
    print(f"  ├─ Sharpe Ratio:       {buy_hold_sharpe:>10.2f}")
    print(f"  ├─ Max Drawdown:       {max_drawdown:>10.2f}%")
    print(f"  └─ Volatility (ann):   {volatility:>10.2f}%")
    print()
    print("  TREND-FOLLOWING STRATEGY (SMA Crossover - Agent Proxy):")
    print(f"  ├─ Total Return:       {strategy_return:>10.2f}%")
    print(f"  ├─ Sharpe Ratio:       {strategy_sharpe:>10.2f}")
    print(f"  ├─ Max Drawdown:       {strategy_max_drawdown:>10.2f}%")
    print(f"  └─ Volatility (ann):   {strategy_volatility:>10.2f}%")
    print()
    print("╚" + "═" * 78 + "╝")
    print()

    # Interpretation
    print("📈 SHARPE RATIO INTERPRETATION:")
    print()
    print("   Sharpe Ratio Scale:")
    print("   ─────────────────────────────────────────")
    print("   < 0.5   : Poor - Risk not adequately compensated")
    print("   0.5-1.0 : Good - Acceptable risk-adjusted returns")
    print("   1.0-2.0 : Very Good - Strong risk-adjusted performance")
    print("   > 2.0   : Excellent - Exceptional risk-adjusted returns")
    print()

    if strategy_sharpe > buy_hold_sharpe:
        improvement = ((strategy_sharpe - buy_hold_sharpe) / abs(buy_hold_sharpe) * 100) if buy_hold_sharpe != 0 else 100
        print(f"   ✅ Trend-following strategy has better Sharpe ratio ({strategy_sharpe:.2f} vs {buy_hold_sharpe:.2f})")
        print(f"      Risk-adjusted returns improved by {improvement:.1f}%")
    else:
        print(f"   ⚠️  Buy & Hold has better Sharpe ratio ({buy_hold_sharpe:.2f} vs {strategy_sharpe:.2f})")
        print(f"      Strategy needs optimization for better risk-adjusted returns")
    print()

    # Save results
    results = {
        'symbol': symbol,
        'period_days': len(data),
        'start_date': str(data.index[0]),
        'end_date': str(data.index[-1]),
        'buy_hold': {
            'total_return_pct': float(buy_hold_return),
            'sharpe_ratio': float(buy_hold_sharpe),
            'max_drawdown_pct': float(max_drawdown),
            'volatility_pct': float(volatility)
        },
        'strategy': {
            'total_return_pct': float(strategy_return),
            'sharpe_ratio': float(strategy_sharpe),
            'max_drawdown_pct': float(strategy_max_drawdown),
            'volatility_pct': float(strategy_volatility)
        },
        'timestamp': datetime.now().isoformat()
    }

    # Save to file
    os.makedirs("backtest_results", exist_ok=True)
    output_file = f"backtest_results/sharpe_analysis_{symbol.replace('/', '-')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"💾 Results saved to: {output_file}")
    print()

    return results


def main():
    """Run quick Sharpe ratio calculation."""
    # Test with BTC-USD
    print("Testing with BTC-USD (30 days)...")
    btc_results = simple_strategy_backtest("BTC-USD", days=30)

    print("\n" + "=" * 80)
    print("\nTesting with traditional asset for comparison...")
    spy_results = simple_strategy_backtest("SPY", days=30)

    print("\n" + "=" * 80)
    print("📊 COMPARATIVE ANALYSIS:")
    print("=" * 80)

    if btc_results and spy_results:
        print(f"\nBTC-USD Sharpe: {btc_results['strategy']['sharpe_ratio']:.2f}")
        print(f"SPY Sharpe:     {spy_results['strategy']['sharpe_ratio']:.2f}")
        print()

        if btc_results['strategy']['sharpe_ratio'] > spy_results['strategy']['sharpe_ratio']:
            print("✅ Crypto strategy shows better risk-adjusted returns than traditional markets")
        else:
            print("⚠️  Traditional markets show better risk-adjusted returns")

    return btc_results, spy_results


if __name__ == "__main__":
    main()
