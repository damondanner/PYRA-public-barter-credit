/**
 * PYRA Barter Credit Web3 Integration
 * 
 * This module provides Web3-compatible functions for interacting with
 * PYRA's Barter Credit in decentralized applications.
 */

// Configuration
const PYRA_API_BASE = 'https://your-deployed-api.com'; // Replace with your actual API URL
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds

// Cache management
let cachedCredit = null;
let cacheTimestamp = 0;

/**
 * Fetch PYRA Barter Credit with caching
 * @returns {Promise<Object>} PYRA credit data
 */
export async function getPyraBarterCredit() {
    const now = Date.now();
    
    // Return cached data if still valid
    if (cachedCredit && (now - cacheTimestamp) < CACHE_DURATION) {
        return cachedCredit;
    }
    
    try {
        const response = await fetch(`${PYRA_API_BASE}/api/barter-credit`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.status !== 'success') {
            throw new Error(data.error || 'Unknown error from PYRA API');
        }
        
        // Update cache
        cachedCredit = data;
        cacheTimestamp = now;
        
        return data;
        
    } catch (error) {
        console.error('Failed to fetch PYRA Barter Credit:', error);
        
        // Return cached data if available, even if stale
        if (cachedCredit) {
            console.warn('Using stale cached data due to fetch error');
            return cachedCredit;
        }
        
        // Return error state
        return {
            value: 0,
            status: 'error',
            error: error.message,
            timestamp: new Date().toISOString()
        };
    }
}

/**
 * Get just the credit value as a number
 * @returns {Promise<number>} PYRA credit value
 */
export async function getPyraCreditValue() {
    const data = await getPyraBarterCredit();
    return data.value || 0;
}

/**
 * Convert amount using PYRA Barter Credit as exchange rate
 * @param {number} amount - Amount to convert
 * @param {string} fromUnit - 'usd' or 'pyra'
 * @param {string} toUnit - 'usd' or 'pyra'
 * @returns {Promise<number>} Converted amount
 */
export async function convertWithPyraCredit(amount, fromUnit = 'usd', toUnit = 'pyra') {
    const creditValue = await getPyraCreditValue();
    
    if (creditValue === 0) {
        throw new Error('Cannot convert: PYRA credit value is 0');
    }
    
    if (fromUnit === toUnit) {
        return amount;
    }
    
    if (fromUnit === 'usd' && toUnit === 'pyra') {
        return amount / creditValue;
    }
    
    if (fromUnit === 'pyra' && toUnit === 'usd') {
        return amount * creditValue;
    }
    
    throw new Error(`Unsupported conversion: ${fromUnit} to ${toUnit}`);
}

/**
 * Create a reactive hook for frameworks like React
 * @param {number} refreshInterval - Refresh interval in milliseconds (default: 5 minutes)
 * @returns {Object} Hook object with credit data and refresh function
 */
export function usePyraBarterCredit(refreshInterval = 5 * 60 * 1000) {
    let credit = null;
    let loading = true;
    let error = null;
    let intervalId = null;
    let subscribers = [];

    const notify = () => {
        subscribers.forEach(callback => callback({ credit, loading, error }));
    };

    const fetchCredit = async () => {
        try {
            loading = true;
            error = null;
            notify();
            
            credit = await getPyraBarterCredit();
            error = credit.status === 'error' ? credit.error : null;
            
        } catch (err) {
            error = err.message;
            credit = null;
        } finally {
            loading = false;
            notify();
        }
    };

    const start = () => {
        fetchCredit(); // Initial fetch
        intervalId = setInterval(fetchCredit, refreshInterval);
    };

    const stop = () => {
        if (intervalId) {
            clearInterval(intervalId);
            intervalId = null;
        }
    };

    const subscribe = (callback) => {
        subscribers.push(callback);
        // Return unsubscribe function
        return () => {
            subscribers = subscribers.filter(cb => cb !== callback);
        };
    };

    const refresh = () => {
        fetchCredit();
    };

    return {
        start,
        stop,
        subscribe,
        refresh,
        get current() {
            return { credit, loading, error };
        }
    };
}

/**
 * Web3 contract interaction helper
 * Get PYRA credit for smart contract calls
 */
export class PyraWeb3Helper {
    constructor(web3Instance, contractAddress, contractABI) {
        this.web3 = web3Instance;
        this.contract = new web3Instance.eth.Contract(contractABI, contractAddress);
    }

    /**
     * Send PYRA credit value to smart contract
     * @param {string} methodName - Contract method name
     * @param {Array} params - Method parameters (credit will be added)
     * @param {Object} options - Transaction options
     */
    async callWithPyraCredit(methodName, params = [], options = {}) {
        const creditValue = await getPyraCreditValue();
        
        // Convert to Wei if needed (assuming 18 decimals)
        const creditValueWei = this.web3.utils.toWei(creditValue.toString(), 'ether');
        
        return this.contract.methods[methodName](...params, creditValueWei).send(options);
    }

    /**
     * Get PYRA credit as Wei for contract interactions
     */
    async getPyraCreditWei() {
        const creditValue = await getPyraCreditValue();
        return this.web3.utils.toWei(creditValue.toString(), 'ether');
    }
}

/**
 * Integration with popular Web3 libraries
 */

// Ethers.js integration
export function createEthersProvider(pyraCreditContract) {
    return {
        async getPyraCredit() {
            const data = await getPyraBarterCredit();
            return {
                value: data.value,
                timestamp: data.timestamp,
                blockNumber: await pyraCreditContract.provider.getBlockNumber()
            };
        },
        
        async updateContractWithCredit(signer) {
            const creditValue = await getPyraCreditValue();
            const tx = await pyraCreditContract.connect(signer).updatePyraCredit(
                ethers.utils.parseEther(creditValue.toString())
            );
            return tx.wait();
        }
    };
}

// Event emitter for credit updates
class PyraEventEmitter {
    constructor() {
        this.listeners = {};
    }

    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }

    off(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
    }
}

// Global event emitter instance
export const pyraEvents = new PyraEventEmitter();

// Auto-update with events
let autoUpdateInterval = null;

export function startAutoUpdate(interval = 5 * 60 * 1000) {
    if (autoUpdateInterval) {
        stopAutoUpdate();
    }

    const updateAndEmit = async () => {
        try {
            const credit = await getPyraBarterCredit();
            pyraEvents.emit('creditUpdate', credit);
            pyraEvents.emit('creditValue', credit.value);
        } catch (error) {
            pyraEvents.emit('error', error);
        }
    };

    updateAndEmit(); // Initial update
    autoUpdateInterval = setInterval(updateAndEmit, interval);
}

export function stopAutoUpdate() {
    if (autoUpdateInterval) {
        clearInterval(autoUpdateInterval);
        autoUpdateInterval = null;
    }
}

// Utility functions
export const utils = {
    /**
     * Format credit value for display
     */
    formatCredit(value, decimals = 6) {
        return `${Number(value).toFixed(decimals)}`;
    },

    /**
     * Calculate percentage change
     */
    calculateChange(oldValue, newValue) {
        if (oldValue === 0) return 0;
        return ((newValue - oldValue) / oldValue) * 100;
    },

    /**
     * Check if credit data is stale
     */
    isStale(timestamp, maxAge = 5 * 60 * 1000) {
        return Date.now() - new Date(timestamp).getTime() > maxAge;
    }
};

// Default export with most commonly used functions
export default {
    getPyraBarterCredit,
    getPyraCreditValue,
    convertWithPyraCredit,
    usePyraBarterCredit,
    PyraWeb3Helper,
    pyraEvents,
    startAutoUpdate,
    stopAutoUpdate,
    utils
};
