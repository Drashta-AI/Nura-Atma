import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { PatientNav } from '@/components/layout/PatientNav';
import { NuraButton } from '@/components/ui/NuraButton';
import { IndicationBadge } from '@/components/ui/IndicationBadge';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  state?: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const mutation = useMutation({
    mutationFn: (message: string) => api.post('/v1/patient/chat', { message }),
    onSuccess: (res) => {
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.reply, state: res.data.latest_state }]);
    },
  });

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    mutation.mutate(input);
    setInput('');
  };

  return (
    <>
      <PatientNav />
      <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 53px)' }}>
        <div style={{ flex: 1, overflow: 'auto', padding: 24, maxWidth: 700, margin: '0 auto', width: '100%' }}>
          {messages.length === 0 && (
            <div className="text-center animate-fade-in" style={{ marginTop: 80, color: 'var(--text-muted)' }}>
              <p style={{ fontSize: '1.1rem' }}>How are you feeling today?</p>
              <p style={{ fontSize: '0.85rem' }}>Start a conversation with your wellness companion.</p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start', marginBottom: 12 }}>
              <div style={{
                maxWidth: '75%',
                background: msg.role === 'user' ? 'var(--sage)' : 'var(--card-bg)',
                color: msg.role === 'user' ? '#fff' : 'var(--text-primary)',
                border: msg.role === 'assistant' ? '1px solid var(--border-custom)' : 'none',
                borderRadius: 16,
                padding: '12px 16px',
                fontSize: '0.9rem',
                lineHeight: 1.6,
              }}>
                {msg.content}
                {msg.state && (
                  <div style={{ marginTop: 8 }}><IndicationBadge level={msg.state as any} /></div>
                )}
              </div>
            </div>
          ))}
          {mutation.isPending && (
            <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: 12 }}>
              <div style={{ background: 'var(--card-bg)', border: '1px solid var(--border-custom)', borderRadius: 16, padding: '12px 16px' }}>
                <span className="animate-pulse" style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Thinking…</span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
        <div style={{ borderTop: '1px solid var(--border-custom)', padding: 16, background: 'var(--card-bg)' }}>
          <div style={{ display: 'flex', gap: 12, maxWidth: 700, margin: '0 auto' }}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
              placeholder="Type a message…"
              style={{
                flex: 1,
                background: 'var(--bg)',
                border: '1px solid var(--border-custom)',
                borderRadius: 'var(--radius-pill)',
                padding: '10px 20px',
                fontFamily: "'DM Sans', sans-serif",
                fontSize: '0.9rem',
                outline: 'none',
                color: 'var(--text-primary)',
              }}
            />
            <NuraButton onClick={handleSend} disabled={!input.trim() || mutation.isPending}>Send</NuraButton>
          </div>
        </div>
      </div>
    </>
  );
}
