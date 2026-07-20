import React, { createContext, useContext, useState, useEffect } from 'react';
import * as api from '../services/api';

const AuthContext = createContext();

const clearStoredSession = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('refresh_token');
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        const profile = await api.getProfile();
        setUser(profile);
      } else {
        setUser(null);
      }
    } catch (err) {
      console.error('Failed to load user session profile:', err);
      clearStoredSession();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Let the axios response interceptor drop React state when a refresh fails.
    api.setSessionExpiredHandler(() => setUser(null));
    fetchProfile();
    return () => api.setSessionExpiredHandler(null);
  }, []);

  const storeSession = (data) => {
    localStorage.setItem('token', data.access_token);
    if (data.refresh_token) {
      localStorage.setItem('refresh_token', data.refresh_token);
    }
  };

  const loginUser = async (credentials) => {
    const data = await api.login(credentials);
    storeSession(data);
    await fetchProfile();
    return data;
  };

  const registerUser = async (userData) => {
    const data = await api.register(userData);
    storeSession(data);
    await fetchProfile();
    return data;
  };

  const logoutUser = async () => {
    try {
      await api.logout();
    } catch (err) {
      console.error('Failed to log out session on server:', err);
    } finally {
      clearStoredSession();
      setUser(null);
    }
  };

  const updateProfile = async (profileData) => {
    const updated = await api.updateProfile(profileData);
    setUser(updated);
    return updated;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login: loginUser,
        register: registerUser,
        logout: logoutUser,
        updateProfile,
        refreshUser: fetchProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
