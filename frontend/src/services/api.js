// API configuration and base client setup
import axios from 'axios';

// API base configuration
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';
const ML_BASE_URL = import.meta.env.VITE_ML_SERVICE_URL || 'http://localhost:5001';

// Create axios instances
export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const mlClient = axios.create({
  baseURL: ML_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptors
apiClient.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle common error cases
    if (error.response?.status === 404) {
      throw new Error('Resource not found');
    }
    if (error.response?.status >= 500) {
      throw new Error('Server error. Please try again later.');
    }
    throw error;
  }
);

mlClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. Please try again.');
    }
    throw error;
  }
);