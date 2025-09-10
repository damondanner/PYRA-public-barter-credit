#!/usr/bin/env python3
"""
Flask API server for PYRA's Barter Credit

Provides REST API endpoints and web interfaces for accessing
PYRA's Barter Credit data.
"""

import os
import json
import time
import threading
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
from calculate_credit import PyraBarterCreditCalculator

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables for caching
cached_data = None
last_update_time = 0
update_lock = threading.Lock()

# Configuration
UPDATE_INTERVAL = int(os.environ.get('UPDATE_INTERVAL', 300))  # 5 minutes default
API_KEY = os.environ.get('COINGECKO_API_KEY', None)

calculator = PyraBarterCreditCalculator(api_key=API_KEY)

def should_update_cache():
    """Check if cache should be updated."""
    return (cached_data is None or 
            time.time() - last_update_time > UPDATE_INTERVAL)

def update_cache_background():
    """Update cache in background thread."""
    global cached_data, last_update_time
    
    try:
        with update_lock:
            new_data = calculator.get_barter_credit()
            cached_data = new_data
            last_update_time = time.time()
            print(f"Cache updated: PYRA Barter Credit = ${new_data.get('value', 0):.6f}")
    except Exception as e:
        print(f"Error updating cache: {e}")

def get_current_data():
    """Get current barter credit data, updating cache if needed."""
    global cached_data
    
    if should_update_cache():
        # If no cache exists, update synchronously
        if cached_data is None:
            update_cache_background()
        else:
            # If cache exists but is stale, update in background
            threading.Thread(target=update_cache_background, daemon=True).start()
    
    return cached_data or {
        'value': 0.0,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'total_coins_processed': 0,
        'valid_coins_used': 0,
        'status': 'error',
        'error': 'Data not available'
    }

@app.route('/')
def index():
    """Main page with documentation and live display."""
    html_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PYRA's Barter Credit API</title>
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏛️ PYRA's Barter Credit API</h1>
            
            <div class="credit-display">
                <h2>Current PYRA Barter Credit</h2>
                <div class="credit-value" id="creditValue">Loading...</div>
                <p id="lastUpdated">Fetching data...</p>
                <button onclick="updateCredit()">🔄 Refresh</button>
            </div>

            <div id="status" class="status"></div>

            <h3>📡 API Endpoints</h3>
            <div class="endpoint">
                GET /api/barter-credit - JSON format
            </div>
            <div class="endpoint">
                GET /api/barter-credit/html - HTML format
            </div>
            <div class="endpoint">
                GET /embed.js - JavaScript embed
            </div>
            <div class="endpoint">
                GET /health - Health check
            </div>

            <h3>🔗 Quick Integration</h3>
            <div class="endpoint">
                // JavaScript fetch example<br>
                fetch('/api/barter-credit')<br>
                &nbsp;&nbsp;.then(r => r.json())<br>
                &nbsp;&nbsp;.then(data => console.log('PYRA:', data.value));
            </div>

            <h3>📊 Statistics</h3>
            <div id="stats">Loading statistics...</div>
        </div>

        <script>
            function updateCredit() {
                document.getElementById('creditValue').innerText = 'Loading...';
                document.getElementById('status').innerHTML = '';
                
                fetch('/api/barter-credit')
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            document.getElementById('creditValue').innerText = '$' + data.value.toFixed(6);
                            document.getElementById('lastUpdated').innerText = 
                                'Last updated: ' + new Date(data.timestamp).toLocaleString();
                            document.getElementById('status').innerHTML = 
                                '<div class="success">✅ Data updated successfully</div>';
                            document.getElementById('stats').innerHTML = `
                                <strong>Total coins processed:</strong> ${data.total_coins_processed.toLocaleString()}<br>
                                <strong>Valid coins used:</strong> ${data.valid_coins_used.toLocaleString()}<br>
                                <strong>Filter rate:</strong> ${((data.valid_coins_used / data.total_coins_processed) * 100).toFixed(1)}%
                            `;
                        } else {
                            document.getElementById('creditValue').innerText = 'Error';
                            document.getElementById('status').innerHTML = 
                                '<div class="error">❌ Error: ' + (data.error || 'Unknown error') + '</div>';
                        }
                    })
                    .catch(error => {
                        document.getElementById('creditValue').innerText = 'Error';
                        document.getElementById('status').innerHTML = 
                            '<div class="error">❌ Network error: ' + error.message + '</div>';
                    });
            }

            // Auto-update every 60 seconds
            setInterval(updateCredit, 60000);
            
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
                Last updated: {datetime.fromisoformat(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S UTC')}
            </p>
        </div>
        '''
    else:
        html = f'''
        <div style="font-family: Arial, sans-serif; padding: 20px; background: #ffe6e6; border-radius: 10px; text-align: center;">
            <h2 style="color: #e74c3c;">PYRA's Barter Credit - Error</h2>
            <p style="color: #c0392b;">{data.get('error', 'Unknown error occurred')}</p>
        </div>
        '''
    
    return html

@app.route('/embed.js')
def embed_js():
    """JavaScript embed code for easy integration."""
    js_code = f'''
(function() {{
    // PYRA Barter Credit Embed
    function loadPyraCredit() {{
        fetch('{os.environ.get("BASE_URL", "")}/api/barter-credit')
            .then(response => response.json())
            .then(data => {{
                const elements = document.querySelectorAll('.pyra-barter-credit');
                elements.forEach(el => {{
                    if (data.status === 'success') {{
                        el.innerHTML = `
                            <div style="font-family: Arial, sans-serif; padding: 15px; background: linear-gradient(45deg, #667eea, #764ba2); color: white; border-radius: 8px; text-align: center;">
                                <h3 style="margin: 0 0 10px 0;">PYRA Barter Credit</h3>
                                <div style="font-size: 1.8em; font-weight: bold;">$${{data.value.toFixed(6)}}</div>
                                <small style="opacity: 0.8;">Updated: ${{new Date(data.timestamp).toLocaleTimeString()}}</small>
                            </div>
                        `;
                    }} else {{
                        el.innerHTML = '<div style="color: red;">Error loading PYRA Barter Credit</div>';
                    }}
                }});
            }})
            .catch(error => {{
                console.error('PYRA Barter Credit error:', error);
                const elements = document.querySelectorAll('.pyra-barter-credit');
                elements.forEach(el => {{
                    el.innerHTML = '<div style="color: red;">Failed to load PYRA Barter Credit</div>';
                }});
            }});
    }}

    // Load immediately and then every 5 minutes
    loadPyraCredit();
    setInterval(loadPyraCredit, 300000);

    // Expose global function
    window.updatePyraCredit = loadPyraCredit;
}})();

// Usage: Add <div class="pyra-barter-credit"></div> to your HTML
'''
    
    response = app.response_class(
        response=js_code,
        status=200,
        mimetype='application/javascript'
    )
    return response

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'cache_age_seconds': int(time.time() - last_update_time) if cached_data else None,
        'update_interval': UPDATE_INTERVAL
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    # Initial cache update
    print("Starting PYRA Barter Credit API...")
    update_cache_background()
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=port, debug=False)
