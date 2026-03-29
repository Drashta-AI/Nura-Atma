import { ClinicianNav } from '@/components/layout/ClinicianNav';
import { NuraCard } from '@/components/ui/NuraCard';

const clinicianProfile = {
  fullName: 'Dr. Aanya Rao',
  role: 'Consultant Clinical Psychologist',
  registrationId: 'MHP-CL-2026-1184',
  email: 'aanya.rao@atma-care.example',
  phone: '+91 98765 11223',
  experienceYears: 11,
  specialization: ['Anxiety care', 'Trauma-informed therapy', 'Sleep and burnout support'],
  languages: ['English', 'Hindi', 'Tamil'],
  availability: 'Mon-Fri, 10:00 AM - 6:00 PM',
  activePatients: 18,
  averageReviewTurnaround: '24 hours',
  careApproach: [
    'Compassion-first communication',
    'Evidence-based interventions with realistic pacing',
    'Collaborative goal setting with patient autonomy',
  ],
};

export default function ClinicianProfilePage() {
  return (
    <>
      <ClinicianNav />
      <div style={{ padding: 24, maxWidth: 980, margin: '0 auto' }}>
        <h1 style={{ fontStyle: 'italic', color: 'var(--sage)', marginBottom: 20, fontSize: '1.6rem' }}>Clinician Profile</h1>

        <NuraCard style={{ marginBottom: 16 }}>
          <h2 style={{ margin: '0 0 14px', fontSize: '1.2rem' }}>{clinicianProfile.fullName}</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 10 }}>
            <p style={{ margin: 0, color: 'var(--text-muted)' }}>Role: {clinicianProfile.role}</p>
            <p style={{ margin: 0, color: 'var(--text-muted)' }}>Registration ID: {clinicianProfile.registrationId}</p>
            <p style={{ margin: 0, color: 'var(--text-muted)' }}>Experience: {clinicianProfile.experienceYears} years</p>
            <p style={{ margin: 0, color: 'var(--text-muted)' }}>Email: {clinicianProfile.email}</p>
            <p style={{ margin: 0, color: 'var(--text-muted)' }}>Phone: {clinicianProfile.phone}</p>
            <p style={{ margin: 0, color: 'var(--text-muted)' }}>Availability: {clinicianProfile.availability}</p>
          </div>
        </NuraCard>

        <NuraCard style={{ marginBottom: 16 }}>
          <h3 style={{ margin: '0 0 10px', fontSize: '1rem' }}>Clinical Focus</h3>
          <ul style={{ margin: 0, paddingLeft: 20, color: 'var(--text-muted)', display: 'grid', gap: 6 }}>
            {clinicianProfile.specialization.map((item, index) => (
              <li key={`spec-${index}`}>{item}</li>
            ))}
          </ul>
        </NuraCard>

        <NuraCard style={{ marginBottom: 16 }}>
          <h3 style={{ margin: '0 0 10px', fontSize: '1rem' }}>Care Approach</h3>
          <ul style={{ margin: 0, paddingLeft: 20, color: 'var(--text-muted)', display: 'grid', gap: 6 }}>
            {clinicianProfile.careApproach.map((item, index) => (
              <li key={`approach-${index}`}>{item}</li>
            ))}
          </ul>
        </NuraCard>

        <NuraCard>
          <h3 style={{ margin: '0 0 10px', fontSize: '1rem' }}>Practice Snapshot</h3>
          <p style={{ margin: '0 0 6px', color: 'var(--text-muted)' }}>Active patients: {clinicianProfile.activePatients}</p>
          <p style={{ margin: '0 0 6px', color: 'var(--text-muted)' }}>Average review turnaround: {clinicianProfile.averageReviewTurnaround}</p>
          <p style={{ margin: 0, color: 'var(--text-muted)' }}>Languages: {clinicianProfile.languages.join(', ')}</p>
        </NuraCard>
      </div>
    </>
  );
}
