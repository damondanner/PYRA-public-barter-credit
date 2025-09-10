#!/usr/bin/env python3
"""
Static JSON Generator for PYRA's Barter Credit

This script generates static JSON files that can be served from GitHub Pages
or any static hosting service. Useful for simple integrations that don't need
a full API server.
"""

import os
import json
import time
from datetime import datetime, timezone
from calculate_credit import PyraBarterCreditCalculator

def generate_static_files():
    """Generate static JSON files for PYRA Barter Credit."""
    
    # Create output directory
    output_dir = 'static-output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize calculator
    api_key = os.environ.get('COINGECKO_API_KEY', None)
    calculator = PyraBarterCreditCalculator(api_key=api_key)
    
    print("Generating PYRA Barter Credit static files...")
    
    # Get current barter credit data
    credit_data = calculator.get_barter_credit()
    
    # Generate main JSON file
    with open(f'{output_dir}/barter-credit.json', 'w') as f:
        json.dump(credit_data, f, indent=2)
    
    # Generate simple value-only file
    value_data = {
        'value': credit_data.get('value', 0),
        'timestamp': credit_data.get('timestamp'),
        'status': credit_data.get('status')
    }
    
    with open(f'{output_dir}/value.json', 'w') as f:
        json.dump(value_data, f, indent=2)
    
    # Generate JSONP files for cross-origin requests
    jsonp_callback = f"pyraCreditCallback({json.dumps(credit_data)})"
    with open(f'{output_dir}/barter-credit.jsonp', 'w') as f:
        f.write(jsonp_callback)
    
    # Generate HTML display file
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PYRA's Barter Credit</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .container {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            max-width: 500px;
        }}
        .title {{
            font-size: 2em;
            margin-bottom: 20px;
            font-weight: bold;
        }}
        .value {{
            font-size: 3em;
            color: #FFD700;
            font-weight: bold;
            margin: 30px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .info {{
            opacity: 0.9;
            margin: 15px 0;
            font-size: 1.1em;
        }}
        .stats {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }}
        .stat {{
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
        }}
        .refresh-info {{
            font-size: 0.9em;
            opacity: 0.7;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="title">🏛️ PYRA's Barter Credit</div>
        <div class="value">${credit_data.get('value', 0):.6f}</div>
        <div class="info">
            Updated: {datetime.fromisoformat(credit_data.get('timestamp', '')).strftime('%Y-%m-%d %H:%M:%S UTC') if credit_data.get('timestamp') else 'Unknown'}
        </div>
        {f'''
        <div class="stats">
            <div class="stat">
                <span>Total Coins Processed:</span>
                <span>{credit_data.get('total_coins_processed', 0):,}</span>
            </div>
            <div class="stat">
                <span>Valid Coins Used:</span>
                <span>{credit_data.get('valid_coins_used', 0):,}</span>
            </div>
            <div class="stat">
                <span>Success Rate:</span>
                <span>{((credit_data.get('valid_coins_used', 0) / max(credit_data.get('total_coins_processed', 1), 1)) * 100):.1f}%</span>
            </div>
        </div>
        ''' if credit_data.get('status') == 'success' else ''}
        <div class="refresh-info">
            📅 Static files updated via GitHub Actions<br>
            🔄 Data refreshes automatically
        </div>
    </div>
</body>
</html>'''
    
    with open(f'{output_dir}/index.html', 'w') as f:
        f.write(html_content)
    
    # Generate JavaScript embed file
    js_embed = f'''
// PYRA Barter Credit Static Embed
(function() {{
    const PYRA_DATA = {json.dumps(credit_data)};
    
    function loadPyraCredit() {{
        const elements = document.querySelectorAll('.pyra-barter-credit');
        elements.forEach(el => {{
            if (PYRA_DATA.status === 'success') {{
                el.innerHTML = `
                    <div style="font-family: Arial, sans-serif; padding: 15px; background: linear-gradient(45deg, #667eea, #764ba2); color: white; border-radius: 8px; text-align: center;">
                        <h3 style="margin: 0 0 10px 0;">PYRA Barter Credit</h3>
                        <div style="font-size: 1.8em; font-weight: bold;">$${{PYRA_DATA.value.toFixed(6)}}</div>
                        <small style="opacity: 0.8;">Updated: ${{new Date(PYRA_DATA.timestamp).toLocaleString()}}</small>
                    </div>
                `;
            }} else {{
                el.innerHTML = '<div style="color: red;">Error loading PYRA Barter Credit</div>';
            }}
        }});
    }}

    // Load when DOM is ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', loadPyraCredit);
    }} else {{
        loadPyraCredit();
    }}

    // Expose global function
    window.updatePyraCredit = loadPyraCredit;
    window.PYRA_CREDIT_DATA = PYRA_DATA;
}})();
'''
    
    with open(f'{output_dir}/embed.js', 'w') as f:
        f.write(js_embed)
    
    # Generate CORS-friendly JSON with CORS headers info
    cors_info = {
        'data': credit_data,
        'cors_note': 'This is a static file. For CORS support, use the API endpoints.',
        'api_endpoints': {
            'json': 'https://your-api-domain.com/api/barter-credit',
            'html': 'https://your-api-domain.com/api/barter-credit/html',
            'embed': 'https://your-api-domain.com/embed.js'
        }
    }
    
    with open(f'{output_dir}/cors.json', 'w') as f:
        json.dump(cors_info, f, indent=2)
    
    # Generate XML format for legacy systems
    xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<pyra_barter_credit>
    <value>{credit_data.get('value', 0)}</value>
    <timestamp>{credit_data.get('timestamp', '')}</timestamp>
    <total_coins_processed>{credit_data.get('total_coins_processed', 0)}</total_coins_processed>
    <valid_coins_used>{credit_data.get('valid_coins_used', 0)}</valid_coins_used>
    <status>{credit_data.get('status', 'unknown')}</status>
    <last_updated>{datetime.now(timezone.utc).isoformat()}</last_updated>
</pyra_barter_credit>'''
    
    with open(f'{output_dir}/barter-credit.xml', 'w') as f:
        f.write(xml_content)
    
    # Generate CSV format
    csv_content = f'''field,value
current_value,{credit_data.get('value', 0)}
timestamp,{credit_data.get('timestamp', '')}
total_coins_processed,{credit_data.get('total_coins_processed', 0)}
valid_coins_used,{credit_data.get('valid_coins_used', 0)}
status,{credit_data.get('status', 'unknown')}
last_updated,{datetime.now(timezone.utc).isoformat()}'''
    
    with open(f'{output_dir}/barter-credit.csv', 'w') as f:
        f.write(csv_content)
    
    # Generate a simple text file with just the value
    with open(f'{output_dir}/value.txt', 'w') as f:
        f.write(str(credit_data.get('value', 0)))
    
    # Create a robots.txt file
    robots_content = '''User-agent: *
Allow: /

# PYRA Barter Credit Data
# Generated automatically via GitHub Actions
# Visit https://github.com/yourusername/pyras-public-barter-credit for source
'''
    
    with open(f'{output_dir}/robots.txt', 'w') as f:
        f.write(robots_content)
    
    # Create README for the static files
    readme_content = f'''# PYRA's Barter Credit - Static Files

Generated on: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
Current Value: ${credit_data.get('value', 0):.6f}

## Available Files:

- `barter-credit.json` - Complete data in JSON format
- `value.json` - Simplified value-only JSON
- `barter-credit.jsonp` - JSONP format for cross-origin requests
- `index.html` - Web display page
- `embed.js` - JavaScript embed code
- `cors.json` - CORS information and API endpoints
- `barter-credit.xml` - XML format
- `barter-credit.csv` - CSV format
- `value.txt` - Plain text value only

## Usage Examples:

### Direct JSON Access:
```javascript
fetch('./barter-credit.json')
  .then(r => r.json())
  .then(data => console.log('PYRA Credit:', data.value));
```

### HTML Embed:
```html
<div class="pyra-barter-credit"></div>
<script src="./embed.js"></script>
```

### JSONP (for legacy browsers):
```html
<script>
function pyraCreditCallback(data) {{
    console.log('PYRA Credit:', data.value);
}}
</script>
<script src="./barter-credit.jsonp"></script>
```

## Automatic Updates

These static files are automatically updated every day at 6 AM UTC via GitHub Actions.
For real-time data, use the API endpoints listed in `cors.json`.
'''
    
    with open(f'{output_dir}/README.md', 'w') as f:
        f.write(readme_content)
    
    print(f"✅ Static files generated successfully!")
    print(f"   Current PYRA Barter Credit: ${credit_data.get('value', 0):.6f}")
    print(f"   Status: {credit_data.get('status', 'unknown')}")
    print(f"   Files generated in: {output_dir}/")
    print(f"   Timestamp: {credit_data.get('timestamp', 'unknown')}")
    
    return credit_data

def main():
    """Main function for command line execution."""
    try:
        result = generate_static_files()
        print(f"\n📊 Generation Summary:")
        print(f"   Value: ${result.get('value', 0):.6f}")
        print(f"   Total coins: {result.get('total_coins_processed', 0):,}")
        print(f"   Valid coins: {result.get('valid_coins_used', 0):,}")
        
        if result.get('status') == 'error':
            print(f"   ⚠️  Error: {result.get('error')}")
            return 1
        else:
            print(f"   ✅ Success!")
            return 0
            
    except Exception as e:
        print(f"❌ Error generating static files: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
