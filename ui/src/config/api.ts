/**
 * API Configuration
 * 
 * In development: Uses relative paths which Vite proxies to localhost:8000
 * In production/Docker: Uses internal service name (backend) or environment variable
 */

// Determine the API base URL based on environment
const getApiBaseUrl = (): string => {
  // In development, use relative path (Vite will proxy to backend)
  if (import.meta.env.DEV) {
    return '/api/v1';
  }

  // In production, use environment variable or fallback to /api/v1
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl) {
    return envUrl;
  }

  // Default to relative path for production
  return '/api/v1';
};

export const API_BASE_URL = getApiBaseUrl();

/**
 * Construct a full API URL
 * Usage: getApiUrl('/users/login') -> '/api/v1/users/login' (dev) or 'http://backend:8000/api/v1/users/login' (prod)
 */
export const getApiUrl = (endpoint: string): string => {
  const baseUrl = API_BASE_URL;
  const url = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return baseUrl + url;
};
