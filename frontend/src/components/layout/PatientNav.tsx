import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

export function PatientNav() {
  const { logout } = useAuth();
  const { pathname } = useLocation();

  const linkStyle = (path: string): React.CSSProperties => ({
    color: pathname === path ? 'var(--sage)' : 'var(--text-muted)',
    textDecoration: 'none',
    fontWeight: pathname === path ? 500 : 400,
    fontSize: '0.9rem',
    transition: 'color 0.2s',
  });

  return (
    <nav style={{
      background: 'var(--card-bg)',
      borderBottom: '1px solid var(--border-custom)',
      padding: '12px 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 40,
    }}>
      <Link to="/patient/home" style={{ textDecoration: 'none' }}>
        <span style={{ fontFamily: "'DM Serif Display', serif", fontSize: '1.3rem', color: 'var(--sage)', fontStyle: 'italic' }}>Nura</span>
      </Link>
      <div style={{ display: 'flex', gap: 20, alignItems: 'center' }}>
        <Link to="/patient/home" style={linkStyle('/patient/home')}>Home</Link>
        <Link to="/patient/journal" style={linkStyle('/patient/journal')}>Journal</Link>
        <Link to="/patient/chat" style={linkStyle('/patient/chat')}>Chat</Link>
        <Link to="/patient/profile" style={linkStyle('/patient/profile')}>Profile</Link>
        <Link to="/reports" style={linkStyle('/reports')}>Reports</Link>
        <button onClick={logout} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.85rem' }}>Sign out</button>
      </div>
    </nav>
  );
}
