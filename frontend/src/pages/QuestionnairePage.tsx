import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { NuraCard } from '@/components/ui/NuraCard';
import { NuraButton } from '@/components/ui/NuraButton';
import { NuraTextarea } from '@/components/ui/NuraInput';

export default function QuestionnairePage() {
  const navigate = useNavigate();
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const { data: statusData } = useQuery({
    queryKey: ['onboarding-status'],
    queryFn: () => api.get('/v1/patient/onboarding-status').then(r => r.data),
  });

  useEffect(() => {
    if (statusData?.questionnaire_submitted && statusData?.onboarding_completed) {
      navigate('/patient/home', { replace: true });
    }
  }, [statusData, navigate]);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['questionnaire'],
    queryFn: () => api.get('/v1/patient/questionnaire').then(r => r.data),
  });

  const questions = Array.isArray(data?.questions)
    ? data.questions
    : Array.isArray(data?.items)
      ? data.items
      : Array.isArray(data)
        ? data
        : [];

  useEffect(() => {
    if (questions.length > 0) {
      const initial: Record<string, string> = {};
      questions.forEach((q: any) => {
        initial[q.question] = data.latest_responses?.[q.question] || q.suggested_answer || '';
      });
      setAnswers(initial);
    }
  }, [data, questions]);

  const mutation = useMutation({
    mutationFn: () => api.post('/v1/patient/questionnaire', { responses: answers }),
    onSuccess: (res) => {
      if (res.data?.onboarding_completed) navigate('/patient/home');
    },
  });

  if (isLoading) return (
    <div className="flex items-center justify-center min-h-screen" style={{ background: 'var(--bg)' }}>
      <div className="animate-pulse" style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--sage-light)' }} />
    </div>
  );

  return (
    <div className="flex items-center justify-center min-h-screen" style={{ background: 'var(--bg)', padding: 24 }}>
      <NuraCard style={{ maxWidth: 600, width: '100%' }}>
        <h1 style={{ fontStyle: 'italic', color: 'var(--sage)', marginBottom: 24, fontSize: '1.5rem' }}>A few questions</h1>
        {isError && (
          <p style={{ color: 'var(--terracotta)', fontSize: '0.9rem', marginBottom: 14 }}>
            Unable to load questionnaire. {(error as any)?.response?.data?.detail || (error as any)?.message || 'Please try again.'}
          </p>
        )}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {questions.map((q: any, i: number) => (
            <NuraTextarea
              key={i}
              label={q.question}
              value={answers[q.question] || ''}
              onChange={e => setAnswers(prev => ({ ...prev, [q.question]: e.target.value }))}
            />
          ))}
          {!isLoading && !isError && questions.length === 0 && (
            <p style={{ color: 'var(--text-muted)', margin: 0 }}>
              No questionnaire items are available right now.
            </p>
          )}
        </div>
        {mutation.isError && <p style={{ color: 'var(--terracotta)', fontSize: '0.85rem', marginTop: 12 }}>Failed to submit. Please try again.</p>}
        <div style={{ marginTop: 24 }}>
          <NuraButton onClick={() => mutation.mutate()} disabled={mutation.isPending || questions.length === 0}>
            {mutation.isPending ? 'Submitting…' : 'Submit'}
          </NuraButton>
        </div>
      </NuraCard>
    </div>
  );
}
