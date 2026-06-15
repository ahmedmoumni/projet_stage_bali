import axios from 'axios';
import type { AxiosInstance } from 'axios';
import type { AuthResponse, LoginRequest, RegisterRequest, UploadResponse, DocumentListResponse, DocumentDetailResponse } from '../types/index';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Add token to requests if it exists
api.interceptors.request.use((config) => {
  // Check both 'token' and 'auth_token' keys for compatibility
  const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
  console.log('Request interceptor - Token check:', {
    url: config.url,
    token: token ? `${token.substring(0, 20)}...` : 'NO TOKEN',
    hasAuth: !!token
  });
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    console.log('Token added to request:', {
      url: config.url,
      authHeader: config.headers.Authorization?.substring(0, 30) + '...'
    });
  } else {
    console.warn('NO TOKEN FOUND - Request will likely fail with 401');
  }
  return config;
});

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', {
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url,
      headers: error.config?.headers
    });
    
    if (error.response?.status === 401) {
      console.warn('Unauthorized (401) - Redirecting to login');
      localStorage.removeItem('auth_token');
      localStorage.removeItem('token');
      localStorage.removeItem('auth_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  login: (data: LoginRequest) =>
    api.post<AuthResponse>('/login', data),

  register: (data: RegisterRequest) =>
    api.post<AuthResponse>('/register', data),

  me: () =>
    api.get<{ user: any }>('/me'),

  logout: () =>
    api.post('/logout'),
};

// Document endpoints
export const documentAPI = {
  upload: (file: File, visibility: 'public' | 'private' = 'private') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('visibility', visibility);

    return api.post<UploadResponse>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  list: () =>
    api.get<DocumentListResponse>('/documents'),

  get: (id: number) =>
    api.get<DocumentDetailResponse>(`/documents/${id}`),
};

export default api;
