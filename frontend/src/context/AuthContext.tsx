import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import { useNavigate } from 'react-router-dom';

interface AuthState {
  token: string | null;
  role: 'patient' | 'clinician' | null;
  patientId: string | null;
  user: any;
  loading: boolean;
}

interface AuthContextType extends AuthState {
  login: (token: string, role: 'patient' | 'clinician', patientId?: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    token: localStorage.getItem('nura_token'),
    role: localStorage.getItem('nura_role') as any,
    patientId: localStorage.getItem('nura_patient_id'),
    user: null,
    loading: true,
  });

  const logout = useCallback(() => {
    localStorage.removeItem('nura_token');
    localStorage.removeItem('nura_role');
    localStorage.removeItem('nura_patient_id');
    setState({ token: null, role: null, patientId: null, user: null, loading: false });
  }, []);

  const login = useCallback((token: string, role: 'patient' | 'clinician', patientId?: string) => {
    localStorage.setItem('nura_token', token);
    localStorage.setItem('nura_role', role);
    if (patientId) localStorage.setItem('nura_patient_id', patientId);
    setState(prev => ({ ...prev, token, role, patientId: patientId || null, loading: false }));
  }, []);

  useEffect(() => {
    if (!state.token) {
      setState(prev => ({ ...prev, loading: false }));
      return;
    }
    api.get('/v1/me')
      .then(res => {
        const { role, patient_id } = res.data;
        localStorage.setItem('nura_role', role);
        if (patient_id) localStorage.setItem('nura_patient_id', patient_id);
        setState(prev => ({ ...prev, role, patientId: patient_id || null, user: res.data, loading: false }));
      })
      .catch(() => {
        logout();
      });
  }, [state.token, logout]);

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
}
