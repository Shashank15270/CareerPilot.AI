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
export const getResumeReview = async () => {
  const response = await api.post('/resume-review');
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
  logout,
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
