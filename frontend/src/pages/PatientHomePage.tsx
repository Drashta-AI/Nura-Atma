import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { HeartHandshake, Sparkles, LineChart } from 'lucide-react';
import { api } from '@/lib/api';
import { PatientNav } from '@/components/layout/PatientNav';
import { NuraCard } from '@/components/ui/NuraCard';
import { NuraButton } from '@/components/ui/NuraButton';
import { IndicationBadge } from '@/components/ui/IndicationBadge';
import { AgentChart } from '@/components/ui/AgentChart';
import { NuraModal } from '@/components/ui/NuraModal';

const agentMap: Record<string, { label: string; icon: string }> = {
  behavioral: { label: 'Mood & Behaviour', icon: '🧠' },
  physiological: { label: 'Body Signals', icon: '💗' },
  context: { label: 'Context & Environment', icon: '🌿' },
  language: { label: 'Language Patterns', icon: '💬' },
};

const insightKeyByAgent: Record<string, string> = {
  behavioral: 'behavioral',
  physiological: 'wearable',
  context: 'contextual',
  language: 'language',
};

type AgentMetric = {
  metric_name?: string;
  value?: number;
  baseline?: number;
  pct_change?: number;
  state?: 'normal' | 'watchful' | 'elevated' | string;
  reasoning?: string;
};

type AgentPayload = {
  metric_states?: Record<string, AgentMetric>;
  reasoning?: Record<string, unknown>;
};

const parseAgentPayload = (payload: unknown): unknown => {
  if (typeof payload !== 'string') return payload;
  try {
    return JSON.parse(payload);
  } catch {
    return payload;
  }
};

const formatMetricName = (name: string) =>
  name
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());

const formatNumber = (value: unknown) => {
  if (typeof value !== 'number' || Number.isNaN(value)) return '—';
  if (Math.abs(value) >= 1000) return value.toLocaleString(undefined, { maximumFractionDigits: 1 });
  return value.toLocaleString(undefined, { maximumFractionDigits: 1 });
};

const formatPercent = (value: unknown) => {
  if (typeof value !== 'number' || Number.isNaN(value)) return '—';
  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}%`;
};

const parseBulletList = (text: string): string[] => {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.startsWith('- '))
    .map((line) => line.replace(/^-\s*/, '').trim())
    .filter(Boolean);
};

const getStructuredPayload = (payload: unknown): AgentPayload | null => {
  const parsed = parseAgentPayload(payload);
  if (!parsed || typeof parsed !== 'object') return null;
  const candidate = parsed as AgentPayload;
  if (!candidate.metric_states && !candidate.reasoning) return null;
  return candidate;
};

const getRecommendations = (value: unknown): string[] => {
  if (Array.isArray(value)) return value.map((item) => toDisplayText(item)).filter(Boolean);
  if (typeof value === 'string') {
    const bullets = parseBulletList(value);
    if (bullets.length > 0) return bullets;
    return value
      .split(/\n+/)
      .map((line) => line.trim())
      .filter(Boolean);
  }
  return [];
};

const toDisplayText = (value: unknown): string => {
  if (value == null) return '—';
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') return String(value);

  if (Array.isArray(value)) {
    return value.map((item) => toDisplayText(item)).filter(Boolean).join(' • ') || '—';
  }

  if (typeof value === 'object') {
    const obj = value as Record<string, unknown>;
    return toDisplayText(
      obj.support_message ?? obj.message ?? obj.summary ?? obj.text ?? obj.state ?? JSON.stringify(obj)
    );
  }

  return '—';
};

const getIndicationLevelFromValue = (value: unknown): 'normal' | 'watchful' | 'elevated' => {
  if (!value) return 'normal';
  if (typeof value === 'string') {
    const normalized = value.toLowerCase();
    if (normalized === 'normal' || normalized === 'watchful' || normalized === 'elevated') return normalized;
    return 'normal';
  }
  if (typeof value === 'object') {
    const obj = value as Record<string, unknown>;
    return getIndicationLevelFromValue(obj.indication_level ?? obj.level ?? obj.state);
  }
  return 'normal';
};

export default function PatientHomePage() {
  const queryClient = useQueryClient();
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [agentLatest, setAgentLatest] = useState<any>(null);
  const [showHistory, setShowHistory] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['patient-home'],
    queryFn: () => api.get('/v1/patient/home').then(r => r.data),
    refetchInterval: 25000,
  });

  const { data: historyData } = useQuery({
    queryKey: ['agent-history', selectedAgent],
    queryFn: () => api.get(`/v1/patient/agents/${selectedAgent}/history`).then(r => r.data),
    enabled: !!selectedAgent && showHistory,
  });

  const toggleTracking = useMutation({
    mutationFn: (status: string) => api.patch('/v1/patient/tracking-status', { status, reason: '' }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['patient-home'] }),
  });

  const openAgentDetail = async (agent: string) => {
    setSelectedAgent(agent);
    setShowHistory(false);
    try {
      const res = await api.get(`/v1/patient/agents/${agent}/latest`);
      setAgentLatest(res.data);
    } catch { setAgentLatest(null); }
  };

  const dotColor = (level: string) => level === 'elevated' ? 'var(--terracotta)' : level === 'watchful' ? 'var(--amber)' : 'var(--sage)';

  if (isLoading) return (
    <>
      <PatientNav />
      <div style={{ padding: 24, maxWidth: 960, margin: '0 auto' }}>
        {[1,2,3].map(i => <div key={i} className="animate-pulse" style={{ height: 120, borderRadius: 'var(--radius-card)', background: 'var(--border-custom)', marginBottom: 16 }} />)}
      </div>
    </>
  );

  const trackingActive = data?.tracking_status === 'active';
  const structuredPayload = getStructuredPayload(agentLatest?.payload);
  const payloadMetrics = structuredPayload?.metric_states ? Object.entries(structuredPayload.metric_states) : [];
  const watchfulCount = payloadMetrics.filter(([, metric]) => metric?.state === 'watchful' || metric?.state === 'elevated').length;

  const calmIntroByAgent: Record<string, string> = {
    behavioral: 'This is a gentle snapshot of recent communication patterns. These signals are helpful hints, not judgments.',
    physiological: 'This is a gentle snapshot of body and energy patterns. These signals support reflection, not self-criticism.',
    context: 'This is a gentle snapshot of environment and routine patterns. It can help you notice what supports your wellbeing.',
    language: 'This is a gentle snapshot of language patterns over time. It is meant to guide awareness with care and compassion.',
  };

  const defaultSuggestionsByAgent: Record<string, string[]> = {
    behavioral: [
      'Try a short check-in with someone you trust this week.',
      'Take one small screen break each day and stretch or step outside.',
      'Notice how your energy feels after social time versus solo time.',
    ],
    physiological: [
      'Keep a steady sleep routine this week, even on busy days.',
      'Add one short movement break each day to support energy.',
      'Use gentle focus blocks and short rests when your energy dips.',
    ],
    context: [
      'Make one small change in your space that helps you feel calmer.',
      'Identify one routine that felt supportive and repeat it tomorrow.',
      'Reduce one source of daily friction where possible.',
    ],
    language: [
      'Pause once a day to name what you are feeling without judgment.',
      'Balance self-criticism with one compassionate reframe.',
      'Write a brief note about one thing that felt manageable today.',
    ],
  };

  const reasoning = structuredPayload?.reasoning || {};
  const recommendationBullets = getRecommendations(reasoning.recommendations);
  const dynamicImplications = toDisplayText(
    reasoning.implications || reasoning.energy_assessment || reasoning.sleep_quality || reasoning.reasoning
  );
  const selectedAgentKey = selectedAgent || 'behavioral';
  const defaultSuggestions = defaultSuggestionsByAgent[selectedAgentKey] || defaultSuggestionsByAgent.behavioral;
  const introText = calmIntroByAgent[selectedAgentKey] || calmIntroByAgent.behavioral;

  return (
    <>
      <PatientNav />
      <div style={{ padding: 24, maxWidth: 960, margin: '0 auto' }}>
        {/* Greeting */}
        <NuraCard style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
            <div>
              <h2 style={{ fontSize: '1.5rem', margin: 0 }}>{data?.greeting || 'Hello'}</h2>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 10 }}>
                <span style={{ width: 14, height: 14, borderRadius: '50%', background: dotColor(data?.indication_level), display: 'inline-block' }} />
                <IndicationBadge level={data?.indication_level || 'normal'} />
                <span style={{
                  background: trackingActive ? 'var(--badge-normal-bg)' : 'var(--badge-watchful-bg)',
                  color: trackingActive ? 'var(--badge-normal-text)' : 'var(--badge-watchful-text)',
                  borderRadius: 'var(--radius-pill)',
                  padding: '3px 12px',
                  fontSize: '0.78rem',
                  fontWeight: 500,
                }}>{trackingActive ? 'Tracking Active' : 'Tracking Paused'}</span>
              </div>
            </div>
            <NuraButton variant="outline" onClick={() => toggleTracking.mutate(trackingActive ? 'paused' : 'active')}>
              {trackingActive ? 'Pause' : 'Resume'}
            </NuraButton>
          </div>
        </NuraCard>

        {/* Weekly Summary */}
        {data?.weekly_summary?.length > 0 && (
          <NuraCard style={{ marginBottom: 16 }}>
            <h3 style={{ marginBottom: 12, fontSize: '1.1rem' }}>This week</h3>
            <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
              {toDisplayText(data.weekly_summary[0])}
            </p>
          </NuraCard>
        )}

        {/* Agent Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 16, marginBottom: 16 }}>
          {Object.entries(agentMap).map(([key, { label, icon }]) => (
            <NuraCard key={key} style={{ cursor: 'pointer', minHeight: 210 }} className="hover:shadow-md transition-shadow" onClick={() => openAgentDetail(key)}>
              <div>
                {(() => {
                  const insightKey = insightKeyByAgent[key];
                  const source = data?.key_insights?.[insightKey] ?? data?.agent_states?.[key] ?? data?.agents?.[key];
                  const level = getIndicationLevelFromValue(source);
                  const levelDotColor = dotColor(level);
                  return (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                      <span style={{ width: 8, height: 8, borderRadius: '50%', background: levelDotColor, display: 'inline-block' }} />
                      <IndicationBadge level={level} />
                    </div>
                  );
                })()}
                <div style={{ fontSize: '1.9rem', marginBottom: 10 }}>{icon}</div>
                <h3 style={{ fontSize: '1.08rem', margin: 0 }}>{label}</h3>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: 8 }}>View details →</p>
              </div>
            </NuraCard>
          ))}
        </div>

        <NuraCard style={{ marginBottom: 16, background: 'linear-gradient(135deg, rgba(207,106,86,0.08), rgba(143,170,140,0.08))' }}>
          <Link
            to="/patient/chat"
            style={{
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: 12,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{
                width: 46,
                height: 46,
                borderRadius: '999px',
                background: 'rgba(207,106,86,0.14)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                <HeartHandshake size={22} color="var(--terracotta)" />
              </div>
              <div>
                <p style={{ margin: 0, color: 'var(--text-primary)', fontSize: '0.98rem', fontWeight: 600 }}>Chat with a warm therapist companion</p>
                <p style={{ margin: '4px 0 0', color: 'var(--text-muted)', fontSize: '0.84rem' }}>A gentle space for support, reflection, and calm next steps.</p>
              </div>
            </div>
            <span style={{ color: 'var(--sage)', fontSize: '0.92rem', fontWeight: 600 }}>Open chat →</span>
          </Link>
        </NuraCard>

        {/* Agent Detail Modal */}
        <NuraModal open={!!selectedAgent} onClose={() => { setSelectedAgent(null); setShowHistory(false); }} title={selectedAgent ? agentMap[selectedAgent]?.label : ''}>
          {agentLatest && (
            <div style={{ display: 'grid', gap: 16 }}>
              <div style={{
                border: '1px solid var(--border-custom)',
                borderRadius: 14,
                padding: 14,
                background: 'linear-gradient(145deg, rgba(143,170,140,0.10), rgba(207,106,86,0.06))',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{
                      width: 34,
                      height: 34,
                      borderRadius: 999,
                      background: 'rgba(143,170,140,0.2)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}>
                      <Sparkles size={18} color="var(--sage)" />
                    </div>
                    <div>
                      <p style={{ margin: 0, color: 'var(--text-primary)', fontSize: '0.95rem', fontWeight: 600 }}>Weekly Agent Snapshot</p>
                      <p style={{ margin: '2px 0 0', color: 'var(--text-muted)', fontSize: '0.8rem' }}>A calm summary of patterns and support guidance.</p>
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                    <IndicationBadge level={agentLatest.state} />
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', padding: '5px 9px', borderRadius: 999, border: '1px solid var(--border-custom)', background: 'rgba(255,255,255,0.55)' }}>
                      Week {agentLatest.week_number}
                    </span>
                  </div>
                </div>
              </div>

              {agentLatest.payload && (
                structuredPayload ? (
                  <div style={{ display: 'grid', gap: 14 }}>
                    <div style={{ background: 'var(--bg)', borderRadius: 12, padding: 14, border: '1px solid var(--border-custom)' }}>
                      <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.6 }}>
                        {introText}
                      </p>
                    </div>

                    {payloadMetrics.length > 0 && (
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: 12 }}>
                        {payloadMetrics.map(([key, metric]) => (
                          <div key={key} style={{ border: '1px solid var(--border-custom)', borderRadius: 14, padding: 13, background: 'linear-gradient(180deg, rgba(255,255,255,0.7), rgba(255,255,255,0.5))' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                              <h4 style={{ margin: 0, fontSize: '0.93rem', color: 'var(--text-primary)' }}>{formatMetricName(metric.metric_name || key)}</h4>
                              <IndicationBadge level={metric.state || 'normal'} />
                            </div>
                            <p style={{ margin: 0, fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                              {toDisplayText(metric.reasoning)}
                            </p>
                            <div style={{ marginTop: 10, display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 6 }}>
                              <div style={{ padding: '7px 8px', borderRadius: 9, background: 'rgba(143,170,140,0.08)' }}>
                                <p style={{ margin: 0, fontSize: '0.68rem', color: 'var(--text-muted)' }}>This week</p>
                                <p style={{ margin: '2px 0 0', fontSize: '0.78rem', color: 'var(--text-primary)', fontWeight: 600 }}>{formatNumber(metric.value)}</p>
                              </div>
                              <div style={{ padding: '7px 8px', borderRadius: 9, background: 'rgba(114,122,131,0.08)' }}>
                                <p style={{ margin: 0, fontSize: '0.68rem', color: 'var(--text-muted)' }}>Typical</p>
                                <p style={{ margin: '2px 0 0', fontSize: '0.78rem', color: 'var(--text-primary)', fontWeight: 600 }}>{formatNumber(metric.baseline)}</p>
                              </div>
                              <div style={{ padding: '7px 8px', borderRadius: 9, background: 'rgba(207,106,86,0.08)' }}>
                                <p style={{ margin: 0, fontSize: '0.68rem', color: 'var(--text-muted)' }}>Change</p>
                                <p style={{ margin: '2px 0 0', fontSize: '0.78rem', color: 'var(--text-primary)', fontWeight: 600 }}>{formatPercent(metric.pct_change)}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    <div style={{ border: '1px solid var(--border-custom)', borderRadius: 14, padding: 14, background: 'var(--card-bg)' }}>
                      <h4 style={{ margin: '0 0 8px', fontSize: '0.95rem' }}>What this may mean</h4>
                      <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.88rem', lineHeight: 1.6 }}>
                        {toDisplayText(
                          dynamicImplications && dynamicImplications !== 'Unable to parse response'
                            ? dynamicImplications
                            : watchfulCount > 0
                              ? 'A few patterns suggest a heavier week. A little extra care, connection, and rest could help you feel more balanced.'
                              : 'Your recent patterns look steady overall. Keep your current routines and check in with yourself regularly.'
                        )}
                      </p>
                    </div>

                    <div style={{ border: '1px solid var(--border-custom)', borderRadius: 14, padding: 14, background: 'var(--card-bg)' }}>
                      <h4 style={{ margin: '0 0 8px', fontSize: '0.95rem' }}>Gentle next steps</h4>
                      <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--text-muted)', display: 'grid', gap: 6, fontSize: '0.88rem', lineHeight: 1.5 }}>
                        {(recommendationBullets.length > 0 ? recommendationBullets : defaultSuggestions).map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ) : (
                  <pre style={{ background: 'var(--bg)', borderRadius: 12, padding: 16, fontSize: '0.82rem', overflow: 'auto', whiteSpace: 'pre-wrap', color: 'var(--text-muted)' }}>
                    {typeof agentLatest.payload === 'string' ? agentLatest.payload : JSON.stringify(agentLatest.payload, null, 2)}
                  </pre>
                )
              )}
              <div style={{ marginTop: 4, display: 'flex', justifyContent: 'flex-end' }}>
                <NuraButton variant="outline" onClick={() => setShowHistory(true)} style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                  <LineChart size={16} />
                  View trend
                </NuraButton>
              </div>
              {showHistory && historyData && (
                <div style={{ marginTop: 20 }}>
                  <AgentChart data={historyData.history || historyData} />
                </div>
              )}
            </div>
          )}
        </NuraModal>
      </div>
    </>
  );
}
