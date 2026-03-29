import React from 'react';

type Variant = 'primary' | 'outline' | 'ghost';

interface Props extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

const styles: Record<Variant, React.CSSProperties> = {
  primary: {
    background: 'var(--sage)',
    color: '#fff',
    borderRadius: 'var(--radius-pill)',
    padding: '10px 28px',
    fontFamily: "'DM Sans', sans-serif",
    fontWeight: 500,
    letterSpacing: '0.04em',
    border: 'none',
    cursor: 'pointer',
  },
  outline: {
    background: 'transparent',
    color: 'var(--sage)',
    border: '1.5px solid var(--sage)',
    borderRadius: 'var(--radius-pill)',
    padding: '10px 28px',
    fontFamily: "'DM Sans', sans-serif",
    fontWeight: 500,
    letterSpacing: '0.04em',
    cursor: 'pointer',
  },
  ghost: {
    background: 'transparent',
    color: 'var(--sage)',
    border: 'none',
    borderRadius: 'var(--radius-pill)',
    padding: '10px 28px',
    fontFamily: "'DM Sans', sans-serif",
    fontWeight: 500,
    cursor: 'pointer',
  },
};

export function NuraButton({ variant = 'primary', style, disabled, ...props }: Props) {
  return (
    <button
      {...props}
      disabled={disabled}
      style={{
        ...styles[variant],
        opacity: disabled ? 0.5 : 1,
        ...style,
      }}
    />
  );
}
