"""
Phase 4 - Pure Trend-Following Strategy

CRITICAL STRATEGY SHIFT from Phase 3/3.1/3.2:
- Phase 3.x: Contrarian (buy fear, sell greed) → FAILED (-0.10% return, 25% win rate)
- Phase 4: Trend-Following (buy strength, ride momentum) → NEW APPROACH

Key Philosophy Changes:
1. BUY when price > MAs (uptrend confirmed), NOT when Fear Index < 40
2. ENTRY on momentum signals (MACD cross, RSI > 50), NOT on fear/oversold
3. EXIT on trailing stop (20-day MA break), NOT fixed +7% target
4. HOLD during downtrends, NO TRADES when price < 50-day MA
5. Let winners run (no profit cap), cut losers tight (2-3% stop)

Expected Improvements:
- Win rate: 40-50% (vs 25% contrarian)
- Avg win: +15-25% (vs +7% capped)
- Avg loss: -2 to -3% (vs -3.5%)
- Risk:Reward: 5:1 to 8:1 (vs 2:1)
- Return: +2.5% to +4% (vs -0.10%)
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict
import shutil

# Import the Phase 4 decide function
from run_decision_phase4_simple import decide
import yfinance as yf


class Phase4TrendFollowingBacktest:
    """Phase 4 backtest with pure trend-following strategy."""

    def __init__(self, initial_capital: float = 10000.0, base_risk: float = 0.02):
        """
        Initialize Phase 4 trend-following backtest.

        Args:
            initial_capital: Starting capital in USD
            base_risk: Base risk percentage per trade (0.02 = 2%)
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.base_risk = base_risk
        self.trades = []
        self.equity_curve = []
        self.conviction_tracker = {'high': 0, 'medium': 0, 'low': 0}
        self.blocked_trades = {'downtrend_filter': 0, 'no_momentum_filter': 0}

    def _clean_memory(self):
        """Clean up persistent vector database between backtest runs."""
        chroma_dirs = ["./chroma_db", "./.chroma", "./bull_memory", "./bear_memory"]
        for dir_path in chroma_dirs:
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                    print(f"   Cleaned: {dir_path}")
                except Exception as e:
                    print(f"   Warning: Could not clean {dir_path}: {e}")

    def _get_next_business_day(self, current_date: pd.Timestamp, price_data: pd.DataFrame) -> pd.Timestamp:
        """Get the next available trading day after current_date."""
        available_dates = price_data.index
        next_day = current_date + timedelta(days=1)

        # Find the next available date
        idx = available_dates.searchsorted(next_day)

        if idx < len(available_dates):
            return available_dates[idx]
        else:
            return available_dates[-1]

    def check_trend_entry_signal(self, price_data: pd.DataFrame, current_date: pd.Timestamp) -> tuple:
        """
        PHASE 4 TREND-FOLLOWING ENTRY SIGNAL.

        Entry criteria (ALL must be true):
        1. Uptrend: Price > 50-MA > 200-MA (golden cross)
        2. Momentum: RSI > 50 AND MACD > Signal
        3. NOT overbought: RSI < 70 OR price not within 3% of 30-day high

        Returns:
            (allow_entry: bool, signal_strength: str, details: str)
        """
        try:
            # Normalize current_date to match price_data index (handle timezone)
            if hasattr(price_data.index, 'tz') and price_data.index.tz is not None:
                # price_data has timezone, localize current_date
                if not hasattr(current_date, 'tz') or current_date.tz is None:
                    current_date = current_date.tz_localize(price_data.index.tz)
            else:
                # price_data has no timezone, remove from current_date if present
                if hasattr(current_date, 'tz') and current_date.tz is not None:
                    current_date = current_date.tz_localize(None)

            # Ensure current_date is in the index
            if current_date not in price_data.index:
                # Find the closest date
                idx = price_data.index.searchsorted(current_date)
                if idx >= len(price_data):
                    idx = len(price_data) - 1
                current_date = price_data.index[idx]

            # Calculate indicators
            ma_50 = price_data['Close'].rolling(50).mean()
            ma_200 = price_data['Close'].rolling(200).mean()

            current_price = price_data.loc[current_date, 'Close']
            current_ma50 = ma_50.loc[current_date]
            current_ma200 = ma_200.loc[current_date]

            # RSI
            delta = price_data['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.loc[current_date]

            # MACD (12, 26, 9)
            exp1 = price_data['Close'].ewm(span=12, adjust=False).mean()
            exp2 = price_data['Close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            current_macd = macd.loc[current_date]
            current_signal = signal.loc[current_date]

            # Overbought check
            recent_high = price_data['High'].loc[:current_date].tail(30).max()
            pct_from_high = ((current_price / recent_high) - 1) * 100

            # Extract scalar values from Series for boolean operations
            current_price_val = float(current_price)
            current_ma50_val = float(current_ma50)
            current_ma200_val = float(current_ma200)
            current_rsi_val = float(current_rsi)
            current_macd_val = float(current_macd)
            current_signal_val = float(current_signal)

            # 1. Uptrend check
            uptrend = (current_price_val > current_ma50_val) and (current_ma50_val > current_ma200_val)

            # 2. Momentum check
            momentum_positive = (current_rsi_val > 50) and (current_macd_val > current_signal_val)

            # 3. NOT strongly overbought
            not_overbought = (current_rsi_val < 70) or (pct_from_high < -3.0)

            # Determine signal strength
            if uptrend and momentum_positive and not_overbought:
                signal_strength = "STRONG"
                details = (f"Uptrend: ${current_price_val:,.0f} > ${current_ma50_val:,.0f} > ${current_ma200_val:,.0f}, "
                          f"RSI: {current_rsi_val:.1f}, MACD: {current_macd_val:.2f} > {current_signal_val:.2f}")
                allow_entry = True
            elif uptrend and momentum_positive:
                signal_strength = "MODERATE"
                details = f"Uptrend + Momentum but overbought (RSI {current_rsi_val:.1f})"
                allow_entry = True  # Still allow but will downgrade conviction
            elif uptrend:
                signal_strength = "WEAK"
                details = f"Uptrend confirmed but no momentum (RSI {current_rsi_val:.1f}, MACD bearish)"
                allow_entry = False  # Wait for momentum
            else:
                signal_strength = "NO_TREND"
                details = f"Downtrend or sideways: Price ${current_price_val:,.0f} < MA50 ${current_ma50_val:,.0f}"
                allow_entry = False

            return allow_entry, signal_strength, details

        except Exception as e:
            print(f"   ⚠️  Entry signal check error: {e}")
            return False, "ERROR", str(e)

    def calculate_trailing_stop(self, price_data: pd.DataFrame, entry_date: pd.Timestamp) -> float:
        """
        Calculate trailing stop based on 20-day MA.

        Phase 4: Use 20-day MA as trailing stop (dynamic, follows price up)
        """
        ma_20 = price_data['Close'].rolling(20).mean()
        current_ma20 = ma_20.loc[entry_date]
        return float(current_ma20)

    def _calculate_position_size(self, conviction: str, entry_price: float, stop_loss: float) -> tuple:
        """
        Calculate position size based on conviction and stop distance.

        Phase 4: Risk-based sizing using actual stop distance

        Args:
            conviction: "high", "medium", or "low"
            entry_price: Entry price for the trade
            stop_loss: Stop loss price

        Returns:
            (risk_amount, position_size, risk_pct)
        """
        # Risk per trade based on conviction
        risk_pct_map = {
            'high': 0.03,    # 3% risk
            'medium': 0.02,  # 2% risk
            'low': 0.01      # 1% risk
        }

        risk_pct = risk_pct_map.get(conviction.lower(), 0.02)
        risk_amount = self.capital * risk_pct

        # Calculate position size based on stop distance
        stop_distance = abs(entry_price - stop_loss)
        position_size = risk_amount / stop_distance if stop_distance > 0 else 0

        return risk_amount, position_size, risk_pct

    def _execute_trade_with_stops(self, decision: Dict, decision_date: str, price_data: pd.DataFrame):
        """
        Execute trade with PHASE 4 TREND-FOLLOWING logic.

        Key differences from Phase 3.2:
        1. Entry only on uptrend + momentum (not fear-based)
        2. Trailing stop (20-day MA) instead of fixed -3.5%
        3. No take profit target - ride trend until it breaks
        4. Tighter initial stop (-2 to -3%) based on volatility
        """
        action = decision.get("action", "HOLD").upper()

        if action == "HOLD":
            print(f"   Decision: HOLD - No trade executed")
            return

        if action != "BUY":
            print(f"   Skipping {action} - currently only supporting BUY trades")
            return

        # Get conviction level
        conviction = decision.get("conviction", "medium").lower()
        self.conviction_tracker[conviction] = self.conviction_tracker.get(conviction, 0) + 1

        decision_dt = pd.to_datetime(decision_date)

        # PHASE 4: Check TREND-FOLLOWING entry signal
        print(f"\n   🔍 PHASE 4 TREND-FOLLOWING FILTERS:")

        allow_entry, signal_strength, details = self.check_trend_entry_signal(price_data, decision_dt)
        print(f"   📊 Signal Strength: {signal_strength}")
        print(f"      {details}")

        if not allow_entry:
            if signal_strength == "NO_TREND":
                print(f"   ❌ DOWNTREND FILTER BLOCKED: No uptrend confirmed")
                self.blocked_trades['downtrend_filter'] += 1
            else:
                print(f"   ❌ MOMENTUM FILTER BLOCKED: Uptrend exists but no momentum")
                self.blocked_trades['no_momentum_filter'] += 1
            return

        # Downgrade conviction if signal is only MODERATE
        if signal_strength == "MODERATE" and conviction == "high":
            print(f"   ⚠️  Signal is MODERATE (overbought): Downgrading HIGH → MEDIUM conviction")
            conviction = "medium"
            self.conviction_tracker['high'] -= 1
            self.conviction_tracker['medium'] += 1

        print(f"   ✅ Entry signal CONFIRMED: {signal_strength} trend-following setup")

        # Entry at next business day
        entry_date = self._get_next_business_day(decision_dt, price_data)

        try:
            entry_price = float(price_data.loc[entry_date, 'Open'])
        except (KeyError, IndexError) as e:
            print(f"   ❌ Entry price not available for {entry_date}: {e}")
            return

        # Calculate initial stop loss (2.5% below entry, tighter than Phase 3.2's 3.5%)
        initial_stop_loss = entry_price * 0.975  # -2.5% initial stop

        # Calculate position size based on stop distance
        risk_amount, position_size, risk_pct = self._calculate_position_size(
            conviction, entry_price, initial_stop_loss
        )

        # Calculate trailing stop (20-day MA)
        trailing_stop = self.calculate_trailing_stop(price_data, entry_date)

        # Use the tighter of initial stop or 20-day MA
        stop_loss = max(initial_stop_loss, trailing_stop)

        print(f"\n   🎯 TRADE SETUP (TREND-FOLLOWING):")
        print(f"   Action: {action}")
        print(f"   Signal: {signal_strength}")
        print(f"   Conviction: {conviction.upper()} (Risk: {risk_pct*100:.1f}%)")
        print(f"   Entry Date: {entry_date.strftime('%Y-%m-%d')}")
        print(f"   Entry Price: ${entry_price:,.2f}")
        print(f"   Position Size: {position_size:.6f} BTC (${risk_amount:,.2f})")
        print(f"   Initial Stop: ${initial_stop_loss:,.2f} (-2.5%)")
        print(f"   Trailing Stop (20-MA): ${trailing_stop:,.2f}")
        print(f"   Active Stop: ${stop_loss:,.2f}")
        print(f"   Take Profit: NONE (trailing stop only)")

        # Monitor trade with trailing stop (no max holding period - ride the trend)
        exit_price = None
        exit_date = None
        exit_reason = None

        available_dates = price_data.index
        entry_idx = available_dates.get_loc(entry_date)

        # Track trade day by day
        for i in range(entry_idx + 1, len(available_dates)):
            current_date = available_dates[i]
            day_low = price_data.loc[current_date, 'Low']
            day_high = price_data.loc[current_date, 'High']
            day_close = price_data.loc[current_date, 'Close']

            # Update trailing stop (20-day MA)
            ma_20 = price_data['Close'].loc[:current_date].rolling(20).mean()
            new_trailing_stop = float(ma_20.iloc[-1])

            # Only move stop UP, never down (trailing)
            if new_trailing_stop > stop_loss:
                stop_loss = new_trailing_stop

            # Check if stop hit
            if day_low <= stop_loss:
                exit_price = stop_loss
                exit_date = current_date
                exit_reason = "Trailing Stop Hit (20-day MA)"
                break

            # Check 50-day MA break (major trend reversal)
            ma_50 = price_data['Close'].loc[:current_date].rolling(50).mean()
            current_ma50 = float(ma_50.iloc[-1])

            if day_close < current_ma50:
                exit_price = day_close
                exit_date = current_date
                exit_reason = "50-day MA Break (Trend Reversal)"
                break

        # If no exit triggered, close at end of data
        if exit_price is None:
            exit_date = available_dates[-1]
            exit_price = float(price_data.loc[exit_date, 'Close'])
            exit_reason = "End of Data"

        # Calculate P&L
        pnl = (exit_price - entry_price) * position_size
        pnl_pct = ((exit_price / entry_price) - 1) * 100

        result = "WIN" if pnl > 0 else "LOSS"

        print(f"\n   📤 EXIT:")
        print(f"   Exit Date: {exit_date.strftime('%Y-%m-%d')}")
        print(f"   Exit Price: ${exit_price:,.2f}")
        print(f"   Exit Reason: {exit_reason}")
        print(f"   Final Trailing Stop: ${stop_loss:,.2f}")
        print(f"   P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%) - {result}")

        # Update capital
        self.capital += pnl

        # Record trade
        self.trades.append({
            'decision_date': decision_date,
            'entry_date': entry_date.strftime('%Y-%m-%d'),
            'exit_date': exit_date.strftime('%Y-%m-%d'),
            'action': action,
            'signal_strength': signal_strength,
            'conviction': conviction,
            'risk_pct': risk_pct,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'initial_stop_loss': initial_stop_loss,
            'final_trailing_stop': stop_loss,
            'position_size': position_size,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'exit_reason': exit_reason,
            'result': result
        })

        self.equity_curve.append({
            'date': exit_date.strftime('%Y-%m-%d'),
            'capital': self.capital
        })

    def run_backtest(self, symbol: str, start_date: str, end_date: str) -> Dict:
        """
        Run Phase 4 trend-following backtest.

        Args:
            symbol: Trading symbol (e.g., 'BTC-USD')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format

        Returns:
            Dict with backtest results
        """
        print("🚀 Running Phase 4 TREND-FOLLOWING Backtest")
        print()
        print("=" * 80)
        print("🔄 PHASE 4 - STRATEGY OVERHAUL: CONTRARIAN → TREND-FOLLOWING")
        print("=" * 80)
        print(f"Symbol: {symbol}")
        print(f"Period: {start_date} to {end_date}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Base Risk per Trade: {self.base_risk*100:.1f}%")
        print()
        print("⚡ PHASE 4 CRITICAL STRATEGY CHANGES:")
        print("  1. 🔄 BUY STRENGTH not fear (Price > MAs, RSI > 50, MACD positive)")
        print("  2. 🔄 ENTRY on momentum signals (not Fear Index < 40)")
        print("  3. 🔄 TRAILING STOP (20-day MA) instead of fixed stop")
        print("  4. 🔄 NO TAKE PROFIT - ride trend until break")
        print("  5. 🔄 TIGHTER initial stop (-2.5% vs -3.5%)")
        print("  6. 🔄 HOLD during downtrends (no contrarian catches)")
        print()
        print("📊 Why This Should Work:")
        print("  - Avoids falling knives (Trade 1, 7, 8 from Phase 3.2)")
        print("  - Lets winners run (no +7% cap)")
        print("  - Exits on trend breaks (not arbitrary time stops)")
        print("  - Targets 40-50% win rate, 5:1+ R:R ratio")
        print("=" * 80)
        print()

        # Clean memory
        print("🧹 Cleaning persistent memory...")
        self._clean_memory()
        print()

        # Fetch price data
        print(f"📥 Fetching price data for {symbol}...")
        ticker = yf.Ticker(symbol)
        price_data = ticker.history(start=start_date, end=end_date, interval='1d')

        if price_data.empty:
            print(f"❌ No data available for {symbol}")
            return {}

        print(f"✅ Fetched {len(price_data)} days of data")
        print()

        # Generate weekly decision dates (Fridays)
        decision_dates = pd.date_range(start=start_date, end=end_date, freq='W-FRI')
        decision_dates = [d.strftime('%Y-%m-%d') for d in decision_dates if d.strftime('%Y-%m-%d') in price_data.index.strftime('%Y-%m-%d')]

        print(f"📅 Generated {len(decision_dates)} weekly decision points")
        print()

        # Run backtest
        for i, decision_date in enumerate(decision_dates, 1):
            print(f"\n{'='*80}")
            print(f"Decision #{i}/{len(decision_dates)}: {decision_date}")
            print(f"Capital: ${self.capital:,.2f}")
            print(f"{'='*80}")

            # Get agent decision
            print("\n🤖 Running multi-agent decision system...")
            decision = decide(
                company_ticker=symbol,
                decision_date=decision_date,
                online_mode=True
            )

            print(f"\n💡 Agent Decision: {decision.get('action', 'HOLD')} (Conviction: {decision.get('conviction', 'N/A')})")

            # Execute trade
            self._execute_trade_with_stops(decision, decision_date, price_data)

        # Calculate final metrics
        print("\n" + "="*80)
        print("📊 Calculating final metrics...")
        print("="*80)

        total_trades = len(self.trades)
        wins = [t for t in self.trades if t['result'] == 'WIN']
        losses = [t for t in self.trades if t['result'] == 'LOSS']

        win_rate = (len(wins) / total_trades * 100) if total_trades > 0 else 0
        avg_win = np.mean([t['pnl'] for t in wins]) if wins else 0
        avg_loss = np.mean([t['pnl'] for t in losses]) if losses else 0

        total_return_pct = ((self.capital - self.initial_capital) / self.initial_capital) * 100

        # Buy & Hold return
        buy_hold_return_pct = ((price_data['Close'].iloc[-1] / price_data['Close'].iloc[0]) - 1) * 100

        # Sharpe ratio
        if self.trades:
            returns = [t['pnl_pct'] for t in self.trades]
            sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(52) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0

        # Max drawdown
        equity = [self.initial_capital] + [t['pnl'] for t in self.trades]
        cumulative = np.cumsum(equity)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max * 100
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0

        results = {
            'symbol': symbol,
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_return_pct': total_return_pct,
            'buy_hold_return_pct': buy_hold_return_pct,
            'total_trades': total_trades,
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'conviction_distribution': self.conviction_tracker,
            'blocked_trades': self.blocked_trades
        }

        self._print_results(results)
        self._save_results(results, symbol)

        return results

    def _print_results(self, results: Dict):
        """Print formatted backtest results with Phase comparison."""

        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 18 + "PHASE 4 TREND-FOLLOWING BACKTEST RESULTS" + " " * 20 + "║")
        print("╠" + "=" * 78 + "╣")
        print(f"║  Symbol: {results['symbol']:<68} ║")
        print("╠" + "=" * 78 + "╣")
        print(f"║  Initial Capital:        ${results['initial_capital']:>16,.2f}" + " " * 25 + "║")
        print(f"║  Final Capital:          ${results['final_capital']:>16,.2f}" + " " * 25 + "║")
        print(f"║  Total Return:                        {results['total_return_pct']:>6.2f}%" + " " * 25 + "║")
        print(f"║  Buy & Hold Return:                   {results['buy_hold_return_pct']:>6.2f}%" + " " * 25 + "║")
        print("╠" + "=" * 78 + "╣")
        print(f"║  Total Trades:                              {results['total_trades']:>4}" + " " * 27 + "║")
        print(f"║  Wins / Losses:                     {results['wins']:>4} / {results['losses']:<4}" + " " * 25 + "║")
        print(f"║  Win Rate:                            {results['win_rate']:>6.1f}%" + " " * 25 + "║")
        print(f"║  Average Win:            ${results['avg_win']:>16.2f}" + " " * 25 + "║")
        print(f"║  Average Loss:           ${results['avg_loss']:>16.2f}" + " " * 25 + "║")
        print("╠" + "=" * 78 + "╣")
        print(f"║  Sharpe Ratio:                            {results['sharpe_ratio']:>6.2f}" + " " * 26 + "║")
        print(f"║  Max Drawdown:                            {results['max_drawdown']:>6.2f}%" + " " * 25 + "║")
        print("╚" + "=" * 78 + "╝")
        print()

        # Multi-phase comparison
        print("📈 PHASE 4 vs PHASE 3.2 vs PHASE 3.1 COMPARISON:")
        print()

        phase32_return = -0.10
        phase32_winrate = 25.0
        phase32_sharpe = -1.03

        phase31_return = -0.00
        phase31_winrate = 25.0
        phase31_sharpe = 0.00

        # Return comparison
        if results['total_return_pct'] > 0:
            print(f"   ✅ Phase 4 Return: {results['total_return_pct']:+.2f}% (PROFITABLE)")
        else:
            print(f"   ❌ Phase 4 Return: {results['total_return_pct']:+.2f}% (UNPROFITABLE)")

        print(f"      Phase 3.2: {phase32_return:+.2f}%")
        print(f"      Phase 3.1: {phase31_return:+.2f}%")
        print(f"      Improvement: {results['total_return_pct'] - phase32_return:+.2f}% vs Phase 3.2")
        print()

        # Win rate comparison
        if results['win_rate'] > phase32_winrate:
            print(f"   ✅ Phase 4 Win Rate: {results['win_rate']:.1f}% (IMPROVED)")
        else:
            print(f"   ❌ Phase 4 Win Rate: {results['win_rate']:.1f}% (SAME/WORSE)")

        print(f"      Phase 3.2: {phase32_winrate:.1f}%")
        print(f"      Phase 3.1: {phase31_winrate:.1f}%")
        print(f"      Improvement: {results['win_rate'] - phase32_winrate:+.1f}% vs Phase 3.2")
        print()

        # Sharpe comparison
        if results['sharpe_ratio'] > 1.0:
            print(f"   ✅ Phase 4 Sharpe: {results['sharpe_ratio']:.2f} (GOOD RISK-ADJUSTED)")
        elif results['sharpe_ratio'] > 0:
            print(f"   ⚠️  Phase 4 Sharpe: {results['sharpe_ratio']:.2f} (MARGINAL)")
        else:
            print(f"   ❌ Phase 4 Sharpe: {results['sharpe_ratio']:.2f} (POOR)")

        print(f"      Phase 3.2: {phase32_sharpe:.2f}")
        print(f"      Phase 3.1: {phase31_sharpe:.2f}")
        print()

        # Conviction distribution
        print("🔍 CONVICTION DISTRIBUTION:")
        total_attempts = sum(results['conviction_distribution'].values())
        if total_attempts > 0:
            for level in ['high', 'medium', 'low']:
                count = results['conviction_distribution'].get(level, 0)
                pct = (count / total_attempts) * 100
                print(f"   {level.upper()}: {count}/{total_attempts} ({pct:.1f}%)")
        print()

        # Blocked trades
        print("🚫 BLOCKED TRADES (Trend-Following Filters):")
        print(f"   Downtrend Filter: {results['blocked_trades']['downtrend_filter']} trades blocked")
        print(f"   No Momentum Filter: {results['blocked_trades']['no_momentum_filter']} trades blocked")
        total_blocked = sum(results['blocked_trades'].values())
        print(f"   Total Blocked: {total_blocked} trades")
        print()

        # vs Buy & Hold
        if results['total_return_pct'] > results['buy_hold_return_pct']:
            outperform = results['total_return_pct'] - results['buy_hold_return_pct']
            print(f"   🎉 Strategy OUTPERFORMED Buy & Hold by {outperform:+.2f}%")
        else:
            underperform = results['buy_hold_return_pct'] - results['total_return_pct']
            print(f"   ⚠️  Strategy underperformed Buy & Hold by {underperform:.2f}%")

        print()

    def _save_results(self, results: Dict, symbol: str):
        """Save backtest results and trade details."""

        output_dir = f"eval_results/phase4_trend_following/{symbol}"
        os.makedirs(output_dir, exist_ok=True)

        # Save summary
        results_file = f"{output_dir}/backtest_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        # Save trades
        if self.trades:
            trades_df = pd.DataFrame(self.trades)
            trades_file = f"{output_dir}/trades_detail.csv"
            trades_df.to_csv(trades_file, index=False)
            print(f"\n💾 Results saved to: {output_dir}/")


def main():
    """Run Phase 4 trend-following backtest."""

    backtest = Phase4TrendFollowingBacktest(
        initial_capital=10000.0,
        base_risk=0.02
    )

    # Run on full year 2024
    results = backtest.run_backtest(
        symbol="BTC-USD",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )

    return results


if __name__ == "__main__":
    results = main()
