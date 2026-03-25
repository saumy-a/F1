import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Create axios instance with default config
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add request ID and logging
apiClient.interceptors.request.use(
  (config) => {
    // Generate request ID for tracing
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    config.headers['X-Request-ID'] = requestId
    
    // Log request in development
    if (import.meta.env.DEV) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
        requestId,
        params: config.params,
        data: config.data,
      })
    }
    
    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors and logging
apiClient.interceptors.response.use(
  (response) => {
    // Log response in development
    if (import.meta.env.DEV) {
      console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        requestId: response.headers['x-request-id'],
        data: response.data,
      })
    }
    
    return response
  },
  (error) => {
    // Enhanced error handling
    if (error.response) {
      // Server responded with error status
      console.error('[API Error]', {
        status: error.response.status,
        url: error.config?.url,
        requestId: error.response.headers?.['x-request-id'],
        message: error.response.data?.detail || error.message,
      })
    } else if (error.request) {
      // Request made but no response
      console.error('[API Network Error]', {
        url: error.config?.url,
        message: 'No response received from server',
      })
    } else {
      // Error in request setup
      console.error('[API Setup Error]', error.message)
    }
    
    return Promise.reject(error)
  }
)

export default apiClient
