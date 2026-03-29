import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { api } from '@/lib/api';
import { ClinicianNav } from '@/components/layout/ClinicianNav';
import { NuraCard } from '@/components/ui/NuraCard';
import { IndicationBadge } from '@/components/ui/IndicationBadge';

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

export default function PatientsListPage() {
  const navigate = useNavigate();

  const { data, isLoading } = useQuery({
    queryKey: ['clinician-patients'],
    queryFn: () => api.get('/v1/clinician/patients').then(r => r.data),
  });

  return (
    <>
      <ClinicianNav />
      <div style={{ padding: 24, maxWidth: 900, margin: '0 auto' }}>
        <h1 style={{ fontStyle: 'italic', color: 'var(--sage)', marginBottom: 24, fontSize: '1.5rem' }}>Your Patients</h1>

        {isLoading ? (
          [1,2,3].map(i => <div key={i} className="animate-pulse" style={{ height: 80, borderRadius: 'var(--radius-card)', background: 'var(--border-custom)', marginBottom: 12 }} />)
        ) : (
          <div style={{ display: 'grid', gap: 12 }}>
            {data?.patients?.map((p: any) => (
              <NuraCard
                key={p.patient_id}
                style={{ cursor: 'pointer', transition: 'box-shadow 0.2s' }}
                className="hover:shadow-md"
              >
                <div onClick={() => navigate(`/clinician/patients/${p.patient_id}`)} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.05rem' }}>{p.full_name}</h3>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Age {randomizedAge(p.age, `${p.patient_id}-${p.full_name || ''}`)}</span>
                  </div>
                  <IndicationBadge level={p.indication_level || 'normal'} />
                </div>
              </NuraCard>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
