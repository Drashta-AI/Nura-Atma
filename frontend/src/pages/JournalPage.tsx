import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { PatientNav } from '@/components/layout/PatientNav';
import { NuraCard } from '@/components/ui/NuraCard';
import { NuraButton } from '@/components/ui/NuraButton';
import { NuraTextarea } from '@/components/ui/NuraInput';

const moods = ['😊', '😐', '😔', '😰', '😡', '😴'];

const getJournalEntryKey = (entry: any, index: number) => {
  if (entry?.journal_id !== undefined && entry?.journal_id !== null && entry?.journal_id !== '') {
    return `journal-${entry.journal_id}`;
  }
  const created = entry?.created_at ? String(entry.created_at) : 'unknown-date';
  const mood = entry?.mood ? String(entry.mood) : 'no-mood';
  return `journal-fallback-${created}-${mood}-${index}`;
};

export default function JournalPage() {
  const queryClient = useQueryClient();
  const [content, setContent] = useState('');
  const [mood, setMood] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['journal'],
    queryFn: () => api.get('/v1/patient/journal').then(r => r.data),
  });

  const mutation = useMutation({
    mutationFn: () => api.post('/v1/patient/journal', { content, mood }),
    onSuccess: (res) => {
      const newEntry = { journal_id: res.data.journal_id, created_at: res.data.created_at || new Date().toISOString(), content, mood };
      queryClient.setQueryData(['journal'], (old: any) => ({
        ...old,
        entries: [newEntry, ...(old?.entries || [])],
      }));
      setContent('');
      setMood('');
    },
  });

  return (
    <>
      <PatientNav />
      <div style={{ padding: 24, maxWidth: 640, margin: '0 auto' }}>
        <h1 style={{ fontStyle: 'italic', color: 'var(--sage)', marginBottom: 20, fontSize: '1.5rem' }}>Journal</h1>

        <NuraCard style={{ marginBottom: 24 }}>
          <NuraTextarea placeholder="What's on your mind today?" value={content} onChange={e => setContent(e.target.value)} />
          <div style={{ display: 'flex', gap: 8, marginTop: 12, flexWrap: 'wrap', alignItems: 'center' }}>
            {moods.map(m => (
              <button
                key={m}
                onClick={() => setMood(m)}
                style={{
                  fontSize: '1.4rem',
                  background: mood === m ? 'var(--sage-light)' : 'transparent',
                  border: mood === m ? '2px solid var(--sage)' : '2px solid transparent',
                  borderRadius: '50%',
                  width: 40, height: 40,
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
              >{m}</button>
            ))}
            <div style={{ flex: 1 }} />
            <NuraButton onClick={() => mutation.mutate()} disabled={!content || mutation.isPending}>
              {mutation.isPending ? 'Saving…' : 'Save entry'}
            </NuraButton>
          </div>
          {mutation.isError && <p style={{ color: 'var(--terracotta)', fontSize: '0.85rem', marginTop: 8 }}>Failed to save entry</p>}
        </NuraCard>

        {isLoading ? (
          [1,2,3].map(i => <div key={i} className="animate-pulse" style={{ height: 80, borderRadius: 'var(--radius-card)', background: 'var(--border-custom)', marginBottom: 12 }} />)
        ) : (
          data?.entries?.map((entry: any, index: number) => (
            <NuraCard key={getJournalEntryKey(entry, index)} style={{ marginBottom: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{new Date(entry.created_at).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}</span>
                {entry.mood && <span style={{ fontSize: '1.2rem' }}>{entry.mood}</span>}
              </div>
              <p style={{ margin: 0, fontSize: '0.9rem', lineHeight: 1.6, color: 'var(--text-primary)' }}>{entry.content}</p>
            </NuraCard>
          ))
        )}
      </div>
    </>
  );
}
