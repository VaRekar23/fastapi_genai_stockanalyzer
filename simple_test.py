#!/usr/bin/env python3
"""
Simple test to verify Yahoo Finance API calls with rate limiting.
This version doesn't require langchain dependencies.
"""

import yfinance as yf
import time
import json
from datetime import datetime

def test_yahoo_finance_with_delay():
    """Test Yahoo Finance API with proper delays."""
    
    print("🧪 Testing Yahoo Finance API with Rate Limiting")
    print("=" * 50)
    
    symbols = ["TCS", "INFY", "WIPRO"]
    results = {}
    
    for i, symbol in enumerate(symbols):
        print(f"\n🔍 Fetching data for {symbol} (attempt {i+1}/{len(symbols)})...")
        
        try:
            # Add delay between requests
            if i > 0:
                delay = 1.5  # 1.5 seconds delay
                print(f"⏱️  Waiting {delay} seconds to avoid rate limiting...")
                time.sleep(delay)
            
            # Try NSE format first for Indian stocks
            nse_symbol = f"{symbol}.NS"
            
            start_time = time.time()
            stock = yf.Ticker(nse_symbol)
            info = stock.info
            
            if info and info.get('regularMarketPrice'):
                current_price = info.get('regularMarketPrice', info.get('currentPrice'))
                company_name = info.get('shortName', symbol)
                market_cap = info.get('marketCap')
                
                results[symbol] = {
                    'symbol': nse_symbol,
                    'name': company_name,
                    'price': current_price,
                    'market_cap': market_cap,
                    'fetch_time': time.time() - start_time,
                    'status': 'success'
                }
                
                print(f"✅ {symbol}: ₹{current_price} ({company_name})")
                
            else:
                print(f"⚠️  No price data available for {symbol}")
                results[symbol] = {
                    'symbol': nse_symbol,
                    'status': 'no_data',
                    'fetch_time': time.time() - start_time
                }
                
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")
            results[symbol] = {
                'symbol': symbol,
                'status': 'error',
                'error': str(e),
                'fetch_time': time.time() - start_time if 'start_time' in locals() else 0
            }
    
    print("\n📊 Summary Report:")
    print("-" * 30)
    
    total_time = sum(r.get('fetch_time', 0) for r in results.values())
    successful = sum(1 for r in results.values() if r.get('status') == 'success')
    
    print(f"Total symbols tested: {len(symbols)}")
    print(f"Successful fetches: {successful}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per request: {total_time/len(symbols):.2f} seconds")
    
    print("\n📋 Detailed Results:")
    for symbol, data in results.items():
        print(f"\n{symbol}:")
        print(f"  Status: {data['status']}")
        print(f"  Time: {data['fetch_time']:.2f}s")
        if data['status'] == 'success':
            print(f"  Price: ₹{data['price']}")
            print(f"  Name: {data['name']}")
            if data['market_cap']:
                print(f"  Market Cap: ₹{data['market_cap']:,}")
        elif data['status'] == 'error':
            print(f"  Error: {data.get('error', 'Unknown')}")
    
    print("\n✨ Test completed!")
    
    return results

if __name__ == "__main__":
    test_results = test_yahoo_finance_with_delay()
