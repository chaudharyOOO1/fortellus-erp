import { useState, useEffect } from 'react';
import axios from 'axios';
import { AuthContext } from './auth-context-base';
import api from '../api/axios';
import { INITIAL_USERS } from '../api/mockData';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('user');
      if (!stored || stored === 'undefined' || stored === 'null') return null;
      return JSON.parse(stored);
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState(() => {
    const storedToken = localStorage.getItem('access_token');
    if (!storedToken || storedToken === 'undefined' || storedToken === 'null') return null;
    return storedToken;
  });
  const [loading, setLoading] = useState(false);
  const [apiConnected, setApiConnected] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const base = api.defaults.baseURL || '';
    const healthUrl = base.includes('/api/v1')
      ? base.replace(/\/api\/v1\/?$/, '/health')
      : (base ? `${base}/health` : '/health');

    axios.get(healthUrl, { timeout: 3000 })
      .then((res) => {
        // Only mark connected if response is JSON with healthy status
        if (isMounted && res.data && typeof res.data === 'object' && res.data.status === 'healthy') {
          setApiConnected(true);
        } else if (isMounted) {
          setApiConnected(false);
        }
      })
      .catch(() => {
        if (isMounted) setApiConnected(false);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const isAuthenticated = !!user;

  async function login(email, password) {
    setLoading(true);
    try {
      const response = await api.post('/auth/login', { email, password });
      if (!response.data || typeof response.data !== 'object' || !response.data.access_token) {
        throw new Error('Invalid authentication response from server');
      }
      const { access_token, user: userData } = response.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      setToken(access_token);
      setUser(userData);
      setApiConnected(true);
      return { success: true };
    } catch (error) {
      // Production mode: never create a client-only token when the API rejects login.
      // This keeps all protected ERP screens backed by real JWT authentication.


      const message = error.response?.data?.detail || 'Invalid email or password.';
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  }

  async function switchPersona(role) {
    const matched = INITIAL_USERS.find(u => u.role === role);
    if (!matched?.email || !matched?.personaPassword) {
      return { success: false, error: 'Persona credentials are not configured.' };
    }
    return login(matched.email, matched.personaPassword);
  }

  function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  }

  const value = {
    user,
    token,
    isAuthenticated,
    loading,
    apiConnected,
    login,
    logout,
    switchPersona,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export { useAuth } from './useAuth';
export default AuthProvider;

