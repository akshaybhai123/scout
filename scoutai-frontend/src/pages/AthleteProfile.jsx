import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getAthlete, getAthleteHistory, getPdfUrl } from '../api/scoutApi';
import ScoreCard from '../components/ScoreCard';
import MetricsRadar from '../components/MetricsRadar';
import { motion } from 'framer-motion';

const AthleteProfile = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: athlete, isLoading: athleteLoading } = useQuery({
    queryKey: ['athlete', id],
    queryFn: () => getAthlete(id).then(res => res.data),
  });

  const { data: history, isLoading: historyLoading } = useQuery({
    queryKey: ['athleteHistory', id],
    queryFn: () => getAthleteHistory(id).then(res => res.data.history || []),
  });

  if (athleteLoading || historyLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-12 h-12 border-4 border-primary-blue/20 border-t-primary-blue rounded-full animate-spin"></div>
      </div>
    );
  }

  const latestJob = history && history.length > 0 ? history[0] : null;
  const latestAssessment = latestJob?.result || null;
  const metrics = latestAssessment?.metrics || {};
  const breakdown = latestAssessment?.breakdown || {};

  return (
    <div className="py-12 space-y-12 pb-32">
      {/* Header Info */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
           <div className="flex items-center gap-3 mb-2">
             <span className="px-3 py-1 bg-primary-blue/10 text-primary-blue text-[10px] font-black uppercase tracking-widest rounded-full">
               {athlete?.sport}
             </span>
             <span className="text-slate-500 text-xs">ID: #{athlete?.id}</span>
           </div>
           <h1 className="text-5xl font-black text-white">{athlete?.name}</h1>
           <div className="flex items-center gap-4 mt-2">
             <p className="text-slate-500 text-lg">{athlete?.region} • Age {athlete?.age}</p>
             {latestAssessment?.jersey_number && (
               <span className="bg-white/10 px-3 py-1 rounded-lg border border-white/10 text-primary-blue font-black tracking-tighter text-xl">
                 #{latestAssessment.jersey_number}
               </span>
             )}
           </div>
        </div>
        <div className="flex gap-4">
             <Link 
               to={`/compare?a1=${athlete?.id}`}
               className="btn-secondary flex items-center gap-2 border-primary-blue/30 text-primary-blue hover:bg-primary-blue/5"
             >
               <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" /></svg>
               Compare Performance
             </Link>
           {latestAssessment && (
             <a 
               href={getPdfUrl(latestAssessment.id)} 
               target="_blank" 
               rel="noopener noreferrer"
               className="btn-secondary flex items-center gap-2"
             >
               <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
               Download Report
             </a>
           )}
           <button className="btn-primary">Connect with Scout</button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Overall Score */}
        <ScoreCard 
          score={latestAssessment?.talent_score || 0} 
          grade={latestAssessment?.grade} 
        />

        {/* Center: Attribute Radar */}
        <MetricsRadar metrics={breakdown} />

        {/* Right: AI Summary */}
        <div className="glass-card p-8 flex flex-col justify-between">
           <div>
             <h3 className="text-slate-400 text-sm font-medium mb-6 uppercase tracking-widest">AI Intelligence Summary</h3>
             <div className="relative">
                <svg className="absolute -left-2 -top-2 w-8 h-8 text-primary-blue opacity-20" fill="currentColor" viewBox="0 0 24 24"><path d="M14.017 21L14.017 18C14.017 16.8954 14.9124 16 16.017 16H19.017C19.5693 16 20.017 15.5523 20.017 15V9C20.017 8.44772 19.5693 8 19.017 8H15.017C14.4647 8 14.017 8.44772 14.017 9V11.5147C14.017 12.0451 13.8063 12.5538 13.4312 12.9289L10.017 16.3431V21H14.017ZM6.017 21L6.017 18C6.017 16.8954 6.91243 16 8.017 16H11.017C11.5693 16 12.017 15.5523 12.017 15V9C12.017 8.44772 11.5693 8 11.017 8H7.017C6.46472 8 6.017 8.44772 6.017 9V11.5147C6.017 12.0451 5.80628 12.5538 5.43118 12.9289L2.017 16.3431V21H6.017Z"/></svg>
                <p className="text-slate-200 text-xl leading-relaxed italic font-medium pl-6">
                  {latestAssessment?.ai_summary || "No assessment data available yet. Please complete a performance upload."}
                </p>
             </div>
           </div>
           
           <div className="mt-8 pt-8 border-t border-white/5 flex items-center justify-between">
              <div className="flex -space-x-2">
                 {[1,2,3].map(i => (
                   <div key={i} className="w-8 h-8 rounded-full border-2 border-background bg-slate-800"></div>
                 ))}
                 <div className="w-8 h-8 rounded-full border-2 border-background bg-primary-blue flex items-center justify-center text-[10px] font-bold text-black">+14</div>
              </div>
              <span className="text-xs text-slate-500 font-bold uppercase tracking-widest">Scouts interested</span>
           </div>
        </div>
      </div>

      {/* Raw Metrics & History */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
         <div className="glass-card p-8">
            <h3 className="text-slate-400 text-sm font-medium mb-8 uppercase tracking-widest border-b border-white/5 pb-4">Detailed Metrics</h3>
            <div className="grid grid-cols-2 gap-8">
               {Object.entries(metrics).map(([key, value]) => (
                 <div key={key}>
                    <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">{key.replace('_', ' ')}</p>
                    <p className="text-3xl font-black text-white">{value}</p>
                 </div>
               ))}
            </div>

            {latestAssessment?.scoreboard_text && (
              <div className="mt-8 p-4 bg-black/40 rounded-xl border border-white/5">
                <p className="text-[10px] font-black uppercase text-slate-500 mb-2 tracking-widest">Scoreboard OCR</p>
                <p className="text-slate-300 italic font-mono text-sm leading-relaxed">{latestAssessment.scoreboard_text}</p>
              </div>
            )}
         </div>

         <div className="glass-card p-8">
            <h3 className="text-slate-400 text-sm font-medium mb-8 uppercase tracking-widest border-b border-white/5 pb-4">Assessment History</h3>
            <div className="space-y-4">
                {history?.slice(0, 5).map((job, i) => (
                  <div key={job.job_id} className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/5 group hover:border-primary-blue/30 transition-all">
                     <div>
                       <p className="text-white font-bold">{new Date(job.created_at).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</p>
                       <p className="text-xs text-slate-500 uppercase font-black tracking-widest">Score: {job.result?.talent_score || 'N/A'}</p>
                     </div>
                     <div className={`px-3 py-1 rounded-full text-[10px] font-black ${
                        job.result?.grade === 'Elite' ? 'bg-primary-green/20 text-primary-green' : 'bg-primary-blue/20 text-primary-blue'
                     }`}>
                       {job.result?.grade || job.status}
                     </div>
                  </div>
                ))}
            </div>
         </div>
      </div>
    </div>
  );
};

export default AthleteProfile;
