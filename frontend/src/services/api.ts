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
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
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
