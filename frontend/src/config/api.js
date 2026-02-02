const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:5000',

  ENDPOINTS: {
    ROUTE: '/api/route',
    MULTI_ROUTE: '/api/multi-route',
    HEALTH: '/health'
  },

  TIMEOUT: 60000,

  DEFAULT_OPTIONS: {
    headers: {
      'Content-Type': 'application/json',
    },
  }
};

export default API_CONFIG;
