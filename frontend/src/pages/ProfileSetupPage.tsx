import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '@/lib/api';
import { NuraCard } from '@/components/ui/NuraCard';
import { NuraButton } from '@/components/ui/NuraButton';
import { NuraInput } from '@/components/ui/NuraInput';

export default function ProfileSetupPage() {
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/v1/patient/profile', { full_name: name, age: Number(age) });
      navigate('/patient/questionnaire');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen" style={{ background: 'var(--bg)', padding: 24 }}>
      <NuraCard style={{ maxWidth: 480, width: '100%' }}>
        <h1 style={{ fontStyle: 'italic', color: 'var(--sage)', marginBottom: 24, fontSize: '1.5rem' }}>Tell us a little about you</h1>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <NuraInput label="Full name" value={name} onChange={e => setName(e.target.value)} required />
          <NuraInput label="Age" type="number" min={1} max={120} value={age} onChange={e => setAge(e.target.value)} required />
          {error && <p style={{ color: 'var(--terracotta)', fontSize: '0.85rem' }}>{error}</p>}
          <NuraButton type="submit" disabled={loading}>{loading ? 'Saving…' : 'Save & continue'}</NuraButton>
        </form>
      </NuraCard>
    </div>
  );
}
