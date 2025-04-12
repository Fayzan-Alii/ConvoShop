import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { userAPI } from './api';

interface User {
  email: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true); // Added loading state for better UX

  const login = async (email: string, password: string) => {
    try {
      const { token } = await userAPI.login(email, password);
      localStorage.setItem('token', token);
      const userData = await userAPI.getProfile(token);
      setUser(userData);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const register = async (email: string, password: string) => {
    try {
      await userAPI.register(email, password);
    } catch (error: any) {
      console.error('Registration failed:', error);
      if (error.response && error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail); // Use the backend error message
      }
      throw new Error('Registration failed'); // Fallback error message
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      userAPI
        .getProfile(token)
        .then(setUser)
        .catch(() => setUser(null))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  if (loading) {
    return <div>Loading...</div>; // Show a loading indicator while checking authentication
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
}