import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const imagingApi = axios.create({
  baseURL: API_BASE_URL,
});

imagingApi.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('aiot_access_token');
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getPatientImages = (patientId) => imagingApi.get(`/api/patients/${patientId}/images`);
export const uploadPatientImage = (patientId, formData) => imagingApi.post(`/api/patients/${patientId}/images`, formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
});
