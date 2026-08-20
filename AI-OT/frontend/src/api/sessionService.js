import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const sessionApi = axios.create({
  baseURL: API_BASE_URL,
});

sessionApi.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('aiot_access_token');
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getSessions = () => sessionApi.get('/api/sessions');
export const createSession = (payload) => sessionApi.post('/api/sessions', payload);
export const getSession = (id) => sessionApi.get(`/api/sessions/${id}`);
export const pauseSession = (id) => sessionApi.post(`/api/sessions/${id}/pause`);
export const resumeSession = (id) => sessionApi.post(`/api/sessions/${id}/resume`);
export const endSession = (id) => sessionApi.post(`/api/sessions/${id}/end`);
export const recordSessionEvent = (id, event, details = {}) => sessionApi.post(`/api/sessions/${id}/events`, { event, details });
