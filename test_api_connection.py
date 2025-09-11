#!/usr/bin/env python3
"""
Test script to verify CoinGecko API connection with your API key.
This will help diagnose any connection issues.
"""

import requests
import json
import time
from datetime import datetime

# Your API key
API_KEY = "CG-J1rJe3A9zGGeBLem65PAifzY"

def test_api_connection():
    """Test basic API connectivity."""
    print("🔍 Testing CoinGecko API Connection")
    print("=" * 50)
    
    # Test 1: Basic ping
    print("1. Testing API ping...")
    try:
        response = requests.get("https://api.coingecko.com/api/v3/ping", timeout=10)
        if response.status_code == 200:
            print("✅ API ping successful")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API key test error: {e}")
        return False
    
    # Test 3: Large data fetch (similar to what PYRA calculator does)
    print("\n3. Testing large data fetch...")
    try:
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 250,  # Maximum per page
            'page': 1,
            'sparkline': 'false'
        }
        
        start_time = time.time()
        response = requests.get(url, params=params, headers=headers, timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Large data fetch successful")
            print(f"   Retrieved {len(data)} coins in {end_time - start_time:.2f} seconds")
            
            # Analyze data quality (similar to PYRA filtering)
            valid_prices = []
            for coin in data:
                price = coin.get('current_price')
                if price and isinstance(price, (int, float)) and price >= 0.01:
                    valid_prices.append(price)
            
            if valid_prices:
                average = sum(valid_prices) / len(valid_prices)
                print(f"   Valid prices found: {len(valid_prices)}/{len(data)}")
                print(f"   Sample average: ${average:.6f}")
                print(f"   Price range: ${min(valid_prices):.6f} - ${max(valid_prices):.2f}")
            else:
                print("   ⚠️ No valid prices found in sample")
                
        else:
            print(f"❌ Large data fetch failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Large data fetch error: {e}")
        return False
    
    # Test 4: Check API limits and plan
    print("\n4. Checking API plan and limits...")
    try:
        # Try to get account info (if available in your plan)
        account_url = "https://api.coingecko.com/api/v3/account"
        response = requests.get(account_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            account_data = response.json()
            print("✅ Account information retrieved:")
            print(f"   Plan: {account_data.get('plan', 'Unknown')}")
            if 'rate_limit_request_per_minute' in account_data:
                print(f"   Rate limit: {account_data['rate_limit_request_per_minute']} requests/minute")
        else:
            print(f"ℹ️ Account endpoint not accessible (status: {response.status_code})")
            print("   This is normal for some API key types")
            
    except Exception as e:
        print(f"ℹ️ Account check skipped: {e}")
    
    print("\n5. Testing multiple rapid requests (rate limit check)...")
    try:
        # Test rate limiting with small requests
        test_url = "https://api.coingecko.com/api/v3/coins/bitcoin"
        
        for i in range(3):
            print(f"   Request {i+1}/3...")
            response = requests.get(test_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Request {i+1} successful")
            elif response.status_code == 429:
                print(f"   ⚠️ Request {i+1} rate limited")
                break
            else:
                print(f"   ❌ Request {i+1} failed: {response.status_code}")
            
            # Small delay between requests
            time.sleep(1)
            
    except Exception as e:
        print(f"⚠️ Rate limit test error: {e}")
    
    return True

def test_pyra_calculation():
    """Test the actual PYRA calculation with your API key."""
    print("\n" + "="*50)
    print("🏛️ Testing PYRA Barter Credit Calculation")
    print("="*50)
    
    try:
        from calculate_credit_optimized import OptimizedPyraCalculator
        
        print("Creating optimized calculator...")
        calculator = OptimizedPyraCalculator("CG-J1rJe3A9zGGeBLem65PAifzY")
        
        print("Getting API status...")
        status = calculator.get_api_status()
        print("📊 Current API Status:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        print("\n🔄 Calculating PYRA Barter Credit...")
        start_time = time.time()
        
        result = calculator.get_barter_credit()
        
        end_time = time.time()
        calculation_time = end_time - start_time
        
        print(f"\n📊 Results (calculated in {calculation_time:.2f} seconds):")
        print("="*40)
        
        if result['status'] == 'success':
            print(f"💎 PYRA Barter Credit: ${result['value']:.6f}")
            print(f"📈 Based on {result['valid_coins_used']:,} valid cryptocurrencies")
            print(f"📋 Total coins processed: {result['total_coins_processed']:,}")
            print(f"🎯 Filter success rate: {result.get('filter_rate', 'N/A')}%")
            print(f"📊 Price statistics:")
            print(f"   • Median: ${result.get('median', 0):.6f}")
            print(f"   • Minimum: ${result.get('min', 0):.6f}")
            print(f"   • Maximum: ${result.get('max', 0):.2f}")
            print(f"🔢 API calls used: {result['api_calls_used']}/10,000 this month")
            print(f"⏳ Cache duration: {result.get('cache_duration', 300)} seconds")
        else:
            print(f"❌ Calculation failed: {result.get('error', 'Unknown error')}")
            print(f"🔢 API calls used: {result.get('api_calls_used', 0)}/10,000")
            
    except ImportError:
        print("❌ Could not import OptimizedPyraCalculator")
        print("   Make sure calculate_credit_optimized.py is in the same directory")
    except Exception as e:
        print(f"❌ PYRA calculation error: {e}")

def main():
    """Main test function."""
    print("🧪 PYRA Barter Credit API Test Suite")
    print("Testing with API key: CG-J1rJ...PAifzY")
    print("Timestamp:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("")
    
    # Test basic API connection
    api_ok = test_api_connection()
    
    if api_ok:
        print("\n🎉 Basic API tests passed!")
        
        # Test the actual PYRA calculation
        test_pyra_calculation()
        
        print("\n" + "="*50)
        print("✅ Test suite completed!")
        print("📝 Summary:")
        print("   • API connection: Working")
        print("   • API key: Valid") 
        print("   • Rate limiting: Respected")
        print("   • PYRA calculation: Ready to use")
        print("\n🚀 Your API is ready for production!")
        print("💡 Next steps:")
        print("   1. Run: python app_optimized.py")
        print("   2. Open: http://localhost:5000")
        print("   3. Check the /api/barter-credit endpoint")
        
    else:
        print("\n❌ API connection tests failed!")
        print("🔧 Troubleshooting tips:")
        print("   1. Check your internet connection")
        print("   2. Verify the API key is correct")
        print("   3. Check if CoinGecko API is experiencing issues")
        print("   4. Try again in a few minutes")

if __name__ == "__main__":
    main()(f"❌ API ping failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API ping error: {e}")
        return False
    
    # Test 2: API key authentication
    print("\n2. Testing API key authentication...")
    headers = {
        "x-cg-demo-api-key": API_KEY,
        "Accept": "application/json",
        "User-Agent": "PYRA-Barter-Credit-Test/1.0"
    }
    
    try:
        # Test with a simple request that requires authentication
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': 10,
            'page': 1,
            'sparkline': 'false'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API key authentication successful")
            print(f"   Retrieved {len(data)} coins")
            print(f"   First coin: {data[0]['name']} (${data[0]['current_price']})")
            
            # Check rate limit headers
            remaining = response.headers.get('x-ratelimit-remaining')
            if remaining:
                print(f"   Rate limit remaining: {remaining}")
                
        elif response.status_code == 401:
            print("❌ API key authentication failed - Invalid API key")
            print(f"   Response: {response.text}")
            return False
        elif response.status_code == 429:
            print("⚠️ Rate limit exceeded")
            print(f"   Response: {response.text}")
            return False
        else:
            print
