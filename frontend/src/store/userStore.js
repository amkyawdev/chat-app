// User store - authentication and user state
import { create } from 'zustand';
import { authAPI, userAPI } from '../services/api';
import { socketService } from '../services/socket';

export const useUserStore = create((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  // Login
  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authAPI.login({ email, password });
      const { access_token, user } = response.data;
      localStorage.setItem('access_token', access_token);
      set({ user, isAuthenticated: true, isLoading: false });
      // Connect WebSocket
      socketService.connect(user.id);
      return true;
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Login failed', isLoading: false });
      return false;
    }
  },

  // Register
  register: async (username, email, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authAPI.register({ username, email, password });
      const { access_token, user } = response.data;
      localStorage.setItem('access_token', access_token);
      set({ user, isAuthenticated: true, isLoading: false });
      socketService.connect(user.id);
      return true;
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Registration failed', isLoading: false });
      return false;
    }
  },

  // Logout
  logout: async () => {
    try {
      await authAPI.logout();
    } catch (e) {
      // Ignore logout errors
    }
    localStorage.removeItem('access_token');
    socketService.disconnect();
    set({ user: null, isAuthenticated: false });
  },

  // Fetch current user
  fetchCurrentUser: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return false;
    
    set({ isLoading: true });
    try {
      const response = await authAPI.getMe();
      set({ user: response.data, isAuthenticated: true, isLoading: false });
      socketService.connect(response.data.id);
      return true;
    } catch (error) {
      localStorage.removeItem('access_token');
      set({ user: null, isAuthenticated: false, isLoading: false });
      return false;
    }
  },

  // Update profile
  updateProfile: async (data) => {
    try {
      const response = await userAPI.updateProfile(data);
      set({ user: response.data });
      return true;
    } catch (error) {
      return false;
    }
  },

  // Refresh avatar
  refreshAvatar: async () => {
    try {
      const response = await userAPI.updateAvatar();
      set((state) => ({ user: { ...state.user, avatar: response.data.avatar } }));
      return true;
    } catch (error) {
      return false;
    }
  },
}));

export default useUserStore;