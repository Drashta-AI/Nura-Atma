type Level = 'normal' | 'watchful' | 'elevated';

const map: Record<Level, { bg: string; text: string; label: string }> = {
  normal: { bg: 'var(--badge-normal-bg)', text: 'var(--badge-normal-text)', label: 'Normal' },
  watchful: { bg: 'var(--badge-watchful-bg)', text: 'var(--badge-watchful-text)', label: 'Watchful' },
  elevated: { bg: 'var(--badge-elevated-bg)', text: 'var(--badge-elevated-text)', label: 'Elevated' },
};

export function IndicationBadge({ level }: { level: Level }) {
  const s = map[level] ?? map.normal;
  return (
    <span
      style={{
        background: s.bg,
        color: s.text,
        borderRadius: 'var(--radius-pill)',
        padding: '4px 14px',
        fontSize: '0.82rem',
        fontWeight: 500,
        letterSpacing: '0.02em',
      }}
    >
      {s.label}
    </span>
  );
}
