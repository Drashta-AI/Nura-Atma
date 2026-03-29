import React from 'react';

type NuraCardProps = React.HTMLAttributes<HTMLDivElement> & {
  children: React.ReactNode;
};

export function NuraCard({ children, className = '', style = {}, ...rest }: NuraCardProps) {
  return (
    <div
      {...rest}
      className={`animate-fade-in ${className}`}
      style={{
        background: 'var(--card-bg)',
        borderRadius: 'var(--radius-card)',
        boxShadow: 'var(--shadow-card)',
        border: '1px solid var(--border-custom)',
        padding: '24px',
        ...style,
      }}
    >
      {children}
    </div>
  );
}
