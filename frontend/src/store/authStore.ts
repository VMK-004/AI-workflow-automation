import { create } from 'zustand';
import { authApi } from '../api/auth';
import type { User } from '../api/auth';
import { setToken, removeToken, getToken } from '../utils/token';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
  checkAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: false,
  isAuthenticated: !!getToken(),

  login: async (username: string, password: string) => {
    set({ isLoading: true });
    try {
      const response = await authApi.login({ username, password });
      setToken(response.access_token);
      
      // Fetch user data
      const user = await authApi.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  register: async (username: string, email: string, password: string) => {
    set({ isLoading: true });
    try {
      await authApi.register({ username, email, password });
      set({ isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    removeToken();
    set({ user: null, isAuthenticated: false });
  },

  fetchUser: async () => {
    if (!getToken()) {
      set({ isAuthenticated: false });
      return;
    }

    set({ isLoading: true });
    try {
      const user = await authApi.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ user: null, isAuthenticated: false, isLoading: false });
      removeToken();
    }
  },

  checkAuth: () => {
    const token = getToken();
    set({ isAuthenticated: !!token });
  },
}));

