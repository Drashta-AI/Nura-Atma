import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const stateToNum: Record<string, number> = { normal: 1, watchful: 2, elevated: 3 };
const stateLabel: Record<number, string> = { 1: 'Normal', 2: 'Watchful', 3: 'Elevated' };

interface HistoryPoint {
  week_number: number;
  state: string;
  payload?: any;
}

export function AgentChart({ data }: { data: HistoryPoint[] }) {
  const chartData = data.map(d => ({ ...d, stateNum: stateToNum[d.state] || 1 }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={chartData} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
        <XAxis dataKey="week_number" label={{ value: 'Week', position: 'bottom', offset: -5 }} tick={{ fontSize: 12 }} />
        <YAxis
          domain={[1, 3]}
          ticks={[1, 2, 3]}
          tickFormatter={(v: number) => stateLabel[v] || ''}
          tick={{ fontSize: 11 }}
          width={70}
        />
        <Tooltip
          formatter={(v: number) => stateLabel[v] || v}
          labelFormatter={(l) => `Week ${l}`}
          contentStyle={{ borderRadius: 12, border: '1px solid var(--border-custom)', fontSize: '0.85rem' }}
        />
        <Line
          type="monotone"
          dataKey="stateNum"
          stroke="var(--sage)"
          strokeWidth={2}
          dot={{ r: 5, fill: 'var(--sage)' }}
          activeDot={{ r: 7 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
