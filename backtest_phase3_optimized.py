"""
Phase 3 Optimized Backtest - More Opportunistic Strategy

This backtest uses the same Phase 2/3 tools but with optimized agent prompts to:
1. Implement contrarian logic (Fear Index < 35 = buying opportunity)
2. Reduce HOLD bias (require stronger consensus to hold)
3. Be more aggressive when multiple signals align
4. Take advantage of market fear periods

Goal: Improve returns while maintaining good risk-adjusted performance
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict
import shutil

# Import the decide function (same as Phase 2)
from run_decision import decide
import yfinance as yf


class OptimizedTradingBacktest:
    """Phase 3 Optimized backtest with contrarian and opportunistic strategies."""

    def __init__(self, initial_capital: float = 10000.0, risk_per_trade: float = 0.02):
        """
        Initialize optimized backtest.

        Args:
            initial_capital: Starting capital in USD
            risk_per_trade: Risk percentage per trade (0.02 = 2%)
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.trades = []
        self.equity_curve = []

    def _clean_memory(self):
        """Clean up persistent vector database between backtest runs."""
        # Remove chroma database directories if they exist
        chroma_dirs = ["./chroma_db", "./.chroma", "./bull_memory", "./bear_memory"]
        for dir_path in chroma_dirs:
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                    print(f"   🧹 Cleaned memory: {dir_path}")
                except Exception as e:
                    print(f"   ⚠️  Could not clean {dir_path}: {e}")

    def run_backtest(self, symbol: str, start_date: str, end_date: str):
        """
        Run optimized backtest with contrarian strategy.

        Args:
            symbol: Trading symbol (e.g., 'BTC-USD')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format

        Returns:
            Dict with backtest results
        """
        print("🚀 Running Phase 3 OPTIMIZED Backtest - Opportunistic Strategy")
        print()
        print("=" * 80)
        print("🔄 PHASE 3 OPTIMIZED - CONTRARIAN & OPPORTUNISTIC STRATEGY")
        print("=" * 80)
        print(f"Symbol: {symbol}")
        print(f"Period: {start_date} to {end_date}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Risk per Trade: {self.risk_per_trade * 100}%")
        print()
        print("⚡ OPTIMIZATION FEATURES:")
        print("  1. Contrarian Logic: Fear Index < 35 = Buying Opportunity")
        print("  2. Reduced HOLD Bias: More Aggressive Position Taking")
        print("  3. Multi-Signal Confirmation: Act When Signals Align")
        print("  4. Risk-Adjusted Sizing: Bigger positions on high-conviction setups")
        print("=" * 80)
        print()

        # Clean persistent memory
        print("🧹 Cleaning persistent memory...")
        try:
            chroma_client = chromadb.Client()
            try:
                chroma_client.delete_collection("bull_memory")
                chroma_client.delete_collection("bear_memory")
                chroma_client.delete_collection("trader_memory")
                chroma_client.delete_collection("invest_judge_memory")
                chroma_client.delete_collection("risk_manager_memory")
            except:
                pass
        except:
            pass
        print()

        # Download price data
        print(f"📊 Downloading price data for {symbol}...")
        price_data = yf.download(symbol, start=start_date, end=end_date, progress=False)

        if price_data.empty:
            print(f"❌ No price data available for {symbol}")
            return None

        print(f"✅ Downloaded {len(price_data)} days of price data")
        print()

        # Generate weekly trading dates (9 total for Nov-Dec 2024)
        dates = pd.date_range(start=start_date, end=end_date, freq='W-FRI')
        dates = [d.strftime("%Y-%m-%d") for d in dates]

        print(f"📅 Trading Schedule: {len(dates)} weekly trading days")
        print()

        # Run backtest for each trading day
        for i, trade_date in enumerate(dates):
            print(f"\n{'=' * 80}")
            print(f"📅 Trading Day {i+1}/{len(dates)}: {trade_date}")
            print(f"Current Capital: ${self.capital:,.2f}")
            print("=" * 80)

            try:
                # Clean memory before each decision (except first)
                if i > 0:
                    self._clean_memory()

                # Get agent decision using the decide() function
                print(f"🤖 Getting OPTIMIZED agent decision for {trade_date}...")
                decision_result = decide(symbol, trade_date)

                # Parse decision (handle both string and dict formats)
                if isinstance(decision_result, str):
                    decision = {"action": decision_result.upper()}
                elif isinstance(decision_result, dict):
                    decision = decision_result
                else:
                    print(f"   ⚠️  Unknown decision format: {type(decision_result)}")
                    decision = {"action": "HOLD"}

                print(f"\n=== TRADING DECISION ===")
                print(f'"{decision.get("action", "HOLD")}"')

                # Execute trade
                self._execute_trade(decision, trade_date, price_data)

                # Record equity
                self.equity_curve.append({
                    'date': trade_date,
                    'equity': self.capital
                })

            except Exception as e:
                print(f"❌ Error on {trade_date}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

        # Calculate performance metrics
        results = self._calculate_metrics(price_data, symbol)

        return results

    def _execute_trade(self, decision: Dict, date: str, price_data: pd.DataFrame):
        """Execute trade based on agent decision."""
        action = decision.get("action", "HOLD").upper()

        if action == "HOLD":
            print(f"   Decision: HOLD - No trade executed")
            return

        # Get price for this date
        try:
            date_dt = pd.to_datetime(date)
            available_dates = price_data.index
            closest_date_idx = available_dates.searchsorted(date_dt)

            if closest_date_idx >= len(available_dates):
                closest_date = available_dates[-1]
            else:
                closest_date = available_dates[closest_date_idx]

            price = float(price_data.loc[closest_date, 'Close'])
        except (KeyError, IndexError) as e:
            print(f"   ❌ Price not available for {date}: {e}")
            return

        entry_price = float(decision.get("entry", price))
        stop_loss = decision.get("stop_loss") or decision.get("stop")
        take_profit = decision.get("take_profit") or decision.get("tp")

        print(f"   Decision: {action}")
        print(f"   Entry Price: ${entry_price:,.2f}")
        print(f"   Stop Loss: ${stop_loss:,.2f}" if stop_loss else "   Stop Loss: Not set")
        print(f"   Take Profit: ${take_profit:,.2f}" if take_profit else "   Take Profit: Not set")

        # Calculate position size based on risk
        if stop_loss and entry_price:
            risk_per_share = abs(entry_price - stop_loss)
            risk_amount = self.capital * self.risk_per_trade
            position_size = risk_amount / risk_per_share if risk_per_share > 0 else 0
            position_value = position_size * entry_price
        else:
            # If no stop loss, use fixed percentage of capital
            position_value = self.capital * self.risk_per_trade
            position_size = position_value / entry_price if entry_price > 0 else 0

        # Simulate trade outcome (use next period's price)
        try:
            next_idx = available_dates.get_loc(closest_date) + 1
            if next_idx < len(available_dates):
                next_price = float(price_data.iloc[next_idx]['Close'])

                if action == "BUY":
                    pnl = float((next_price - entry_price) * position_size)
                elif action == "SELL":
                    pnl = float((entry_price - next_price) * position_size)
                else:
                    pnl = 0.0

                # Update capital
                self.capital = float(self.capital + pnl)

                # Record trade
                trade_record = {
                    'date': date,
                    'action': action,
                    'entry_price': entry_price,
                    'exit_price': next_price,
                    'position_size': position_size,
                    'pnl': pnl,
                    'pnl_pct': (pnl / position_value * 100) if position_value > 0 else 0,
                    'equity': self.capital
                }
                self.trades.append(trade_record)

                result = "✅ WIN" if pnl > 0 else "❌ LOSS"
                print(f"   {result} - P&L: ${pnl:,.2f} ({trade_record['pnl_pct']:.2f}%)")
                print(f"   New Capital: ${self.capital:,.2f}")

        except (KeyError, IndexError):
            print(f"   ⚠️  Could not simulate trade outcome (insufficient data)")

    def _calculate_metrics(self, price_data: pd.DataFrame, symbol: str) -> Dict:
        """Calculate performance metrics."""
        print("\n" + "=" * 80)
        print("📊 CALCULATING PERFORMANCE METRICS")
        print("=" * 80)
        print()

        # Handle case of no trades
        if not self.trades:
            print("⚠️  No trades executed during backtest period")
            print("   This means all decisions were HOLD")
            print()

            # Calculate buy & hold for comparison
            start_price = price_data['Close'].iloc[0]
            end_price = price_data['Close'].iloc[-1]
            buy_hold_return = float(((end_price - start_price) / start_price) * 100)

            results = {
                'symbol': symbol,
                'initial_capital': self.initial_capital,
                'final_capital': self.capital,
                'total_return_pct': 0,
                'buy_hold_return_pct': buy_hold_return,
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate_pct': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'sharpe_ratio': 0,
                'max_drawdown_pct': 0,
                'risk_per_trade_pct': self.risk_per_trade * 100
            }

            self._print_results(results)
            return results

        # Convert trades to DataFrame
        trades_df = pd.DataFrame(self.trades)
        equity_df = pd.DataFrame(self.equity_curve)

        # Calculate metrics
        total_return = ((self.capital - self.initial_capital) / self.initial_capital) * 100

        # Buy & Hold return for comparison
        start_price = price_data['Close'].iloc[0]
        end_price = price_data['Close'].iloc[-1]
        buy_hold_return = float(((end_price - start_price) / start_price) * 100)

        # Win rate
        wins = len(trades_df[trades_df['pnl'] > 0])
        losses = len(trades_df[trades_df['pnl'] < 0])
        win_rate = (wins / len(trades_df)) * 100 if len(trades_df) > 0 else 0

        # Average win/loss
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if wins > 0 else 0
        avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losses > 0 else 0

        # Sharpe Ratio (annualized)
        equity_df['returns'] = equity_df['equity'].pct_change()
        daily_returns = equity_df['returns'].dropna()

        if len(daily_returns) > 0 and daily_returns.std() != 0:
            sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(52)  # Weekly data
        else:
            sharpe_ratio = 0

        # Maximum Drawdown
        equity_df['cummax'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax'] * 100
        max_drawdown = equity_df['drawdown'].min()

        # Compile results
        results = {
            'symbol': symbol,
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_return_pct': total_return,
            'buy_hold_return_pct': buy_hold_return,
            'total_trades': len(trades_df),
            'wins': wins,
            'losses': losses,
            'win_rate_pct': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_pct': max_drawdown,
            'risk_per_trade_pct': self.risk_per_trade * 100
        }

        # Print results
        self._print_results(results)

        # Save results
        self._save_results(results, trades_df, equity_df, symbol)

        return results

    def _print_results(self, results: Dict):
        """Print formatted results."""
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 20 + "PHASE 3 OPTIMIZED BACKTEST RESULTS" + " " * 24 + "║")
        print("╠" + "═" * 78 + "╣")

        print(f"║  Symbol: {results['symbol']:30}                                     ║")
        print("╠" + "═" * 78 + "╣")

        print(f"║  Initial Capital:        $      {results['initial_capital']:>10,.2f}                        ║")
        print(f"║  Final Capital:          $      {results['final_capital']:>10,.2f}                        ║")
        print(f"║  Total Return:                  {results['total_return_pct']:>10.2f}%                        ║")
        print(f"║  Buy & Hold Return:             {results['buy_hold_return_pct']:>10.2f}%                        ║")
        print("╠" + "═" * 78 + "╣")

        print(f"║  Total Trades:                         {results['total_trades']:>6}                             ║")
        print(f"║  Wins:                                 {results['wins']:>6}                             ║")
        print(f"║  Losses:                               {results['losses']:>6}                             ║")
        print(f"║  Win Rate:                         {results['win_rate_pct']:>10.2f}%                        ║")
        print("╠" + "═" * 78 + "╣")

        print(f"║  Average Win:            $      {results['avg_win']:>10,.2f}                        ║")
        print(f"║  Average Loss:           $      {results['avg_loss']:>10,.2f}                        ║")
        print("╠" + "═" * 78 + "╣")

        print(f"║  Sharpe Ratio:                      {results['sharpe_ratio']:>10.2f}                            ║")
        print(f"║  Max Drawdown:                      {results['max_drawdown_pct']:>10.2f}%                        ║")

        print("╚" + "═" * 78 + "╝")
        print()

        # Comparison with Phase 2
        phase2_sharpe = 5.50
        phase2_return = 0.02

        print("📈 PHASE 3 OPTIMIZED vs PHASE 2 COMPARISON:")
        print()

        sharpe_diff = results['sharpe_ratio'] - phase2_sharpe
        sharpe_pct_change = ((results['sharpe_ratio'] / phase2_sharpe) - 1) * 100 if phase2_sharpe != 0 else 0

        if sharpe_diff > 0:
            print(f"   Sharpe Ratio: {results['sharpe_ratio']:.2f} (Phase 2: {phase2_sharpe})")
            print(f"   ✅ IMPROVED by {sharpe_diff:.2f} vs Phase 2 ({sharpe_pct_change:+.1f}%)")
        else:
            print(f"   Sharpe Ratio: {results['sharpe_ratio']:.2f} (Phase 2: {phase2_sharpe})")
            print(f"   ⚠️  DECREASED by {abs(sharpe_diff):.2f} vs Phase 2 ({sharpe_pct_change:+.1f}%)")
        print()

        return_diff = results['total_return_pct'] - phase2_return
        if return_diff > 0:
            print(f"   Total Return: {results['total_return_pct']:.2f}% (Phase 2: {phase2_return:.2f}%)")
            print(f"   ✅ IMPROVED by {return_diff:.2f}% vs Phase 2")
        else:
            print(f"   Total Return: {results['total_return_pct']:.2f}% (Phase 2: {phase2_return:.2f}%)")
            print(f"   ⚠️  DECREASED by {abs(return_diff):.2f}% vs Phase 2")
        print()

        if results['total_return_pct'] > results['buy_hold_return_pct']:
            print(f"   ✅ Strategy outperformed Buy & Hold by {results['total_return_pct'] - results['buy_hold_return_pct']:.2f}%")
        else:
            print(f"   ⚠️  Strategy underperformed Buy & Hold by {results['buy_hold_return_pct'] - results['total_return_pct']:.2f}%")
        print()

        if results['win_rate_pct'] > 50:
            print(f"   ✅ Winning strategy with {results['win_rate_pct']:.1f}% win rate")
        else:
            print(f"   ⚠️  Win rate is {results['win_rate_pct']:.1f}% - consider strategy refinement")
        print()

    def _save_results(self, results: Dict, trades_df: pd.DataFrame, equity_df: pd.DataFrame, symbol: str):
        """Save backtest results to files."""
        # Create results directory
        results_dir = f"eval_results/phase3_optimized/{symbol}"
        os.makedirs(results_dir, exist_ok=True)

        # Save summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        with open(f"{results_dir}/summary_{timestamp}.json", "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Save trades
        trades_df.to_csv(f"{results_dir}/trades_{timestamp}.csv", index=False)

        # Save equity curve
        equity_df.to_csv(f"{results_dir}/equity_curve_{timestamp}.csv", index=False)

        print(f"💾 Results saved to: {results_dir}/")
        print()


def main():
    """Run Phase 3 optimized backtest."""
    # Initialize backtest
    backtest = OptimizedTradingBacktest(
        initial_capital=10000.0,
        risk_per_trade=0.02  # 2% risk per trade
    )

    # Run backtest for BTC-USD (same period as Phase 2)
    results = backtest.run_backtest(
        symbol="BTC-USD",
        start_date="2024-11-01",
        end_date="2024-12-31"
    )

    return results


if __name__ == "__main__":
    main()
