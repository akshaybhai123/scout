import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { getLeaderboard } from '../api/scoutApi';

const FitnessPage = () => {
  const [isExporting, setIsExporting] = useState(false);

  const handleGlobalExport = async () => {
    setIsExporting(true);
    try {
      const res = await getLeaderboard({ limit: 100 });
      const athletes = res.data;
      if (!athletes) return;
      
      const headers = "Rank,Name,Sport,Age,Region,Talent Score,Grade\n";
      const csvContent = "data:text/csv;charset=utf-8," + headers + 
        athletes.map(a => `${a.rank},"${a.name}",${a.sport},${a.age},"${a.region}",${a.talent_score},${a.grade}`).join("\n");
      
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", `global_scout_rankings.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Export failed", error);
    } finally {
      setIsExporting(false);
    }
  };
  return (
    <div className="py-12 max-w-4xl mx-auto text-center space-y-12">
      <div className="space-y-4">
        <h1 className="text-6xl font-black text-white">Real-Time <span className="scout-gradient-text">Fitness Tracker</span></h1>
        <p className="text-slate-400 text-lg">Webcam-based bicep curl counter with AI pose estimation.</p>
      </div>

      <div className="glass-card p-12 space-y-12 border-primary-blue/20">
        <div className="relative w-32 h-32 mx-auto">
          <div className="absolute inset-0 bg-primary-blue/20 rounded-full animate-ping"></div>
          <div className="relative w-32 h-32 bg-primary-blue/10 rounded-full flex items-center justify-center text-primary-blue backdrop-blur-xl border border-primary-blue/30">
            <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
        </div>
        
        <div className="max-w-xl mx-auto space-y-4">
          <h2 className="text-3xl font-black text-white">Advanced AI Personal Assistant</h2>
          <p className="text-slate-400">
            Experience peak efficiency with our real-time pose estimation engine. 
            Track every movement with sub-millisecond precision to optimize your form and speed.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="glass-card p-6 border-white/5 text-left group hover:border-primary-blue/30 transition-colors">
            <div className="w-10 h-10 bg-primary-blue/10 rounded-lg flex items-center justify-center text-primary-blue mb-4">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h4 className="font-bold text-white mb-1">Efficiency Tracking</h4>
            <p className="text-xs text-slate-500">Analyze energy expenditure and movement economy.</p>
          </div>
          
          <div className="glass-card p-6 border-white/5 text-left group hover:border-primary-green/30 transition-colors">
            <div className="w-10 h-10 bg-primary-green/10 rounded-lg flex items-center justify-center text-primary-green mb-4">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h4 className="font-bold text-white mb-1">Speed Optimization</h4>
            <p className="text-xs text-slate-500">Real-time velocity tracking for explosive performance.</p>
          </div>

          <div className="glass-card p-6 border-white/5 text-left group hover:border-primary-blue/30 transition-colors">
            <div className="w-10 h-10 bg-primary-blue/10 rounded-lg flex items-center justify-center text-primary-blue mb-4">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h4 className="font-bold text-white mb-1">Skill Precision</h4>
            <p className="text-xs text-slate-500">ML-driven form correction and technical analysis.</p>
          </div>
        </div>
      </div>

      <div className="glass-card p-8 bg-gradient-to-r from-primary-blue/5 to-primary-green/5 border-white/5 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="text-left">
          <h3 className="text-xl font-bold text-white mb-1">Strategic Performance Export</h3>
          <p className="text-sm text-slate-500">Download the full performance data for all global athletes in a single report.</p>
        </div>
        <button 
          onClick={handleGlobalExport}
          disabled={isExporting}
          className="btn-primary whitespace-nowrap flex items-center gap-2"
        >
          {isExporting ? (
            <div className="w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin"></div>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          )}
          {isExporting ? 'Preparing...' : 'Export Global Leaderboard (CSV)'}
        </button>
      </div>
    </div>
  );
};

export default FitnessPage;
