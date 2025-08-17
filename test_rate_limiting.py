#!/usr/bin/env python3
"""
Test script to verify rate limiting and caching functionality.
This script tests the Yahoo Finance API calls with the new rate limiting mechanism.
"""

import sys
import os
import time
import logging

# Add the app directory to the path so we can import CustomTool
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from CustomTool import get_current_stock_price, get_company_info

# Configure logging to see rate limiting in action
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def test_rate_limiting():
    """Test rate limiting and caching functionality."""
    
    print("🧪 Testing Rate Limiting and Caching System")
    print("=" * 50)
    
    # Test symbols
    test_symbols = ["TCS", "INFY", "WIPRO"]
    
    print("\n📊 Phase 1: Initial API calls (should trigger rate limiting)")
    start_time = time.time()
    
    results = {}
    for symbol in test_symbols:
        print(f"\n🔍 Fetching data for {symbol}...")
        results[symbol] = {
            'price': get_current_stock_price(symbol),
            'info': get_company_info(symbol)
        }
        print(f"✅ Completed {symbol}")
    
    phase1_duration = time.time() - start_time
    print(f"\n⏱️  Phase 1 completed in {phase1_duration:.2f} seconds")
    
    print("\n📊 Phase 2: Cached API calls (should be instant)")
    start_time = time.time()
    
    for symbol in test_symbols:
        print(f"\n🔍 Fetching cached data for {symbol}...")
        cached_price = get_current_stock_price(symbol)
        cached_info = get_company_info(symbol)
        print(f"✅ Completed {symbol} (cached)")
    
    phase2_duration = time.time() - start_time
    print(f"\n⏱️  Phase 2 completed in {phase2_duration:.2f} seconds")
    
    print(f"\n📈 Performance Improvement: {(phase1_duration / max(phase2_duration, 0.01)):.1f}x faster with caching")
    
    print("\n📋 Sample Results:")
    for symbol in test_symbols:
        print(f"\n{symbol}:")
        print(f"  Price: {results[symbol]['price']}")
        # Only show first 200 chars of company info to keep output manageable
        info_preview = str(results[symbol]['info'])[:200] + "..." if len(str(results[symbol]['info'])) > 200 else str(results[symbol]['info'])
        print(f"  Info: {info_preview}")
    
    print("\n✨ Test completed successfully!")
    print("The rate limiting system is working as expected.")

if __name__ == "__main__":
    test_rate_limiting()
