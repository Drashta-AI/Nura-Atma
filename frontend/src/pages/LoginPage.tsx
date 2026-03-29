import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { NuraCard } from '@/components/ui/NuraCard';
import { NuraButton } from '@/components/ui/NuraButton';
import { NuraInput } from '@/components/ui/NuraInput';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<'patient' | 'clinician'>('patient');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const getPatientNextRoute = async () => {
    try {
      const status = (await api.get('/v1/patient/onboarding-status')).data || {};

      // Hard-coded onboarding flow entry: privacy promise always first unless onboarding is complete.
      if (status.onboarding_completed === true) return '/patient/home';
      return '/patient/consent';
    } catch {
      return '/patient/consent';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await api.post('/v1/auth/login', { email, password, role });
      const { access_token, patient_id } = res.data;
      login(access_token, role, patient_id);

      if (role === 'patient') {
        const nextRoute = await getPatientNextRoute();
        navigate(nextRoute);
      } else {
        navigate('/clinician/patients');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const pillStyle = (selected: boolean): React.CSSProperties => ({
    background: selected ? 'var(--sage)' : 'transparent',
    color: selected ? '#fff' : 'var(--sage)',
    border: `1.5px solid var(--sage)`,
    borderRadius: 'var(--radius-pill)',
    padding: '8px 22px',
    fontWeight: 500,
    fontSize: '0.85rem',
    cursor: 'pointer',
    transition: 'all 0.2s',
  });

  return (
    <div className="flex items-center justify-center min-h-screen" style={{ background: 'var(--bg)', padding: 24 }}>
      <NuraCard style={{ maxWidth: 420, width: '100%' }}>
        <div className="text-center" style={{ marginBottom: 32 }}>
          <h1 style={{ fontStyle: 'italic', color: 'var(--sage)', fontSize: '2rem', marginBottom: 4 }}>Nura-Atma</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>Mental wellness, clearly seen.</p>
        </div>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <NuraInput label="Email" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          <NuraInput label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          <div style={{ display: 'flex', gap: 8, justifyContent: 'center' }}>
            <button type="button" onClick={() => setRole('patient')} style={pillStyle(role === 'patient')}>I'm a Patient</button>
            <button type="button" onClick={() => setRole('clinician')} style={pillStyle(role === 'clinician')}>I'm a Clinician</button>
          </div>
          {error && <p style={{ color: 'var(--terracotta)', fontSize: '0.85rem', textAlign: 'center' }}>{error}</p>}
          <NuraButton type="submit" disabled={loading} style={{ width: '100%' }}>
            {loading ? 'Signing in…' : 'Sign in'}
          </NuraButton>
        </form>
      </NuraCard>
    </div>
  );
}
