import { createContext, useContext, useMemo, useState } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const TOKEN_KEY = 'aiot_access_token';
const USER_KEY = 'aiot_user';

function storedUser() { try { return JSON.parse(sessionStorage.getItem(USER_KEY) || 'null'); } catch { return null; } }

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => sessionStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState(storedUser);
  const login = async (email, password) => {
    const { data } = await axios.post(`${API_BASE_URL}/api/auth/login`, { email, password });
    sessionStorage.setItem(TOKEN_KEY, data.access_token); sessionStorage.setItem(USER_KEY, JSON.stringify(data.user));
    setToken(data.access_token); setUser(data.user); return data.user;
  };
  const logout = () => { sessionStorage.removeItem(TOKEN_KEY); sessionStorage.removeItem(USER_KEY); setToken(null); setUser(null); };
  const value = useMemo(() => ({ token, user, login, logout, isAuthenticated: Boolean(token && user) }), [token, user]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() { const context = useContext(AuthContext); if (!context) throw new Error('useAuth must be used inside AuthProvider'); return context; }
