import axios from 'axios';

// 1. Create the instance
const apiClient = axios.create({
  baseURL: '/api/v1', // Proxy will forward to backend
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds timeout for ERP operations
});

// 2. Request Interceptor (The "Middleware" of the frontend)
apiClient.interceptors.request.use((config) => {
    // A. Inject Auth Token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // B. Inject Localization Context (CRITICAL FOR YOUR ERP)
    const companyId = localStorage.getItem('active_company_id') || '1';
    const countryCode = localStorage.getItem('erp_country_code') || 'SG';
  
    config.headers['X-Company-ID'] = companyId; // For data isolation (Multi-tenant)
    config.headers['X-Country-Code'] = countryCode; // For logic switching (Strategy Pattern)

    return config;
  },
  (error) => Promise.reject(error)
);

// 3. Response Interceptor (Global Error Handling)
apiClient.interceptors.response.use(
  (response) => response, // Return full response, not just data
  (error) => {
    const message = error.response?.data?.detail || error.message;
    
    // Handle 401 (Unauthorized) - Auto logout
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }

    // You can trigger a global toast here if you want
    console.error("API Error:", message);
    return Promise.reject(error);
  }
);

export default apiClient;