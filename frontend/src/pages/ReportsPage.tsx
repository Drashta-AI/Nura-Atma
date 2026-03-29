import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { PatientNav } from '@/components/layout/PatientNav';
import { ClinicianNav } from '@/components/layout/ClinicianNav';
import { NuraCard } from '@/components/ui/NuraCard';
import ReactMarkdown from 'react-markdown';

type ReportListItem = {
  week_number: number;
  name?: string;
  modified_at?: string;
};

type ReportDetail = {
  week_number?: number;
  name?: string;
  content?: string;
};

const getWeekNumber = (item: any): number | null => {
  const candidate = item?.week_number ?? item?.week ?? item?.weekNumber ?? item?.id;
  const parsed = Number(candidate);
  return Number.isFinite(parsed) ? parsed : null;
};

const getWeekNumberFromText = (value: unknown): number | null => {
  if (typeof value !== 'string') return null;
  const match = value.match(/week[_-]?(\d+)[_-]?report/i);
  if (!match) return null;
  const parsed = Number(match[1]);
  return Number.isFinite(parsed) ? parsed : null;
};

const getListSource = (raw: unknown): any[] => {
  if (Array.isArray(raw)) return raw;
  if (!raw || typeof raw !== 'object') return [];

  const obj = raw as Record<string, unknown>;
  const explicitKeys = ['reports', 'items', 'data', 'weeks', 'results'];

  for (const key of explicitKeys) {
    const value = obj[key];
    if (Array.isArray(value)) return value;
  }

  const firstArrayValue = Object.values(obj).find((value) => Array.isArray(value));
  return Array.isArray(firstArrayValue) ? firstArrayValue : [];
};

const normalizeReportList = (raw: unknown): ReportListItem[] => {
  const source = getListSource(raw);

  return source
    .map((item: any) => {
      const weekNumber =
        getWeekNumber(item) ??
        getWeekNumberFromText(item?.name) ??
        getWeekNumberFromText(item?.path);
      if (weekNumber === null) return null;

      return {
        week_number: weekNumber,
        name: item?.name ?? item?.title ?? (typeof item?.content === 'string' ? `Week ${weekNumber} Report` : undefined),
        modified_at: item?.modified_at ?? item?.updated_at ?? item?.created_at,
      } as ReportListItem;
    })
    .filter((item): item is ReportListItem => item !== null)
    .sort((a, b) => b.week_number - a.week_number);
};

const normalizeReportDetail = (raw: unknown): ReportDetail => {
  if (!raw || typeof raw !== 'object') {
    if (typeof raw === 'string') return { content: raw };
    return {};
  }

  const obj = raw as Record<string, unknown>;
  const item = (obj.report && typeof obj.report === 'object' ? obj.report : obj) as any;
  const weekNumber = getWeekNumber(item);

  return {
    week_number: weekNumber ?? undefined,
    name: typeof item.name === 'string' ? item.name : (typeof item.title === 'string' ? item.title : undefined),
    content:
      typeof item.content === 'string'
        ? item.content
        : (typeof item.markdown === 'string'
          ? item.markdown
          : (typeof item.report === 'string' ? item.report : '')),
  };
};

const getErrorText = (error: unknown, fallback: string) => {
  const maybe = error as any;
  return maybe?.response?.data?.detail || maybe?.response?.data?.message || maybe?.message || fallback;
};

export default function ReportsPage() {
  const { role } = useAuth();
  const [selectedWeek, setSelectedWeek] = useState<number | null>(null);
  const Nav = role === 'clinician' ? ClinicianNav : PatientNav;

  const { data: listData, isLoading, isError: isListError, error: listError } = useQuery({
    queryKey: ['reports'],
    queryFn: () => api.get('/v1/reports').then(r => r.data),
  });

  const { data: reportData, isError: isDetailError, error: detailError } = useQuery({
    queryKey: ['report', selectedWeek],
    queryFn: () => api.get(`/v1/reports/${selectedWeek}`).then(r => r.data),
    enabled: selectedWeek !== null,
  });

  const reportList = normalizeReportList(listData);
  const selectedReport = normalizeReportDetail(reportData);

  const openWeek = (weekNumber: number) => setSelectedWeek(weekNumber);

  useEffect(() => {
    if (selectedWeek === null && reportList.length > 0) {
      setSelectedWeek(reportList[0].week_number);
    }
  }, [selectedWeek, reportList]);

  return (
    <>
      <Nav />
      <div style={{ padding: 24, maxWidth: 1100, margin: '0 auto' }}>
        <h1 style={{ fontStyle: 'italic', color: 'var(--sage)', marginBottom: 20, fontSize: '1.5rem' }}>Reports</h1>
        <div style={{ display: 'grid', gridTemplateColumns: selectedWeek !== null ? '280px 1fr' : '1fr', gap: 20 }}>
          {/* List */}
          <div>
            {isLoading ? (
              [1,2,3].map(i => <div key={i} className="animate-pulse" style={{ height: 56, borderRadius: 'var(--radius-card)', background: 'var(--border-custom)', marginBottom: 8 }} />)
            ) : isListError ? (
              <NuraCard>
                <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--terracotta)' }}>
                  Unable to load weekly reports. {getErrorText(listError, 'Please check your API connection and login token.')}
                </p>
              </NuraCard>
            ) : reportList.length === 0 ? (
              <NuraCard>
                <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-muted)' }}>No weekly reports are available yet.</p>
              </NuraCard>
            ) : (
              reportList.map((r) => (
                <NuraCard
                  key={r.week_number}
                  style={{ marginBottom: 8, cursor: 'pointer', borderLeft: selectedWeek === r.week_number ? '3px solid var(--sage)' : 'none' }}
                  className="hover:shadow-md"
                >
                  <div onClick={() => openWeek(r.week_number)}>
                    <h3 style={{ fontSize: '0.95rem', margin: 0 }}>{r.name || `Week ${r.week_number} Report`}</h3>
                    {r.modified_at && <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{new Date(r.modified_at).toLocaleDateString()}</span>}
                  </div>
                </NuraCard>
              ))
            )}
          </div>

          {/* Viewer */}
          {selectedWeek !== null && (
            <NuraCard className="animate-fade-in">
              <h2 style={{ marginBottom: 16, fontSize: '1.2rem' }}>{selectedReport.name || `Week ${selectedWeek} Report`}</h2>
              <div style={{ fontSize: '0.9rem', lineHeight: 1.8, color: 'var(--text-primary)' }} className="prose prose-sm max-w-none">
                {isDetailError ? (
                  <p style={{ margin: 0, color: 'var(--terracotta)' }}>
                    Unable to load this report. {getErrorText(detailError, 'Please verify the week number exists on the server.')}
                  </p>
                ) : (
                  <ReactMarkdown>{selectedReport.content || 'No report content available for this week.'}</ReactMarkdown>
                )}
              </div>
            </NuraCard>
          )}
        </div>
      </div>
    </>
  );
}
