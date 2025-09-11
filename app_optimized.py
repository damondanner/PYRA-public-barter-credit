#!/usr/bin/env python3
"""
Optimized Flask API server for PYRA's Barter Credit
Uses your CoinGecko API key efficiently within the 10,000 monthly call limit.
"""

import os
import json
import time
import threading
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template_string, send_from_directory
from flask_cors import CORS

# Import the optimized calculator
try:
    from calculate_credit_optimized import OptimizedPyraCalculator
except ImportError:
    print("❌ Error: calculate_credit_optimized.py not found!")
    print("Make sure to save the optimized calculator file first.")
    exit(1)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables for caching
cached_data = None
last_update_time = 0
update_lock = threading.Lock()
calculator = None

# Configuration - Optimized for your API key
API_KEY = "CG-J1rJe3A9zGGeBLem65PAifzY"  # Your CoinGecko API key
UPDATE_INTERVAL = int(os.environ.get('UPDATE_INTERVAL', 900))  # 15 minutes default (more conservative)

def initialize_calculator():
    """Initialize the optimized calculator."""
    global calculator
    try:
        calculator = OptimizedPyraCalculator(API_KEY)
        print("✅ Calculator initialized with your API key")
        return True
    except Exception as e:
        print(f"❌ Error initializing calculator: {e}")
        return False

def should_update_cache():
    """Check if cache should be updated - more conservative with API calls."""
    global cached_data, last_update_time
    
    if cached_data is None:
        return True
        
    # Check if we have recent data
    time_since_update = time.time() - last_update_time
    
    # If we have an error status, try again sooner
    if cached_data.get('status') == 'error' and time_since_update > 300:  # 5 minutes
        return True
        
    # Normal update interval
    return time_since_update > UPDATE_INTERVAL

def update_cache_background():
    """Update cache in background thread with error handling."""
    global cached_data, last_update_time, calculator
    
    try:
        with update_lock:
            if calculator is None:
                if not initialize_calculator():
                    return
                    
            print(f"🔄 Updating PYRA Barter Credit... (API calls used: {calculator.monthly_calls_used}/10,000)")
            
            new_data = calculator.get_barter_credit()
            cached_data = new_data
            last_update_time = time.time()
            
            if new_data.get('status') == 'success':
                print(f"✅ Cache updated: PYRA Barter Credit = ${new_data.get('value', 0):.6f}")
                print(f"📊 Stats: {new_data.get('valid_coins_used', 0):,} valid coins from {new_data.get('total_coins_processed', 0):,} total")
                print(f"🔢 API Usage: {new_data.get('api_calls_used', 0)}/10,000 monthly calls ({new_data.get('api_calls_remaining', 0)} remaining)")
            else:
                print(f"⚠️ Update completed with error: {new_data.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"❌ Error updating cache: {e}")
        # Create error response if cache update fails
        cached_data = {
            'value': 0.0,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_coins_processed': 0,
            'valid_coins_used': 0,
            'status': 'error',
            'error': f'Update failed: {str(e)}',
            'api_calls_used': calculator.monthly_calls_used if calculator else 0,
            'api_calls_remaining': (10000 - calculator.monthly_calls_used) if calculator else 10000
        }

def get_current_data():
    """Get current barter credit data, updating cache if needed."""
    global cached_data
    
    if should_update_cache():
        if cached_data is None:
            # If no cache exists, update synchronously for first request
            print("🚀 First request - updating synchronously...")
            update_cache_background()
        else:
            # If cache exists but is stale, update in background
            print("🔄 Starting background update...")
            threading.Thread(target=update_cache_background, daemon=True).start()
    
    return cached_data or {
        'value': 0.0,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'total_coins_processed': 0,
        'valid_coins_used': 0,
        'status': 'initializing',
        'error': 'Service starting up...',
        'api_calls_used': 0,
        'api_calls_remaining': 10000
    }

@app.route('/')
def index():
    """Enhanced main page with API usage tracking."""
    html_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PYRA's Barter Credit API - Optimized</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            }
            .credit-display {
                text-align: center;
                background: rgba(255, 255, 255, 0.2);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
            .credit-value {
                font-size: 2.5em;
                font-weight: bold;
                color: #FFD700;
            }
            .api-usage {
                background: rgba(0, 0, 0, 0.2);
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
            }
            .progress-bar {
                background: rgba(255, 255, 255, 0.2);
                height: 20px;
                border-radius: 10px;
                overflow: hidden;
                margin: 10px 0;
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #4CAF50, #FFC107, #FF5722);
                transition: width 0.3s ease;
            }
            .endpoint {
                background: rgba(0, 0, 0, 0.2);
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
                font-family: 'Courier New', monospace;
            }
            button {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background: #45a049;
            }
            .status {
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
            }
            .success { background: rgba(76, 175, 80, 0.3); }
            .error { background: rgba(244, 67, 54, 0.3); }
            .warning { background: rgba(255, 193, 7, 0.3); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏛️ PYRA's Barter Credit API</h1>
            <p><strong>Optimized Version</strong> - Efficient API usage within 10,000 monthly calls</p>
            
            <div class="credit-display">
                <h2>Current PYRA Barter Credit</h2>
                <div class="credit-value" id="creditValue">Loading...</div>
                <p id="lastUpdated">Fetching data...</p>
                <button onclick="updateCredit()">🔄 Refresh</button>
            </div>

            <div class="api-usage">
                <h3>📊 API Usage Monitor</h3>
                <div id="apiUsage">Loading usage stats...</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressBar" style="width: 0%"></div>
                </div>
                <small id="usageDetails">API call details loading...</small>
            </div>

            <div id="status" class="status"></div>

            <h3>📡 API Endpoints</h3>
            <div class="endpoint">GET /api/barter-credit - JSON format</div>
            <div class="endpoint">GET /api/barter-credit/html - HTML format</div>
            <div class="endpoint">GET /api/usage - API usage statistics</div>
            <div class="endpoint">GET /health - Health check</div>

            <h3>📊 Enhanced Statistics</h3>
            <div id="stats">Loading statistics...</div>
        </div>

        <script>
            function updateCredit() {
                document.getElementById('creditValue').innerText = 'Loading...';
                document.getElementById('status').innerHTML = '';
                
                fetch('/api/barter-credit')
                    .then(response => response.json())
                    .then(data => {
                        updateDisplay(data);
                    })
                    .catch(error => {
                        document.getElementById('creditValue').innerText = 'Error';
                        document.getElementById('status').innerHTML = 
                            '<div class="error">❌ Network error: ' + error.message + '</div>';
                    });
            }
            
            function updateDisplay(data) {
                if (data.status === 'success') {
                    document.getElementById('creditValue').innerText = '$' + data.value.toFixed(6);
                    document.getElementById('lastUpdated').innerText = 
                        'Last updated: ' + new Date(data.timestamp).toLocaleString();
                    document.getElementById('status').innerHTML = 
                        '<div class="success">✅ Data updated successfully</div>';
                } else if (data.status === 'error') {
                    document.getElementById('creditValue').innerText = 'Error';
                    document.getElementById('status').innerHTML = 
                        '<div class="error">❌ Error: ' + (data.error || 'Unknown error') + '</div>';
                } else {
                    document.getElementById('creditValue').innerText = 'Starting...';
                    document.getElementById('status').innerHTML = 
                        '<div class="warning">⏳ Service initializing...</div>';
                }
                
                // Update API usage
                if (data.api_calls_used !== undefined) {
                    const usagePercent = (data.api_calls_used / 10000) * 100;
                    document.getElementById('apiUsage').innerHTML = 
                        `<strong>${data.api_calls_used}/10,000</strong> monthly calls used (${usagePercent.toFixed(1)}%)`;
                    document.getElementById('progressBar').style.width = usagePercent + '%';
                    document.getElementById('usageDetails').innerText = 
                        `${data.api_calls_remaining || 0} calls remaining this month`;
                }
                
                // Update stats
                if (data.total_coins_processed) {
                    document.getElementById('stats').innerHTML = `
                        <strong>Coins processed:</strong> ${data.total_coins_processed.toLocaleString()}<br>
                        <strong>Valid coins:</strong> ${data.valid_coins_used.toLocaleString()}<br>
                        <strong>Filter rate:</strong> ${data.filter_rate || 'N/A'}%<br>
                        <strong>Price range:</strong> $${data.min || 0} - $${data.max || 0}<br>
                        <strong>Median price:</strong> $${data.median || 0}
                    `;
                }
            }

            // Auto-update every 2 minutes (but API only updates every 15 minutes due to caching)
            setInterval(updateCredit, 120000);
            
            // Initial load
            updateCredit();
        </script>
    </body>
    </html>
    '''
    return html_template

@app.route('/api/barter-credit')
def api_barter_credit():
    """JSON API endpoint for barter credit."""
    data = get_current_data()
    return jsonify(data)

@app.route('/api/usage')
def api_usage():
    """API usage statistics endpoint."""
    global calculator
    
    if calculator is None:
        return jsonify({
            'error': 'Calculator not initialized',
            'monthly_calls_used': 0,
            'monthly_calls_remaining': 10000
        })
    
    usage_stats = calculator.get_api_status()
    return jsonify(usage_stats)

@app.route('/api/barter-credit/html')
def api_barter_credit_html():
    """HTML formatted barter credit."""
    data = get_current_data()
    
    if data['status'] == 'success':
        html = f'''
        <div style="font-family: Arial, sans-serif; padding: 20px; background: #f0f8ff; border-radius: 10px; text-align: center;">
            <h2 style="color: #2c3e50;">PYRA's Barter Credit</h2>
            <div style="font-size: 2em; font-weight: bold; color: #27ae60;">${data['value']:.6f}</div>
            <p style="color: #7f8c8d;">
                Based on {data['valid_coins_used']:,} valid cryptocurrencies<br>
                Last updated: {datetime.fromisoformat(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S UTC')}<br>
                API calls used: {data.get('api_calls_used', 0)}/10,000 this month
            </p>
        </div>
        '''
    else:
        html = f'''
        <div style="font-family: Arial, sans-serif; padding: 20px; background: #ffe6e6; border-radius: 10px; text-align: center;">
            <h2 style="color: #e74c3c;">PYRA's Barter Credit - {data['status'].title()}</h2>
            <p style="color: #c0392b;">{data.get('error', 'Service unavailable')}</p>
            <small>API calls used: {data.get('api_calls_used', 0)}/10,000 this month</small>
        </div>
        '''
    
    return html

@app.route('/health')
def health_check():
    """Enhanced health check with API usage info."""
    global calculator, cached_data
    
    health_data = {
        'status': 'healthy' if cached_data and cached_data.get('status') == 'success' else 'degraded',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'cache_age_seconds': int(time.time() - last_update_time) if cached_data else None,
        'update_interval': UPDATE_INTERVAL,
        'last_credit_value': cached_data.get('value') if cached_data else None,
        'api_initialized': calculator is not None
    }
    
    if calculator:
        usage_stats = calculator.get_api_status()
        health_data.update(usage_stats)
    
    return jsonify(health_data)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("🏛️ Starting PYRA Barter Credit API (Optimized)")
    print("=" * 50)
    print(f"🔑 API Key: CG-J1rJ...{API_KEY[-4:]} (last 4 digits)")
    print(f"⏰ Update interval: {UPDATE_INTERVAL} seconds ({UPDATE_INTERVAL/60} minutes)")
    print(f"📊 Monthly limit: 10,000 API calls")
    
    # Initialize calculator and get first data
    if initialize_calculator():
        print("🔄 Getting initial PYRA Barter Credit data...")
        update_cache_background()
        print(f"✅ Initial data loaded")
    else:
        print("⚠️ Calculator initialization failed - will retry on first request")
    
    print(f"🚀 Starting server on port {port}")
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=port, debug=False)
