import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { getLeaderboard, getPdfUrl, deleteAthlete } from '../api/scoutApi';
import { Link } from 'react-router-dom';

const LeaderBoard = ({ limit = 10, sport = '' }) => {
  const { data: athletes, isLoading } = useQuery({
    queryKey: ['leaderboard', sport, limit],
    queryFn: () => getLeaderboard({ limit, sport }).then(res => res.data),
  });

  const queryClient = useQueryClient();

  const handleDelete = async (e, id, name) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (window.confirm(`Are you sure you want to permanently delete athlete "${name}" and all their performance data?`)) {
      try {
        await deleteAthlete(id);
        queryClient.invalidateQueries(['leaderboard']);
      } catch (error) {
        console.error("Delete failed", error);
        alert("Failed to delete athlete. Please try again.");
      }
    }
  };

  const exportToCSV = () => {
    if (!athletes) return;
    const headers = "Rank,Name,Sport,Age,Region,Talent Score,Grade\n";
    const csvContent = "data:text/csv;charset=utf-8," + headers + 
      athletes.map(a => `${a.rank},"${a.name}",${a.sport},${a.age},"${a.region}",${a.talent_score},${a.grade}`).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `leaderboard_${sport || 'global'}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3, 4, 5].map(i => (
          <div key={i} className="h-16 w-full glass-card animate-pulse opacity-20"></div>
        ))}
      </div>
    );
  }

  return (
    <div className="w-full overflow-hidden">
      <div className="flex justify-between items-center px-6 py-4 bg-white/2">
        <h3 className="text-xs font-black uppercase tracking-widest text-slate-500">Rankings Overview</h3>
        <button 
          onClick={exportToCSV}
          className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-primary-blue hover:text-white transition-colors bg-primary-blue/10 px-3 py-1.5 rounded-lg border border-primary-blue/20"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Export CSV
        </button>
      </div>

      <div className="w-full overflow-x-auto">
        <div className="min-w-[750px]">
          <div className="grid grid-cols-12 gap-4 px-6 py-4 text-[10px] font-black uppercase tracking-widest text-slate-500 border-b border-white/5">
            <div className="col-span-1">#</div>
            <div className="col-span-4">Athlete / Sport</div>
            <div className="col-span-3 text-center">Talent Score</div>
            <div className="col-span-2 text-center">Grade</div>
            <div className="col-span-2 text-right flex justify-end">Actions</div>
          </div>
          
          <div className="divide-y divide-white/5">
            <AnimatePresence>
              {athletes?.map((athlete, index) => (
                <motion.div
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: index * 0.05 }}
                  key={athlete.athlete_id}
                  className="group"
                >
                  <div className="grid grid-cols-12 gap-4 px-6 py-5 items-center hover:bg-white/5 transition-all">
                    <div className="col-span-1 font-black text-slate-600 group-hover:text-primary-blue transition-colors">
                      {index + 1}
                    </div>
                    <Link to={`/athlete/${athlete.athlete_id}`} className="col-span-4 cursor-pointer">
                      <p className="text-white font-bold group-hover:text-primary-blue transition-colors">{athlete.name}</p>
                      <p className="text-[10px] text-slate-500 uppercase tracking-widest font-black">{athlete.sport}</p>
                    </Link>
                    <div className="col-span-3">
                      <div className="flex flex-col items-center gap-1">
                        <span className="text-xl font-black text-white">{athlete.talent_score || 0}</span>
                        <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-primary-blue transition-all duration-1000" 
                            style={{ width: `${athlete.talent_score}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                    <div className="col-span-2 text-center">
                      <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest flex items-center justify-center ${
                        athlete.grade === 'Elite' ? 'bg-primary-green/20 text-primary-green shadow-[0_0_15px_rgba(0,255,136,0.1)]' : 
                        athlete.grade === 'Advanced' ? 'bg-primary-blue/20 text-primary-blue' : 
                        'bg-slate-800 text-slate-400'
                      }`}>
                        {athlete.grade || 'Evaluating'}
                      </span>
                    </div>
                    <div className="col-span-2 text-right flex justify-end items-center gap-2">
                      <button 
                        onClick={(e) => handleDelete(e, athlete.athlete_id, athlete.name)}
                        className="p-2 rounded-lg bg-red-500/10 border border-red-500/20 text-red-500 hover:bg-red-500 hover:text-white transition-all"
                        title="Delete Athlete"
                      >
                        <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                      <a 
                        href={getPdfUrl(athlete.result_id)} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="inline-flex items-center justify-center p-2 rounded-lg bg-white/5 border border-white/10 text-slate-400 hover:text-primary-blue hover:border-primary-blue/30 transition-all flex-shrink-0"
                        title="Download individual Report"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                      </a>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeaderBoard;
