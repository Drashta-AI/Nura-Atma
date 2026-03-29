import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

export function ClinicianNav() {
  const { logout } = useAuth();
  const { pathname } = useLocation();

  const linkStyle = (path: string): React.CSSProperties => ({
    color: pathname.startsWith(path) ? 'var(--sage)' : 'var(--text-muted)',
    textDecoration: 'none',
    fontWeight: pathname.startsWith(path) ? 500 : 400,
    fontSize: '0.9rem',
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
      <Link to="/clinician/patients" style={{ textDecoration: 'none' }}>
        <span style={{ fontFamily: "'DM Serif Display', serif", fontSize: '1.3rem', color: 'var(--sage)', fontStyle: 'italic' }}>Atma</span>
      </Link>
      <div style={{ display: 'flex', gap: 20, alignItems: 'center' }}>
        <Link to="/clinician/patients" style={linkStyle('/clinician/patients')}>Patients</Link>
        <Link to="/clinician/profile" style={linkStyle('/clinician/profile')}>Profile</Link>
        <Link to="/reports" style={linkStyle('/reports')}>Reports</Link>
        <button onClick={logout} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.85rem' }}>Sign out</button>
      </div>
    </nav>
  );
}
