import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const patientApi = axios.create({
  baseURL: API_BASE_URL,
});

patientApi.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('aiot_access_token');
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getPatients = (params = {}) => patientApi.get('/api/patients', { params });
export const getPatient = (id) => patientApi.get(`/api/patients/${id}`);
export const createPatient = (payload) => patientApi.post('/api/patients', payload);
export const updatePatient = (id, payload) => patientApi.put(`/api/patients/${id}`, payload);
export const archivePatient = (id) => patientApi.delete(`/api/patients/${id}`);
