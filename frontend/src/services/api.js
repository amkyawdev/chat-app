// API Service - Axios configuration for backend communication
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
  getMe: () => api.get('/auth/me'),
  refreshToken: () => api.post('/auth/refresh'),
};

// User API
export const userAPI = {
  getProfile: (userId) => api.get(`/users/${userId}`),
  updateProfile: (data) => api.put('/users/profile', data),
  updateAvatar: () => api.put('/users/avatar'),
  blockUser: (userId) => api.post('/users/block', { user_id: userId }),
  unblockUser: (userId) => api.post('/users/unblock', { user_id: userId }),
  searchUsers: (query) => api.get(`/users/search/${query}`),
};

// Chat API
export const chatAPI = {
  sendMessage: (data) => api.post('/chat/send', data),
  getMessages: (userId, params) => api.get(`/chat/messages/${userId}`, { params }),
  deleteMessage: (messageId) => api.delete(`/chat/messages/${messageId}`),
  addReaction: (data) => api.post('/chat/reactions', data),
  removeReaction: (reactionId) => api.delete(`/chat/reactions/${reactionId}`),
  getReactions: (messageId) => api.get(`/chat/messages/${messageId}/reactions`),
};

// Group API
export const groupAPI = {
  create: (data) => api.post('/groups', data),
  get: (groupId) => api.get(`/groups/${groupId}`),
  update: (groupId, data) => api.put(`/groups/${groupId}`, data),
  delete: (groupId) => api.delete(`/groups/${groupId}`),
  getMembers: (groupId) => api.get(`/groups/${groupId}/members`),
  addMember: (groupId, data) => api.post(`/groups/${groupId}/members`, data),
  removeMember: (groupId, userId) => api.delete(`/groups/${groupId}/members/${userId}`),
  updateMember: (groupId, userId, data) => api.put(`/groups/${groupId}/members/${userId}`, data),
  getMessages: (groupId, params) => api.get(`/groups/${groupId}/messages`, { params }),
};

// System API
export const systemAPI = {
  health: () => api.get('/system/health'),
  getBatchStatus: () => api.get('/system/batch/status'),
  triggerBatch: (data) => api.post('/system/batch/trigger', data),
  getQueueStats: () => api.get('/system/queue/stats'),
  getStorageStats: () => api.get('/system/storage/stats'),
};

export default api;