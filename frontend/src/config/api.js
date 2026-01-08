/**
 * API Configuration
 */
const API_CONFIG = {
  // Backend API base URL
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  
  // API endpoints
  ENDPOINTS: {
    ROUTE: '/api/route',
    MULTI_ROUTE: '/api/multi-route',
    HEALTH: '/health'
  },
  
  // Request timeout (ms)
  TIMEOUT: 30000,
  
  // Default request options
  DEFAULT_OPTIONS: {
    headers: {
      'Content-Type': 'application/json',
    },
  }
};

export default API_CONFIG;

