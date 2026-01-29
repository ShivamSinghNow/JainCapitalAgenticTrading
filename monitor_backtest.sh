#!/bin/bash

echo "🔍 Monitoring backtest progress..."
echo ""

# Wait for the backtest process to complete
while ps aux | grep -v grep | grep -q "python backtest_phase2.py"; do
    # Show current progress
    current_day=$(grep -c "Trading Day" final_backtest.log)
    echo "⏳ Progress: $current_day/9 trading days completed ($(date '+%H:%M:%S'))"
    sleep 30
done

echo ""
echo "✅ BACKTEST COMPLETE!"
echo "================================"
echo ""

# Show final results
if grep -q "PHASE 2 BACKTEST RESULTS" final_backtest.log; then
    echo "📊 FINAL RESULTS:"
    echo "================================"
    tail -80 final_backtest.log | grep -A 80 "PHASE 2 BACKTEST RESULTS"
else
    echo "⚠️  Results not found in expected format. Check final_backtest.log"
    echo ""
    echo "Last 50 lines of log:"
    tail -50 final_backtest.log
fi

echo ""
echo "📁 Full results saved to: final_backtest.log"
echo "📈 Results directory: eval_results/phase2_backtest/BTC-USD/"
echo ""
echo "🎉 Phase 2 Backtest Finished at $(date)"
