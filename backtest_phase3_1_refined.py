"""
Phase 3.1 Refined Backtest - Fixed Execution + Risk Management

Key Improvements over Phase 3:
1. Fixed execution timing (entry at Monday open, not Friday close)
2. Stop loss (-2%) and take profit (+6%) with intraday monitoring
3. Conviction-based position sizing (1-3% risk)
4. Improved agent prompts with trend confirmation and overbought filters
5. Better exit logic (stop/target/time-based)

Goal: Turn Phase 3's -0.05% return into 1.5-3.5% with better risk management
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict
import shutil

# Import the decide function
from run_decision import decide
import yfinance as yf


class Phase31RefinedBacktest:
    """Phase 3.1 backtest with refined execution and risk management."""

    def __init__(self, initial_capital: float = 10000.0, base_risk: float = 0.02):
        """
        Initialize Phase 3.1 backtest.

        Args:
            initial_capital: Starting capital in USD
            base_risk: Base risk percentage per trade (0.02 = 2%)
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.base_risk = base_risk
        self.trades = []
        self.equity_curve = []

    def _clean_memory(self):
        """Clean up persistent vector database between backtest runs."""
        chroma_dirs = ["./chroma_db", "./.chroma", "./bull_memory", "./bear_memory"]
        for dir_path in chroma_dirs:
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                    print(f"   🧹 Cleaned memory: {dir_path}")
                except Exception as e:
                    print(f"   ⚠️  Could not clean {dir_path}: {e}")

    def _get_next_business_day(self, date: pd.Timestamp, price_data: pd.DataFrame) -> pd.Timestamp:
        """
        Get the next business day after the given date.

        Args:
            date: Starting date
            price_data: Price DataFrame with DatetimeIndex

        Returns:
            Next available trading day
        """
        # Start from the day after the decision date
        next_day = date + timedelta(days=1)

        # Find the next available date in price_data
        available_dates = price_data.index

        # Search for the next date >= next_day
        idx = available_dates.searchsorted(next_day)

        if idx < len(available_dates):
            return available_dates[idx]
        else:
            # If no data after this date, use the last available date
            return available_dates[-1]

    def _calculate_position_size(self, conviction: str, entry_price: float) -> tuple:
        """
        Calculate position size based on conviction level.

        Args:
            conviction: "high", "medium", or "low"
            entry_price: Entry price for the trade

        Returns:
            (risk_amount, position_size, risk_pct)
        """
        # 3-Tier conviction-based sizing
        if conviction == "high":
            risk_pct = 0.03  # 3% risk
        elif conviction == "low":
            risk_pct = 0.01  # 1% risk
        else:  # medium or default
            risk_pct = 0.02  # 2% risk (baseline)

        risk_amount = self.capital * risk_pct
        position_size = risk_amount / entry_price if entry_price > 0 else 0

        return risk_amount, position_size, risk_pct

    def _execute_trade_with_stops(self, decision: Dict, decision_date: str, price_data: pd.DataFrame):
        """
        Execute trade with improved timing and stop/target monitoring.

        Key improvements:
        1. Entry at Monday open (next business day after Friday decision)
        2. Daily monitoring for stop loss and take profit
        3. Conviction-based position sizing
        4. Exit on stop/target hit or max 7-day holding
        """
        action = decision.get("action", "HOLD").upper()

        if action == "HOLD":
            print(f"   Decision: HOLD - No trade executed")
            return

        if action != "BUY":
            print(f"   Skipping {action} - currently only supporting BUY trades")
            return

        # Get conviction level from decision (default to medium)
        conviction = decision.get("conviction", "medium").lower()

        # Convert decision date to pandas Timestamp
        decision_dt = pd.to_datetime(decision_date)

        # Entry: Next business day (Monday after Friday decision)
        entry_date = self._get_next_business_day(decision_dt, price_data)

        try:
            # Use Open price for entry (more realistic than Close)
            entry_price = float(price_data.loc[entry_date, 'Open'])
        except (KeyError, IndexError) as e:
            print(f"   ❌ Entry price not available for {entry_date}: {e}")
            return

        # Calculate position size based on conviction
        risk_amount, position_size, risk_pct = self._calculate_position_size(conviction, entry_price)

        # Calculate stop loss and take profit
        stop_loss = entry_price * 0.98  # -2% stop
        take_profit = entry_price * 1.06  # +6% target (3:1 R:R)

        print(f"\n   🎯 TRADE SETUP:")
        print(f"   Action: {action}")
        print(f"   Conviction: {conviction.upper()} (Risk: {risk_pct*100:.1f}%)")
        print(f"   Entry Date: {entry_date.strftime('%Y-%m-%d')}")
        print(f"   Entry Price: ${entry_price:,.2f}")
        print(f"   Position Size: {position_size:.6f} BTC (${risk_amount:,.2f})")
        print(f"   Stop Loss: ${stop_loss:,.2f} (-2.0%)")
        print(f"   Take Profit: ${take_profit:,.2f} (+6.0%)")

        # Monitor trade daily for up to 7 days
        max_holding_days = 7
        exit_price = None
        exit_date = None
        exit_reason = None

        available_dates = price_data.index
        entry_idx = available_dates.get_loc(entry_date)

        for day_offset in range(max_holding_days):
            current_idx = entry_idx + day_offset

            if current_idx >= len(available_dates):
                # Reached end of data
                exit_price = float(price_data.iloc[-1]['Close'])
                exit_date = available_dates[-1]
                exit_reason = "End of Data"
                break

            current_date = available_dates[current_idx]
            high = float(price_data.loc[current_date, 'High'])
            low = float(price_data.loc[current_date, 'Low'])
            close = float(price_data.loc[current_date, 'Close'])

            # Check stop loss (use Low of the day)
            if low <= stop_loss:
                exit_price = stop_loss
                exit_date = current_date
                exit_reason = "Stop Loss Hit"
                break

            # Check take profit (use High of the day)
            if high >= take_profit:
                exit_price = take_profit
                exit_date = current_date
                exit_reason = "Take Profit Hit"
                break

            # If last day of holding period, exit at close
            if day_offset == max_holding_days - 1:
                exit_price = close
                exit_date = current_date
                exit_reason = "Time Stop (7 days)"
                break

        # If no exit triggered, use the close of the 7th day
        if exit_price is None:
            final_idx = min(entry_idx + max_holding_days - 1, len(available_dates) - 1)
            exit_price = float(price_data.iloc[final_idx]['Close'])
            exit_date = available_dates[final_idx]
            exit_reason = "Time Stop (7 days)"

        # Calculate P&L
        if action == "BUY":
            pnl = (exit_price - entry_price) * position_size
            pnl_pct = ((exit_price - entry_price) / entry_price) * 100
        else:
            pnl = (entry_price - exit_price) * position_size
            pnl_pct = ((entry_price - exit_price) / entry_price) * 100

        # Update capital
        self.capital = self.capital + pnl

        # Determine if win or loss
        result = "WIN" if pnl > 0 else "LOSS" if pnl < 0 else "BREAKEVEN"
        emoji = "✅" if result == "WIN" else "❌" if result == "LOSS" else "➖"

        # Record trade
        trade_record = {
            'decision_date': decision_date,
            'entry_date': entry_date.strftime('%Y-%m-%d'),
            'exit_date': exit_date.strftime('%Y-%m-%d'),
            'action': action,
            'conviction': conviction,
            'risk_pct': risk_pct,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'position_size': position_size,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'exit_reason': exit_reason,
            'result': result
        }
        self.trades.append(trade_record)

        print(f"\n   📊 TRADE RESULT:")
        print(f"   Exit Date: {exit_date.strftime('%Y-%m-%d')}")
        print(f"   Exit Price: ${exit_price:,.2f}")
        print(f"   Exit Reason: {exit_reason}")
        print(f"   {emoji} {result} - P&L: ${pnl:,.2f} ({pnl_pct:+.2f}%)")
        print(f"   New Capital: ${self.capital:,.2f}")

    def _calculate_metrics(self, price_data: pd.DataFrame, symbol: str) -> Dict:
        """Calculate performance metrics."""

        # Buy & Hold comparison
        start_price = float(price_data['Close'].iloc[0])
        end_price = float(price_data['Close'].iloc[-1])
        buy_hold_return = ((end_price - start_price) / start_price) * 100

        if not self.trades:
            print("⚠️  No trades executed during backtest period")
            print("   This means all decisions were HOLD")
            print()

            return {
                'symbol': symbol,
                'initial_capital': self.initial_capital,
                'final_capital': self.capital,
                'total_return_pct': 0,
                'buy_hold_return_pct': buy_hold_return,
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0
            }

        # Convert trades to DataFrame for analysis
        trades_df = pd.DataFrame(self.trades)

        # Calculate metrics
        total_return = ((self.capital - self.initial_capital) / self.initial_capital) * 100

        wins = len(trades_df[trades_df['pnl'] > 0])
        losses = len(trades_df[trades_df['pnl'] < 0])
        win_rate = (wins / len(trades_df)) * 100 if len(trades_df) > 0 else 0

        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if wins > 0 else 0
        avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losses > 0 else 0

        # Sharpe Ratio calculation
        if len(trades_df) > 1:
            returns = trades_df['pnl_pct'].values
            sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(52) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0

        # Max Drawdown
        equity_values = [self.initial_capital]
        running_capital = self.initial_capital
        for trade in self.trades:
            running_capital += trade['pnl']
            equity_values.append(running_capital)

        peak = equity_values[0]
        max_dd = 0
        for value in equity_values:
            if value > peak:
                peak = value
            dd = ((peak - value) / peak) * 100
            if dd > max_dd:
                max_dd = dd

        results = {
            'symbol': symbol,
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_return_pct': total_return,
            'buy_hold_return_pct': buy_hold_return,
            'total_trades': len(trades_df),
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_dd
        }

        return results

    def run_backtest(self, symbol: str, start_date: str, end_date: str):
        """
        Run Phase 3.1 refined backtest.

        Args:
            symbol: Trading symbol (e.g., 'BTC-USD')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format

        Returns:
            Dict with backtest results
        """
        print("🚀 Running Phase 3.1 REFINED Backtest")
        print()
        print("=" * 80)
        print("🔄 PHASE 3.1 - REFINED EXECUTION + RISK MANAGEMENT")
        print("=" * 80)
        print(f"Symbol: {symbol}")
        print(f"Period: {start_date} to {end_date}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Base Risk per Trade: {self.base_risk*100:.1f}%")
        print()
        print("⚡ PHASE 3.1 IMPROVEMENTS:")
        print("  1. ✅ Fixed Execution: Entry at Monday open, not Friday close")
        print("  2. ✅ Stop Loss: -2% automatic stop")
        print("  3. ✅ Take Profit: +6% target (3:1 reward:risk)")
        print("  4. ✅ Conviction Sizing: 1-3% risk based on signal strength")
        print("  5. ✅ Daily Monitoring: Exit on stop/target/7-day time stop")
        print("=" * 80)
        print()

        # Clean memory before starting
        print("🧹 Cleaning persistent memory...")
        self._clean_memory()
        print()

        # Download price data (need daily OHLC for stop/target monitoring)
        print(f"📊 Downloading OHLC price data for {symbol}...")
        price_data = yf.download(symbol, start=start_date, end=end_date, progress=False)

        if price_data.empty:
            print(f"❌ No price data available for {symbol}")
            return None

        print(f"✅ Downloaded {len(price_data)} days of price data")
        print()

        # Generate weekly decision dates (Fridays)
        dates = pd.date_range(start=start_date, end=end_date, freq='W-FRI')
        dates = [d.strftime("%Y-%m-%d") for d in dates]

        print(f"📅 Trading Schedule: {len(dates)} weekly decision days")
        print()

        # Run backtest for each decision day
        for i, decision_date in enumerate(dates):
            print(f"\n{'=' * 80}")
            print(f"📅 Decision Day {i+1}/{len(dates)}: {decision_date}")
            print(f"Current Capital: ${self.capital:,.2f}")
            print("=" * 80)

            try:
                # Clean memory before each decision (except first)
                if i > 0:
                    self._clean_memory()

                # Get agent decision
                print(f"🤖 Getting agent decision for {decision_date}...")
                decision_result = decide(symbol, decision_date)

                # Parse decision
                if isinstance(decision_result, str):
                    decision = {"action": decision_result.upper(), "conviction": "medium"}
                elif isinstance(decision_result, dict):
                    decision = decision_result
                    if "action" not in decision:
                        decision["action"] = "HOLD"
                    if "conviction" not in decision:
                        decision["conviction"] = "medium"
                else:
                    print(f"   ⚠️  Unknown decision format: {type(decision_result)}")
                    decision = {"action": "HOLD", "conviction": "medium"}

                print(f"\n=== DECISION ===")
                print(f"Action: {decision.get('action', 'HOLD')}")
                print(f"Conviction: {decision.get('conviction', 'medium').upper()}")

                # Execute trade with improved logic
                self._execute_trade_with_stops(decision, decision_date, price_data)

                # Record equity
                self.equity_curve.append({
                    'date': decision_date,
                    'equity': self.capital
                })

            except Exception as e:
                print(f"❌ Error on {decision_date}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

        # Calculate performance metrics
        print("\n" + "=" * 80)
        print("📊 CALCULATING PERFORMANCE METRICS")
        print("=" * 80)
        print()

        results = self._calculate_metrics(price_data, symbol)

        # Print results
        self._print_results(results)

        # Save detailed trades
        self._save_results(results, symbol)

        return results

    def _print_results(self, results: Dict):
        """Print formatted backtest results."""

        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 20 + "PHASE 3.1 REFINED BACKTEST RESULTS" + " " * 24 + "║")
        print("╠" + "=" * 78 + "╣")
        print(f"║  Symbol: {results['symbol']:<68} ║")
        print("╠" + "=" * 78 + "╣")
        print(f"║  Initial Capital:        ${results['initial_capital']:>16,.2f}" + " " * 25 + "║")
        print(f"║  Final Capital:          ${results['final_capital']:>16,.2f}" + " " * 25 + "║")
        print(f"║  Total Return:                        {results['total_return_pct']:>6.2f}%" + " " * 25 + "║")
        print(f"║  Buy & Hold Return:                   {results['buy_hold_return_pct']:>6.2f}%" + " " * 25 + "║")
        print("╠" + "=" * 78 + "╣")
        print(f"║  Total Trades:                              {results['total_trades']:>3}" + " " * 28 + "║")
        print(f"║  Wins:                                      {results['wins']:>3}" + " " * 28 + "║")
        print(f"║  Losses:                                    {results['losses']:>3}" + " " * 28 + "║")
        print(f"║  Win Rate:                              {results['win_rate']:>6.2f}%" + " " * 25 + "║")
        print("╠" + "=" * 78 + "╣")
        print(f"║  Average Win:            ${results['avg_win']:>16.2f}" + " " * 25 + "║")
        print(f"║  Average Loss:           ${results['avg_loss']:>16.2f}" + " " * 25 + "║")
        print("╠" + "=" * 78 + "╣")
        print(f"║  Sharpe Ratio:                            {results['sharpe_ratio']:>6.2f}" + " " * 26 + "║")
        print(f"║  Max Drawdown:                            {results['max_drawdown']:>6.2f}%" + " " * 25 + "║")
        print("╚" + "=" * 78 + "╝")
        print()

        # Comparison to Phase 3
        print("📈 PHASE 3.1 vs PHASE 3 COMPARISON:")
        print()
        phase3_sharpe = -2.53
        phase3_return = -0.05

        sharpe_change = results['sharpe_ratio'] - phase3_sharpe
        return_change = results['total_return_pct'] - phase3_return

        if sharpe_change > 0:
            print(f"   Sharpe Ratio: {results['sharpe_ratio']:.2f} (Phase 3: {phase3_sharpe})")
            print(f"   ✅ IMPROVED by {sharpe_change:+.2f} vs Phase 3")
        else:
            print(f"   Sharpe Ratio: {results['sharpe_ratio']:.2f} (Phase 3: {phase3_sharpe})")
            print(f"   ⚠️  DECREASED by {sharpe_change:.2f} vs Phase 3")

        print()

        if return_change > 0:
            print(f"   Total Return: {results['total_return_pct']:.2f}% (Phase 3: {phase3_return:.2f}%)")
            print(f"   ✅ IMPROVED by {return_change:+.2f}% vs Phase 3")
        else:
            print(f"   Total Return: {results['total_return_pct']:.2f}% (Phase 3: {phase3_return:.2f}%)")
            print(f"   ⚠️  DECREASED by {return_change:.2f}% vs Phase 3")

        print()

        if results['total_return_pct'] < results['buy_hold_return_pct']:
            underperform = results['buy_hold_return_pct'] - results['total_return_pct']
            print(f"   ⚠️  Strategy underperformed Buy & Hold by {underperform:.2f}%")
        else:
            outperform = results['total_return_pct'] - results['buy_hold_return_pct']
            print(f"   🎉 Strategy OUTPERFORMED Buy & Hold by {outperform:+.2f}%")

        print()

        if results['win_rate'] < 50:
            print(f"   ⚠️  Win rate is {results['win_rate']:.1f}% - consider strategy refinement")
        else:
            print(f"   ✅ Win rate is {results['win_rate']:.1f}% - good performance")

    def _save_results(self, results: Dict, symbol: str):
        """Save backtest results and trade details to files."""

        # Create output directory
        output_dir = f"eval_results/phase3_1_refined/{symbol}"
        os.makedirs(output_dir, exist_ok=True)

        # Save summary results
        results_file = f"{output_dir}/backtest_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        # Save detailed trades
        if self.trades:
            trades_df = pd.DataFrame(self.trades)
            trades_file = f"{output_dir}/trades_detail.csv"
            trades_df.to_csv(trades_file, index=False)
            print(f"\n💾 Results saved to: {output_dir}/")


def main():
    """Run Phase 3.1 refined backtest."""

    # Initialize backtest
    backtest = Phase31RefinedBacktest(
        initial_capital=10000.0,
        base_risk=0.02  # 2% base risk
    )

    # Run backtest on same period as Phase 3 (for direct comparison)
    results = backtest.run_backtest(
        symbol="BTC-USD",
        start_date="2024-11-01",
        end_date="2024-12-31"
    )

    return results


if __name__ == "__main__":
    results = main()
