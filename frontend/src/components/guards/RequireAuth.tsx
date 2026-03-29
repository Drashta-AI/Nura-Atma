import { Navigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const { token, loading } = useAuth();
  if (loading) return <div className="flex items-center justify-center min-h-screen" style={{ background: 'var(--bg)' }}><div className="h-8 w-8 rounded-full animate-pulse" style={{ background: 'var(--sage-light)' }} /></div>;
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export function RequireRole({ role, children }: { role: 'patient' | 'clinician'; children: React.ReactNode }) {
  const { role: userRole, loading } = useAuth();
  if (loading) return null;
  if (userRole !== role) {
    return (
      <div className="flex items-center justify-center min-h-screen" style={{ background: 'var(--bg)' }}>
        <div className="text-center animate-fade-in" style={{ background: 'var(--card-bg)', borderRadius: 'var(--radius-card)', boxShadow: 'var(--shadow-card)', padding: '48px' }}>
          <h2 style={{ color: 'var(--terracotta)' }}>Role Mismatch</h2>
          <p style={{ color: 'var(--text-muted)', marginTop: 8 }}>You don't have access to this section.</p>
        </div>
      </div>
    );
  }
  return <>{children}</>;
}
