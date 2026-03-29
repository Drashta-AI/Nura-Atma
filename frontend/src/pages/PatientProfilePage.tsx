import { PatientNav } from '@/components/layout/PatientNav';
import { NuraCard } from '@/components/ui/NuraCard';

const profile = {
  fullName: 'Maya Thompson',
  age: 29,
  pronouns: 'She/Her',
  email: 'maya.thompson@example.com',
  phone: '+1 (555) 214-7719',
  timezone: 'Asia/Kolkata',
  emergencyContact: 'Arun Thompson (+1 555-881-9021)',
  preferredCheckIn: 'Evening (7:00 PM - 9:00 PM)',
  careGoals: [
    'Improve sleep consistency across weekdays',
    'Build a calmer journaling routine',
    'Reduce high-stress evening patterns',
  ],
  supportPreferences: [
    'Gentle reminders over frequent alerts',
    'Weekly trend summaries in plain language',
    'Actionable suggestions with low pressure',
  ],
};

export default function PatientProfilePage() {
  return (
    <>
      <PatientNav />
      <div style={{ padding: 24, maxWidth: 900, margin: '0 auto' }}>
        <h1 style={{ fontStyle: 'italic', color: 'var(--sage)', marginBottom: 20, fontSize: '1.6rem' }}>Your Profile</h1>

        <NuraCard style={{ marginBottom: 16 }}>
          <h2 style={{ margin: '0 0 14px', fontSize: '1.2rem' }}>{profile.fullName}</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 10 }}>
            <p style={{ margin: 0, color: 'var(--text-muted)' }}>Age: {profile.age}</p>
            <p style={{ margin: 0, color: 'var(--text-muted)' }}>Pronouns: {profile.pronouns}</p>
            <p style={{ margin: 0, color: 'var(--text-muted)' }}>Email: {profile.email}</p>
            <p style={{ margin: 0, color: 'var(--text-muted)' }}>Phone: {profile.phone}</p>
            <p style={{ margin: 0, color: 'var(--text-muted)' }}>Timezone: {profile.timezone}</p>
            <p style={{ margin: 0, color: 'var(--text-muted)' }}>Preferred check-in: {profile.preferredCheckIn}</p>
          </div>
        </NuraCard>

        <NuraCard style={{ marginBottom: 16 }}>
          <h3 style={{ margin: '0 0 10px', fontSize: '1rem' }}>Care Goals</h3>
          <ul style={{ margin: 0, paddingLeft: 20, color: 'var(--text-muted)', display: 'grid', gap: 6 }}>
            {profile.careGoals.map((goal, index) => (
              <li key={`goal-${index}`}>{goal}</li>
            ))}
          </ul>
        </NuraCard>

        <NuraCard style={{ marginBottom: 16 }}>
          <h3 style={{ margin: '0 0 10px', fontSize: '1rem' }}>Support Preferences</h3>
          <ul style={{ margin: 0, paddingLeft: 20, color: 'var(--text-muted)', display: 'grid', gap: 6 }}>
            {profile.supportPreferences.map((preference, index) => (
              <li key={`pref-${index}`}>{preference}</li>
            ))}
          </ul>
        </NuraCard>

        <NuraCard>
          <h3 style={{ margin: '0 0 10px', fontSize: '1rem' }}>Emergency Contact</h3>
          <p style={{ margin: 0, color: 'var(--text-muted)' }}>{profile.emergencyContact}</p>
        </NuraCard>
      </div>
    </>
  );
}
