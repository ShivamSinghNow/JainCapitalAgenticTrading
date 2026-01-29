#!/usr/bin/env python3
"""
Test script to verify Yahoo Finance functionality
"""

import yfinance as yf
from datetime import datetime, timedelta

def test_yfinance():
    """Test basic Yahoo Finance functionality"""
    print("Testing Yahoo Finance functionality...")
    
    # Test with a common symbol
    symbols_to_test = ["AAPL", "BTC-USD", "NVDA"]
    
    for symbol in symbols_to_test:
        try:
            print(f"\nTesting symbol: {symbol}")
            
            # Use a proper historical date range (2024)
            end_date = datetime(2024, 12, 31)  # End of 2024
            start_date = datetime(2024, 12, 1)  # December 2024
            
            # Format dates
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")
            
            print(f"Fetching data from {start_str} to {end_str}")
            
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Fetch historical data (removed progress parameter)
            data = ticker.history(start=start_str, end=end_str)
            
            if data.empty:
                print(f"❌ No data found for {symbol}")
            else:
                print(f"✅ Successfully fetched {len(data)} records for {symbol}")
                print(f"   Latest close price: ${data['Close'].iloc[-1]:.2f}")
                print(f"   Date range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
                
        except Exception as e:
            print(f"❌ Error testing {symbol}: {str(e)}")
    
    print("\n" + "="*50)
    print("Yahoo Finance test completed!")

if __name__ == "__main__":
    test_yfinance()
