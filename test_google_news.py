#!/usr/bin/env python3
"""
Test script to debug Google News functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'TradingAgents'))

from TradingAgents.tradingagents.dataflows.googlenews_utils import getNewsData

def test_google_news():
    """Test Google News scraping functionality"""
    print("Testing Google News functionality...")
    
    try:
        # Test with a simple query
        query = "Bitcoin"
        start_date = "2024-12-23"
        end_date = "2024-12-30"
        
        print(f"Query: {query}")
        print(f"Date range: {start_date} to {end_date}")
        print("Fetching news...")
        
        results = getNewsData(query, start_date, end_date)
        
        print(f"Number of results: {len(results)}")
        
        if results:
            print("\nFirst few results:")
            for i, result in enumerate(results[:3]):
                print(f"\n--- Result {i+1} ---")
                print(f"Title: {result.get('title', 'N/A')}")
                print(f"Source: {result.get('source', 'N/A')}")
                print(f"Snippet: {result.get('snippet', 'N/A')[:100]}...")
        else:
            print("No results found!")
            
    except Exception as e:
        print(f"Error testing Google News: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_google_news()

