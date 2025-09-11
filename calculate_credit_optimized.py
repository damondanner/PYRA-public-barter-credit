#!/usr/bin/env python3
"""
Optimized PYRA Barter Credit Calculator

This optimized version maximizes the use of your 10,000 monthly CoinGecko API calls
by implementing smart caching, batching, and call optimization strategies.
"""

import requests
import json
import time
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import pickle
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizedPyraCalculator:
    """Optimized PYRA Barter Credit Calculator with smart API usage."""
    
    def __init__(self, api_key: str):
        if not api_key or api_key == 'your_api_key_here':
            raise ValueError("Valid CoinGecko API key is required!")
            
        self.api_key = api_key
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        
        # Set headers for API requests - CoinGecko Pro API format
        self.session.headers.update({
            "x-cg-demo-api-key": self.api_key,
            "Accept": "application/json",
            "User-Agent": "PYRA-Barter-Credit/1.0"
        })
        
        # Call tracking for monthly limit management
        self.calls_made_today = 0
        self.monthly_calls_used = 0
        self.max_monthly_calls = 10000
        
        # Optimized timing - with API key we can make more frequent calls
        self.min_request_interval = 0.5  # 500ms between requests (120 calls/minute max)
        self.last_request_time = 0
        
        # Cache settings for maximum efficiency
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_duration = 300  # 5 minutes cache
        
        # Load call tracking
        self.load_call_tracking()
        
    def load_call_tracking(self):
        """Load API call tracking data."""
        tracking_file = self.cache_dir / "call_tracking.json"
        if tracking_file.exists():
            try:
                with open(tracking_file, 'r') as f:
                    data = json.load(f)
                    self.monthly_calls_used = data.get('monthly_calls', 0)
                    last_reset = datetime.fromisoformat(data.get('last_reset', '2000-01-01'))
                    
                    # Reset monthly counter if it's a new month
                    if last_reset.month != datetime.now().month:
                        self.monthly_calls_used = 0
                        self.save_call_tracking()
                        
            except Exception as e:
                logger.warning(f"Could not load call tracking: {e}")
    
    def save_call_tracking(self):
        """Save API call tracking data."""
        tracking_file = self.cache_dir / "call_tracking.json"
        data = {
            'monthly_calls': self.monthly_calls_used,
            'last_reset': datetime.now().isoformat(),
            'calls_today': self.calls_made_today
        }
        with open(tracking_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def can_make_api_call(self) -> bool:
        """Check if we can make an API call within limits."""
        if self.monthly_calls_used >= self.max_monthly_calls:
            logger.error(f"Monthly API limit reached: {self.monthly_calls_used}/{self.max_monthly_calls}")
            return False
        return True
    
    def _rate_limit_and_track(self):
        """Apply rate limiting and track API calls."""
        if not self.can_make_api_call():
            raise Exception("Monthly API call limit reached!")
            
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.calls_made_today += 1
        self.monthly_calls_used += 1
        
        # Save tracking every 10 calls
        if self.monthly_calls_used % 10 == 0:
            self.save_call_tracking()
    
    def get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """Get cached data if still valid."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    
                cached_time = datetime.fromisoformat(cached_data.get('cached_at', '2000-01-01'))
                if datetime.now() - cached_time < timedelta(seconds=self.cache_duration):
                    logger.info(f"Using cached data for {cache_key}")
                    return cached_data['data']
                    
            except Exception as e:
                logger.warning(f"Error reading cache {cache_key}: {e}")
                
        return None
    
    def save_cached_data(self, cache_key: str, data: Dict):
        """Save data to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        cached_data = {
            'cached_at': datetime.now().isoformat(),
            'data': data
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cached_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Error saving cache {cache_key}: {e}")
    
    def fetch_coins_optimized(self) -> List[Dict]:
        """
        Fetch cryptocurrency data using optimized batching strategy.
        Uses larger pages and smart caching to minimize API calls.
        """
        # Check cache first
        cached_coins = self.get_cached_data("all_coins")
        if cached_coins:
            return cached_coins
        
        all_coins = []
        page = 1
        per_page = 250  # Maximum allowed by CoinGecko
        max_pages = 20  # Limit to ~5000 coins to save API calls
        
        logger.info("Fetching cryptocurrency data with optimized strategy...")
        
        while page <= max_pages:
            try:
                self._rate_limit_and_track()
                
                url = f"{self.base_url}/coins/markets"
                params = {
                    'vs_currency': 'usd',
                    'order': 'market_cap_desc',
                    'per_page': per_page,
                    'page': page,
                    'sparkline': 'false',
                    'price_change_percentage': '24h'
                }
                
                logger.info(f"API Call #{self.monthly_calls_used}: Fetching page {page} ({len(all_coins)} coins so far)")
                response = self.session.get(url, params=params, timeout=15)
                
                if response.status_code == 429:
                    logger.warning("Rate limit hit, waiting 60 seconds...")
                    time.sleep(60)
                    continue
                    
                response.raise_for_status()
                data = response.json()
                
                if not data or len(data) < per_page:
                    all_coins.extend(data)
                    logger.info(f"Finished fetching. Final page {page} with {len(data)} coins")
                    break
                
                all_coins.extend(data)
                page += 1
                
                # Progress logging
                logger.info(f"Page {page-1} complete. Total coins: {len(all_coins)}")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed on page {page}: {e}")
                if page == 1:
                    raise  # If first page fails, we have no data
                break
            except Exception as e:
                logger.error(f"Unexpected error on page {page}: {e}")
                break
        
        logger.info(f"Total API calls made: {self.calls_made_today} today, {self.monthly_calls_used} this month")
        logger.info(f"Remaining monthly calls: {self.max_monthly_calls - self.monthly_calls_used}")
        
        # Cache the results
        self.save_cached_data("all_coins", all_coins)
        
        return all_coins
    
    def filter_and_calculate(self, coins: List[Dict]) -> Dict:
        """Filter coins and calculate PYRA Barter Credit with enhanced validation."""
        valid_prices = []
        total_processed = len(coins)
        
        # Enhanced filtering for better data quality
        for coin in coins:
            try:
                price = coin.get('current_price')
                market_cap = coin.get('market_cap')
                volume = coin.get('total_volume')
                
                # Skip if price is None or invalid
                if price is None or not isinstance(price, (int, float)):
                    continue
                
                price_float = float(price)
                
                # Enhanced filtering criteria
                if (price_float <= 0 or 
                    price_float < 0.01 or  # Below 1 cent
                    price_float > 1000000 or  # Above $1M (likely error)
                    market_cap is None or 
                    market_cap <= 0):  # No market cap data
                    continue
                
                # Additional quality filters
                if volume is not None and volume <= 0:  # No trading volume
                    continue
                    
                valid_prices.append(price_float)
                
            except (ValueError, TypeError) as e:
                continue
        
        valid_count = len(valid_prices)
        
        if not valid_prices:
            logger.error("No valid cryptocurrency prices found!")
            return {
                'value': 0.0,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'total_coins_processed': total_processed,
                'valid_coins_used': 0,
                'status': 'error',
                'error': 'No valid cryptocurrency prices found',
                'api_calls_used': self.monthly_calls_used,
                'api_calls_remaining': self.max_monthly_calls - self.monthly_calls_used
            }
        
        # Calculate average
        average_price = sum(valid_prices) / len(valid_prices)
        
        # Calculate additional statistics
        sorted_prices = sorted(valid_prices)
        median_price = sorted_prices[len(sorted_prices)//2]
        min_price = min(valid_prices)
        max_price = max(valid_prices)
        
        result = {
            'value': round(average_price, 6),
            'median': round(median_price, 6),
            'min': round(min_price, 6),
            'max': round(max_price, 6),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_coins_processed': total_processed,
            'valid_coins_used': valid_count,
            'filter_rate': round((valid_count / total_processed) * 100, 1),
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'status': 'success',
            'api_calls_used': self.monthly_calls_used,
            'api_calls_remaining': self.max_monthly_calls - self.monthly_calls_used,
            'cache_duration': self.cache_duration
        }
        
        logger.info(f"PYRA Barter Credit calculated: ${result['value']:.6f}")
        logger.info(f"Stats: {valid_count}/{total_processed} coins valid ({result['filter_rate']}%)")
        
        return result
    
    def get_barter_credit(self) -> Dict:
        """Main method to get PYRA Barter Credit with optimization."""
        try:
            # Check if we have recent cached result
            cached_result = self.get_cached_data("final_result")
            if cached_result:
                logger.info("Returning cached PYRA Barter Credit result")
                return cached_result
            
            logger.info("Calculating fresh PYRA Barter Credit...")
            
            # Fetch cryptocurrency data
            all_coins = self.fetch_coins_optimized()
            
            if not all_coins:
                return {
                    'value': 0.0,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'total_coins_processed': 0,
                    'valid_coins_used': 0,
                    'status': 'error',
                    'error': 'No cryptocurrency data retrieved',
                    'api_calls_used': self.monthly_calls_used,
                    'api_calls_remaining': self.max_monthly_calls - self.monthly_calls_used
                }
            
            # Calculate result
            result = self.filter_and_calculate(all_coins)
            
            # Cache the final result
            if result['status'] == 'success':
                self.save_cached_data("final_result", result)
            
            # Save call tracking
            self.save_call_tracking()
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating barter credit: {e}")
            return {
                'value': 0.0,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'total_coins_processed': 0,
                'valid_coins_used': 0,
                'status': 'error',
                'error': str(e),
                'api_calls_used': self.monthly_calls_used,
                'api_calls_remaining': self.max_monthly_calls - self.monthly_calls_used
            }
    
    def get_api_status(self) -> Dict:
        """Get current API usage status."""
        return {
            'monthly_calls_used': self.monthly_calls_used,
            'monthly_calls_remaining': self.max_monthly_calls - self.monthly_calls_used,
            'calls_today': self.calls_made_today,
            'monthly_limit': self.max_monthly_calls,
            'usage_percentage': round((self.monthly_calls_used / self.max_monthly_calls) * 100, 2),
            'estimated_daily_budget': round(self.max_monthly_calls / 30, 0),
            'cache_duration_minutes': self.cache_duration / 60
        }

# Create optimized instance with your API key
def create_calculator():
    """Create calculator instance with your API key."""
    api_key = "CG-J1rJe3A9zGGeBLem65PAifzY"  # Your API key
    return OptimizedPyraCalculator(api_key)

def main():
    """Test the optimized calculator."""
    try:
        calculator = create_calculator()
        
        print("🔍 API Status Check:")
        status = calculator.get_api_status()
        print(json.dumps(status, indent=2))
        
        print("\n🏛️ Calculating PYRA Barter Credit...")
        result = calculator.get_barter_credit()
        
        print("\n📊 Results:")
        print(json.dumps(result, indent=2))
        
        print(f"\n💎 PYRA Barter Credit: ${result.get('value', 0):.6f}")
        print(f"📈 Based on {result.get('valid_coins_used', 0):,} cryptocurrencies")
        print(f"🔢 API calls used: {result.get('api_calls_used', 0)}/10,000 this month")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
