import React, { useState } from 'react';

interface Props extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export function NuraInput({ label, style, ...props }: Props) {
  const [focused, setFocused] = useState(false);
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {label && <label style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-muted)' }}>{label}</label>}
      <input
        {...props}
        onFocus={(e) => { setFocused(true); props.onFocus?.(e); }}
        onBlur={(e) => { setFocused(false); props.onBlur?.(e); }}
        style={{
          background: 'var(--card-bg)',
          border: `1px solid ${focused ? 'var(--sage)' : 'var(--border-custom)'}`,
          borderRadius: 12,
          padding: '12px 16px',
          fontFamily: "'DM Sans', sans-serif",
          fontSize: '0.95rem',
          color: 'var(--text-primary)',
          width: '100%',
          outline: 'none',
          transition: 'border-color 0.2s',
          ...style,
        }}
      />
    </div>
  );
}

export function NuraTextarea({ label, style, ...props }: { label?: string } & React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  const [focused, setFocused] = useState(false);
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {label && <label style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-muted)' }}>{label}</label>}
      <textarea
        {...props}
        onFocus={(e) => { setFocused(true); props.onFocus?.(e); }}
        onBlur={(e) => { setFocused(false); props.onBlur?.(e); }}
        style={{
          background: 'var(--card-bg)',
          border: `1px solid ${focused ? 'var(--sage)' : 'var(--border-custom)'}`,
          borderRadius: 12,
          padding: '12px 16px',
          fontFamily: "'DM Sans', sans-serif",
          fontSize: '0.95rem',
          color: 'var(--text-primary)',
          width: '100%',
          outline: 'none',
          resize: 'vertical',
          minHeight: 80,
          transition: 'border-color 0.2s',
          ...style,
        }}
      />
    </div>
  );
}
