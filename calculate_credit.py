#!/usr/bin/env python3
"""
PYRA Barter Credit Calculator

This module fetches cryptocurrency data from CoinGecko's free API,
filters out invalid entries, and calculates the average price
which becomes PYRA's Barter Credit.
"""

import requests
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PyraBarterCreditCalculator:
    """Calculate PYRA's Barter Credit from CoinGecko data."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = api_key
        self.session = requests.Session()
        
        # Set headers for API requests
        if self.api_key:
            self.session.headers.update({"x-cg-demo-api-key": self.api_key})
        
        # Rate limiting - CoinGecko free tier allows 30 calls/minute
        self.last_request_time = 0
        self.min_request_interval = 2  # seconds between requests
    
    def _rate_limit(self):
        """Ensure we don't exceed API rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def fetch_all_cryptocurrencies(self) -> List[Dict]:
        """
        Fetch all cryptocurrencies from CoinGecko.
        
        Returns:
            List of cryptocurrency data dictionaries
        """
        all_coins = []
        page = 1
        per_page = 250  # Maximum allowed by CoinGecko
        
        logger.info("Starting to fetch cryptocurrency data from CoinGecko...")
        
        while True:
            try:
                self._rate_limit()
                
                url = f"{self.base_url}/coins/markets"
                params = {
                    'vs_currency': 'usd',
                    'order': 'market_cap_desc',
                    'per_page': per_page,
                    'page': page,
                    'sparkline': 'false',
                    'price_change_percentage': '24h'
                }
                
                logger.info(f"Fetching page {page}...")
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                # If we get an empty list or less than per_page items, we're done
                if not data or len(data) < per_page:
                    all_coins.extend(data)
                    logger.info(f"Finished fetching. Total pages: {page}")
                    break
                
                all_coins.extend(data)
                page += 1
                
                # Safety check to prevent infinite loops
                if page > 100:  # Should cover all coins as of 2025
                    logger.warning("Reached maximum page limit (100). Stopping fetch.")
                    break
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching data from CoinGecko: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                break
        
        logger.info(f"Total cryptocurrencies fetched: {len(all_coins)}")
        return all_coins
    
    def filter_valid_coins(self, coins: List[Dict]) -> Tuple[List[float], int, int]:
        """
        Filter coins to remove null, error, and sub-penny values.
        
        Args:
            coins: List of cryptocurrency data dictionaries
            
        Returns:
            Tuple of (valid_prices, total_processed, valid_count)
        """
        valid_prices = []
        total_processed = len(coins)
        
        for coin in coins:
            try:
                # Check if current_price exists and is valid
                price = coin.get('current_price')
                
                # Skip if price is None, null, or not a number
                if price is None:
                    continue
                
                # Convert to float and validate
                price_float = float(price)
                
                # Skip if price is not a positive number or below $0.01
                if price_float <= 0 or price_float < 0.01:
                    continue
                
                # Skip if price seems unreasonably high (potential data error)
                if price_float > 1000000:  # $1M per coin seems unreasonable
                    logger.warning(f"Skipping {coin.get('name', 'Unknown')} with suspicious price: ${price_float}")
                    continue
                
                valid_prices.append(price_float)
                
            except (ValueError, TypeError) as e:
                # Skip coins with invalid price data
                logger.debug(f"Skipping coin due to price conversion error: {e}")
                continue
        
        valid_count = len(valid_prices)
        logger.info(f"Filtered coins: {total_processed} total, {valid_count} valid (above $0.01)")
        
        return valid_prices, total_processed, valid_count
    
    def calculate_average(self, prices: List[float]) -> float:
        """
        Calculate simple average of valid prices.
        
        Args:
            prices: List of valid prices
            
        Returns:
            Average price (PYRA Barter Credit)
        """
        if not prices:
            logger.error("No valid prices to calculate average")
            return 0.0
        
        average = sum(prices) / len(prices)
        logger.info(f"Calculated average: ${average:.6f}")
        
        return average
    
    def get_barter_credit(self) -> Dict:
        """
        Main method to calculate PYRA's Barter Credit.
        
        Returns:
            Dictionary with barter credit data
        """
        try:
            # Fetch all cryptocurrency data
            all_coins = self.fetch_all_cryptocurrencies()
            
            if not all_coins:
                return {
                    'value': 0.0,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'total_coins_processed': 0,
                    'valid_coins_used': 0,
                    'status': 'error',
                    'error': 'No cryptocurrency data available'
                }
            
            # Filter valid coins and get prices
            valid_prices, total_processed, valid_count = self.filter_valid_coins(all_coins)
            
            if not valid_prices:
                return {
                    'value': 0.0,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'total_coins_processed': total_processed,
                    'valid_coins_used': 0,
                    'status': 'error',
                    'error': 'No valid cryptocurrency prices found'
                }
            
            # Calculate the average (PYRA Barter Credit)
            barter_credit = self.calculate_average(valid_prices)
            
            result = {
                'value': round(barter_credit, 6),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'total_coins_processed': total_processed,
                'valid_coins_used': valid_count,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'status': 'success'
            }
            
            logger.info(f"PYRA Barter Credit calculated successfully: ${result['value']}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating barter credit: {e}")
            return {
                'value': 0.0,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'total_coins_processed': 0,
                'valid_coins_used': 0,
                'status': 'error',
                'error': str(e)
            }


def main():
    """Command line interface for testing."""
    calculator = PyraBarterCreditCalculator()
    result = calculator.get_barter_credit()
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
