import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '@/lib/api';
import { NuraCard } from '@/components/ui/NuraCard';
import { NuraButton } from '@/components/ui/NuraButton';

export default function ConsentPage() {
  const [accepted, setAccepted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleContinue = async () => {
    setLoading(true);
    try {
      await api.post('/v1/patient/consent', { accepted: true, policy_version: '1.0' });
      navigate('/patient/profile-setup');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit consent');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen" style={{ background: 'var(--bg)', padding: 24 }}>
      <NuraCard style={{ maxWidth: 560, width: '100%' }}>
        <h1 style={{ fontStyle: 'italic', color: 'var(--sage)', marginBottom: 16, fontSize: '1.6rem' }}>A promise before we begin</h1>
        <div style={{ color: 'var(--text-muted)', lineHeight: 1.7, marginBottom: 24, fontSize: '0.95rem' }}>
          <p>Your mental health data is deeply personal. We want you to know how it will be used.</p>
          <p style={{ marginTop: 12 }}>Our AI agents analyze your journal entries, questionnaire responses, and — if connected — wearable data to surface patterns and insights. These insights are shared with your assigned clinician to support your care.</p>
          <p style={{ marginTop: 12 }}>Your data is encrypted, never sold, and you can request deletion at any time. We are committed to treating your information with the same care we'd want for our own.</p>
        </div>
        <label style={{ display: 'flex', gap: 10, alignItems: 'center', cursor: 'pointer', marginBottom: 20 }}>
          <input type="checkbox" checked={accepted} onChange={e => setAccepted(e.target.checked)} style={{ accentColor: 'var(--sage)', width: 18, height: 18 }} />
          <span style={{ fontSize: '0.9rem', fontWeight: 400 }}>I understand and accept</span>
        </label>
        {error && <p style={{ color: 'var(--terracotta)', fontSize: '0.85rem', marginBottom: 12 }}>{error}</p>}
        <NuraButton onClick={handleContinue} disabled={!accepted || loading}>
          {loading ? 'Submitting…' : 'Continue →'}
        </NuraButton>
      </NuraCard>
    </div>
  );
}
