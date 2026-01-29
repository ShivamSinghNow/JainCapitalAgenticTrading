"""
Backtest Phase 2 Implementation - Measures Impact of On-Chain & Social Sentiment Tools

This script backtests the trading agent system with Phase 2 tools enabled and calculates:
- Total Return
- Sharpe Ratio
- Maximum Drawdown
- Win Rate
- Comparison vs Buy & Hold
"""

import os
import json
import pandas as pd
import numpy as np
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from run_decision import decide
import yfinance as yf

class Phase2Backtest:
    """Backtest the trading agent system with Phase 2 on-chain and social sentiment tools."""

    def __init__(self, initial_capital: float = 10000.0, risk_per_trade: float = 0.02):
        """
        Initialize backtest parameters.

        Args:
            initial_capital: Starting capital in USD
            risk_per_trade: Risk percentage per trade (0.02 = 2%)
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.trades = []
        self.equity_curve = []
        self.daily_returns = []

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

    def run_backtest(self, symbol: str, start_date: str, end_date: str, frequency: str = "daily"):
        """
        Run backtest over historical period.

        Args:
            symbol: Trading symbol (e.g., 'BTC-USD', 'AAPL')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            frequency: Trading frequency ('daily', 'weekly')

        Returns:
            DataFrame with backtest results
        """
        print("=" * 80)
        print(f"🔄 PHASE 2 BACKTEST - ON-CHAIN & SOCIAL SENTIMENT TOOLS")
        print("=" * 80)
        print(f"Symbol: {symbol}")
        print(f"Period: {start_date} to {end_date}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Risk per Trade: {self.risk_per_trade * 100}%")
        print("=" * 80)
        print()

        # Clean memory before starting
        print("🧹 Cleaning persistent memory...")
        self._clean_memory()
        print()

        # Generate trading dates
        dates = self._generate_trading_dates(start_date, end_date, frequency)

        # Download price data for the entire period
        print(f"📊 Downloading price data for {symbol}...")
        price_data = yf.download(symbol, start=start_date, end=end_date, progress=False)

        if price_data.empty:
            print(f"❌ No price data available for {symbol}")
            return None

        print(f"✅ Downloaded {len(price_data)} days of price data")
        print()

        # Run backtest for each date
        for i, trade_date in enumerate(dates):
            print(f"\n{'=' * 80}")
            print(f"📅 Trading Day {i+1}/{len(dates)}: {trade_date}")
            print(f"Current Capital: ${self.capital:,.2f}")
            print("=" * 80)

            try:
                # Clean memory before each decision to avoid conflicts
                if i > 0:  # Skip first iteration (already cleaned)
                    self._clean_memory()

                # Get agent decision
                print(f"🤖 Getting agent decision for {trade_date}...")
                decision_result = decide(symbol, trade_date)

                # Parse decision (handle both string and dict formats)
                if isinstance(decision_result, str):
                    # Simple string decision like "HOLD" or "BUY"
                    decision = {"action": decision_result.upper()}
                elif isinstance(decision_result, dict):
                    decision = decision_result
                else:
                    print(f"   ⚠️  Unknown decision format: {type(decision_result)}")
                    decision = {"action": "HOLD"}

                # Execute trade based on decision
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

    def _generate_trading_dates(self, start_date: str, end_date: str, frequency: str) -> List[str]:
        """Generate list of trading dates based on frequency."""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        dates = []
        current = start

        if frequency == "daily":
            delta = timedelta(days=1)
        elif frequency == "weekly":
            delta = timedelta(days=7)
        else:
            raise ValueError(f"Unsupported frequency: {frequency}")

        while current <= end:
            # For crypto, no need to skip weekends (24/7 market)
            dates.append(current.strftime("%Y-%m-%d"))
            current += delta

        return dates

    def _execute_trade(self, decision: Dict, date: str, price_data: pd.DataFrame):
        """Execute trade based on agent decision."""
        action = decision.get("action", "HOLD").upper()

        if action == "HOLD":
            print(f"   Decision: HOLD - No trade executed")
            return

        # Get price for this date
        try:
            date_dt = pd.to_datetime(date)
            # Find the closest available price (handle gaps)
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

        # Simulate trade outcome (simplified - use next day's price movement)
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

        except (KeyError, IndexError) as e:
            print(f"   ⚠️  Could not simulate trade outcome: {e}")

    def _calculate_metrics(self, price_data: pd.DataFrame, symbol: str) -> Dict:
        """Calculate performance metrics."""
        print("\n" + "=" * 80)
        print("📊 CALCULATING PERFORMANCE METRICS")
        print("=" * 80)
        print()

        # Convert trades to DataFrame
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
            sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)  # Annualized
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
        print("║" + " " * 20 + "PHASE 2 BACKTEST RESULTS" + " " * 34 + "║")
        print("╠" + "═" * 78 + "╣")

        print(f"║  Symbol: {results['symbol']:30}                                     ║")
        print("╠" + "═" * 78 + "╣")

        print(f"║  Initial Capital:        ${results['initial_capital']:>15,.2f}                        ║")
        print(f"║  Final Capital:          ${results['final_capital']:>15,.2f}                        ║")
        print(f"║  Total Return:           {results['total_return_pct']:>15.2f}%                        ║")
        print(f"║  Buy & Hold Return:      {results['buy_hold_return_pct']:>15.2f}%                        ║")
        print("╠" + "═" * 78 + "╣")

        print(f"║  Total Trades:           {results['total_trades']:>15}                             ║")
        print(f"║  Wins:                   {results['wins']:>15}                             ║")
        print(f"║  Losses:                 {results['losses']:>15}                             ║")
        print(f"║  Win Rate:               {results['win_rate_pct']:>15.2f}%                        ║")
        print("╠" + "═" * 78 + "╣")

        print(f"║  Average Win:            ${results['avg_win']:>15,.2f}                        ║")
        print(f"║  Average Loss:           ${results['avg_loss']:>15,.2f}                        ║")
        print("╠" + "═" * 78 + "╣")

        print(f"║  Sharpe Ratio:           {results['sharpe_ratio']:>15.2f}                            ║")
        print(f"║  Max Drawdown:           {results['max_drawdown_pct']:>15.2f}%                        ║")

        print("╚" + "═" * 78 + "╝")
        print()

        # Interpretation
        print("📈 PHASE 2 IMPACT ANALYSIS:")
        print()

        # Sharpe Ratio comparison (baseline: 2.34 for BTC)
        baseline_sharpe = 2.34
        print(f"   Sharpe Ratio: {results['sharpe_ratio']:.2f} (Baseline: {baseline_sharpe})")
        if results['sharpe_ratio'] > baseline_sharpe:
            improvement = results['sharpe_ratio'] - baseline_sharpe
            print(f"   ✅ IMPROVED by {improvement:.2f} vs baseline ({(improvement/baseline_sharpe)*100:.1f}% increase)")
        elif results['sharpe_ratio'] > 1.0:
            print(f"   ⚠️  Good Sharpe but below baseline (room for improvement)")
        else:
            print(f"   ❌ Below baseline - Phase 2 tools may need refinement")
        print()

        if results['total_return_pct'] > results['buy_hold_return_pct']:
            print(f"   ✅ Strategy outperformed Buy & Hold by {results['total_return_pct'] - results['buy_hold_return_pct']:.2f}%")
        else:
            print(f"   ⚠️  Strategy underperformed Buy & Hold by {results['buy_hold_return_pct'] - results['total_return_pct']:.2f}%")
        print()

        if results['total_trades'] == 0:
            print(f"   ⚠️  No trades executed - agents were very cautious (all HOLD decisions)")
            print(f"      This may indicate Phase 2 tools provide valuable risk signals")
        elif results['win_rate_pct'] > 50:
            print(f"   ✅ Winning strategy with {results['win_rate_pct']:.1f}% win rate")
        else:
            print(f"   ⚠️  Win rate is {results['win_rate_pct']:.1f}% - consider strategy refinement")
        print()

    def _save_results(self, results: Dict, trades_df: pd.DataFrame, equity_df: pd.DataFrame, symbol: str):
        """Save backtest results to files."""
        # Create results directory
        results_dir = f"eval_results/phase2_backtest/{symbol}"
        os.makedirs(results_dir, exist_ok=True)

        # Save summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        with open(f"{results_dir}/summary_{timestamp}.json", "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Save trades
        if not trades_df.empty:
            trades_df.to_csv(f"{results_dir}/trades_{timestamp}.csv", index=False)

        # Save equity curve
        if not equity_df.empty:
            equity_df.to_csv(f"{results_dir}/equity_curve_{timestamp}.csv", index=False)

        print(f"💾 Results saved to: {results_dir}/")
        print()


def main():
    """Run Phase 2 backtest."""
    # Initialize backtest
    backtest = Phase2Backtest(
        initial_capital=10000.0,
        risk_per_trade=0.02  # 2% risk per trade
    )

    # Run backtest for BTC-USD over 2 months (weekly to reduce API load)
    print("🚀 Running Phase 2 Backtest with On-Chain & Social Sentiment Tools")
    print()

    results = backtest.run_backtest(
        symbol="BTC-USD",
        start_date="2024-11-01",
        end_date="2024-12-31",
        frequency="weekly"  # Weekly to keep it fast
    )

    return results


if __name__ == "__main__":
    main()
