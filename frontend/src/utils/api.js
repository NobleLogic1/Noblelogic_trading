// API configuration and utilities
const API_CONFIG = {
    BASE_URL: 'http://localhost:5000/api',
    ENDPOINTS: {
        NEWS: '/news',
        MARKET_SENTIMENT: '/market-sentiment',
        HEALTH: '/health',
        ACTIVE_TRADES: '/trades/active',
        STRATEGY_PERFORMANCE: '/strategy/performance'
    }
};

// Helper function to construct full API URLs
export const getApiUrl = (endpoint) => `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS[endpoint]}`;

// Common fetch wrapper with error handling
export async function fetchApi(endpoint, options = {}) {
    try {
        const response = await fetch(getApiUrl(endpoint), {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`API call failed: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error);
        throw error;
    }
}

export const API_ENDPOINTS = {
    NEWS: getApiUrl('NEWS'),
    MARKET_SENTIMENT: getApiUrl('MARKET_SENTIMENT'),
    HEALTH: getApiUrl('HEALTH'),
    ACTIVE_TRADES: getApiUrl('ACTIVE_TRADES'),
    STRATEGY_PERFORMANCE: getApiUrl('STRATEGY_PERFORMANCE')
};