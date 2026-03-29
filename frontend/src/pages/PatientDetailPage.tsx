import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { ClinicianNav } from '@/components/layout/ClinicianNav';
import { NuraCard } from '@/components/ui/NuraCard';
import { NuraButton } from '@/components/ui/NuraButton';
import { IndicationBadge } from '@/components/ui/IndicationBadge';
import { AgentChart } from '@/components/ui/AgentChart';
import { NuraModal } from '@/components/ui/NuraModal';
import { Sparkles, LineChart } from 'lucide-react';

const agentMap: Record<string, { label: string; icon: string; key: string }> = {
  behavioral: { label: 'Mood & Behaviour', icon: '🧠', key: 'behavioral' },
  physiological: { label: 'Body Signals', icon: '💗', key: 'physiological' },
  context: { label: 'Context & Environment', icon: '🌿', key: 'context' },
  language: { label: 'Language Patterns', icon: '💬', key: 'language' },
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

const hashSeed = (seed: string) => {
  let hash = 0;
  for (let i = 0; i < seed.length; i += 1) {
    hash = (hash * 31 + seed.charCodeAt(i)) >>> 0;
  }
  return hash;
};

const randomizedAge = (baseAge: unknown, seed: string) => {
  const hash = hashSeed(seed);
  const jitter = (hash % 9) - 4;
  const parsedAge = Number(baseAge);

  if (Number.isFinite(parsedAge)) {
    return Math.max(18, Math.min(90, Math.round(parsedAge + jitter)));
  }

  return 20 + (hash % 51);
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

export default function PatientDetailPage() {
  const { patient_id } = useParams();
  const navigate = useNavigate();
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);

  const { data: overview, isLoading: loadingOverview } = useQuery({
    queryKey: ['patient-overview', patient_id],
    queryFn: () => api.get(`/v1/clinician/patients/${patient_id}/overview`).then(r => r.data),
  });

  const { data: agents } = useQuery({
    queryKey: ['patient-agents', patient_id],
    queryFn: () => api.get(`/v1/clinician/patients/${patient_id}/agents/latest`).then(r => r.data),
    refetchInterval: 45000,
  });

  const { data: historyData } = useQuery({
    queryKey: ['patient-agent-history', patient_id, selectedAgent],
    queryFn: () => api.get(`/v1/clinician/patients/${patient_id}/agents/${selectedAgent}/history`).then(r => r.data),
    enabled: !!selectedAgent && showHistory,
  });

  const selectedAgentData = selectedAgent ? (agents?.agents?.[selectedAgent] || agents?.[selectedAgent]) : null;
  const structuredPayload = getStructuredPayload(selectedAgentData?.payload);
  const payloadMetrics = structuredPayload?.metric_states ? Object.entries(structuredPayload.metric_states) : [];
  const watchfulCount = payloadMetrics.filter(([, metric]) => metric?.state === 'watchful' || metric?.state === 'elevated').length;
  const reasoning = structuredPayload?.reasoning || {};
  const recommendationBullets = getRecommendations(reasoning.recommendations);
  const dynamicImplications = toDisplayText(
    reasoning.implications || reasoning.energy_assessment || reasoning.sleep_quality || reasoning.reasoning
  );

  const calmIntroByAgent: Record<string, string> = {
    behavioral: 'This is a gentle snapshot of recent communication patterns. These signals are helpful hints, not judgments.',
    physiological: 'This is a gentle snapshot of body and energy patterns. These signals support reflection, not self-criticism.',
    context: 'This is a gentle snapshot of environment and routine patterns. It can help you notice what supports wellbeing.',
    language: 'This is a gentle snapshot of language patterns over time. It is meant to guide awareness with care.',
  };

  const defaultSuggestionsByAgent: Record<string, string[]> = {
    behavioral: [
      'Encourage a brief social check-in with a trusted person this week.',
      'Suggest one restorative break each day to reduce overload.',
      'Track whether social or solo time feels more regulating this week.',
    ],
    physiological: [
      'Support a stable sleep rhythm across the week.',
      'Add short movement and hydration breaks to support energy.',
      'Use smaller focus blocks with short rests when fatigue appears.',
    ],
    context: [
      'Reduce one source of daily friction in routine or environment.',
      'Repeat one routine that felt supportive yesterday.',
      'Identify one calming cue in the patient’s environment.',
    ],
    language: [
      'Use reflective prompts that encourage self-compassion.',
      'Help reframe one critical self-statement into a balanced one.',
      'Track language shifts across the week for trend direction.',
    ],
  };

  const selectedAgentKey = selectedAgent || 'behavioral';
  const introText = calmIntroByAgent[selectedAgentKey] || calmIntroByAgent.behavioral;
  const defaultSuggestions = defaultSuggestionsByAgent[selectedAgentKey] || defaultSuggestionsByAgent.behavioral;

  if (loadingOverview) return (
    <>
      <ClinicianNav />
      <div style={{ padding: 24, maxWidth: 900, margin: '0 auto' }}>
        {[1,2,3].map(i => <div key={i} className="animate-pulse" style={{ height: 100, borderRadius: 'var(--radius-card)', background: 'var(--border-custom)', marginBottom: 12 }} />)}
      </div>
    </>
  );

  return (
    <>
      <ClinicianNav />
      <div style={{ padding: 24, maxWidth: 900, margin: '0 auto' }}>
        <button onClick={() => navigate('/clinician/patients')} style={{ background: 'none', border: 'none', color: 'var(--sage)', cursor: 'pointer', marginBottom: 16, fontSize: '0.9rem' }}>← Back to patients</button>

        <h1 style={{ fontStyle: 'italic', color: 'var(--sage)', marginBottom: 20, fontSize: '1.6rem' }}>{overview?.full_name}</h1>

        {/* Profile Card */}
        <NuraCard style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'center' }}>
            <div>
              <p style={{ margin: 0, fontSize: '0.9rem' }}>Age: {randomizedAge(overview?.age, `${patient_id || ''}-${overview?.full_name || ''}`)}</p>
              <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                {overview?.consent_given && <span style={{ color: 'var(--sage)', fontSize: '0.82rem' }}>✓ Consent</span>}
                {overview?.onboarding_completed && <span style={{ color: 'var(--sage)', fontSize: '0.82rem' }}>✓ Onboarded</span>}
              </div>
            </div>
            <div style={{ marginLeft: 'auto' }}>
              <IndicationBadge level={overview?.indication_level || 'normal'} />
            </div>
          </div>
        </NuraCard>

        {/* Orchestrator Summary */}
        {overview?.orchestrator && (
          <NuraCard style={{ marginBottom: 16, borderLeft: '4px solid var(--sage)' }}>
            <h3 style={{ fontSize: '1rem', marginBottom: 8 }}>✦ Overall Synthesis</h3>
            <p style={{ margin: 0, fontSize: '0.9rem', lineHeight: 1.7, color: 'var(--text-muted)' }}>{toDisplayText(overview.orchestrator)}</p>
          </NuraCard>
        )}

        {/* Weekly Summary */}
        {overview?.weekly_summary?.length > 0 && (
          <NuraCard style={{ marginBottom: 16 }}>
            <h3 style={{ fontSize: '1rem', marginBottom: 12 }}>This week</h3>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {overview.weekly_summary.map((item: unknown, i: number) => (
                <li key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, marginBottom: 8, fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                  <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--sage)', marginTop: 7, flexShrink: 0 }} />
                  {toDisplayText(item)}
                </li>
              ))}
            </ul>
          </NuraCard>
        )}

        {/* Agent Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
          {Object.entries(agentMap).map(([key, { label, icon }]) => {
            const agentData = agents?.agents?.[key] || agents?.[key];
            return (
              <NuraCard key={key} style={{ cursor: 'pointer' }} className="hover:shadow-md transition-shadow" onClick={() => { setSelectedAgent(key); setShowHistory(false); }}>
                <div style={{ fontSize: '1.4rem', marginBottom: 8 }}>{icon}</div>
                <h3 style={{ fontSize: '0.95rem', marginBottom: 6 }}>{label}</h3>
                {agentData && <IndicationBadge level={agentData.state || 'normal'} />}
                <p style={{ margin: '10px 0 0', fontSize: '0.82rem', color: 'var(--text-muted)' }}>View details →</p>
              </NuraCard>
            );
          })}
        </div>

        {/* Agent Detail Modal */}
        <NuraModal open={!!selectedAgent} onClose={() => { setSelectedAgent(null); setShowHistory(false); }} title={selectedAgent ? agentMap[selectedAgent]?.label : ''}>
          {selectedAgentData && (
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
                      <p style={{ margin: 0, color: 'var(--text-primary)', fontSize: '0.95rem', fontWeight: 600 }}>Agent Insight Brief</p>
                      <p style={{ margin: '2px 0 0', color: 'var(--text-muted)', fontSize: '0.8rem' }}>Structured view for quick clinical interpretation.</p>
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                    <IndicationBadge level={selectedAgentData.state || 'normal'} />
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', padding: '5px 9px', borderRadius: 999, border: '1px solid var(--border-custom)', background: 'rgba(255,255,255,0.55)' }}>
                      Week {toDisplayText(selectedAgentData.week_number)}
                    </span>
                  </div>
                </div>
              </div>

              {selectedAgentData.payload && (
                structuredPayload ? (
                  <div style={{ display: 'grid', gap: 14 }}>
                    <div style={{ background: 'var(--bg)', borderRadius: 12, padding: 14, border: '1px solid var(--border-custom)' }}>
                      <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.6 }}>{introText}</p>
                    </div>

                    {payloadMetrics.length > 0 && (
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: 12 }}>
                        {payloadMetrics.map(([metricKey, metric]) => (
                          <div key={metricKey} style={{ border: '1px solid var(--border-custom)', borderRadius: 14, padding: 13, background: 'linear-gradient(180deg, rgba(255,255,255,0.7), rgba(255,255,255,0.5))' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                              <h4 style={{ margin: 0, fontSize: '0.93rem', color: 'var(--text-primary)' }}>{formatMetricName(metric.metric_name || metricKey)}</h4>
                              <IndicationBadge level={metric.state || 'normal'} />
                            </div>
                            <p style={{ margin: 0, fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>{toDisplayText(metric.reasoning)}</p>
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
                              ? 'A few patterns suggest a heavier week. A supportive, paced plan may help improve balance.'
                              : 'Patterns look steady overall. Continue current supports and monitor trends over time.'
                        )}
                      </p>
                    </div>

                    <div style={{ border: '1px solid var(--border-custom)', borderRadius: 14, padding: 14, background: 'var(--card-bg)' }}>
                      <h4 style={{ margin: '0 0 8px', fontSize: '0.95rem' }}>Suggested follow-up</h4>
                      <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--text-muted)', display: 'grid', gap: 6, fontSize: '0.88rem', lineHeight: 1.5 }}>
                        {(recommendationBullets.length > 0 ? recommendationBullets : defaultSuggestions).map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ) : (
                  <pre style={{ background: 'var(--bg)', borderRadius: 12, padding: 16, fontSize: '0.82rem', overflow: 'auto', whiteSpace: 'pre-wrap', color: 'var(--text-muted)' }}>
                    {typeof selectedAgentData.payload === 'string' ? selectedAgentData.payload : JSON.stringify(selectedAgentData.payload, null, 2)}
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
