import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const otControlApi = axios.create({
  baseURL: API_BASE_URL,
});

otControlApi.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('aiot_access_token');
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getOtDevices = () => otControlApi.get('/api/ot/devices');
export const sendOtDeviceCommand = (deviceId, command, payload = {}) => otControlApi.post(`/api/ot/devices/${deviceId}/command`, {
  command,
  payload,
});
