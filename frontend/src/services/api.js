import API_CONFIG from '../config/api';

class ApiService {
  constructor() {
    this.baseURL = API_CONFIG.BASE_URL;
    this.timeout = API_CONFIG.TIMEOUT;
  }

  getFullUrl(endpoint) {
    return `${this.baseURL}${endpoint}`;
  }

  async handleResponse(response) {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: `HTTP ${response.status}: ${response.statusText}`
      }));
      throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    if (data.success === false) {
      throw new Error(data.error || 'Có lỗi xảy ra');
    }

    return data;
  }

  async findRoute(start, end) {
    const url = this.getFullUrl(API_CONFIG.ENDPOINTS.ROUTE);
    const params = new URLSearchParams({ start, end });

    const response = await fetch(`${url}?${params}`, {
      ...API_CONFIG.DEFAULT_OPTIONS,
      method: 'GET',
    });

    return this.handleResponse(response);
  }

  async findMultiRoute(points, options = {}) {
    const url = this.getFullUrl(API_CONFIG.ENDPOINTS.MULTI_ROUTE);

    const requestBody = {
      points: points.map(point => ({
        lat: point.lat,
        lng: point.lng
      })),
      consider_traffic: options.consider_traffic !== false,
      ga_population_size: options.ga_population_size || 100,
      ga_generations: options.ga_generations || 500
    };

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...API_CONFIG.DEFAULT_OPTIONS,
        method: 'POST',
        body: JSON.stringify(requestBody),
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      return this.handleResponse(response);
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new Error('Request timeout. Vui lòng thử lại.');
      }
      throw error;
    }
  }

  async checkHealth() {
    const url = this.getFullUrl(API_CONFIG.ENDPOINTS.HEALTH);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(url, {
        method: 'GET',
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      return false;
    }
  }
}

export default new ApiService();
