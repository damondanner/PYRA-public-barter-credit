import React, { useState, useEffect, useCallback } from 'react';

/**
 * PYRA Barter Credit React Component
 * 
 * A complete React component that displays PYRA's barter credit
 * with automatic updates and error handling.
 */

// Configuration
const PYRA_API_URL = 'https://your-api-domain.com/api/barter-credit';
const UPDATE_INTERVAL = 5 * 60 * 1000; // 5 minutes

// Main PYRA Barter Credit Component
const PyraBarterCredit = ({ 
    apiUrl = PYRA_API_URL,
    updateInterval = UPDATE_INTERVAL,
    showStats = true,
    compact = false,
    theme = 'gradient'
}) => {
    const [credit, setCredit] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(null);

    // Fetch PYRA credit data
    const fetchCredit = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000);

            const response = await fetch(apiUrl, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.status === 'success') {
                setCredit(data);
                setLastUpdate(new Date());
                
                // Cache data
                localStorage.setItem('pyra-credit-cache', JSON.stringify({
                    data,
                    timestamp: Date.now()
                }));
            } else {
                throw new Error(data.error || 'API returned error status');
            }

        } catch (err) {
            console.error('Failed to fetch PYRA credit:', err);
            setError(err.message);

            // Try to load cached data
            try {
                const cached = localStorage.getItem('pyra-credit-cache');
                if (cached) {
                    const { data, timestamp } = JSON.parse(cached);
                    const cacheAge = Date.now() - timestamp;
                    
                    // Use cache if less than 1 hour old
                    if (cacheAge < 60 * 60 * 1000) {
                        setCredit(data);
                        setError(prev => `${prev} (showing cached data)`);
                    }
                }
            } catch (cacheError) {
                console.warn('Failed to load cached data:', cacheError);
            }

        } finally {
            setLoading(false);
        }
    }, [apiUrl]);

    // Set up automatic updates
    useEffect(() => {
        fetchCredit();
        const interval = setInterval(fetchCredit, updateInterval);
        return () => clearInterval(interval);
    }, [fetchCredit, updateInterval]);

    // Handle visibility change (refresh when tab becomes active)
    useEffect(() => {
        const handleVisibilityChange = () => {
            if (!document.hidden && credit && lastUpdate) {
                const timeSinceUpdate = Date.now() - lastUpdate.getTime();
                // Refresh if more than 2 minutes since last update
                if (timeSinceUpdate > 2 * 60 * 1000) {
                    fetchCredit();
                }
            }
        };

        document.addEventListener('visibilitychange', handleVisibilityChange);
        return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
    }, [credit, lastUpdate, fetchCredit]);

    // Render methods
    const renderLoading = () => (
        <div className={`pyra-loading ${compact ? 'compact' : ''}`}>
            <div className="loading-spinner"></div>
            <span>Loading PYRA Credit...</span>
        </div>
    );

    const renderError = () => (
        <div className={`pyra-error ${compact ? 'compact' : ''}`}>
            <div className="error-icon">⚠️</div>
            <div className="error-message">
                <strong>Failed to load PYRA Credit</strong>
                <p>{error}</p>
                <button onClick={fetchCredit} className="retry-button">
                    Retry
                </button>
            </div>
        </div>
    );

    const renderCredit = () => (
        <div className={`pyra-credit-display ${theme} ${compact ? 'compact' : ''}`}>
            <div className="pyra-header">
                <h3>🏛️ PYRA's Barter Credit</h3>
            </div>
            
            <div className="pyra-value">
                ${credit.value.toFixed(6)}
            </div>
            
            {!compact && (
                <div className="pyra-timestamp">
                    Last updated: {new Date(credit.timestamp).toLocaleString()}
                </div>
            )}
            
            {showStats && !compact && (
                <div className="pyra-stats">
                    <div className="stat-item">
                        <span className="stat-label">Coins Analyzed:</span>
                        <span className="stat-value">{credit.total_coins_processed?.toLocaleString()}</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">Valid Coins:</span>
                        <span className="stat-value">{credit.valid_coins_used?.toLocaleString()}</span>
                    </div>
                    {credit.total_coins_processed && credit.valid_coins_used && (
                        <div className="stat-item">
                            <span className="stat-label">Success Rate:</span>
                            <span className="stat-value">
                                {((credit.valid_coins_used / credit.total_coins_processed) * 100).toFixed(1)}%
                            </span>
                        </div>
                    )}
                </div>
            )}
            
            <button onClick={fetchCredit} className="refresh-button" disabled={loading}>
                🔄 Refresh
            </button>
        </div>
    );

    // Main render
    if (loading && !credit) return renderLoading();
    if (error && !credit) return renderError();
    if (credit) return renderCredit();
    
    return null;
};

// Compact version for smaller spaces
export const PyraBarterCreditCompact = (props) => (
    <PyraBarterCredit {...props} compact={true} showStats={false} />
);

// Hook for using PYRA credit in other components
export const usePyraBarterCredit = (apiUrl = PYRA_API_URL, updateInterval = UPDATE_INTERVAL) => {
    const [credit, setCredit] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchCredit = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            const response = await fetch(apiUrl);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            if (data.status === 'success') {
                setCredit(data);
            } else {
                throw new Error(data.error);
            }

        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [apiUrl]);

    useEffect(() => {
        fetchCredit();
        const interval = setInterval(fetchCredit, updateInterval);
        return () => clearInterval(interval);
    }, [fetchCredit, updateInterval]);

    return { credit, loading, error, refetch: fetchCredit };
};

// CSS Styles (include in your CSS file or styled-components)
const styles = `
.pyra-credit-display {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    max-width: 400px;
    margin: 20px auto;
    padding: 24px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    backdrop-filter: blur(10px);
    color: white;
}

.pyra-credit-display.gradient {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.pyra-credit-display.dark {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
}

.pyra-credit-display.compact {
    max-width: 200px;
    padding: 16px;
}

.pyra-header h3 {
    margin: 0 0 16px 0;
    font-size: 1.4em;
    font-weight: 600;
}

.pyra-value {
    font-size: 2.2em;
    font-weight: bold;
    color: #FFD700;
    margin: 16px 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.pyra-credit-display.compact .pyra-value {
    font-size: 1.6em;
    margin: 12px 0;
}

.pyra-timestamp {
    font-size: 0.9em;
    opacity: 0.8;
    margin-bottom: 16px;
}

.pyra-stats {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0;
    backdrop-filter: blur(5px);
}

.stat-item {
    display: flex;
    justify-content: space-between;
    margin: 8px 0;
    font-size: 0.9em;
}

.stat-label {
    opacity: 0.8;
}

.stat-value {
    font-weight: 600;
}

.refresh-button {
    background: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 20px;
    cursor: pointer;
    font-size: 0.9em;
    margin-top: 12px;
    transition: all 0.3s ease;
}

.refresh-button:hover:not(:disabled) {
    background: #45a049;
    transform: scale(1.05);
}

.refresh-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

.pyra-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40px;
    color: #667eea;
}

.pyra-loading.compact {
    padding: 20px;
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16px;
}

.pyra-loading.compact .loading-spinner {
    width: 24px;
    height: 24px;
    margin-bottom: 8px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.pyra-error {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40px;
    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
    color: white;
    border-radius: 16px;
    max-width: 400px;
    margin: 20px auto;
    box-shadow: 0 8px 32px rgba(231, 76, 60, 0.3);
}

.pyra-error.compact {
    padding: 20px;
    max-width: 200px;
}

.error-icon {
    font-size: 3em;
    margin-bottom: 16px;
}

.pyra-error.compact .error-icon {
    font-size: 2em;
    margin-bottom: 8px;
}

.error-message {
    text-align: center;
}

.error-message strong {
    display: block;
    margin-bottom: 8px;
    font-size: 1.1em;
}

.error-message p {
    margin: 8px 0;
    opacity: 0.9;
    font-size: 0.9em;
}

.retry-button {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: 2px solid rgba(255, 255, 255, 0.3);
    padding: 8px 16px;
    border-radius: 16px;
    cursor: pointer;
    margin-top: 16px;
    transition: all 0.3s ease;
}

.retry-button:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
}
`;

// Example usage components
export const ExampleUsage = () => {
    const { credit, loading, error } = usePyraBarterCredit();
    
    return (
        <div>
            <h2>Example: Using PYRA Credit in Calculations</h2>
            
            {loading && <p>Loading PYRA credit...</p>}
            {error && <p>Error: {error}</p>}
            {credit && (
                <div>
                    <p>Current PYRA Credit: ${credit.value.toFixed(6)}</p>
                    <p>Convert $100 to PYRA: {(100 / credit.value).toFixed(4)} PYRA units</p>
                    <p>Convert 50 PYRA to USD: ${(50 * credit.value).toFixed(2)}</p>
                </div>
            )}
        </div>
    );
};

// Advanced component with custom styling
export const PyraBarterCreditAdvanced = ({ 
    onCreditChange,
    showConverter = false,
    customStyles = {},
    ...props 
}) => {
    const { credit, loading, error } = usePyraBarterCredit();
    const [convertAmount, setConvertAmount] = useState(100);
    const [convertDirection, setConvertDirection] = useState('usd-to-pyra');

    // Notify parent component of credit changes
    useEffect(() => {
        if (credit && onCreditChange) {
            onCreditChange(credit);
        }
    }, [credit, onCreditChange]);

    const calculateConversion = () => {
        if (!credit || !credit.value) return 0;
        
        if (convertDirection === 'usd-to-pyra') {
            return (convertAmount / credit.value).toFixed(6);
        } else {
            return (convertAmount * credit.value).toFixed(2);
        }
    };

    return (
        <div style={{ ...customStyles }}>
            <PyraBarterCredit {...props} />
            
            {showConverter && credit && !loading && (
                <div className="pyra-converter">
                    <h4>💱 PYRA Converter</h4>
                    <div className="converter-controls">
                        <input
                            type="number"
                            value={convertAmount}
                            onChange={(e) => setConvertAmount(parseFloat(e.target.value) || 0)}
                            placeholder="Amount"
                        />
                        <select 
                            value={convertDirection}
                            onChange={(e) => setConvertDirection(e.target.value)}
                        >
                            <option value="usd-to-pyra">USD → PYRA</option>
                            <option value="pyra-to-usd">PYRA → USD</option>
                        </select>
                    </div>
                    <div className="converter-result">
                        Result: {calculateConversion()} {convertDirection === 'usd-to-pyra' ? 'PYRA' : 'USD'}
                    </div>
                </div>
            )}
        </div>
    );
};

// Widget for dashboards
export const PyraBarterCreditWidget = ({ size = 'medium', theme = 'gradient' }) => {
    const sizeClasses = {
        small: 'compact',
        medium: '',
        large: 'large'
    };

    return (
        <div className={`pyra-widget ${sizeClasses[size]}`}>
            <PyraBarterCredit 
                compact={size === 'small'} 
                theme={theme}
                showStats={size !== 'small'}
            />
        </div>
    );
};

// Export the styles constant for easy importing
export const pyraCreditStyles = styles;

// Default export
export default PyraBarterCredit;

// Additional converter utility
export const convertWithPyraCredit = (amount, fromUnit, toUnit, creditValue) => {
    if (fromUnit === toUnit) return amount;
    
    if (fromUnit === 'usd' && toUnit === 'pyra') {
        return amount / creditValue;
    }
    
    if (fromUnit === 'pyra' && toUnit === 'usd') {
        return amount * creditValue;
    }
    
    throw new Error(`Unsupported conversion: ${fromUnit} to ${toUnit}`);
};

/*
USAGE EXAMPLES:

1. Basic Usage:
```jsx
import PyraBarterCredit from './PyraBarterCredit';

function App() {
    return (
        <div>
            <PyraBarterCredit />
        </div>
    );
}
```

2. Compact Version:
```jsx
import { PyraBarterCreditCompact } from './PyraBarterCredit';

function Sidebar() {
    return (
        <div>
            <PyraBarterCreditCompact theme="dark" />
        </div>
    );
}
```

3. Using the Hook:
```jsx
import { usePyraBarterCredit } from './PyraBarterCredit';

function MyComponent() {
    const { credit, loading, error } = usePyraBarterCredit();
    
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    
    return (
        <div>
            <h3>Current PYRA Credit: ${credit.value.toFixed(6)}</h3>
            <p>Based on {credit.valid_coins_used} cryptocurrencies</p>
        </div>
    );
}
```

4. Advanced Component with Converter:
```jsx
import { PyraBarterCreditAdvanced } from './PyraBarterCredit';

function TradingDashboard() {
    const handleCreditChange = (credit) => {
        console.log('PYRA credit updated:', credit.value);
        // Update your trading calculations here
    };
    
    return (
        <PyraBarterCreditAdvanced 
            onCreditChange={handleCreditChange}
            showConverter={true}
            customStyles={{ margin: '20px 0' }}
        />
    );
}
```

5. Widget for Dashboard:
```jsx
import { PyraBarterCreditWidget } from './PyraBarterCredit';

function Dashboard() {
    return (
        <div className="dashboard-grid">
            <PyraBarterCreditWidget size="small" theme="dark" />
            <PyraBarterCreditWidget size="medium" theme="gradient" />
        </div>
    );
}
```
*/
