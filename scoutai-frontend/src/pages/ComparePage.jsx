import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getAthleteHistory } from '../api/scoutApi';
import MetricsRadar from '../components/MetricsRadar';
import ScoreCard from '../components/ScoreCard';
import { motion } from 'framer-motion';

const ComparePage = () => {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  
  const [athlete1Id, setAthlete1Id] = useState(searchParams.get('a1') || '');
  const [athlete2Id, setAthlete2Id] = useState(searchParams.get('a2') || '');

  const { data: h1 } = useQuery({
    queryKey: ['history', athlete1Id],
    queryFn: () => getAthleteHistory(athlete1Id).then(res => res.data),
    enabled: !!athlete1Id,
  });

  const { data: h2 } = useQuery({
    queryKey: ['history', athlete2Id],
    queryFn: () => getAthleteHistory(athlete2Id).then(res => res.data),
    enabled: !!athlete2Id,
  });

  const a1 = h1?.history?.[0]?.result;
  const a2 = h2?.history?.[0]?.result;

  const handleSwap = () => {
    const temp = athlete1Id;
    setAthlete1Id(athlete2Id);
    setAthlete2Id(temp);
  };

  return (
    <div className="py-12 space-y-12 pb-32">
      <div className="text-center space-y-4">
        <h1 className="text-6xl font-black text-white">Compare <span className="scout-gradient-text">Athletes</span></h1>
        <p className="text-slate-400">Select two athletes to compare their ML-scored performance metrics side-by-side.</p>
      </div>

      <div className="flex items-center gap-4 sticky top-20 z-10 py-4 bg-background/80 backdrop-blur-xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-grow">
          <input 
            type="text" 
            placeholder="Athlete 1 ID" 
            className="input-field"
            value={athlete1Id}
            onChange={(e) => setAthlete1Id(e.target.value)}
          />
          <input 
            type="text" 
            placeholder="Athlete 2 ID" 
            className="input-field"
            value={athlete2Id}
            onChange={(e) => setAthlete2Id(e.target.value)}
          />
        </div>
        <button 
          onClick={handleSwap}
          className="p-3 bg-white/5 border border-white/10 rounded-xl text-primary-blue hover:bg-white/10 transition-all"
          title="Swap Athletes"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" /></svg>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
        {/* Athlete 1 Column */}
        <div className="space-y-8">
          {a1 ? (
            <motion.div initial={{ x: -20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} className="space-y-8">
              <div className="glass-card p-8 border-primary-blue/30">
                <h2 className="text-3xl font-black text-white mb-2">{h1.athlete.name}</h2>
                <div className="flex items-center gap-4">
                  <ScoreCard score={a1.talent_score} grade={a1.grade} />
                </div>
              </div>
              <MetricsRadar metrics={a1.breakdown} />
              <div className="glass-card p-8">
                 <h3 className="text-xs font-black uppercase text-slate-500 mb-6">AI Assessment</h3>
                 <p className="text-slate-200">{a1.ai_summary}</p>
              </div>
            </motion.div>
          ) : (
            <div className="h-96 glass-card flex items-center justify-center text-slate-600 font-bold uppercase tracking-widest border-dashed">
              Search for Athlete 1
            </div>
          )}
        </div>

        {/* Athlete 2 Column */}
        <div className="space-y-8">
          {a2 ? (
            <motion.div initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} className="space-y-8">
              <div className="glass-card p-8 border-primary-green/30">
                <h2 className="text-3xl font-black text-white mb-2">{h2.athlete.name}</h2>
                <div className="flex items-center gap-4">
                  <ScoreCard score={a2.talent_score} grade={a2.grade} />
                </div>
              </div>
              <MetricsRadar metrics={a2.breakdown} />
              <div className="glass-card p-8">
                 <h3 className="text-xs font-black uppercase text-slate-500 mb-6">AI Assessment</h3>
                 <p className="text-slate-200">{a2.ai_summary}</p>
              </div>
            </motion.div>
          ) : (
            <div className="h-96 glass-card flex items-center justify-center text-slate-600 font-bold uppercase tracking-widest border-dashed">
              Search for Athlete 2
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ComparePage;
