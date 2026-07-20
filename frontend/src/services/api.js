import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Request interceptor to attach bearer token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Callback registered by AuthContext so a failed refresh can clear React state
let onSessionExpired = null;
export const setSessionExpiredHandler = (handler) => {
  onSessionExpired = handler;
};

const clearSession = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('refresh_token');
  if (onSessionExpired) onSessionExpired();
};

// A single in-flight refresh shared by every request that 401s at the same time,
// so a burst of parallel calls triggers one refresh instead of N competing ones.
let refreshPromise = null;

const refreshAccessToken = async () => {
  const storedRefresh = localStorage.getItem('refresh_token');
  if (!storedRefresh) throw new Error('No refresh token available');

  // Bare axios, not `api` — this must not run through the response interceptor.
  const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
    refresh_token: storedRefresh,
  });
  localStorage.setItem('token', response.data.access_token);
  localStorage.setItem('refresh_token', response.data.refresh_token);
  return response.data.access_token;
};

// Response interceptor: on 401, refresh once and replay the original request.
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    if (error.response?.status !== 401 || !original || original._retry) {
      return Promise.reject(error);
    }

    // The refresh endpoint itself failing means the session is genuinely dead.
    if (original.url?.includes('/auth/refresh')) {
      clearSession();
      return Promise.reject(error);
    }

    original._retry = true;

    try {
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null;
        });
      }
      const newToken = await refreshPromise;
      original.headers = original.headers || {};
      original.headers.Authorization = `Bearer ${newToken}`;
      return api(original);
    } catch (refreshError) {
      clearSession();
      return Promise.reject(error);
    }
  }
);

// Auth endpoints
export const login = async (credentials) => {
  const response = await api.post('/auth/login', credentials);
  return response.data;
};

export const register = async (userData) => {
  const response = await api.post('/auth/register', userData);
  return response.data;
};

export const getProfile = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

export const updateProfile = async (profileData) => {
  const response = await api.put('/auth/profile', profileData);
  return response.data;
};

export const updateApiSettings = async (apiPreferences) => {
  const response = await api.put('/auth/api-settings', { api_preferences: apiPreferences });
  return response.data;
};

export const logout = async () => {
  const response = await api.post('/auth/logout');
  return response.data;
};

// Recommendation and scan endpoints
export const getRecommendations = async (resumeFile, options = {}) => {
  const formData = new FormData();
  formData.append('resume', resumeFile);
  
  // Append all filter parameters (only non-empty values)
  const fields = [
    'query', 'top_k', 'country', 'state', 'city',
    'experience_level', 'employment_type', 'workplace_type',
    'salary_min', 'company_name', 'skills', 'industry'
  ];
  for (const field of fields) {
    const value = options[field];
    if (value !== undefined && value !== null && value !== '') {
      formData.append(field, value);
    }
  }
  
  const response = await api.post('/recommend', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Career Coach AI operations
// Passing the job makes the ATS/overall scores specific to that posting.
// Called without a job it still returns a general, resume-wide review.
export const getResumeReview = async (job = null) => {
  const response = await api.post('/resume-review', job || null);
  return response.data;
};

export const getJobAnalysis = async (job) => {
  const response = await api.post('/job-analysis', job);
  return response.data;
};

export const getSkillGap = async (job) => {
  const response = await api.post('/skill-gap', job);
  return response.data;
};

export const prepareInterview = async (job) => {
  const response = await api.post('/prepare-interview', job);
  return response.data;
};



export const getCareerCoach = async () => {
  const response = await api.post('/career-coach');
  return response.data;
};

// Saved Job bookmarks
export const saveJob = async (job) => {
  const response = await api.post('/saved-jobs', job);
  return response.data;
};

export const unsaveJob = async (jobId) => {
  const response = await api.delete(`/saved-jobs/${jobId}`);
  return response.data;
};

export const getSavedJobs = async () => {
  const response = await api.get('/saved-jobs');
  return response.data;
};

// History logs
export const getResumeHistory = async () => {
  const response = await api.get('/history/resumes');
  return response.data;
};

export const getRecommendationHistory = async () => {
  const response = await api.get('/history/recommendations');
  return response.data;
};

export const getInterviewHistory = async () => {
  const response = await api.get('/history/interviews');
  return response.data;
};

export const getCareerCoachHistory = async () => {
  const response = await api.get('/history/career-coach');
  return response.data;
};

export const getInterviewHistoryDetails = async (sessionId) => {
  const response = await api.get(`/history/interviews/${sessionId}`);
  return response.data;
};

// Export default object for standard imports e.g., import api from '../services/api'
export default {
  login,
  register,
  getProfile,
  updateProfile,
  updateApiSettings,
  logout,
  setSessionExpiredHandler,
  getRecommendations,
  getResumeReview,
  getJobAnalysis,
  getSkillGap,
  prepareInterview,
  getCareerCoach,
  saveJob,
  unsaveJob,
  getSavedJobs,
  getResumeHistory,
  getRecommendationHistory,
  getInterviewHistory,
  getCareerCoachHistory,
  getInterviewHistoryDetails
};
