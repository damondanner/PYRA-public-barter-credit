# PYRA's Public Barter Credit

A comprehensive API service that calculates PYRA's Barter Credit by averaging all valid cryptocurrencies from CoinGecko's free API. This repository provides multiple integration methods for Web2, Web3, and various platforms.

## What is PYRA's Barter Credit?

PYRA's Barter Credit is calculated by:
1. Fetching all cryptocurrencies from CoinGecko's free API
2. Removing null values, errors, and any cryptocurrencies below $0.01
3. Taking a simple average of all remaining valid prices
4. This average becomes the PYRA Barter Credit value

## Features

- **Real-time calculation** from CoinGecko API
- **Multiple output formats** (JSON, HTML, JavaScript)
- **Easy integration** for Web2, Web3, and platforms like Wix
- **Error handling** and data validation
- **Caching** to respect API rate limits
- **CORS enabled** for web applications

## Quick Start

### For Developers

```bash
# Clone the repository
git clone https://github.com/yourusername/pyras-public-barter-credit.git
cd pyras-public-barter-credit

# Install dependencies
pip install -r requirements.txt

# Run the API server
python app.py
```

### For Web Integration

#### Direct JSON Access
```javascript
fetch('https://yourdomain.com/api/barter-credit')
  .then(response => response.json())
  .then(data => console.log('PYRA Barter Credit:', data.value));
```

#### HTML Embed (for Wix, etc.)
```html
<div id="pyra-credit">Loading PYRA Barter Credit...</div>
<script src="https://yourdomain.com/embed.js"></script>
```

#### Web3 Integration
```javascript
// Use the Web3 compatible version
import { getPyraBarterCredit } from './web3-integration.js';
const credit = await getPyraBarterCredit();
```

## API Endpoints

- `GET /api/barter-credit` - Returns current PYRA Barter Credit in JSON
- `GET /api/barter-credit/html` - Returns formatted HTML
- `GET /embed.js` - JavaScript embed for easy integration
- `GET /health` - Health check endpoint

## Response Format

```json
{
  "value": 2.34567,
  "timestamp": "2025-09-10T15:30:00Z",
  "total_coins_processed": 15234,
  "valid_coins_used": 8456,
  "last_updated": "2025-09-10T15:30:00Z",
  "status": "success"
}
```

## File Structure

```
├── app.py                 # Main Flask API server
├── calculate_credit.py    # Core calculation logic
├── requirements.txt       # Python dependencies
├── static/
│   ├── embed.js          # JavaScript embed code
│   └── widget.html       # HTML widget
├── templates/
│   └── display.html      # HTML template for display
├── web3/
│   └── integration.js    # Web3 specific integration
├── examples/
│   ├── wix-embed.html    # Example for Wix integration
│   ├── react-example.jsx # React component example
│   └── vanilla-js.html   # Pure JavaScript example
├── Dockerfile            # Docker deployment
├── .github/workflows/
│   └── deploy.yml        # GitHub Actions for deployment
└── README.md            # This file
```

## Integration Examples

### Wix HTML Component
Paste this into a Wix HTML component:
```html
<div id="pyra-display"></div>
<script>
fetch('YOUR_API_URL/api/barter-credit')
  .then(r => r.json())
  .then(d => {
    document.getElementById('pyra-display').innerHTML = 
      `<h3>PYRA Barter Credit: $${d.value.toFixed(6)}</h3>
       <p>Last updated: ${new Date(d.timestamp).toLocaleString()}</p>`;
  });
</script>
```

### React Component
```jsx
import { useState, useEffect } from 'react';

function PyraBarterCredit() {
  const [credit, setCredit] = useState(null);
  
  useEffect(() => {
    fetch('/api/barter-credit')
      .then(r => r.json())
      .then(setCredit);
  }, []);
  
  return (
    <div>
      {credit && <h2>PYRA Barter Credit: ${credit.value.toFixed(6)}</h2>}
    </div>
  );
}
```

## Deployment Options

### GitHub Pages (Static)
- Use the static JSON generation method
- Files automatically update via GitHub Actions

### Heroku/Railway/Vercel
- Deploy the Flask app directly
- Environment variables for configuration

### Docker
```bash
docker build -t pyra-barter-credit .
docker run -p 5000:5000 pyra-barter-credit
```

## Environment Variables

```bash
COINGECKO_API_KEY=your_api_key_here  # Optional for higher rate limits
PORT=5000                            # Server port
UPDATE_INTERVAL=300                  # Update interval in seconds
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues or questions, please open a GitHub issue or contact the maintainers.

---

**Note**: This service uses CoinGecko's free API. For production use with high traffic, consider upgrading to CoinGecko's paid plan for higher rate limits.
