import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

const MetricsRadar = ({ metrics }) => {
  const data = [
    { subject: 'Speed', A: metrics.speed || 0, fullMark: 100 },
    { subject: 'Technique', A: metrics.technique || 0, fullMark: 100 },
    { subject: 'Athleticism', A: metrics.athleticism || 0, fullMark: 100 },
    { subject: 'Agility', A: metrics.agility || 0, fullMark: 100 },
    { subject: 'Consistency', A: metrics.consistency || 0, fullMark: 100 },
  ];

  return (
    <div className="glass-card p-6 h-[400px]">
      <h3 className="text-slate-400 text-sm font-medium mb-4 uppercase tracking-widest">Attribute Breakdown</h3>
      <ResponsiveContainer width="100%" height="90%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
          <PolarGrid stroke="#334155" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
          <Radar
            name="Metrics"
            dataKey="A"
            stroke="#00D4FF"
            fill="#00D4FF"
            fillOpacity={0.4}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default MetricsRadar;
